import os
import sys

try:
	from pnp_cmd_naoqi import *
except:
    print "Please set PNP_HOME environment variable to PetriNetPlans folder."
    sys.exit(1)


p = PNPCmd()

p.begin()



#### 1 - WAIT FOR THE PERSON TO FOLLOW

#previously recdata_on;
p.exec_action('recdata', 'on')

#previosly headpose_0_-30;
p.exec_action('headpose', '0_-30')

#previosly waitfor_personhere; 
while (not p.get_condition('personhere')):
    time.sleep(1)

#previously vsay_hello;
p.exec_action('vsay', 'hello')


#### 2 - START THE FOLLOWING PHASE

#previously asrenable;
p.exec_action('asrenable')

#previously reccam_on;
p.exec_action('reccam', 'on')

#previously  followuntil_stopfollowing; ! *if* (personlost) *do* vsay_waitforme; navigateto_start; waitfor_personhere; restart_action !
p.exec_action('followuntil', 'stopfollowing', interrupt='personlost', recovery='vsay_waitforme; navigateto_start; waitfor_personhere; restart_action')


#previously asrenable_off;
p.exec_action('asrenable','off')

#previously reccam_off;
p.exec_action('reccam','off')

#previously saveposition_car;
p.exec_action('saveposition','car')



#### 3 - LOOK FOR HELP

#previously dialogue_lookforhelp;
p.exec_action('dialogue','lookforhelp')
#previously headpose_0_-20;
p.exec_action('headpose','0_-20')

#previously navigateto_^helplocation; # ! *if* personhere *do* dialogue_whattime; restart_action !
p.exec_action('navigateto', '^helplocation')

#previously reccam_on;
p.exec_action('reccam','on')
#previously  lookfor_persondetected; ! *if* timeout_lookfor_20 *do* 
p.exec_action('lookfor', 'persondetected',  interrupt='timeout_lookfor_20')
#previously reccam_off;
p.exec_action('reccam','off')

#previously  vsay_comehere; restart_action !
p.exec_action('vsay', 'comehere',  recovery='restart_action')


#previously arm_up;
p.exec_action('arm','up')
#previously vsay_guide; # we could use this action to acquire the name of the guy. At the end of this action, vsay_followme is automatically triggered
p.exec_action('vsay','guide')
#previously turn_180;
p.exec_action('turn','180')



#### 4 - COMING BACK TO THE CAR

#previously waitfor_personbehind;
while (not p.get_condition('personbehind')):
    time.sleep(1)

#previously navigateto_^car/waypoint; ! *if* (not personbehind) *do*  turn_180; arm_up ; vsay_comehere ; turn_180 ; waitfor_personbehind; restart_action !
p.exec_action('navigateto', '^car/waypoint', interrupt='not personbehind', recovery='turn_180; arm_up ; vsay_comehere ; turn_180 ; waitfor_personbehind; restart_action')

#previously gotopos_^car/coordinates; ! *if* (not personbehind) *do*  turn_180; arm_up ; vsay_comehere ; turn_180 ; waitfor_personbehind; restart_action !
p.exec_action('gotopos', '^car/coordinates', interrupt='not personbehind', recovery='turn_180; arm_up ; vsay_comehere ; turn_180 ; waitfor_personbehind; restart_action')


#previously dialogue_arrivedcar;
p.exec_action('dialogue','arrivedcar')

#previously vsay_farewell;
p.exec_action('vsay','farewell')

#previously recdata_off;
p.exec_action('recdata', 'off')






while (not p.get_condition('dooropen')):
    time.sleep(1)
    
#p.exec_action('interact', 'party')
p.exec_action('enter', '30_0_0_4_true')

p.exec_action('goto', 'partyroom', interrupt='aborted', recovery='skip_action')

#while (not p.get_condition('personhere')):
#    time.sleep(1)

p.exec_action('lookfor', 'personhere')
#print p.memory_service.getData('Actions/personhere/PersonAngleYaw')
#print p.memory_service.getData('Actions/personhere/PersonAngleTurn')navigto
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

