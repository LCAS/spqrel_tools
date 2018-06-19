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

p.exec_action('taskstep', 'waiting')
p.exec_action('modiminit', 'cocktailparty')
p.exec_action('interact', 'ready')

while (not p.get_condition('dooropen')):
    time.sleep(1)
    
p.exec_action('interact', 'party')
p.exec_action('taskstep', 'Entering')
p.exec_action('enter', '30_0_0_4_true')

p.exec_action('taskstep', 'going_to_party_room')
p.exec_action('navigateto', 'wp8', interrupt='aborted', recovery='restart_action')

p.exec_action('turn','-135_ABS')

# start looking for orders
p.exec_action('say', 'I_am_ready_to_take_the_orders')


# Search for the person sitting
p.exec_action('lookfor','personsitting',interrupt='timeout_20')

sitfound = p.get_condition('personsitting')

if not sitfound:
    p.exec_action('turn','-45_ABS')
    p.exec_action('lookfor','personsitting',interrupt='timeout_20')

    sitfound = p.get_condition('personsitting')

if sitfound:

    xsitting = p.memory_service.getData("Condition/personsitting/robot_coordinates_x")
    ysitting = p.memory_service.getData("Condition/personsitting/robot_coordinates_y")

    print "SITTING X: ",xsitting
    print "SITTING Y: ",ysitting
    
    p.exec_action("navigateto_naoqi",str(xsitting)+'_'+str(ysitting))

    # TODO 
    p.exec_action("say", "hello,_whats_your_name?")

    got_name = False
    attempts = 0
    name_response = ''
    while (not got_name and attempts < 2):
        p.exec_action("asr", "name")

        name_response = p.memory_service.getData("asrresponse").replace(" ", "_")
        print "name response", name_response
    
        if name_response != "":
            p.exec_action("say", "Is_"+ name_response +"_your_name?")

            p.exec_action("asr", "confirm")
        
            confirm_response = p.memory_service.getData("asrresponse").replace(" ", "_")

            if confirm_response != "" and confirm_response == "yes":
                got_name = True
            else:
                attempts = attempts + 1
                p.exec_action("say", "then_could_you_repeat_it_please?")

    got_drink = False
    attempts = 0
    drink_response = ''
    while (not got_drink and attempts < 2):
        p.exec_action("say", "What_drink_do_you_want?")
        p.exec_action("asr", "drink")

        drink_response = p.memory_service.getData("asrresponse").replace(" ", "_")
        print "drink response", drink_response
        
        if drink_response != "":
            p.exec_action("say", "I_will_bring_you_a_" + drink_response)
            p.exec_action("say", "Is_that_correct")

            p.exec_action("asr", "confirm")

            confirm_response = p.memory_service.getData("asrresponse").replace(" ", "_")

            if confirm_response != "" and confirm_response == "yes":
                got_drink = True
            else:
                attempts = attempts + 1
                p.exec_action("say", "then_could_you_repeat_it_please?")

    p.exec_action("say","ok_"+name_response+"_I_will_bring_you_a_" + drink_response)
    
    p.exec_action("say","can_you_look_at_me_for_some_seconds")
    p.exec_action('persondescription', 'order1')


    p.exec_action("say", "thanks")

    p.exec_action('navigateto', 'wp8', interrupt='aborted', recovery='restart_action')


p.exec_action('turn','-135_ABS')

p.exec_action("iswaving","0.2_0.5_wavingdetected",interrupt='timeout_20')

wavefound = p.get_condition('wavingdetected')

if not wavefound:
	p.exec_action('turn','-45_ABS')
	p.exec_action("iswaving","0.2_0.5_wavingdetected",interrupt='timeout_20')

	wavefound = p.get_condition('wavingdetected')

    
#xwaving = p.memory_service.getData('Actions/wavingdetected/wavingpersonx')
#ywaving = p,memory_service.getData('Actions/wavingdetected/wavingpersony')

#print "WAVING X: ",xwaving
#print "WAVING Y: ",ywaving

#p.exec_action("navigateto_naoqi",str(xwaving)+'_'+str(ywaving))





# Go to the bar

p.exec_action('goto', 'bar', interrupt='aborted', recovery='skip_action')


#say order1


try:
    name = name_response
    age = memory_service.insertData("Actions/persondescription/order1/age")
    gender = memory_service.insertData("Actions/persondescription/order1/gender")
    haircolor = memory_service.insertData("Actions/persondescription/order1/hair")
    glasses = memory_service.insertData("Actions/persondescription/order1/glasses")
    drink = drink_response

    if gender == "male":
        feat = memory_service.insertData("Actions/persondescription/order1/beard")
        if feat == "yes":
            extra = "with beard"
        else:
            extra = "no beard"

    else
        feat = memory_service.insertData("Actions/persondescription/order1/makeup")
        if feat == "yes":
            extra = "with makeup"
        else:
            extra = "no makeup"


order_sentence = "Order 1"
say()

# example: 'John', who is a 'male/female', around '25' years old, with 'black' hair, 'nobeard/nomakeup', and 'noglasses' wants a 'coke'.




	


p.exec_action('headpose', '0_0')


#p.exec_action("iswaving","0.2_0.5_wavingdetected")

#xwaving = p.memory_service.getData('Actions/wavingdetected/wavingpersonx')
#ywaving = p,memory_service.getData('Actions/wavingdetected/wavingpersony')

#print "WAVING X: ",xwaving
#print "WAVING Y: ",ywaving

#p.exec_action("navigateto_naoqi",str(xwaving)+'_'+str(ywaving))













p.exec_action('say', 'I_will_look_for_someone_calling_me')

#while (not p.get_condition('personhere')):
#    time.sleep(1)

p.exec_action('lookfor', 'personhere')
#print p.memory_service.getData('Actions/personhere/PersonAngleYaw')
#print p.memory_service.getData('Actions/personhere/PersonAngleTurn')

p.exec_action('turn', '^Actions/personhere/PersonAngleTurn')

p.exec_action('say', 'hello')

p.exec_action('goto', 'bar', interrupt='aborted', recovery='skip_action')

p.exec_action('goto', 'door', interrupt='aborted', recovery='skip_action')

#p.exec_action('interact', 'comehere')

# p.exec_action('say', 'hello')

# while (not p.get_condition('screentouched')):
#     time.sleep(1)

# p.exec_action('say', 'starting')

# i=0

#remove comment if you want the robot to move
#p.exec_action('turn', '-90', interrupt='screentouched', recovery='skip_action')

# while (i<5 and not p.get_condition('screentouched')):
    
#     y = -40 + 20*i
#     p.exec_action('headpose', '%d_20' %y)
#     time.sleep(0.5)
#     i += 1

# p.exec_action('headpose', '0_-10')

# p.exec_action('say', 'goodbye')

p.end()

