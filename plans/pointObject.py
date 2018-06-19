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

def targetInView(currPlan,objectName):
    isObjectMissing = False
    foundItem =None
    try:
        detection = eval(currPlan.memory_service.getData('Actions/DarknetPerception/Detection'))
    except:
        detection =[]

    for item in detection:           
        if (item['name'] == objectName):
            isObjectMissing=True
            foundItem = item

    return (isObjectMissing,foundItem)


def main(params,p):

    k = 3.141592/180.0                        
    pointForward   = [           7.9*k,          -0.7*k,      81.1*k,       18.2*k,      63.7*k,    24*k] 

    relaxPose = [ 1.12900996208, -0.061359167099, 0.492407798767, 0.0122718811035, 0.806842088699, 0.58435857296]

    relaxPoseStr = '_'.join( str(e) for e in relaxPose)
    pointForwardStr = '_'.join( str(e) for e in pointForward)


    #object to track
    target=params.replace('_',' ') #'cell phone'
    step = 15
    # camera properties in pixels
    maxX = 320 # by 240

    #make sure hand is relaxed
    p.exec_action('movearm', relaxPoseStr)

    # start detecting objects
    p.action_cmd('darknetClient', '0.1', 'start')
    
    p.exec_action('say', "Hi,_let's_find_a_"+params )

    # first start turning robot until object apperars in range
    totalAngle=0
    turnAngle=30
    objectMissing=True
    while ( (totalAngle<360) or (objectMissing) ):
       p.exec_action('say', "Let_me_see_around" )    
       time.sleep(1)
       (objectMissing,item)=targetInView(p,target)

        if objectMissing:
            p.exec_action('say', "Nothing_here." )    
            p.exec_action('turn', str(turnAngle))       
            totalAngle+=turnAngle
        else:
            p.exec_action('say', "I_found_it" )    

    # after turning arround, did we succeeded?
    if objectMissing:
        p.exec_action('say', "Couldn't_find_your_item" ) 
        p.exec_action('say', 'sorry' )
        return False
    else:
        # let's align header
        lastT = 0
        angleInc=1000.0
        #main loop
        p.exec_action('say', "There._Let_me_point_the_"+params )
        count = 0
        while (angleInc!=0.0):
            #print "."
            # read memory data
            (objectMissing,item)=targetInView(p,target)

            # what was our latest detection?
            if not objectMissing:
                # get tracked object
                count = count+1
                if ( ( count %20 ) ==0):
                    print "Detected "+item['name'] +" at time "+str(item['timestamp']) 
               
                if (item['name'] == target) and (item['timestamp'] > lastT):

                    # to prevent reusing the same detection
                    lastT=item['timestamp']

                    # get x,y as integers, they are pixels?
                    x = int( (  int(item['Xmax']) + int(item['Xmin']) ) / 2.0 )

                    # distance to the center
                    dx = x - (maxX/2)  

                    #step = 5
                    # is it on the left side?
                    if dx>0:
                        print "It's right side, turning right!"
                        angleInc = - (step)

                    if dx<0:
                        print "It's left side, turning left!"
                        angleInc = (step)

                    if abs(dx)<(10):
                        print "not worth moving ..."
                        angleInc= 0.0
                    
                    # some debug data
                    print "I see a little: "+item['name'] 
                    print "at: "+str(x) 
                    print "inc: "+str(dx) 
                    
                    if (angleInc!=0.0):
                        p.exec_action('turn', str(angleInc))
            time.sleep(0.5)


        p.exec_action('movearm', pointForwardStr)
        p.exec_action('say', 'See?_I_found_your_'+params )
        time.sleep(3.0)
        p.exec_action('movearm', relaxPoseStr)

        # finish
        p.action_cmd('darknetClient', '0.2', 'stop')
        p.exec_action('say', 'see_you' )
        


if __name__ == "__main__":
    # execute only if run as a script
    plan = PNPCmd()

    plan.begin()

    params = 'cell_phone'
    main(params,plan)

    plan.end()
