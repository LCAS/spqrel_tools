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

p.exec_action("asrenable", "")

p.exec_action("understandCommand", "")

p.exec_action("asrenable", "off")

p.exec_action("modiminit", "cocktailparty")
time.sleep(1)


p.set_condition(p.memory_service, 'drink_coke', "false")
p.set_condition(p.memory_service, 'drink_beer', "false")

p.exec_action('interactq', 'whichdrink')

if p.get_condition('drink_coke'):
    p.exec_action("say", "bringcoke")
if p.get_condition('drink_beer'):
    p.exec_action("say", "bringbeer")
p.end()
