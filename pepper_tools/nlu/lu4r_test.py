import qi
import argparse
import json
import sys
import os

from lu4r.client import LU4RClient

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("--pip", type=str, default=os.environ['PEPPER_IP'],
                        help="Robot IP address.  On robot or Local Naoqi: use '127.0.0.1'.")
	parser.add_argument("--pport", type=int, default=9559,
                        help="Naoqi port number")
	parser.add_argument("--lip", type=str, default="127.0.0.1",
                        help="LU4R IP address.")
	parser.add_argument("--lport", type=int, default="9001",
                        help="LU4R listening port.")
	args = parser.parse_args()
	pip = args.pip
	pport = args.pport
	lip = args.lip
	lport = args.lport

	#state = args.state

    #Start working session
	session = qi.Session()
	try:
		session.connect("tcp://" + pip + ":" + str(pport))
	except RuntimeError:
		print ("Can't connect to Naoqi at ip \"" + pip + "\" on port " + str(pport) +".\n"
			   "Please check your script arguments. Run with -h option for help.")
		sys.exit(1)

	configuration = {"bodyLanguageMode":"contextual"}
	tts_service = session.service("ALAnimatedSpeech")
	rp_service = session.service("ALRobotPosture")

	client = LU4RClient(lip, lport)

	sentence = 'could you bring me the mug'
	sentences = ['move to the kitchen','bring me the mug','take the glass']
	interpretation1 = client.parse_sentence(sentence)
	interpretation2 = client.parse_sentences(sentences)

	print interpretation1
	phraseToSay = "^start(animations/Stand/Gestures/Hey_1) Hello! ^wait(animations/Stand/Gestures/Hey_1) This is what I understood " + interpretation1 + ". Is it correct?"
	tts_service.say(phraseToSay, configuration)

if __name__ == "__main__":
	main()
