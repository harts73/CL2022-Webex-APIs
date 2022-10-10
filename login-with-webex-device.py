from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
import PyQt6.QtCore as QtCore

import qrcode
import time
import os
import sys
import urllib.parse
import requests


class Image(qrcode.image.base.BaseImage):
	# overriding the QR Code image creation, so it is in a format that we can give straight to pyqt
	# you can ignore this code for the most part.
	def __init__(self, border, width, box_size):
		self.border = border
		self.width = width
		self.box_size = box_size
		size = (width + border * 2) * box_size
		self._image = QImage(size, size, QImage.Format.Format_RGB16)
		self._image.fill(QtCore.Qt.GlobalColor.white)

	def pixmap(self):
		return QPixmap.fromImage(self._image)

	def drawrect(self, row, col):
		painter = QPainter(self._image)
		painter.fillRect((col + self.border) * self.box_size, (row + self.border) * self.box_size, self.box_size, self.box_size, QtCore.Qt.GlobalColor.black)

	def save(self, stream, kind=None):
		pass


class MyWindow(QMainWindow):
	def __init__(self, ci=None, cs=None, rd=None, parent=None):
		super(MyWindow, self).__init__(parent)
		self.ci = ci
		self.cs = cs
		self.rd = rd
		self.auth_interval = None
		self.auth_device_code = None
		self.device_token = None
		self.all_recordings = []

		# MAIN WINDOW size
		self.setMinimumSize(800,600)

		# CENTRAL WIDGET
		self.central_wid = QWidget()
		self.layout_for_wids = QStackedLayout()

		# 2 WIDGETS
		self.wid1 = QWidget()
		link = "https://www.cisco.com"
		qr = qrcode.QRCode(version=1, box_size=10, border=5)
		qr.add_data(link)
		img2 = self.webex_qr()
		label = QLabel(self)
		label.setPixmap(img2)
		vbox = QVBoxLayout()
		vbox.addWidget(label)
		vbox.addStretch()
		self.wid1.setLayout(vbox)
		self.wid1.resize(img2.width(), img2.height())
		self.wid2 = QWidget()

		# LAYOUT CONTAINER FOR WIDGETS AND BUTTON
		# self.layout_for_wids.addWidget(self.btn_switch)
		self.layout_for_wids.addWidget(self.wid1)
		self.layout_for_wids.addWidget(self.wid2)
		# ENTERING LAYOUT
		self.central_wid.setLayout(self.layout_for_wids)
		# CHOOSE YOUR CENTRAL WIDGET
		self.setCentralWidget(self.central_wid)
		# WHICH WIDGET IS ON THE FRONT
		self.show()
		if self.webex_token():
			print("Switching widgets")
			self.switch_wids()
		else:
			print("Nothing")

	def token(self):
		QApplication.processEvents()
		time.sleep(10)
		return True

	def switch_wids(self):
		list_widget = QListWidget()
		font = QFont()
		font.setFamily("Arial")
		font.setPointSize(40)
		list_widget.setFont(font)
		the_recordings = self.get_recording_list()
		for recording in the_recordings:
			list_widget.addItem(recording)
			print(recording)
		list_widget.setMinimumSize(QtCore.QSize(1200, 700))
		vbox = QVBoxLayout()
		vbox.addWidget(list_widget)
		vbox.addStretch()
		self.wid2.setLayout(vbox)
		self.wid2.setMinimumSize(QtCore.QSize(1280, 720))
		self.wid1.hide()
		self.wid2.show()

	def webex_qr(self):
		# get the URL and create the QR code.
		webex_auth_url = f"https://webexapis.com/v1/device/authorize"
		webex_auth_params = f"client_id={self.ci}&scope=meeting%3Arecordings_read%20spark%3Akms"
		auth_headers = {"Content-Type": "application/x-www-form-urlencoded"}
		try:
			webex_auth_request = requests.post(webex_auth_url, params=webex_auth_params, headers=auth_headers)
		except:
			print(f"ERROR {webex_auth_request.status_code}  {webex_auth_request.text}")
		webex_auth_json = webex_auth_request.json()
		print(webex_auth_json)
		link = webex_auth_json["verification_uri_complete"]
		self.auth_interval = webex_auth_json["interval"]
		self.auth_device_code = webex_auth_json["device_code"]
		print(link)
		qr = qrcode.QRCode(version=1, box_size=10, border=5)
		qr.add_data(link)
		return qrcode.make(link, image_factory=Image).pixmap()

	def webex_token(self):
		webex_token_url = "https://webexapis.com/v1/device/token"
		webex_token_params = f"grant_type=urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Adevice_code&device_code={self.auth_device_code}&client_id={self.ci}"
		auth_headers = {"Content-Type": "application/x-www-form-urlencoded"}
		loops_number = 0
		# we need to allow PyQt to continue to do its thing.
		QApplication.processEvents()
		# lets loop for a while until we get an auth or it fails or timesout
		while not self.device_token:
			loops_number = loops_number + 1
			try:
				webex_token_request = requests.post(webex_token_url, headers=auth_headers, params=webex_token_params, auth=(self.ci, self.cs))
			except:
				print(f"Failed to get the token url {webex_token_request.status_code} {webex_token_request.text}")
				return False
			if webex_token_request.status_code == 200:
				token_json = webex_token_request.json()
				self.device_token = token_json["access_token"]
				print(token_json)
				return True
			elif webex_token_request.status_code == 428:
				print("we need to wait for the user still, they have 2 minutes in this script. Sleeping for 10 seconds")
				time.sleep(10)
			else:
				print(f"Some other failure{webex_token_request.status_code} {webex_token_request.text}")

			if loops_number > 10:
				print("User never completed")
				return False

	def get_recording_list(self):
		# QApplication.processEvents()
		headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.device_token}"}
		# just using a range I know I have some recordings.
		recordings_from = "2022-09-25T00:00:00+00:00"
		recordings_to = "2022-09-27T23:59:00+00:00"
		retrieved_recordings = []
		recording_uri = f"""from={recordings_from}&to={recordings_to}&max=10"""  # restricting 10 recordings but you could get them all using pagination
		parsed_recording_uri = urllib.parse.quote(recording_uri, safe="=&[]")
		# print(parsed_recording_uri)
		recordings_url = f"https://webexapis.com/v1/recordings?{parsed_recording_uri}"
		try:
			recordings_req = requests.get(recordings_url, headers=headers)
			recordings_json = recordings_req.json()
			print(recordings_req.text)
		except:
			print("Failed to get recording list")

		else:
			for recording in recordings_json["items"]:
				playback = recording["playbackUrl"]
				title = recording["topic"]
				passcode = recording["password"]
				self.all_recordings.append({"title": title, "playback": playback, "passcode": passcode})
				retrieved_recordings.append(title)
		return retrieved_recordings


if __name__ == "__main__":
	redirect_uri = os.getenv("REDIRECT")
	parsed_redirect_uri = urllib.parse.quote(redirect_uri, safe="=&!")
	client_id = os.getenv("CLIENT-ID")
	client_secret = os.getenv("CLIENT-SECRET")
	app = QApplication([])
	app.setApplicationName('Login with Webex - Device Flow')
	main = MyWindow(ci=client_id, cs=client_secret, rd=redirect_uri)
	main.resize(1280, 720)
	main.setMinimumSize(1280, 720)
	main.show()
	sys.exit(app.exec())

