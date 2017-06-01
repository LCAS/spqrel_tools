import os
import requests
import urllib
import requests
import json
import sys
import tempfile
import time
from speech.google_client import GoogleClient

class ASR:

	recognizing = False
	google_client = None
	nuance_client = None
	mem_service = None
	audio_recorder = None
	leds_controller = None
	vocabulary = []
	channels = [0,0,1,0] #Left, Right, Front, Rear
	filepath = ''

	
	def __init__(self, session, language, key, vocabulary_file):
		self.google_client = GoogleClient(language, key)
		self.audio_recorder = session.service("ALAudioRecorder")
		self.nuance_client = session.service("ALSpeechRecognition")
		self.mem_service = session.service("ALMemory")
		self.nuance_client.pause(True)
		with open(vocabulary_file) as f:
			self.vocabulary = f.readlines()
		self.vocabulary = [x.strip() for x in self.vocabulary]
		self.nuance_client.setLanguage("English")
		self.nuance_client.setVocabulary(self.vocabulary, False)
		#self.leds_controller = ALProxy("ALLeds")
	
	def continuousRecognition(self,timeout):
		results = []
		while not results:
			self.startRecognition()
			time.sleep(timeout)
			results = self.stopRecognition()
			return results

	def startRecognition(self):
		self.nuance_client.pause(False)
		self.nuance_client.subscribe('NuanceASR')
		self.audio_recorder.stopMicrophonesRecording()
		if self.recognizing:
			print '[ASR] Warning! Already recognizing..'
			return 0
		else:
			self.recognizing = True
			#self.nuance_client.subscribe("Test_ASR")
			self.filepath = '/home/nao/test.wav'
			self.audio_recorder.startMicrophonesRecording(self.filepath, "wav", 16000, self.channels)
			print '[ASR] Recording..'
			return 1
	
	def stopRecognition(self):
		self.nuance_client.pause(True)
		self.nuance_client.unsubscribe('NuanceASR')
		if self.recognizing:
			self.recognizing = False
			self.audio_recorder.stopMicrophonesRecording()
			print '[ASR] Recognizing..'
			google_results = self.google_client.recognize(os.path.abspath(self.filepath))
			nuance_results = self.mem_service.getData("WordRecognized")[0]
			google_results.append(nuance_results)
			return google_results
			
		else:
			print '[ASR] Warning! Already stopped..'
			return 0
