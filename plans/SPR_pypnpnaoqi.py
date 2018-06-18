import os
import sys

try:
    sys.path.insert(0, os.getenv('PNP_HOME')+'/PNPnaoqi/py')
except:
    print "Please set PNP_HOME environment variable to PetriNetPlans folder."
    sys.exit(1)

import pnp_cmd_naoqi
from pnp_cmd_naoqi import *





p = PNPCmd()

p.begin()

#p.exec_action('posture', 'stand')



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

p.exec_action("say","Who wants to play ")


p.exec_action("waitfor","personhere")


# = eval(p.memory_service.getData("CommandInterpretation"))

p.exec_action("say","Hello._Go_for_the_question.")

p.exec_action("wait","3")
p.exec_action('say','Sorry,_I_did_not_understand_question_1')

p.exec_action("wait","3")
p.exec_action('say','Sorry,_I_did_not_understand_question_2')

p.exec_action("wait","3")
p.exec_action('say','Sorry,_I_did_not_understand_question_3')

p.exec_action("wait","3")
p.exec_action('say','Sorry,_I_did_not_understand_question_4')

p.exec_action("wait","3")
p.exec_action('say','Sorry,_I_did_not_understand_question_5')


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

p.exec_action("wait","3")


#Question 2
p.exec_action('say','Ask_me_another_question')

while (not p.get_condition('sounddetected')):
    time.sleep(0.5)

p.exec_action('turn', '^AngleSound')

p.exec_action('say','Sorry,_I_did_not_understand_question_2')

p.exec_action("wait","3")


#Question 3
p.exec_action('say','Ask_me_another_question')

while (not p.get_condition('sounddetected')):
    time.sleep(0.5)

p.exec_action('turn', '^AngleSound')

p.exec_action('say','Sorry,_I_did_not_understand_question_3')

p.exec_action("wait","3")


#Question 4
p.exec_action('say','Ask_me_another_question')

while (not p.get_condition('sounddetected')):
    time.sleep(0.5)

p.exec_action('turn', '^AngleSound')

p.exec_action('say','Sorry,_I_did_not_understand_question_4')

p.exec_action("wait","3")


#Question 5
p.exec_action('say','Ask_me_another_question')

while (not p.get_condition('sounddetected')):
    time.sleep(0.5)

p.exec_action('turn', '^AngleSound')

p.exec_action('say','Sorry,_I_did_not_understand_question_5')

p.exec_action("wait","3")


p.exec_action("say", "Bye_mate")




p.end()
