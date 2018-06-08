import os
import argparse
import signal
from naoqi import ALProxy, ALBroker, ALModule
from event_abstract import *
from lu4r_client import LU4RClient
import slu_utils


class LanguageUnderstanding(EventAbstractClass):
    PATH = ''
    RANKED_EVENT = "VRanked"

    def __init__(self, ip, port, lip, lport):
        super(self.__class__, self).__init__(self, ip, port)
        self.__shutdown_requested = False
        signal.signal(signal.SIGINT, self.signal_handler)
        self.lu4r_client = LU4RClient(lip, lport)
        self.memory_proxy = ALProxy('ALMemory')

    def start(self, *args, **kwargs):
        self.subscribe(
            event=LanguageUnderstanding.RANKED_EVENT,
            callback=self.callback
        )

        print "[" + self.inst.__class__.__name__ + "] Subscribers:", self.memory.getSubscribers(LanguageUnderstanding.RANKED_EVENT)

        self._spin()

        self.unsubscribe(LanguageUnderstanding.RANKED_EVENT)
        self.broker.shutdown()

    def callback(self, *args, **kwargs):
        transcriptions_dict = slu_utils.list_to_dict_w_probabilities(args[1])
        best_transcription = slu_utils.pick_best(transcriptions_dict)
        print "[" + self.inst.__class__.__name__ + "] User says: " + best_transcription
        interpretation = str(self.lu4r_client.parse_sentence(best_transcription))
        print "[" + self.inst.__class__.__name__ + "] Interpretation: " + interpretation
        self.memory_proxy.raiseEvent("CommandInterpretations", interpretation)


    def _spin(self, *args):
        while not self.__shutdown_requested:
            for f in args:
                f()
            time.sleep(.1)

    def signal_handler(self, signal, frame):
        print "[" + self.inst.__class__.__name__ + "] Caught Ctrl+C, stopping."
        self.__shutdown_requested = True
        print "[" + self.inst.__class__.__name__ + "] Good-bye"


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--pip", type=str, default=os.environ['PEPPER_IP'],
                        help="Robot ip address")
    parser.add_argument("-p", "--pport", type=int, default=9559,
                        help="Robot port number")
    parser.add_argument("-l", "--luar-ip", type=str, os.environ['LU4R_IP'],
                        help="The LU4R ip address")
    parser.add_argument("-o", "--luar-port", type=int, default=9001,
                        help="The LU4R listening port")

    args = parser.parse_args()

    lu = LanguageUnderstanding(
        ip=args.pip,
        port=args.pport,
        lip=args.luar_ip,
        lport=args.luar_port
    )
    lu.update_globals(globals())
    lu.start()


if __name__ == "__main__":
    main()
