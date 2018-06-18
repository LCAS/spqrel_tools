import os
import sys

try:
    sys.path.insert(0, os.getenv('PNP_HOME')+'/PNPnaoqi/py')
except:
    print "Please set PNP_HOME environment variable to PetriNetPlans folder."
    sys.exit(1)

import pnp_cmd_naoqi
from pnp_cmd_naoqi import *


FAKE = True

p = PNPCmd()

p.begin()
p.exec_action('setpose', '11.5_8.6_0')

p.exec_action('taskstep', 'waiting')
p.exec_action('modiminit', 'cocktailparty')
p.exec_action('interact', 'ready')



###  delete that
if FAKE:
    print 'FAKE'
    p.set_condition('dooropen', "true")
###


while (not p.get_condition('dooropen')):
    time.sleep(1)
    
p.exec_action('interact', 'party')
p.exec_action('taskstep', 'Entering')
p.exec_action('enter', '30_0_0_4_true')

p.exec_action('taskstep', 'going_to_party_room')
p.exec_action('navigateto', 'wp8', interrupt='aborted', recovery='restart_action')

p.exec_action('turn','-135_ABS', interrupt='timeout_30')

# start looking for orders
p.exec_action('say', 'I_am_ready_to_take_the_orders', interrupt='timeout_5')

p.exec_action('headpose','0_-20',interrupt='timeout_5')


# take order 1
p.exec_action('say','Please_can_someone_come_here_for_the_other?',interrupt='timeout_5')

while (not p.get_condition('personhere')):
    if FAKE:
        print 'FAKE'
        p.set_condition('personhere', "true")
    time.sleep(0.5)


p.exec_action("say", "What's_your_name?",interrupt='timeout_5')

p.exec_action("asr", "name")

name_response_1 = p.memory_service.getData("asrresponse").replace(" ", "_")
print "name response", name_response_1

if name_response_1 != "":
    p.exec_action("say", "Is_"+ name_response_1 +"_your_name?",interrupt='timeout_5')

    p.exec_action("asr", "confirm")

    confirm_response = p.memory_service.getData("asrresponse").replace(" ", "_")
    if confirm_response != "" and confirm_response == "yes":
        p.exec_action("say", "What_drink_do_you_want?",interrupt='timeout_5')

        p.exec_action("asr", "drink")

        drink_response_1 = p.memory_service.getData("asrresponse").replace(" ", "_")

        if drink_response_1 != "":
            p.exec_action("say", "I_will_bring_you_a_" + drink_response_1,interrupt='timeout_5')
    else:
        p.exec_action("say", "I_am_not_sure_I_understood_,_can_you_repeat?",interrupt='timeout_5')


p.exec_action("say","Can_you_look_at_me_for_some_seconds?",interrupt='timeout_5')
p.exec_action('persondescription', 'order1',interrupt='timeout_10')
p.exec_action("say", "thanks",interrupt='timeout_5')



# take order 2

# take order 3



# Go to the bar

p.exec_action('goto', 'bar', interrupt='aborted', recovery='skip_action')

# say order1
age = memory_service.insertData("Actions/persondescription/order1/age")
gender = memory_service.insertData("Actions/persondescription/order1/gender")
haircolor = memory_service.insertData("Actions/persondescription/order1/hair")
glasses = memory_service.insertData("Actions/persondescription/order1/glasses")

if gender == "male":
    feat = memory_service.insertData("Actions/persondescription/order1/beard")
    if feat == "yes":
        extra = "with_beard"
    else:
        extra = "no_beard"

else
    feat = memory_service.insertData("Actions/persondescription/order1/makeup")
    if feat == "yes":
        extra = "with_makeup"
    else:
        extra = "no_makeup"

if glasses == "yes":
    isglasses = "glasses"
else:
    isglasses = "no_glasses"


order1_sentence = name_response_1+",_who_is_a_"+gender+",_around"+age+"_years_old,_with_"+haircolor+"_hair,_"+extra+",_and_with_"+isglasses+"_wants_a_"+drink_response_1
p.exec_action('say','order1_sentence',interrupt='timeout_5')

# example: 'John', who is a 'male/female', around '25' years old, with 'black' hair, 'nobeard/nomakeup', and 'noglasses' wants a 'coke'.


# say order2

# say order 3




p.end()

