import os
from Kernel import Kernel
from naoqi import ALProxy, ALBroker, ALModule
import argparse
import signal
import slu_utils
from event_abstract import *
import datetime
import json
from conditions import set_condition


class DialogueManager(EventAbstractClass):
    PATH = ''
    RANKED_EVENT = "VRanked"
    TABLET_ANSWER_EVENT = "TabletAnswer"
    DIALOGUE_REQUEST_EVENT = "DialogueVequest"
    cocktail_data = {}
    location = {}
    order_counter = 0

    def __init__(self, ip, port, aiml_path, drinks_path):
        super(self.__class__, self).__init__(self, ip, port)

        self.__shutdown_requested = False
        signal.signal(signal.SIGINT, self.signal_handler)

        self.memory = ALProxy("ALMemory")

        self.kernel = Kernel()
        self.__learn(aiml_path)

        self.possible_drinks = slu_utils.lines_to_list(drinks_path)

    def start(self, *args, **kwargs):
        self.subscribe(
            event=DialogueManager.RANKED_EVENT,
            callback=self.ranked_callback
        )
        self.subscribe(
            event=DialogueManager.DIALOGUE_REQUEST_EVENT,
            callback=self.request_callback
        )
        self.subscribe(
            event=DialogueManager.TABLET_ANSWER_EVENT,
            callback=self.tablet_callback
        )

        print "[" + self.inst.__class__.__name__ + "] Subscribers:", self.memory.getSubscribers(
            DialogueManager.RANKED_EVENT)
        print "[" + self.inst.__class__.__name__ + "] Subscribers:", self.memory.getSubscribers(
            DialogueManager.DIALOGUE_REQUEST_EVENT)
        print "[" + self.inst.__class__.__name__ + "] Subscribers:", self.memory.getSubscribers(
            DialogueManager.TABLET_ANSWER_EVENT)

        self._spin()

        self.unsubscribe(DialogueManager.RANKED_EVENT)
        self.unsubscribe(DialogueManager.DIALOGUE_REQUEST_EVENT)
        self.unsubscribe(DialogueManager.TABLET_ANSWER_EVENT)
        self.broker.shutdown()

    def ranked_callback(self, *args, **kwargs):
        transcriptions_dict = slu_utils.list_to_dict_w_probabilities(args[1])
        best_transcription = slu_utils.pick_best(transcriptions_dict)
        print "[" + self.inst.__class__.__name__ + "] User says: " + best_transcription
        reply = self.kernel.respond(best_transcription)
        self.do_something(reply)

    def request_callback(self, *args, **kwargs):
        splitted = args[1].split('_')
        to_send = ' '.join(splitted)
        print 'to_send: ' + to_send
        if 'start' in splitted:
            print 'Found start'
            self.memory.raiseEvent("ASR_enable", "1")
        if 'end' in splitted:
            print 'Found end'
            self.memory.raiseEvent("ASR_enable", "0")
        if 'stop' in splitted:
            print 'Found stop'
            self.memory.raiseEvent("ASR_enable", "0")
        if 'SPRinfocollected' in splitted[1]:
            try:
                crowd_info = json.loads(self.memory.getData('Humans/Crowd'))
                total = crowd_info['total']
                males = crowd_info['num_males']
                females = crowd_info['num_females']
                to_send = "say SPRinfocollected total " + total + " males " + males + " females " + females
            except:
                to_send = "say SPRinfocollected donotknow"
        if 'order' == splitted[1] or 'confirmdrink' == splitted[1] or 'confirmnotavailable' == splitted[1] or 'unknownavailable' == splitted[1]:
            try:
                self.current_user_id = splitted[2]
                self.user_profile = json.loads(self.memory.getData("Humans/Profile" + self.current_user_id))
            except:
                print 'Invalid User'
            #Need to define how to get back the names and drink
            name = self.user_profile['Name']
            drink = self.user_profile['Drink']
            to_send = 'say ' + splitted[1] + ' customer ' + name + ' drink ' + drink
        if 'unknownavailable' == splitted[0]:
            print 'Found unknownavailable'
            self.current_user_id = splitted[1]
            try:
                self.user_profile = json.loads(self.memory.getData("Humans/Profile" + self.current_user_id))
            except:
                print 'Invalid User'
            to_send = splitted[0] + ' customer ' + self.user_profile['Name'] + ' drink ' + self.user_profile['Drink'] + ' ' + splitted[2]
        if 'callpersonunavailable' == splitted[1]:
            try:
                self.profile_1 = json.loads(self.memory.getData("Humans/Profile1"))
                self.profile_2 = json.loads(self.memory.getData("Humans/Profile2"))
                self.profile_3 = json.loads(self.memory.getData("Humans/Profile3"))
                if self.profile_1['DrinkAvailability'] == 'False':
                    customer = self.profile_1['Name']
                    drink = self.profile_1['Drink']
                if self.profile_2['DrinkAvailability'] == 'False':
                    customer = self.profile_2['Name']
                    drink = self.profile_2['Drink']
                if self.profile_3['DrinkAvailability'] == 'False':
                    customer = self.profile_3['Name']
                    drink = self.profile_3['Drink']
            except:
                pass
            to_send = 'SAY CALLPERSONUNAVAILABLE CUSTOMER ' + customer + ' DRINK ' + drink
        if 'altdrink' == splitted[0]:
            print 'Found altdrink'
            try:
                self.current_user_id = splitted[1]
                self.user_profile = json.loads(self.memory.getData("Humans/Profile" + self.current_user_id))
            except:
                print 'Invalid User'
            #Need to define how to get back the names and drink
            name = self.user_profile['Name']
            to_send = splitted[0] + ' customer ' + name + ' ' + splitted[2]
        if 'fivequestions' == splitted[0]:
            to_send = splitted[0] + ' ' + splitted[2]
        reply = self.kernel.respond(to_send)
        self.do_something(reply)

    def tablet_callback(self, *args, **kwargs):
        best_transcription = args[1]
        print "[" + self.inst.__class__.__name__ + "] User says: " + best_transcription
        reply = self.kernel.respond(best_transcription)
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
                try:
                    self.person_id = self.memory.getData("Actions/personhere/PersonID")
                except:
                    self.person_id = 9999
                cocktail_data = {}
                cocktail_data['PersonID'] = self.person_id
                cocktail_data['Name'] = customer
                cocktail_data['Drink'] = drink
                self.user_profile['DrinkAvailability'] = True
                self.memory.raiseEvent("DialogueVesponse", json.dumps(cocktail_data))
            elif '[DRINKSALTERNATIVES]' in submessage:
                data = submessage.replace('[DRINKSALTERNATIVES]', '').replace(')', '').strip()
                alternatives = []
                for drink in self.possible_drinks:
                    if drink in data:
                        alternatives.append(drink)
                self.user_profile['DrinkAlternatives'] = alternatives
                self.user_profile['DrinkAvailability'] = False
                reply = 'So'
                for available_drink in alternatives:
                    reply = reply + ', ' + available_drink
                reply = reply + '. I am going to notify the alternatives.'
                self.memory.raiseEvent("Veply", reply)
                self.memory.raiseEvent("DialogueVesponse", json.dumps(self.user_profile))
                self.memory.insertData("Humans/Profile" + self.current_user_id, json.dumps(self.user_profile))
            elif '[DRINKAVAILABLE]' in submessage:
                self.user_profile['DrinkAvailability'] = True
                self.memory.raiseEvent("DialogueVesponse", json.dumps(self.user_profile))
                self.memory.insertData("Humans/Profile" + self.current_user_id, json.dumps(self.user_profile))
            elif '[LOOKFORDATA]' in submessage:
                data = submessage.replace('[LOOKFORDATA]', '').strip()
                self.location['location'] = data
                try:
                    data = str(self.memory.getData('/location_mapping/' + data)).replace("+", " ")
                except Exception as e:
                    reply = "The " + data + " is somewhere!"


                self.memory.insertData("helplocation", data)
                self.memory.raiseEvent("DialogueVesponse", json.dumps(self.location))
            elif '[OPTIONS]' in submessage:
                data = submessage.replace('[OPTIONS]', '').strip()
                data = data.replace('  ', ' ')
                data = data.replace(' ', '+')
                self.memory.raiseEvent('AnswerOptions', 'speechbtn_' + data)
            elif '[STOPFOLLOWING]' in submessage:
                self.memory.raiseEvent("ASR_enable", "0")
                self.memory.raiseEvent("DialogueVesponse", '[STOPFOLLOWING]')
                set_condition(self.memory, "stopfollowing", "true")
            elif '[WHATSTHETIME]' in submessage:
                now = datetime.datetime.now()
                reply = "It's " + str(now.hour) + " " + str(now.minute)
                print "[" + self.inst.__class__.__name__ + "] Robot says: " + reply
                self.memory.raiseEvent("DialogueVesponse", '[WHATSTHETIME]')
                self.memory.raiseEvent("Veply", reply)
            elif '[STOP]' in submessage:
                self.memory.raiseEvent("DialogueVesponse", "Action stopped")
                self.memory.raiseEvent("ASR_enable", "0")
                set_condition(self.memory, "stopfollowing", "false")
            elif '[STOPASR]' in submessage:
                set_condition(self.memory, "stopfollowing", "false")
                self.memory.raiseEvent("DialogueVesponse", "Action stopped")
                self.memory.raiseEvent("ASR_enable", "0")
            elif '[WHEREIS]' in submessage:
                data = submessage.replace('[WHEREIS]', '').strip().replace(" ", "+")
                try:
                    location = str(self.memory.getData('/location_mapping/' + data)).replace("+", " ")
                    reply = "The " + data.replace("+", " ") + " is in the " + location
                except Exception as e:
                    reply = "The " + data.replace("+", " ") + " is somewhere!"
                self.memory.raiseEvent("DialogueVesponse", submessage)
                self.memory.raiseEvent("Veply", reply)
            elif '[HOWMANY]' in submessage:
                data = submessage.replace('[HOWMANY]', '')
                splitted = data.split("#")
                reply = "There are multiple " + splitted[0] + " in the " + splitted[1]
                self.memory.raiseEvent("DialogueVesponse", submessage)
                self.memory.raiseEvent("Veply", reply)
            elif '[CROWD]' in submessage:
                data = submessage.replace('[CROWD]', '')
                try:
                    crowd_info = json.loads(self.memory.getData('Humans/Peoplesummary'))
                    total = crowd_info['total']
                    num_males = crowd_info['num_males']
                    num_females = crowd_info['num_females']
                    if total == 0:
                        reply = "I don't know how many people there are"
                    else:
                        reply = "I may be wrong, but I see " + total + " people: " + num_males + " are males and " + num_females + " are females."
                except Exception as e:
                    reply = "I don't know how many people there are"
                self.memory.raiseEvent("DialogueVesponse", submessage)
                self.memory.raiseEvent("Veply", reply)
            elif '[CHILDREN]' in submessage:
                data = submessage.replace('[CHILDREN]', '')
                reply = "I don't know how many children there are"
                self.memory.raiseEvent("DialogueVesponse", submessage)
                self.memory.raiseEvent("Veply", reply)
            elif '[MALE]' in submessage:
                data = submessage.replace('[MALE]', '')
                try:
                    crowd_info = json.loads(self.memory.getData('Humans/Peoplesummary'))
                    total = crowd_info['total']
                    num_males = crowd_info['num_males']
                    num_females = crowd_info['num_females']
                    if total == 0:
                        reply = "I don't know how many males there are"
                    else:
                        reply = "I may be wrong, but I see " + total + " people: " + num_males + " are males and " + num_females + " are females."
                except Exception as e:
                    reply = "I don't know how many males there are"
                self.memory.raiseEvent("DialogueVesponse", submessage)
                self.memory.raiseEvent("Veply", reply)
            elif '[FEMALE]' in submessage:
                data = submessage.replace('[FEMALE]', '')
                try:
                    crowd_info = json.loads(self.memory.getData('Humans/Peoplesummary'))
                    total = crowd_info['total']
                    num_males = crowd_info['num_males']
                    num_females = crowd_info['num_females']
                    if total == 0:
                        reply = "I don't know how many females there are"
                    else:
                        reply = "I may be wrong, but I see " + total + " people: " + num_males + " are males and " + num_females + " are females."
                except Exception as e:
                    reply = "I don't know how many females there are"
                self.memory.raiseEvent("DialogueVesponse", submessage)
                self.memory.raiseEvent("Veply", reply)
            elif '[WAVING]' in submessage:
                data = submessage.replace('[WAVING]', '')
                reply = "I don't know how many people are waving arms"
                self.memory.raiseEvent("DialogueVesponse", submessage)
                self.memory.raiseEvent("Veply", reply)
            elif '[RISING]' in submessage:
                data = submessage.replace('[RISING]', '')
                reply = "I don't know how many people are rising arms"
                self.memory.raiseEvent("DialogueVesponse", submessage)
                self.memory.raiseEvent("Veply", reply)
            elif '[STANDING]' in submessage:
                data = submessage.replace('[STANDING]', '')
                try:
                    crowd_info = json.loads(self.memory.getData('Humans/Peoplesummary'))
                    total = crowd_info['total']
                    if total == 0:
                        reply = "I don't know how many people are standing"
                    else:
                        reply = "I see " + total + " people that are standing."
                except Exception as e:
                    reply = "I don't know how many people are standing"
                self.memory.raiseEvent("DialogueVesponse", submessage)
                self.memory.raiseEvent("Veply", reply)
            elif '[SITTING]' in submessage:
                data = submessage.replace('[SITTING]', '')
                reply = "I don't know how many people are sitting"
                self.memory.raiseEvent("DialogueVesponse", submessage)
                self.memory.raiseEvent("Veply", reply)
            elif '[LYING]' in submessage:
                data = submessage.replace('[LYING]', '')
                reply = "I don't know how many people are lying"
                self.memory.raiseEvent("DialogueVesponse", submessage)
                self.memory.raiseEvent("Veply", reply)
            elif '[HOWOLD]' in submessage:
                data = submessage.replace('[HOWOLD]', '')
                try:
                    person_info = json.loads(self.memory.getData('Humans/Peoplesummary'))
                    age = person_info['Age']
                    if total == 0:
                        reply = "You are older than me, I guess..."
                    else:
                        reply = "I may be wrong, but you could be " + age + " years old. Don't you?"
                except Exception as e:
                    reply = "You are older than me, I guess..."
                self.memory.raiseEvent("DialogueVesponse", submessage)
                self.memory.raiseEvent("Veply", reply)
            elif '[GENDER]' in submessage:
                data = submessage.replace('[GENDER]', '')
                reply = "Man? Woman? I couldn't tell, sorry!"
                self.memory.raiseEvent("DialogueVesponse", submessage)
                self.memory.raiseEvent("Veply", reply)
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
    parser.add_argument("-d", "--drinks-path", type=str, default="resources/drinks_dictionary.txt",
                        help="Path to a file containing the list of drinks")
    args = parser.parse_args()

    dm = DialogueManager(
        ip=args.pip,
        port=args.pport,
        aiml_path=args.aiml_path,
        drinks_path=args.drinks_path
    )
    dm.update_globals(globals())
    dm.start()


if __name__ == "__main__":
    main()
