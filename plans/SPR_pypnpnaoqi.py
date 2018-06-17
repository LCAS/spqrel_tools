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

#p.exec_action('turn', '180')

p.exec_action("aimlsay", "greetings")

p.exec_action("say", "I want to play a riddle game, I will give you some seconds to get ready.")
#p.exec_action('headpose', '0_0')

p.exec_action("wait","10")

#p.exec_action('turn', '180')

p.exec_action("wait","5")

p.exec_action("say","lookatme")

p.exec_action("wait","1")

p.exec_action("groupdescription", "",interrupt="timeout_30")

p.exec_action("wait","1")

p.exec_action("")

#Question 1
while (not p.get_condition('sounddetected')):
    time.sleep(0.5)

p.exec_action('turn', '^AngleSound')

p.exec_action("wait","2")


#Question 2
while (not p.get_condition('sounddetected')):
    time.sleep(0.5)

p.exec_action('turn', '^AngleSound')

p.exec_action("wait","2")


# 

p.exec_action("aimlsay", "farewell")


#p.exec_action("say", "hello")

#p.exec_action("followuntil","screentouched")
#p.exec_action("persondescription", "order1")
#vsay_starting;


#wait_2;
#p.exec_action("wait", "1")


p.end()
