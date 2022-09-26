import os
import sys
import qrcode
from PyQt6.QtWidgets import QApplication, QWidget, QLabel
from PyQt6.QtGui import QIcon, QPixmap, QImage, QPainter
import PyQt6.QtCore as QtCore
import requests

# Example of how to use Login with Webex to authenticate a device E.g. TV.
# Our scope in this one is simply to be able to read recordings for the logged in user.

# overriding the QR Code image creation, so it is in a format that we can give straight to pyqt

class Image(qrcode.image.base.BaseImage):
        def __init__(self, border, width, box_size):
				self.border = border
				self.width = width
				self.box_size = box_size
				size = (width + border * 2) * box_size
				self._image = QImage(
					size, size, QImage.Format.Format_RGB16)
				self._image.fill(QtCore.Qt.GlobalColor.white)

        def pixmap(self):
                return QPixmap.fromImage(self._image)

        def drawrect(self, row, col):
                painter = QPainter(self._image)
                painter.fillRect(
                    (col + self.border) * self.box_size,
                    (row + self.border) * self.box_size,
                    self.box_size, self.box_size,
                    QtCore.Qt.GlobalColor.black)

                def save(self, stream, kind=None):
                pass


# This is where we create the pyqt app. not going to be MVC but all chucked in together for speed
class App(QWidget):

	def __init__(self, ci=None, cs=None, rd=Node):
		super().__init__()
		self.ci = ci
		self.cs = cs
		self.rd = rd
		self.title = 'Login with Webex - Device Flow'
		self.left = 10
		self.top = 10
		self.width = 600
		self.height = 480
		self.webex_qr = self.get_qr()
		self.initUI()

	def webex_qr(self):
		# get the URL and create the QR code.
        

	def initUI(self):
		link = "https://www.cisco.com"
		qr = qrcode.QRCode(
			version=1,
			box_size=10,
			border=5)
		qr.add_data(link)
		img2 = qrcode.make(link, image_factory=Image).pixmap()
		self.setWindowTitle(self.title)
		self.setGeometry(self.left, self.top, self.width, self.height)


		# Create widget
		label = QLabel(self)
		label.setPixmap(img2)
		self.resize(img2.width(), img2.height())
		self.show()


if __name__ == '__main__':
		redirect_uri = os.getenv("REDIRECT")
		parsed_redirect_uri = urllib.parse.quote(redirect_uri, safe="=&!")
		client_id = os.getenv("CLIENT-ID")
		client_secret = os.getenv("CLIENT-SECRET")
		app = QApplication([])
		ex = App(ci=client_id,cs=client_secret,rd=redirect_uri)
		ex.show()
		sys.exit(app.exec())

