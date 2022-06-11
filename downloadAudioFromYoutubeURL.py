from concurrent.futures import thread
import ffmpeg
import os
from enum import Enum

from youtube_dl import YoutubeDL as ytdl

import PyQt5.QtWidgets as qtw 
import PyQt5.QtGui as qtg

import threading
import time
from PyQt5.QtCore import QObject, QThread, pyqtSignal

class Worker(QObject):
	message = pyqtSignal(str)
	progress = pyqtSignal(int)

	def updateProgress(self, p):
		self.progress.emit(p)
	
	def updateMessage(self, msg):
		self.message.emit(msg)
	

class DownloadOption(Enum):
	OK		= 1
	Error	= 0

class MainWindow(qtw.QWidget, QObject):
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
		# self.textLabel.setFont(qtg.QFont('Helevtica', 18))
		self.layout().addWidget(self.textLabel)

		hbox = qtw.QHBoxLayout()
		self.videoCheckB = qtw.QCheckBox("Video")
		self.videoCheckB.setChecked(False)
		self.audioCheckb = qtw.QCheckBox("Audio")
		self.audioCheckb.setChecked(True)
		self.needConvertCheckb = qtw.QCheckBox("Convert")
		self.needConvertCheckb.setChecked(True)
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
		self.layout().addWidget(self.progressBar)

		# create a textfield
		self.textField = qtw.QLineEdit()
		self.textField.setObjectName("ytLink")
		self.textField.setText("https://youtu.be/NDFeKOLDcfc") # dummy video
		self.layout().addWidget(self.textField)

		# create a button
		self.button = qtw.QPushButton("Download", clicked = lambda: self.startDownload())
		self.layout().addWidget(self.button)

		self.UIWorker = Worker()
		self.setupWorker()
		self.tempCnt = 1

		self.show()
	
	def updateProgress(self, msg):
		self.textLabel.setText(msg)
	
	def updateTextWithProgress(self, percentage):
		self.progressBar.setValue(percentage)
		if self.tempCnt % 1:
			self.textLabel.setText(f"({percentage:02}%) Downloading .")
		elif self.tempCnt % 2:
			self.textLabel.setText(f"({percentage:02}%) Downloading ..")
		elif self.tempCnt % 3:
			self.textLabel.setText(f"({percentage:02}%) Downloading ...")
		else:
			self.tempCnt = 0
			self.textLabel.setText(f"({percentage:02}%) Downloading .")
		self.tempCnt += 1

	def setupWorker(self):
		self.UIWorker.message.connect(self.updateProgress)
		self.UIWorker.progress.connect(self.updateTextWithProgress)

	def startDownload(self):
		youtube_url = self.textField.text()

		self.downloadTask = threading.Thread(target=self.donwloader, args=(youtube_url,))
		self.downloadTask.start()

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

		ytOption['format'] = dlType
		ytOption['progress_hooks'] = [self.my_hook]

		return ytOption

	def my_hook(self, d):
		if d['status'] == 'finished':
			self.UIWorker.updateMessage("Done!")
			self.fileName = d['filename']

		if d['status'] == 'downloading':
			percen = d['_percent_str'].replace('%','')
			percen_int = int(float(percen))
			self.UIWorker.updateProgress(percen_int)

	def donwloader(self, URL):
		self.button.setEnabled(False)
		msg = "Prepare download"
		if "https" in URL:
			try:
				self.UIWorker.updateMessage(msg)
				audio_downloader = ytdl(self.findDownloadType())
				audio_downloader.extract_info(URL)
			except :
				msg = "Download error!"
				self.UIWorker.updateMessage(msg)
			finally:
				if self.needConvertCheckb.isChecked():
					if self.extensionText.text() not in self.fileName:
						self.convertFileTo(self.fileName)
				else:
					self.button.setEnabled(True)
		else:
			msg = "Incorrect Links!"
			self.UIWorker.updateMessage(msg)

	def convertFileTo(self, file):
		self.UIWorker.updateMessage("Converting files")
		outputFile = os.path.splitext(file)[0]+self.extensionText.text()
		
		stream = ffmpeg.input(file)
		stream = ffmpeg.output(stream, outputFile)
		try:
			ffmpeg.run(stream)
			#remove original file
			os.remove(file)

			self.UIWorker.updateMessage("Finished!")
		except:
			self.UIWorker.updateMessage("Convert Fail!")
		
		self.button.setEnabled(True)

def main():
	app = qtw.QApplication([])
	mainW = MainWindow()
	app.exec_()

if __name__ == '__main__':
	main()