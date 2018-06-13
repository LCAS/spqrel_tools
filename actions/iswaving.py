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
import cv2 as cv


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

actionName = "iswaving"


memory_service = None
video_service = None
DarknetSRV = None

# bounding box height ratio upper/lower chunks
factor = 1/3.0

# minimum global flow to start considering waving. Should filter small flows, as noise
global_flow_thres = 0.4

# minimum probability to trigger event
flow_event_thres = 0.5

def imcrop(img, bbox): 
    x1,y1,x2,y2 = bbox
    if x1 < 0 or y1 < 0 or x2 > img.shape[1] or y2 > img.shape[0]:
        img, x1, x2, y1, y2 = pad_img_to_fit_bbox(img, x1, x2, y1, y2)

    if img.ndim==3:
        return img[y1:y2, x1:x2, :]
    else:
        return img[y1:y2, x1:x2]


def pad_img_to_fit_bbox(img, x1, x2, y1, y2):
    if img.ndim==3:
        img = np.pad(img, ((np.abs(np.minimum(0, y1)), np.maximum(y2 - img.shape[0], 0)),
               (np.abs(np.minimum(0, x1)), np.maximum(x2 - img.shape[1], 0)), (0,0)), mode="constant")
    else:
        img = np.pad(img, ((np.abs(np.minimum(0, y1)), np.maximum(y2 - img.shape[0], 0)),
                  (np.abs(np.minimum(0, x1)), np.maximum(x2 - img.shape[1], 0))), mode="constant")

    y1 += np.abs(np.minimum(0, y1))
    y2 += np.abs(np.minimum(0, y1))
    x1 += np.abs(np.minimum(0, x1))
    x2 += np.abs(np.minimum(0, x1))
    return img, x1, x2, y1, y2



def biggestTuple(tA,tB):
    (Ax_min, Ay_min, Ax_max, Ay_max )= tA
    (Bx_min, By_min, Bx_max, By_max )= tB

    tC = ( min(Ax_min,Bx_min) , min(Ay_min,By_min), max(Ax_max,Bx_max), max(Ay_max,By_max))
    return tC


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

def isCorrectImage(result):
    ans = False
    if result == None:
        print 'cannot capture.'
    elif result[6] == None:
        print 'no image data string.'
    else:
        ans = True
    return ans

def image_qi2np(dataImage):
    image = None
    if( dataImage != None ):
        image = np.reshape( np.frombuffer(dataImage[6], dtype='%iuint8' % dataImage[2]), (dataImage[1], dataImage[0], dataImage[2]))
        # image = np.fromstring(str(alImage[6]), dtype=np.uint8).reshape( alImage[1],alImage[0], dataImage[2])
    return image    

def image_np2cv(npImage):
        # dirty way to use in cv2 or cv3
        if cv2.__version__ == '3.3.1-dev':
            open_cv_image = cv2.cvtColor(npImage, cv2.COLOR_BGR2RGB)
        else:
            open_cv_image = cv2.cvtColor(npImage, cv2.cv.CV_BGR2RGB)
        return open_cv_image

def image_qi2cv(qiImg):
    npImg = image_qi2np(qiImg)
    cvImg = image_np2cv(npImg)
    return cvImg

