import ffmpeg
import os
from enum import Enum

from youtube_dl import YoutubeDL as ytdl

import PyQt5.QtWidgets as qtw 
import PyQt5.QtGui as qtg

class DownloadOption(Enum):
	OK		= 1
	Error	= 0

class MainWindow(qtw.QWidget):
	def __init__(self):
		super().__init__()
		self.fileName = ''
		# change window
		self.setWindowTitle("Youtube Downloader!")
		self.setFixedWidth(300)

		# set layout
		self.setLayout(qtw.QVBoxLayout()) # V - vertical layout

		# create a label
		self.textLabel = qtw.QLabel("Enter the URL/Link")
		# change font size of label
		self.textLabel.setFont(qtg.QFont('Helevtica', 18))
		self.layout().addWidget(self.textLabel)

		hbox = qtw.QHBoxLayout()
		self.videoCheckB = qtw.QCheckBox("Video")
		self.videoCheckB.setChecked(False)
		self.audioCheckb = qtw.QCheckBox("Audio")
		self.audioCheckb.setChecked(True)
		self.needConvertCheckb = qtw.QCheckBox("Convert")
		self.needConvertCheckb.setChecked(False)
		self.extensionText = qtw.QLineEdit()
		self.extensionText.setObjectName("extension")
		self.extensionText.setText(".mp3")
		self.extensionText.setFixedWidth(50)
		hbox.addWidget(self.videoCheckB)
		hbox.addWidget(self.audioCheckb)
		hbox.addWidget(self.needConvertCheckb)
		hbox.addWidget(self.extensionText)
		self.layout().addLayout(hbox)

		# create progress bar
		self.progressBar = qtw.QProgressBar()
		self.progressBar.setFixedWidth(270)
		# self.progressBar.setFixedHeight(5)
		self.layout().addWidget(self.progressBar)

		# create a textfield
		self.textField = qtw.QLineEdit()
		self.textField.setObjectName("ytLink")
		self.textField.setText("")
		self.layout().addWidget(self.textField)

		# create a button
		self.button = qtw.QPushButton("Download", clicked = lambda: self.startDownload())
		self.layout().addWidget(self.button)

		self.show()

	def startDownload(self):
		youtube_url = self.textField.text()
		self.findDownloadType()
		# print(f"check box: video {self.videoCheckB.isChecked()} 
		# audio {self.audioCheckb.isChecked()}")
		self.donwloader(youtube_url)

	def findDownloadType(self):
		vcb = self.videoCheckB.isChecked()
		acb = self.audioCheckb.isChecked()
		ext = self.extensionText.text()
		dlType = ''
		ytOption = {}

		if vcb and acb:
			dlType = 'best'
		elif vcb:
			dlType = 'bestvideo/best'
		elif acb:
			dlType = 'bestaudio/best[ext='+ext+']'
		else:
			return DownloadOption.Error

		ytOption['format'] = dlType
		ytOption['progress_hooks'] = [self.my_hook]

		return DownloadOption.OK, ytOption

	def my_hook(self, d):
		if d['status'] == 'finished':
			self.textLabel.setText("Done!")
			self.fileName = d['filename']

		if d['status'] == 'downloading':
			progressPercentage = d['_percent_str']
			progressPercentage = progressPercentage.replace('%','')
			progressPercentage = float(progressPercentage)
			# print(d['filename'], d['_percent_str'], d['_eta_str'])
			self.progressBar.setValue(int(progressPercentage))

	def donwloader(self, URL):
		if "https" in URL:
			self.textLabel.setText("Downloading...")
			dlOption, setting = self.findDownloadType()
			if dlOption is not DownloadOption.Error:
				try:
					audio_downloader = ytdl(setting)
					audio_downloader.extract_info(URL)
				except :
					self.textLabel.setText("Download error!")
				finally:
					if self.needConvertCheckb.isChecked():
						if self.extensionText.text() not in self.fileName:
							self.convertFileTo(self.fileName)
		else:
			self.textLabel.setText("invalid URL or links")

	def convertFileTo(self, file):
		self.textLabel.setText("Converting file..")
		outputFile = os.path.splitext(file)[0]+self.extensionText.text()
		
		stream = ffmpeg.input(file)
		stream = ffmpeg.output(stream, outputFile)
		try:
			ffmpeg.run(stream)
			#remove original file
			os.remove(file)
		except:
			self.textLabel.setText("Conversion Fail!")

def main():
	app = qtw.QApplication([])
	mainW = MainWindow()
	app.exec_()

if __name__ == '__main__':
	main()