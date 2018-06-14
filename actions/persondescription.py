import qi
import argparse
import sys
import time
import threading
import Image
import requests

import action_base
from action_base import *

# define the variable to comunicate with the Microsoft API server
subscription_key = "aab6d4045abc47c1942b7a57f97fc1e5"
assert subscription_key
face_api_url = 'https://westcentralus.api.cognitive.microsoft.com/face/v1.0/detect'

headers = { 'Content-Type': 'application/octet-stream',
            'Ocp-Apim-Subscription-Key': subscription_key}

api_params = {
    'returnFaceId': 'true',
    'returnFaceLandmarks': 'true',
    'returnFaceAttributes': 'age,gender,headPose,smile,facialHair,glasses,' +
                            'emotion,hair,makeup,occlusion,accessories,blur,exposure,noise'
}


actionName = "persondescription"


def actionThread_exec (params):
    t = threading.currentThread()
    session = getattr(t, "session", None)
    memory_service = getattr(t, "mem_serv", None)
    tts_service = getattr(t, "session", None).service("ALTextToSpeech")
    video_service = session.service("ALVideoDevice")

    print "Action "+actionName+" started with params "+params

    resolution = 3
    colorSpace = 11
    fps = 5
    
    videoClient = video_service.subscribe("python_client", resolution, colorSpace, fps)
    image = video_service.getImageRemote(videoClient)
    video_service.unsubscribe(videoClient)

    imageWidth = image[0]
    imageHeight = image[1]
    array = image[6]
    image_string = str(bytearray(array))

    img = Image.frombytes("RGB", (imageWidth, imageHeight), image_string)
    img.save("PersonImage.png") 

    # comment when it is not needed anymore
    #img.show()
    ###########

    with open('PersonImage.png', 'rb') as f:
        img_data = f.read()

    response = requests.post(face_api_url, data = img_data, params=api_params, headers=headers)
    faces = response.json()

    # Look for the face closest to the center
    min_distance = 100000000
    for f in range(len(faces)):
        #print 'Half Image:', imageWidth/2
        #print 'Center Face:', faces[f]["faceLandmarks"]["noseTip"]["x"]
        if abs(imageWidth/2 - faces[f]["faceLandmarks"]["noseTip"]["x"]) < min_distance:
            f_center = f

    # Save the face closest to the center
    #Gender
    print "Gender: " , faces[f_center]["faceAttributes"]["gender"]
    memory_service.insertData("Actions/persondescription/"+params+"/gender",faces[f_center]["faceAttributes"]["gender"])
    #Age
    print "Age: " , faces[f_center]["faceAttributes"]["age"]
    memory_service.insertData("Actions/persondescription/"+params+"/age",faces[f_center]["faceAttributes"]["age"])
    #Hair
    print "Hair: " , faces[f_center]["faceAttributes"]["hair"]["hairColor"][0]["color"]
    memory_service.insertData("Actions/persondescription/"+params+"/hair",faces[f_center]["faceAttributes"]["hair"]["hairColor"][0]["color"])
    #Beard
    if float(faces[f_center]["faceAttributes"]["facialHair"]["beard"]) >= 0.2:
        print "Beard: yes"
        memory_service.insertData("Actions/persondescription/"+params+"/Beard","yes")
    else:
        print "Beard: no"
        memory_service.insertData("Actions/persondescription/"+params+"/Beard","no")  
    # Makeup
    if faces[f_center]["faceAttributes"]["makeup"]["eyeMakeup"] == "true":
        print "Make up: yes"
        memory_service.insertData("Actions/persondescription/"+params+"/makeup","yes")
    else:
        print "Make up: no"
        memory_service.insertData("Actions/persondescription/"+params+"/makeup","no")
    #Glasses
    if faces[f_center]["faceAttributes"]["glasses"] == "NoGlasses":
        print "Glasses: no"
        memory_service.insertData("Actions/persondescription/"+params+"/glasses","yes")
    else:
        print "Glasses: yes"
        memory_service.insertData("Actions/persondescription/"+params+"/glasses","no")
    

    tts_service.say(faces[f_center]["faceAttributes"]["gender"])
    tts_service.say(faces[f_center]["faceAttributes"]["age"])
    tts_service.say("years old")
    tts_service.say(tts_service.say(faces[f_center]["faceAttributes"]["gender"]))



    # action end
    print "Action "+actionName+" "+params+" terminated"
    memory_service.raiseEvent("PNP_action_result_"+actionName,"success");


def init(session):
    print actionName+" init"
    action_base.init(session, actionName, actionThread_exec)


def quit():
    print actionName+" quit"
    actionThread_exec.do_run = False



if __name__ == "__main__":

    app = action_base.initApp(actionName)
    	
    init(app.session)

    #Program stays at this point until we stop it
    app.run()

    quit()