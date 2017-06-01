

import qi
import argparse
import os 

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pip", type=str, default=os.environ['PEPPER_IP'],
                        help="Robot IP address.  On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--pport", type=int, default=9559,
                        help="Naoqi port number")
    parser.add_argument("--state", type=str, default="solitary",
                        help="Desired robot state. Choose among: disabled, solitary, interactive, safeguard")
    args = parser.parse_args()
    pip = args.pip
    pport = args.pport
    state = args.state

    #Start working session
    session = qi.Session()
    try:
        session.connect("tcp://" + pip + ":" + str(pport))
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + pip + "\" on port " + str(pport) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)


    tts_service = session.service("ALTextToSpeech")
    al_service = session.service("ALAutonomousLife")

    current_state = al_service.getState()
    print "Robot state: ", current_state

    phraseToSay = "Hello! My current state is " + current_state
    tts_service.say(phraseToSay)

    if (current_state != state):
        phraseToSay = "Changing my state to " + state
        tts_service.say(phraseToSay)

        al_service.setState(state)
        current_state = al_service.getState()
        print "Robot state: ", current_state
    else:
        phraseToSay = "Nothing to change here."
        tts_service.say(phraseToSay)


        




if __name__ == "__main__":
    main()
