import qi
import argparse
import json
import sys
import time
import os
from speech.asr import ASR

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("--pip", type=str, default="127.0.0.1",
                        help="Robot IP address.  On robot or Local Naoqi: use '127.0.0.1'.")
	parser.add_argument("--pport", type=int, default=9559,
                        help="Naoqi port number")
	args = parser.parse_args()
	pip = args.pip
	pport = args.pport

	#state = args.state

    #Start working session
	session = qi.Session()
	try:
		session.connect("tcp://" + pip + ":" + str(pport))
	except RuntimeError:
		print ("Can't connect to Naoqi at ip \"" + pip + "\" on port " + str(pport) +".\n"
			   "Please check your script arguments. Run with -h option for help.")
		sys.exit(1)

	#AIzaSyAONQ_K4NOIGfRWXmiuXonThf2rs3XzKPY
	#AIzaSyDya-9naDiG0Dm8MVVKhQw50HmsvfZeZfE
	asr = ASR(session, 'en-US', 'AIzaSyAONQ_K4NOIGfRWXmiuXonThf2rs3XzKPY','vocabulary.txt')
	while True:
		print asr.continuousRecognition(10)
	
if __name__ == "__main__":
	main()
