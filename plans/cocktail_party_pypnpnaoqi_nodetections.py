import os
import sys

try:
    sys.path.insert(0, os.getenv('PNP_HOME')+'/PNPnaoqi/py')
except:
    print "Please set PNP_HOME environment variable to PetriNetPlans folder."
    sys.exit(1)

import pnp_cmd_naoqi
from pnp_cmd_naoqi import *

def repeat_order(order_key='order1', name='Linda', drink='coke'):
    try:
        age = memory_service.getData("Actions/persondescription/%s/age" % order_key)
        gender = memory_service.getData("Actions/persondescription/%s/gender" % order_key)
        haircolor = memory_service.getData("Actions/persondescription/%s/hair" % order_key)
        glasses = memory_service.getData("Actions/persondescription/%s/glasses" % order_key)

        if gender == "male":
            feat = memory_service.getData("Actions/persondescription/%s/beard"  % order_key)
            if feat == "yes":
                extra = "with_beard"
            else:
                extra = "no_beard"

        else:
            feat = memory_service.getData("Actions/persondescription/%s/makeup"  % order_key)
            if feat == "yes":
                extra = "with_makeup"
            else:
                extra = "no_makeup"

        if glasses == "yes":
            isglasses = "glasses"
        else:
            isglasses = "no_glasses"

        order1_sentence = name+",_who_is_a_"+gender+",_around"+age+"_years_old,_with_"+haircolor+"_hair,_"+extra+",_and_with_"+isglasses+"_wants_a_"+drink
        p.exec_action('say', order1_sentence, interrupt='timeout_5')
    except:
        p.exec_action(
            'say', 'sorry_I_forgot_who_wanted_%s.' % drink,
            interrupt='timeout_5')



def take_order(order_key='order1'):
    p.exec_action('say','Please_can_someone_come_here_to_place_an_order?',interrupt='timeout_5')

    drink_response = "coke"
    name_response = "Linda"

    while (not p.get_condition('personhere')) and not FAKE:
        time.sleep(0.5)


    p.exec_action("say", "What's_your_name?",interrupt='timeout_5')

    p.exec_action("asr", "name")

    try:
        name_response = p.memory_service.getData("asrresponse").replace(" ", "_")
    except:
        name_response = "Linda"
    print "name response", name_response

    if name_response != "":
        p.exec_action("say", "Is_"+ name_response +"_your_name?",interrupt='timeout_5')

        p.exec_action("asr", "confirm")

        try:
            confirm_response = p.memory_service.getData("asrresponse").replace(" ", "_")
        except:
            confirm_response = "yes"
        if confirm_response != "" and confirm_response == "yes":
            p.exec_action("say", "What_drink_do_you_want?",interrupt='timeout_5')

            p.exec_action("asr", "drink")

            try:
                drink_response = p.memory_service.getData("asrresponse").replace(" ", "_")
            except:
                drink_response = "coke"

            if drink_response != "":
                p.exec_action("say", "I_will_bring_you_a_" + drink_response,interrupt='timeout_5')
        else:
            p.exec_action("say", "I_am_not_sure_I_understood_,_can_you_repeat?",interrupt='timeout_5')
        p.exec_action("say","Can_you_look_at_me_for_some_seconds?",interrupt='timeout_5')
        p.exec_action('persondescription', order_key, interrupt='timeout_10')
        p.exec_action("say", "thanks",interrupt='timeout_5')


    return (name_response, drink_response)




FAKE = True

p = PNPCmd()

p.begin()
p.exec_action('setpose', '5.8_10.6')

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

(name_1, drink_1) = take_order('order1')
time.sleep(5)
(name_2, drink_2) = take_order('order2')
time.sleep(5)
(name_3, drink_3) = take_order('order3')


# Go to the bar

p.exec_action('navigateto', 'wp12', interrupt='aborted', recovery='skip_action')
p.exec_action('turn','90_ABS', interrupt='timeout_30')

# say order1
# example: 'John', who is a 'male/female', around '25' years old, with 'black' hair, 'nobeard/nomakeup', and 'noglasses' wants a 'coke'.

repeat_order('order1', name_1, drink_1)
repeat_order('order1', name_1, drink_1)
repeat_order('order1', name_1, drink_1)

# say order2

# say order 3




p.end()

