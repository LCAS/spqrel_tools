

import qi
import argparse
import sys
import os

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pip", type=str, default=os.environ['PEPPER_IP'],
                        help="Robot IP address.  On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--pport", type=int, default=9559,
                        help="Naoqi port number")
    parser.add_argument("--posture", type=str, default="Stand",
                        help="Desired robot posture. Choose among: Stand, StandZero, Crouch")
    args = parser.parse_args()
    pip = args.pip
    pport = args.pport
    posture = args.posture

    #Start working session
    session = qi.Session()
    try:
        session.connect("tcp://" + pip + ":" + str(pport))
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + pip + "\" on port " + str(pport) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)


    tts_service = session.service("ALTextToSpeech")
    rp_service = session.service("ALRobotPosture")

    current_posture = rp_service.getPosture()
    print "Robot posture: ", current_posture

    phraseToSay = "Hello! My current posture is " + current_posture
    tts_service.say(phraseToSay)

    if (current_posture != posture):
        phraseToSay = "Changing my posture to " + posture
        tts_service.say(phraseToSay)

        rp_service.goToPosture(posture,1.0)
        current_posture = rp_service.getPosture()
        print "Robot posture: ", current_posture
    else:
        phraseToSay = "Nothing to change here."
        tts_service.say(phraseToSay)







if __name__ == "__main__":
    main()
