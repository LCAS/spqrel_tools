#!/usr/bin/python

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


def main(params,p):

	k = 3.141592/180.0                        
	pointForward   = [           7.9*k,          -0.7*k,      81.1*k,       18.2*k,      63.7*k,    24*k] 

	relaxPose = [ 1.12900996208, -0.061359167099, 0.492407798767, 0.0122718811035, 0.806842088699, 0.58435857296]

	relaxPoseStr = '_'.join( str(e) for e in relaxPose)
	pointForwardStr = '_'.join( str(e) for e in pointForward)


	#object to track
	target='cell phone'

	# camera properties in pixels
	maxX = 640



	# start detecting objects
	p.action_cmd('darknetClient', '0.1', 'start')
	lastT = 0
	#main loop
	while True:
		#print "."
		# read memory data

		# what was our latest detection?
		try:
			detection = eval(p.memory_service.getData('Actions/DarknetPerception/Detection'))
		except:
			detection =[]

		for item in detection:
			# get tracked object
			print item['name'] +" "+str(item['timestamp']) 
			if (item['name'] == target) and (item['timestamp'] > lastT):

				# to prevent reusing the same detection
				lastT=item['timestamp']

				# get x,y as integers, they are pixels?
				x = int( (  int(item['Xmax']) + int(item['Xmin']) ) / 2.0 )

				# distance to the center
				dx = (maxX/2) - x 

				step = 5
				# is it on the left side?
				if dx>0:
					print "It's right side, turning right!"
					angleInc = - (step)

				if dx<0:
					print "It's left side, turning left!"
					angleInc = (step)

				if abs(dx)<(100):
					print "not worth moving ..."
					angleInc= 0.0
				
				# some debug data
				print "I see a little: "+item['name'] 
				print "at: "+str(x) 
				print "inc: "+str(dx) 
				
				if (angleInc!=0.0):
					p.exec_action('movearm', relaxPoseStr)
					p.exec_action('turn', str(angleInc))
				else:
					p.exec_action('movearm', pointForwardStr)

		time.sleep(0.5)


	# finish
	p.action_cmd('darknetClient', '0.2', 'stop')

	    


if __name__ == "__main__":
    # execute only if run as a script
	plan = PNPCmd()

	plan.begin()

	main(params,plan)

	plan.end()
