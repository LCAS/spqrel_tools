import os
from Kernel import Kernel
import argparse
import signal
import slu_utils
from event_abstract import *
import datetime


class DialogueManager(EventAbstractClass):
    PATH = ''
    RANKED_EVENT = "VRanked"
    DIALOGUE_REQUEST_EVENT = "DialogueVequest"
    cocktail_data = {}
    location = {}
    order_counter = 0

    def __init__(self, ip, port, aiml_path):
        super(self.__class__, self).__init__(self, ip, port)

        self.__shutdown_requested = False
        signal.signal(signal.SIGINT, self.signal_handler)

        self.kernel = Kernel()
        self.__learn(aiml_path)

    def start(self, *args, **kwargs):
        self.subscribe(
            event=DialogueManager.RANKED_EVENT,
            callback=self.ranked_callback
        )
        self.subscribe(
            event=DialogueManager.DIALOGUE_REQUEST_EVENT,
            callback=self.request_callback
        )

        print "[" + self.inst.__class__.__name__ + "] Subscribers:", self.memory.getSubscribers(
            DialogueManager.RANKED_EVENT)
        print "[" + self.inst.__class__.__name__ + "] Subscribers:", self.memory.getSubscribers(
            DialogueManager.DIALOGUE_REQUEST_EVENT)

        self._spin()

        self.unsubscribe(DialogueManager.RANKED_EVENT)
        self.unsubscribe(DialogueManager.DIALOGUE_REQUEST_EVENT)
        self.broker.shutdown()

    def ranked_callback(self, *args, **kwargs):
        transcriptions_dict = slu_utils.list_to_dict_w_probabilities(args[1])
        best_transcription = slu_utils.pick_best(transcriptions_dict)
        print "[" + self.inst.__class__.__name__ + "] User says: " + best_transcription
        reply = self.kernel.respond(best_transcription)
        self.do_something(reply)
        #print "[" + self.inst.__class__.__name__ + "] Robot says: " + reply
        #self.memory.raiseEvent("Veply", reply)

    def request_callback(self, *args, **kwargs):
        splitted = args[1].split('_')
        to_send = ' '.join(splitted)
        if 'start' in splitted:
            self.memory.raiseEvent("ASR_enable", 1)
        if 'missingdrink' in splitted:
            customer = self.cocktail_data.get(splitted[1], None)['customer']
            drink = self.cocktail_data[splitted[1]]['drink']
            to_send = 'missingdrink customer ' + customer + ' drink ' + drink + ' '+ splitted[2]
        print to_send
        reply = self.kernel.respond(to_send)
        print reply
        self.do_something(reply)


    def _spin(self, *args):
        while not self.__shutdown_requested:
            for f in args:
                f()
            time.sleep(.1)

    def signal_handler(self, signal, frame):
        print "[" + self.inst.__class__.__name__ + "] Caught Ctrl+C, stopping."
        self.__shutdown_requested = True
        print "[" + self.inst.__class__.__name__ + "] Good-bye"

    def __learn(self, path):
        for root, directories, file_names in os.walk(path):
            for filename in file_names:
                if filename.endswith('.aiml'):
                    self.kernel.learn(os.path.join(root, filename))
        print "[" + self.inst.__class__.__name__ + "] Number of categories: " + str(self.kernel.num_categories())

    def do_something(self, message):
        splitted = message.split('|')
        for submessage in splitted:
            if '[SAY]' in submessage:
                reply = submessage.replace('[SAY]', '').strip()
                print "[" + self.inst.__class__.__name__ + "] Robot says: " + reply
                self.memory.raiseEvent("Veply", reply)
            elif '[TAKEORDERDATA]' in submessage:
                data = submessage.replace('[TAKEORDERDATA]', '').replace(')', '').strip()
                customer, drink = data.split('(')
                temp = {}
                temp['drink'] = drink
                temp['customer'] = customer
                self.cocktail_data[str(self.order_counter)] = temp
                print self.cocktail_data
                self.memory.raiseEvent("DialogueVesponse", self.cocktail_data)
                self.order_counter = self.order_counter + 1
            elif '[DRINKSALTERNATIVES]' in submessage:
                data = submessage.replace('[DRINKSALTERNATIVES]', '').replace(')', '').strip()
                # search for drinks from the drinks' list
            elif '[LOOKFORDATA]' in submessage:
                data = submessage.replace('[TAKEORDERDATA]', '').strip()
                self.location['location'] = data
                self.memory.raiseEvent("DialogueVesponse", self.location)
            elif '[WHATSTHETIME]' in submessage:
                now = datetime.datetime.now()
                reply = "It's " + str(now.hour )+ " " + str(now.minute)
                print "[" + self.inst.__class__.__name__ + "] Robot says: " + reply
                self.memory.raiseEvent("Veply", reply)
            elif '[STOP]' in submessage:
                self.memory.raiseEvent("ASR_enable", 1)
            else:
                print submessage


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--pip", type=str, default="127.0.0.1",
                        help="Robot ip address")
    parser.add_argument("-p", "--pport", type=int, default=9559,
                        help="Robot port number")
    parser.add_argument("-a", "--aiml-path", type=str, default="resources/aiml_kbs/spqrel",
                        help="Path to the root folder of AIML Knowledge Base")
    args = parser.parse_args()

    dm = DialogueManager(
        ip=args.pip,
        port=args.pport,
        aiml_path=args.aiml_path
    )
    dm.update_globals(globals())
    dm.start()


if __name__ == "__main__":
    main()
