import qi
import os
import argparse
import signal
from lu4r_client import LU4RClient
import slu_utils


class LanguageUnderstanding(object):
    PATH = ''
    RANKED_EVENT = "VRanked"

    def __init__(self, lip, lport, app):
        super(LanguageUnderstanding, self).__init__()

        app.start()
        session = app.session

        self.__shutdown_requested = False
        signal.signal(signal.SIGINT, self.signal_handler)

        self.lu4r_client = LU4RClient(lip, lport)
        self.memory = session.service('ALMemory')

    def start(self):
        self.ranked_sub = self.memory.subscriber(LanguageUnderstanding.RANKED_EVENT)
        self.ranked_sub_id = self.ranked_sub.signal.connect(self.callback)

        print "[" + self.__class__.__name__ + "] Subscribers:", self.memory.getSubscribers(LanguageUnderstanding.RANKED_EVENT)


    def quit(self):
        self.ranked_sub.signal.disconnect(self.ranked_sub_id)

    def callback(self, msg):
        transcriptions_dict = slu_utils.list_to_dict_w_probabilities(msg)
        best_transcription = slu_utils.pick_best(transcriptions_dict)
        print "[" + self.__class__.__name__ + "] User says: " + best_transcription
        interpretation = str(self.lu4r_client.parse_sentence(best_transcription))
        print "[" + self.__class__.__name__ + "] Interpretation: " + interpretation
        self.memory.raiseEvent("CommandInterpretations", interpretation)



    def signal_handler(self, signal, frame):
        print "[" + self.__class__.__name__ + "] Caught Ctrl+C, stopping."
        self.__shutdown_requested = True
        print "[" + self.__class__.__name__ + "] Good-bye"


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--pip", type=str, default=os.environ['PEPPER_IP'],
                        help="Robot ip address")
    parser.add_argument("-p", "--pport", type=int, default=9559,
                        help="Robot port number")
    parser.add_argument("-l", "--luar-ip", type=str, default=os.environ['LU4R_IP'],
                        help="The LU4R ip address")
    parser.add_argument("-o", "--luar-port", type=int, default=9001,
                        help="The LU4R listening port")

    args = parser.parse_args()

    try:
        # Initialize qi framework.
        connection_url = "tcp://" + args.pip + ":" + str(args.pport)
        app = qi.Application(["dialogue_manager", "--qi-url=" + connection_url], autoExit=False)
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)

    lu = LanguageUnderstanding(
        lip=args.luar_ip,
        lport=args.luar_port,
        app=app
    )

    lu.start()

    app.run()

    lu.quit()


if __name__ == "__main__":
    main()
