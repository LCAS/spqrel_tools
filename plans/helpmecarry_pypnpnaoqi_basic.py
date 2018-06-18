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

#previosly headpose_0_-30;
p.exec_action('headpose', '0_-30')

#previosly waitfor_personhere; 
while (not p.get_condition('personhere')):
    time.sleep(1)

#previously vsay_hello;
p.exec_action('say', 'hello')


#### 2 - START THE FOLLOWING PHASE

#previously asrenable;
p.exec_action('asrenable')

#previously  followuntil_stopfollowing; ! *if* (personlost) *do* vsay_waitforme; navigateto_start; waitfor_personhere; restart_action !

# follow the recorded person to the car
p.exec_action('updatefollowpersoncoord', 'stopfollowing', interrupt='personlost',recovery='say_waitforme; skip_action')

while  (not p.get_condition('stopfollowing') ) or p.get_condition('personlost'):
    p.exec_action('goto', 'door',interrupt='not_personlost',recovery='skip_action')
    p.exec_action('updatefollowpersoncoord', 'stopfollowing', interrupt='personlost',recovery='say_oh_oh; skip_action')


#previously asrenable_off;
p.exec_action('asrenable','off')

#previously saveposition_car;
p.exec_action('saveposition','car')

#### 3 - LOOK FOR HELP

#previously dialogue_lookforhelp;
p.exec_action('dialogue','lookforhelp')

#previously headpose_0_-20;
p.exec_action('headpose','0_-20')

#previously navigateto_^helplocation; # ! *if* personhere *do* dialogue_whattime; restart_action !
p.exec_action('navigateto', '^helplocation',interrupt='personhere',recovery='dialogue_whattime; waitfor_not_personhere; restart_action')

while not  p.get_condition('persondetected'):
    #previously  lookfor_persondetected; ! *if* timeout_lookfor_20 *do* 
    p.exec_action('lookfor', 'persondetected',  interrupt='timeout_20')

    if not  p.get_condition('persondetected'):
        if rand.random()>0.5:
            p.exec_action('turn','180')
        else:
            p.exec_action('say','comehere')

#previously arm_up;
p.exec_action('arm','up')
#previously vsay_guide; # we could use this action to acquire the name of the guy. At the end of this action, vsay_followme is automatically triggered
p.exec_action('say','guide')
#previously turn_180;
p.exec_action('turn','180')



#### 4 - COMING BACK TO THE CAR

#previously waitfor_personbehind;
while (not p.get_condition('personbehind')):
    time.sleep(1)


# non blocking
p.action_cmd('navigateto', '^car/waypoint','start')

patience=0
while (not p.get_condition('personbehind')):
    p.action_cmd('navigateto', '^car/waypoint','stop')
    if patience ==0:
        p.exec_action('say','comehere')
        time.sleep(3)
    if patience ==1:
        p.exec_action('say','comehere2')
        time.sleep(3)
    else:
        break
    patience+=1
    # pray for the judge
    #p.action_cmd('navigateto', '^car/waypoint','start')
    
p.exec_action('navigateto', '^car/waypoint','start')

#previously gotopos_^car/coordinates; ! *if* (not personbehind) *do*  turn_180; arm_up ; vsay_comehere ; turn_180 ; waitfor_personbehind; restart_action !
p.exec_action('gotopos', '^car/coordinates')


#previously dialogue_arrivedcar;
p.exec_action('dialogue','arrivedcar')

#previously vsay_farewell;
p.exec_action('say','farewell')


p.end()