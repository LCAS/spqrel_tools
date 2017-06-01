import os
import requests
import urllib
import requests
import json
import sys

class GoogleClient:

	timeout = 10000
	url = ''
	headers = {"Content-Type": "audio/l16; rate=16000"}
	
	def __init__(self, language, key):
		q = {"output": "json", "lang": language, "key": key}
		self.url = "http://www.google.com/speech-api/v2/recognize?%s" % (urllib.urlencode(q))

	def recognize(self, file):
		try:
			transcriptions = []
			data = open(file, "rb").read()
			response = requests.post(self.url, headers=self.headers, data=data, timeout=self.timeout)
			jsonunits = response.text.split(os.linesep)
			for unit in jsonunits:
				if not unit:
					continue
				obj = json.loads(unit)
				alternatives = obj["result"]
				if len(alternatives) > 0:
					for obj in alternatives:
						results = obj["alternative"]
						for result in results:
							transcriptions.append(result["transcript"])
			return transcriptions
		except requests.exceptions.RequestException as e:
			print e
			print '[RECOGNIZE]ERROR! Unable to reach Google.'
			return 0
