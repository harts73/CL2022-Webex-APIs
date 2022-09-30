import os
import sys
import urllib.parse
import qrcode
from PyQt6.QtWebEngineWidgets import *
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QMessageBox, QListWidget, QMainWindow, QStackedLayout
from PyQt6.QtGui import QIcon, QPixmap, QImage, QPainter
import PyQt6.QtCore as QtCore
import requests
import time


# Example of how to use Login with Webex to authenticate a device E.g. TV.
# Our scope in this one is simply to be able to read recordings for the logged in user.


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
        painter.fillRect((col + self.border) * self.box_size, (row + self.border) * self.box_size, self.box_size,
                         self.box_size, QtCore.Qt.GlobalColor.black)

    def save(self, stream, kind=None):
        pass


# This is where we create the pyqt app. not going to be MVC but all chucked in together for speed
class App(QMainWindow):

	def __init__(self, ci=None, cs=None, rd=None, parent=None):
		super(App, self).__init__(parent)
		self.layout_for_wids = QStackedLayout()
		self.qr_widget = QWidget()
		self.recording_widget = QWidget()
		self.new_window = None
		self.ci = ci
		self.cs = cs
		self.rd = rd
		self.auth_interval = None
		self.auth_device_code = None
		self.device_token = None
		self.all_recordings = []
		self.title = 'Login with Webex - Device Flow'
		self.left = 10
		self.top = 10
		self.width = 800
		self.height = 600
		self.initUI()

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
				webex_token_request = requests.post(webex_token_url, headers=auth_headers, params=webex_token_params,auth=(self.ci, self.cs))
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

	def initUI(self):
		img2 = self.webex_qr()
		self.qr_widget.setWindowTitle(self.title)
		self.qr_widget.setGeometry(self.left, self.top, self.width, self.height)
		label = QLabel(self)
		label.setPixmap(img2)
		vbox = QVBoxLayout()
		vbox.addWidget(label)
		self.qr_widget.setLayout(vbox)
		self.qr_widget.resize(img2.width(), img2.height())
		self.recording_widget.hide()
		self.qr_widget.show()
		if self.webex_token():
			print("Got Token")
			self.listUI()
		else:
			print("No Token :-(")
			QMessageBox.information(self, "Pass Code", "Not able to obtain a token for some reason. You can exit and try again.")
			sys.exit()

	def listUI(self):
		print("In listUI")
		vbox = QVBoxLayout(self)
		list_widget = QListWidget()
		the_recordings = self.get_recording_list()
		for recording in the_recordings:
			list_widget.addItem(recording)
			print(recording)
		list_widget.itemDoubleClicked.connect(self.recording_selected)
		vbox.addWidget(list_widget)
		self.recording_widget.setLayout(vbox)
		print("We should be about to show the List of recordings")
		self.qr_widget.hide()
		self.recording_widget.show()

	def get_recording_list(self):
		# QApplication.processEvents()
		headers = {"Content-Type": "application/json","Authorization": f"Bearer {self.device_token}"}
		# just using a range i know i have some recordings.
		recordings_from = "2022-09-25T00:00:00+00:00"
		recordings_to = "2022-09-27T23:59:00+00:00"
		retrieved_recordings = []
		recording_uri = f"""from={recordings_from}&to={recordings_to}&max=10"""   # restricting 10 recordings but you could get them all using pagination
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

	def recording_selected(self, item):
		#QApplication.processEvents()
		print(self.all_recordings)
		print(f"We got {item.text()}")
		link = None
		for recording in self.all_recordings:
			if recording["title"] == item.text():
				link = recording["playback"]
				passcode = recording["passcode"]
				print(link)
				print(passcode)
				break
		if link:
			self.new_window = ViewRecording(recording=link, passcode=passcode)
			self.new_window.show()
		else:
			QMessageBox.information(self, "Pass Code","We didn't get a link for some reason.")


class ViewRecording(QMainWindow):
	def __init__(self, recording=None, passcode=None):
		super().__init__()
		message_text = f"Pass code is {passcode}"
		QMessageBox.information(self, "Pass Code", message_text)
		web = QWebEngineView()
		web.load(QtCore.QUrl(recording))
		web.show()



if __name__ == '__main__':
	redirect_uri = os.getenv("REDIRECT")
	parsed_redirect_uri = urllib.parse.quote(redirect_uri, safe="=&!")
	client_id = os.getenv("CLIENT-ID")
	client_secret = os.getenv("CLIENT-SECRET")
	app = QApplication([])
	app.setApplicationName('Login with Webex - Device Flow')
	ex = App(ci=client_id, cs=client_secret, rd=redirect_uri)
	ex.show()
	sys.exit(app.exec())
