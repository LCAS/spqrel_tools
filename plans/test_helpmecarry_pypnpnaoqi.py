import os
import sys

try:
	from pnp_cmd_naoqi import *
except:
    print "Please set PNP_HOME environment variable to PetriNetPlans folder."
    sys.exit(1)


p = PNPCmd()

p.begin()

c = 0

#test arsenable AND stopfolloging
p.exec_action('asrenable','')


# follow the recorded person to the car
p.exec_action('updatefollowpersoncoord', 'stopfollowing', interrupt='personlost')

p.exec_action('asrenable','off')



#next thing to test
#p.exec_action('dialogue','lookforhelp')


p.end()