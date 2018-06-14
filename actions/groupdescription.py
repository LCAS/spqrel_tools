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
    'returnFaceLandmarks': 'false',
    'returnFaceAttributes': 'age,gender,headPose,smile,facialHair,glasses,' +
                            'emotion,hair,makeup,occlusion,accessories,blur,exposure,noise'
}


actionName = "groupdescription"


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
    img.save("GroupImage.png") 


    # comment when it is not needed anymore
    #img.show()
    ###########
    with open('GroupImage.png', 'rb') as f:
        img_data = f.read()

    response = requests.post(face_api_url, data = img_data, params=api_params, headers=headers)
    faces = response.json()

    # check the result obtained
    num_people = 0
    num_male = 0
    num_female = 0
    num_children = 0

    for face in faces:
        num_people += 1
        if face["faceAttributes"]["gender"] == "male":
            num_male += 1
        if face["faceAttributes"]["gender"] == "female":
            num_female += 1
        if face["faceAttributes"]["age"] < 10:
           num_children += 1

    print "Num people: " , num_people
    print "Num male: " , num_male
    print "Num female: " , num_female
    print "Num children: " , num_children

    memory_service.insertData('Actions/groupdescription/NumPeople',num_people)
    memory_service.insertData('Actions/groupdescription/NumMale',num_male)
    memory_service.insertData('Actions/groupdescription/NumFemale',num_female)
    memory_service.insertData('Actions/groupdescription/NumChildren',num_children)


    tts_service.say("There are ")
    tts_service.say(str(num_people))
    tts_service.say("people in total in this group.")
    tts_service.say(str(num_male))
    tts_service.say("of them are male and ")
    tts_service.say(str(num_female))
    tts_service.say("are female")


    # action end
    print "Action "+actionName+" "+params+" terminated"
    memory_service.raiseEvent("PNP_action_result_"+actionName,"success");
    action_success(actionName,params)


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

