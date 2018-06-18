import os
import sys

try:
    sys.path.insert(0, os.getenv('PNP_HOME')+'/PNPnaoqi/py')
except:
    print "Please set PNP_HOME environment variable to PetriNetPlans folder."
    sys.exit(1)

from pnp_cmd_naoqi import *

p = PNPCmd()

p.begin()

p.exec_action('taskstep', 'waiting')
p.exec_action('modiminit', 'rips')
p.exec_action('interact', 'ready')

while (not p.get_condition('dooropen')):
    time.sleep(1)

p.exec_action('interact', 'rips')
p.exec_action('taskstep', 'Entering')

p.exec_action('enter', '30_0_0_4_true')

p.exec_action('taskstep', 'going_to_inspection_point')
p.exec_action(
    'navigateto', 'wp8',
    interrupt='obstaclehere',
    recovery='say_hello; waitfor_not_obstaclehere; restart_action')

p.exec_action('interactq', 'inspectme')
print p.get_condition('continue')
if (p.get_condition('continue')):
    print "I'm done"
p.exec_action('say', 'goodbye')

p.exec_action(
    'navigateto',
    'wp13', interrupt='aborted', recovery='restart_action')

p.end()

