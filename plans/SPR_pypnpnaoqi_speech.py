import os
import sys

try:
    sys.path.insert(0, os.getenv('PNP_HOME')+'/PNPnaoqi/py')
except:
    print "Please set PNP_HOME environment variable to PetriNetPlans folder."
    sys.exit(1)

import pnp_cmd_naoqi
from pnp_cmd_naoqi import *

def load_semantic_info():
    sem_locations = eval( p.memory_service.getData("/semantic_info/locations") )

def get_tosay(interpretations):
    to_say = ""
    for inter in interpretations:
        # questions
        if "q" in inter.keys():
                to_say = inter["a"]
                break
        # whereis
        if "whereis" in inter.keys():
            if "spotted" in inter["requires"]["location"].keys():
                location_spot = inter["requires"]["location"]["spotted"]["name"]
                for sem_room in sem_locations:
                    for sem_location in sem_rooms["locationList"]:
                        if sem_location["name"] == location_spot:
                            to_say = "The " + location_spot + " is in the " + sem_rooms["name"]
                            break
        # howmanydoors


    return to_say.replace(" ", "_")

def waitAndUnderstand():
    p.exec_action("asrenable", "")
    p.exec_action("understandcommand", "SPR", interrupt="timeout_30")
    p.exec_action("asrenable", "off")

    try:
        interpretations = eval(p.memory_service.getData("CommandInterpretation"))
        print interpretations
    except:
        return

    tosay = get_tosay(interpretations)

    if tosay != "":
        p.exec_action("say", tosay)
    else:
        #p.exec_action("wait","3")
        p.exec_action('say','Sorry,_I_did_not_understand_your_question')

p = PNPCmd()

p.begin()

#p.exec_action('posture', 'stand')

load_semantic_info()

###### GROUP DESCRIPTION #######


p.exec_action("say", "hello")

p.exec_action("say", "I_want_to_play_a_riddle_game,_I_will_give_you_some_seconds_to_get_ready.")

p.exec_action('headpose', '0_-10')

p.exec_action("wait","10")

p.exec_action('turn', '180')

p.exec_action("wait","5")

p.exec_action("say","lookatme")

p.exec_action("wait","1")

p.exec_action("groupdescription", "",interrupt="timeout_30")

p.exec_action("wait","1")

p.exec_action("say","Who_wants_to_play")


p.exec_action("waitfor","personhere")



p.exec_action("say","Hello._Go_for_the_question.")

waitAndUnderstand()
waitAndUnderstand()
waitAndUnderstand()
waitAndUnderstand()
waitAndUnderstand()

#p.exec_action("wait","3")
#p.exec_action('say','Sorry,_I_did_not_understand_question_2')
#
#p.exec_action("wait","3")
#p.exec_action('say','Sorry,_I_did_not_understand_question_3')
#
#p.exec_action("wait","3")
#p.exec_action('say','Sorry,_I_did_not_understand_question_4')
#
#p.exec_action("wait","3")
#p.exec_action('say','Sorry,_I_did_not_understand_question_5')


p.exec_action("wait","1")
p.exec_action('say','Lets_start_the_blind_game.')


###### BLIND GAME #######

#Question 1
p.exec_action('say','Ask_me_a_question')
p.exec_action("wait","1")



while (not p.get_condition('sounddetected')):
    time.sleep(0.5)

p.exec_action('turn', '^AngleSound')

p.exec_action('say','Sorry,_I_did_not_understand_question_1')

p.exec_action("wait","1")


#Question 2
p.exec_action('say','Ask_me_another_question')

while (not p.get_condition('sounddetected')):
    time.sleep(0.5)

p.exec_action('turn', '^AngleSound')

p.exec_action('say','Sorry,_I_did_not_understand_question_2')

p.exec_action("wait","1")


#Question 3
p.exec_action('say','Ask_me_another_question')

while (not p.get_condition('sounddetected')):
    time.sleep(0.5)

p.exec_action('turn', '^AngleSound')

p.exec_action('say','Sorry,_I_did_not_understand_question_3')

p.exec_action("wait","1")


#Question 4
p.exec_action('say','Ask_me_another_question')

while (not p.get_condition('sounddetected')):
    time.sleep(0.5)

p.exec_action('turn', '^AngleSound')

p.exec_action('say','Sorry,_I_did_not_understand_question_4')

p.exec_action("wait","1")


#Question 5
p.exec_action('say','Ask_me_another_question')

while (not p.get_condition('sounddetected')):
    time.sleep(0.5)

p.exec_action('turn', '^AngleSound')

p.exec_action('say','Sorry,_I_did_not_understand_question_5')

p.exec_action("wait","1")


p.exec_action("say", "Bye_mate")




p.end()
