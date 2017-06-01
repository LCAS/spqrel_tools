#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

"""Example: Use ALSpeechRecognition Module"""

import qi
import argparse
import sys
import time


def main(session):
	asr_service = session.service("ALSpeechRecognition")
	asr_service.setLanguage("English")
	#asr_service.unsubscribe("Test_ASR")
	asr_service.pause(True)
	vocabulary = ["yes", "no", "please"]
	asr_service.setVocabulary(vocabulary, False)

	while True:
		asr_service.subscribe("Test_ASR")
		time.sleep(10)
		if asr_service.SpeechDetected():
			if asr_service.WordRecognized()== "yes":
				print "have a nice day"
				asr_service.unsubscribe("Test_ASR")
				break
			elif asr_service.WordRecognized()== "no":
				print "i will find some help"
				asr_service.unsubscribe("Test_ASR")
				break
			else:
				print "Can you speak louder"
				continue


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="127.0.0.1",
                        help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")

    args = parser.parse_args()
    session = qi.Session()
    try:
        session.connect("tcp://" + args.ip + ":" + str(args.port))
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)
    main(session)