import os
import sys
import time

try:
    sys.path.insert(0, os.getenv('PNP_HOME')+'/PNPnaoqi/py')
except:
    print "Please set PNP_HOME environment variable to PetriNetPlans folder."
    sys.exit(1)


import pnp_cmd_naoqi
from pnp_cmd_naoqi import *

p = PNPCmd()

p.begin()


p.exec_action("say", "hello")

p.exec_action("waitfor","personhere")

p.exec_action("say","lookatme")

p.exec_action("headpose", "0_-20")

time.sleep(1)

p.exec_action("persondescription","John")

p.exec_action("followuntil", "screentouched")

while (not p.get_condition('sounddetected')):
    time.sleep(1)

p.exec_action('turn', '^AngleSound')

p.exec_action("say", "goodbye")


p.end()