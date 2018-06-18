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
p.exec_action('asrenable')
while  (not p.get_condition('stopfollowing'))
	if (c%100==0):
		print("I'll follow until you say so...")
		c = 0

p.exec_action('asrenable','off')



#next thing to test
#p.exec_action('dialogue','lookforhelp')


p.end()