def wavingThread (params):
    # This is awful....
    global actionName
    global memory_service
    global video_service 
    global imgClient
    global DarknetSRV

    global factor
    global global_flow_thres
    global flow_event_thres

    t = threading.currentThread()

    paramList = params.split('_')
    sampleInterval = float(paramList[0])
    throttleInterval = float(paramList[1])

    print actionName+" thread started. Sample Period: "+ str(sampleInterval) + ", throttle Period: " + str(throttleInterval)


    while getattr(t, "do_run", True):
        # get two images with time spacing...
        isOk = False
        while not isOk:
            img0 = video_service.getImageRemote(imgClient)
            time.sleep(sampleInterval)        
            img1 = video_service.getImageRemote(imgClient)
            isOk = isCorrectImage(img0) and isCorrectImage(img1)

        img0 = image_qi2cv(img0)
        img1 = image_qi2cv(img1)

        timestampSecs =  img1[4]
        timestampMicrosecs =  img1[5]
        
        # detect stuff on them
        r0 = DarknetSRV.identify(img0)
        r1 = DarknetSRV.identify(img1)

        if (r0 != []) and (r1 != []):
            cnt = 0
            peopleCounter = 0
            while cnt < (min(len(r0),len(r1))):

                # why using same counter for both? I'm assuming very similar probabilities between frames, hence order in detection.
                # I know this is naive...
                name0 = r0[cnt][0]
                predict0 = r0[cnt][1]

                name1 = r1[cnt][0]
                predict1 = r1[cnt][1]


                # this prevents calculating flow between a dog and a person ...
                isPerson = ('person' in name0) 
                isPerson = isPerson and ('person' in name1)

                if  isPerson:
                    humanProb = min(predict0,predict1)

                    (pixel_list0, pixel_tuple0) = getPixelT(r0[cnt])
                    (pixel_list1, pixel_tuple1) = getPixelT(r1[cnt])
                    
                    max_tuple = biggestTuple(pixel_tuple1,pixel_tuple0)
                    (x_min, y_min, x_max, y_max) = max_tuple
                    gray0 = cv.cvtColor(img0, cv.COLOR_BGR2GRAY)
                    gray1 = cv.cvtColor(img1, cv.COLOR_BGR2GRAY)

                    gray_cropped0 = imcrop(gray0,max_tuple)
                    gray_cropped1 = imcrop(gray1,max_tuple)
                    
                    flow = cv.calcOpticalFlowFarneback(gray_cropped1, gray_cropped0, None, 0.5, 3, 15, 3, 5, 1.2, 0)

                    h, w =  gray_cropped1.shape[:2]


                    hi = int(h*factor)
                    upper_v = (np.mean(np.mean( flow[ 0:hi,:,],axis=0),axis=0))
                    lower_v = (np.mean(np.mean( flow[hi:  ,:,],axis=0),axis=0))

                    #probability of a wave=upper_half/(upper + lower)
                    global_flow = module((upper_v[0]+lower_v[0])/2.0,(upper_v[1]+lower_v[1])/2)
                    up_flow = module(upper_v[0],upper_v[1])  
                    down_flow = module(lower_v[0],lower_v[1])

                    if global_flow>global_flow_thres:
                        waveProb =  up_flow/(up_flow+down_flow) 
                    else:
                        waveProb = 0

                    peopleCounter+=1

                    mem_key_event  = "Actions/PeopleWaving/NewDetection"

                    mem_key0 = "Actions/PeopleWaving/"+"person{0:02}".format(peopleCounter)
                    
                    mem_key = mem_key0 + "/WaveProbability"
                    memory_service.insertData(mem_key, waveProb)

                    mem_key = mem_key0 + "/BBox/Xmin"
                    memory_service.insertData(mem_key, x_min)

                    mem_key = mem_key0 + "/BBox/Ymin"
                    memory_service.insertData(mem_key, y_min)

                    mem_key = mem_key0 + "/BBox/Xmax"
                    memory_service.insertData(mem_key, x_max)

                    mem_key = mem_key0 + "/BBox/Ymax"
                    memory_service.insertData(mem_key, y_max)

                    mem_key = mem_key0 + "/timestamp"
                    memory_service.insertData(mem_key, timestampSecs)

                    isEvent = (waveProb>=flow_event_thres)
                    memory_service.raiseEvent(mem_key_event,isEvent)
                    
                    if isEvent:
                        print "is waving me!"
                cnt+=1

        print ("-------------------------\n\n")
        time.sleep(throttleInterval)
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

    name = time.strftime('imageclient_%S')
    imgClient = video_service.subscribe(name, resolution, colorSpace, 5)

    # Select camera.
    video_service.setParam(vision_definitions.kCameraSelectID, camera)

    # Services
    DarknetSRV = session.service("DarknetSRV")
    
    action_base.init(session, actionName, wavingThread)



def quit():
    global actionName
    print actionName+" quit"
    wavingThread.do_run = False
    


if __name__ == "__main__":

    app = action_base.initApp(actionName)
        
    init(app.session)

    #Program stays at this point until we stop it
    app.run()

    quit()

