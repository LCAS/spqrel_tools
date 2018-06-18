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


# start looking for orders
p.exec_action('say', 'I_am_ready_to_take_the_orders')

p.exec_action('headpose','0_-10')



#order 1
p.exec_action('say','Please_can_you_come_here?')
while (not p.get_condition('personhere')):
     time.sleep(0.5)

p.exec_action("say", "hello,_whats_your_name?")


p.exec_action("say", "what_drink_do_you_want?")


p.exec_action("say", "thanks")



#order 2
p.exec_action('say','Please_can_you_come_here?')
while (not p.get_condition('personhere')):
     time.sleep(0.5)

p.exec_action("say", "hello,_whats_your_name?")



p.exec_action("say", "what_drink_do_you_want?")


p.exec_action("say", "thanks")


#order 3
p.exec_action('say','Please_can_you_come_here?')
while (not p.get_condition('personhere')):
     time.sleep(0.5)

p.exec_action("say", "hello,_whats_your_name?")



p.exec_action("say", "what_drink_do_you_want?")


p.exec_action("say","can_you_look_at_me_for_some_seconds")


p.exec_action("say", "thanks")



# Go to the bar

p.exec_action('goto', 'bar', interrupt='aborted', recovery='skip_action')

#say order1

name = "John"
age = memory_service.insertData("Actions/persondescription/order1/age")
gender = memory_service.insertData("Actions/persondescription/order1/gender")
haircolor = memory_service.insertData("Actions/persondescription/order1/hair")
glasses = memory_service.insertData("Actions/persondescription/order1/glasses")

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














# Search for the person sitting
p.exec_action('lookfor','personsitting',interrupt='timeout_20')

if p.get_condition('personsitting'):
    xsitting = p.memory_service.getData("Condition/personsitting/robot_coordinates_x")
    ysitting = p.memory_service.getData("Condition/personsitting/robot_coordinates_y")

    print "SITTING X: ",xsitting
    print "SITTING Y: ",ysitting

    p.exec_action("navigateto_naoqi",str(xsitting)+'_'+str(ysitting))


    # TODO 
    p.exec_action("say", "whats_your_name?")

    # ASR function 
    p.exec_action("say",'^person1name')


    p.exec_action("say", "what_drink?")



	p.exec_action('persondescription', 'order1')


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

