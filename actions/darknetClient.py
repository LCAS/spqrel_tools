import qi
import argparse
import sys
import time
import threading
import math
import os
import threading
from naoqi import ALProxy
import vision_definitions

import action_base
from action_base import *

import conditions
from conditions import set_condition


"""
This action launches the object detection framework. In order to work, it needs darknetsrv.py running in the GPU and exposing the service.
It uses only 1 param: time between consecutive image captures/detections. The higher, the more network load I will be putting.

Upon detection, it will be publishing into ALMemory, under the address Actions/DarknetPerception/[detected object name]

Timestamp in seconds from the used image:
"Actions/DarknetPerception/"+name+"/timestamp"
Detection probability or confidence of the NN
"Actions/DarknetPerception/"+name+"/Confidence"

Bounding box data (relative to the image)
"Actions/DarknetPerception/"+name+"/BBox/Xmin"
"Actions/DarknetPerception/"+name+"/BBox/Ymin"
"Actions/DarknetPerception/"+name+"/BBox/Xmax"
"Actions/DarknetPerception/"+name+"/BBox/Ymax"


"""

actionName = "darknetClient"


memory_service = None
video_service = None
DarknetSRV = None


def getPixelT(ri):
    x = ri[2][0]
    y = ri[2][1]
    w = ri[2][2]
    z = ri[2][3]
    
    x_max = int(round((2*x+w)/2))
    x_min = int(round((2*x-w)/2))
    y_min = int(round((2*y-z)/2))
    y_max = int(round((2*y+z)/2))

    pixel_list = [ x_min, y_min, x_max, y_max]
    pixel_tuple = (x_min, y_min, x_max, y_max)
    return (pixel_list, pixel_tuple)

def replaceSpaces(catName):
    ans = catName
    spacePosition = catName.find(' ') # at most we have one, not first one, not last one
    if (spacePosition>0):
        ans =  catName[0:spacePosition]+catName[spacePosition+1].upper()+catName[spacePosition+2:]
 
    return ans

def darkThread (params):
    global actionName
    global memory_service
    global video_service 
    global imgClient
    global DarknetSRV

    t = threading.currentThread()

    period = float(params)

    print actionName+" thread started. Period: "+ str(period)


    while getattr(t, "do_run", True):
        result = video_service.getImageRemote(imgClient)
        timestampSecs =  result[4]
        timestampMicrosecs =  result[5]
        
        #print(type(result[0]))
        r = DarknetSRV.identify(result)
        if r != []:
            cnt = 0
            while cnt < len(r):
                name = replaceSpaces(r[cnt][0])
                confidence = r[cnt][1]

                (pixel_list, pixel_tuple) = getPixelT(r[cnt])


                print ("{0}: Confidence {1}".format(name,confidence))
                print ("\t at [{0},{1}  {2},{3}]".format(x, y, w, z))

                cnt+=1

                mem_key = "Actions/DarknetPerception/"+name+"/Confidence"
                memory_service.insertData(mem_key, confidence)

                mem_key = "Actions/DarknetPerception/"+name+"/BBox/Xmin"
                memory_service.insertData(mem_key, pixel_list[0])

                mem_key = "Actions/DarknetPerception/"+name+"/BBox/Ymin"
                memory_service.insertData(mem_key, pixel_list[1])

                mem_key = "Actions/DarknetPerception/"+name+"/BBox/Xmax"
                memory_service.insertData(mem_key, pixel_list[2])

                mem_key = "Actions/DarknetPerception/"+name+"/BBox/Ymax"
                memory_service.insertData(mem_key, pixel_list[3])

                mem_key = "Actions/DarknetPerception/"+name+"/timestamp"
                memory_service.insertData(mem_key, timestampSecs)

        print ("-------------------------\n\n")

        time.sleep(period)
    print actionName+" thread quit"

def init(session):
    global memory_service
    global video_service 
    global imgClient
    global DarknetSRV

    camera = 0 # upper camera

    video_service = session.service("ALVideoDevice")
    resolution = vision_definitions.kQVGA  # kQVGA =320 * 240  ,kVGA =640x480
    colorSpace = vision_definitions.kRGBColorSpace

    imgClient = video_service.subscribe("_clienteMe", resolution, colorSpace, 5)

    # Select camera.
    video_service.setParam(vision_definitions.kCameraSelectID, camera)

    # Services
    DarknetSRV = session.service("DarknetSRV")
    
    action_base.init(session, actionName, darkThread)



def quit():
    global actionName
    print actionName+" quit"
    actionThread_exec.do_run = False
    


if __name__ == "__main__":

    app = action_base.initApp(actionName)
        
    init(app.session)

    #Program stays at this point until we stop it
    app.run()

    quit()

