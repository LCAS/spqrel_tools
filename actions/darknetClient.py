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
This action launches the object detection framework. In order to work, it needs 
darknetsrv.py running in the GPU and exposing the service.
It uses only 1 param: time between consecutive image captures/detections. 
The higher, the less network load it will be putting.


Upon detection, it will be publishing an array of dicts into ALMemory, under the address 
"Actions/DarknetPerception/Detection"

And an event on "Actions/DarknetPerception/DetectionEvent"



Each dict will contain the following entries:
            object name in coco dataset
                entry['name'] 
            detection confidence
                entry['confidence'] 
            Bounding box data (relative to the image)
                entry['Xmin']
                entry['Ymin']
                entry['Xmax']
                entry['Ymax']
            Timestamp in seconds from the used image
                entry['timestamp']
            Current topological map node
                entry['location']

Previously, it was using this:

Upon detection, it will be publishing into ALMemory, under the address 
Actions/DarknetPerception/[detected object name] 

Timestamp in seconds from the used image:
"Actions/DarknetPerception/"+name+"/timestamp"
Detection probability or confidence of the NN
"Actions/DarknetPerception/"+name+"/Confidence"


"Actions/DarknetPerception/"+name+"/BBox/Xmin"
"Actions/DarknetPerception/"+name+"/BBox/Ymin"
"Actions/DarknetPerception/"+name+"/BBox/Xmax"
"Actions/DarknetPerception/"+name+"/BBox/Ymax"


detected object name can be found at darknet folder, under data/coco.data
"""

actionName = "darknetClient"


memory_service = None
video_service = None
DarknetSRV = None

def isCorrectImage(result):
    ans = False
    if result == None:
        print 'cannot capture.'
    elif result[6] == None:
        print 'no image data string.'
    else:
        ans = True
    return ans

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


def getNumberedObject(objDict,newObj):
    if not( newObj in objDict):
         objDict[newObj]=1
    else:
         objDict[newObj]+=1

    ans = objDict[newObj]+"{0:02}".format(objDict[newObj])
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
        isOk = False
        while not isOk:
            result = video_service.getImageRemote(imgClient)
            isOk = isCorrectImage(result) 

        timestampSecs =  result[4]
        timestampMicrosecs =  result[5]
        
        #print(type(result[0]))
        r = DarknetSRV.identify(result)
        foundObjects = []
        if r != []:
            cnt = 0
            while cnt < len(r):
                entry = {}
                name = r[cnt][0]
                confidence = r[cnt][1]
                (pixel_list, pixel_tuple) = getPixelT(r[cnt])
                cnt+=1

                #print ("{0}: Confidence {1}".format(name,confidence))
                #print ("\t at [{0},{1}  {2},{3}]".format(pixel_list[0], 
                #                                         pixel_list[1],
                #                                         pixel_list[2],
                #                                         pixel_list[3]))

                #oldStore()
                entry['name'] = name
                entry['confidence'] = confidence
                entry['Xmin']=str(pixel_list[0])
                entry['Ymin']=str(pixel_list[1])
                entry['Xmax']=str(pixel_list[2])
                entry['Ymax']=str(pixel_list[3])
                entry['timestamp']=str(timestampSecs)
                try:
                    entry['location']=memory_service.getData("TopologicalNav/CurrentNode")
                except RuntimeError:  
                    entry['location']='None'

                foundObjects.append(entry)
        #print ("-------------------------\n\n")
        if len(foundObjects)>0:

            mem_key = "Actions/DarknetPerception/Detection"
            mem_key_event  = "Actions/DarknetPerception/DetectionEvent"

            memory_service.insertData(mem_key,str(foundObjects))
            memory_service.raiseEvent(mem_key_event,True)

        time.sleep(period)
    print actionName+" thread quit"

def init(session):
    global memory_service
    global video_service 
    global imgClient
    global DarknetSRV

    camera = 0 # upper camera
    memory_service =  session.service("ALMemory")
    video_service = session.service("ALVideoDevice")
    resolution = vision_definitions.kQVGA  # kQVGA =320 * 240  ,kVGA =640x480
    colorSpace = vision_definitions.kRGBColorSpace

    name = time.strftime('imageclient_%S')
    imgClient = video_service.subscribe(name, resolution, colorSpace, 5)
    
    # Select camera.
    video_service.setParam(vision_definitions.kCameraSelectID, camera)

    # Services
    DarknetSRV = session.service("DarknetSRV")
    
    action_base.init(session, actionName, darkThread)



def quit():
    global actionName
    print actionName+" quit"
    darkThread.do_run = False
    

# def oldStore(name,foundObjects):
#     #name = replaceSpaces(name)
#     storeName = getNumberedObject(foundObjects,name)

#     mem_key = "Actions/DarknetPerception/"+storeName+"/Confidence"
#     memory_service.insertData(mem_key, str(confidence))

#     mem_key = "Actions/DarknetPerception/"+storeName+"/BBox/Xmin"
#     memory_service.insertData(mem_key, str(pixel_list[0]))

#     mem_key = "Actions/DarknetPerception/"+storeName+"/BBox/Ymin"
#     memory_service.insertData(mem_key, str(pixel_list[1]))

#     mem_key = "Actions/DarknetPerception/"+storeName+"/BBox/Xmax"
#     memory_service.insertData(mem_key, str(pixel_list[2]))

#     mem_key = "Actions/DarknetPerception/"+storeName+"/BBox/Ymax"
#     memory_service.insertData(mem_key, str(pixel_list[3]))

#     mem_key = "Actions/DarknetPerception/"+storeName+"/timestamp"
#     memory_service.insertData(mem_key, str(timestampSecs))


if __name__ == "__main__":

    app = action_base.initApp(actionName)
        
    init(app.session)

    #Program stays at this point until we stop it
    app.run()

    quit()

