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

#object to track
target='apple'

#nao head max degrees
maxYaw =  118 #deg +left/-right
maxPitch = 30 #deg +down/-up

# camera properties in pixels
maxX = 640
maxY = 320

# move head to netural position
p.action_cmd("updateheadpose", "0_0", 'start')

# start detecting objects
p.action_cmd('darknetClient', '0.1', 'start')

#main loop
while True:
	#print "."
	# read memory data

	# what was our latest detection?
	detection = eval(p.memory_service.getData('Actions/DarknetPerception/Detection'))

	# what is our current head position?
	currentYaw = p.memory_service.getData('Device/SubDeviceList/HeadYaw/Position/Sensor/Value')
	currentPitch = p.memory_service.getData('Device/SubDeviceList/HeadPitch/Position/Sensor/Value')

	# cast from radians to degrees  
	currentYaw = currentYaw * 180.0/(3.141592)
	currentPitch = currentPitch * 180.0/(3.141592)

	for item in detection:
		# get tracked object
		if item['name'] == target:

			# get x,y as integers, they are pixels?
			x = int( (  int(item['Xmax']) + int(item['Xmin']) ) / 2.0 )
			y = int( (  int(item['Ymax']) + int(item['Ymin']) ) / 2.0 )

			# distance to the center
			dx = (maxX/2) - x 
			dy = (maxY/2) - y 

			step = 5
			# is it on the left side?
			if dx>0:
				print "It's right side, turning right!"
				newYaw = currentYaw - (4*step)

			if dx<0:
				print "It's left side, turning left!"
				newYaw = currentYaw + (4*step)

			# is it upper side?
			if dy>0:
				print "It's up, uppering head!"
				newPitch = currentPitch - step


			if dy<0:
				print "It's down, lowering head!"
				newPitch = currentPitch + step

			# prevent invalid values ...
			if newYaw<-maxYaw:
				print "can't go more to left!"
				newYaw = -maxYaw

			if newYaw>maxYaw:
				print "can't go more to right!"
				newYaw = maxYaw

			if newPitch<-maxPitch:
				print "can't go upper!"
				newPitch = -maxPitch


			if newPitch>maxPitch:
				print "can't go lower!"
				newPitch = maxPitch

			if abs(currentPitch-newPitch)<step:
				print "not worth moving ..."
				newPitch= currentPitch

			if abs(currentYaw-newYaw)<(4*step):
				print "not worth moving ..."
				newYaw= currentYaw

			#newPitch = int(2.0*dy*maxPitch/maxY)
			#newYaw = - int(2.0*dx*maxYaw/maxX)

			# build params string for the action
			params_string = "{0}_{1}".format(newYaw,newPitch)

			#p.action_cmd("headpose", params_string, 'stop')
			
			# some debug data
			print "I see a little: "+item['name'] 
			print "at: "+str(x)+" "+ str(y)
			print "Current yaw {0}, and pitch {1}".format(currentYaw,currentPitch)

			if (newYaw != currentYaw) or (newPitch != currentPitch):
				print "New yaw: "+ str(newYaw)+ " and pitch: "+str(newPitch) 
				p.memory_service.insertData('Action/UpdateHeadPose/HeadYaw/Value',str(newYaw))
				p.memory_service.insertData('Action/UpdateHeadPose/HeadPitch/Value',str(newPitch))

	time.sleep(0.5)
	p.memory_service.insertData('Actions/DarknetPerception/Detection','[]')


# finish
p.action_cmd('darknetClient', '0.2', 'stop')

    
p.end()

