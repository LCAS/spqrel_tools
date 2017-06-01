import qi
import argparse
import sys
import os
from aiml.dialogue_manager import DialogueManager


def main(session,args):
	dm = DialogueManager()
	dm.learn(args.aiml_path)
	while 1:
		s = raw_input('You: ')
		print 'Pepper: ' + dm.respond(s)

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("--pip", type=str, default="127.0.0.1",
                        help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
	parser.add_argument("--pport", type=int, default=9559,
                        help="Naoqi port number")
	parser.add_argument("--aiml_path", type=str, default="aiml/kbs", help="AIML KB path.")

	args = parser.parse_args()
	session = qi.Session()
	#try:
	#	session.connect("tcp://" + args.pip + ":" + str(args.pport))
	#except RuntimeError:
	#	print ("Can't connect to Naoqi at ip \"" + args.pip + "\" on port " + str(args.pport) +".\n"
    #           "Please check your script arguments. Run with -h option for help.")
	#	sys.exit(1)
	main(session,args)