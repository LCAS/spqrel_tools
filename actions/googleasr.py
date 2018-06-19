import qi
import re
import argparse
import sys
import time
import threading

import action_base
from action_base import *


actionName = "googleasr"

memory_service = None

response = None

asr_service = None

audio_filename = ""

recording = False

channels = [0, 0, 1, 0] # only front (maybe)


def onSpeechDetected(msg):
    #global audio_filename, recording, audio_recorder
    #print "onSpeechDetected=", msg
    #if msg == 1 and not recording:
    #    # start the microphone
    #    audio_filename = os.path.join("/tmp", file_basename + str(time.time()))
    #    audio_recorder.startMicrophonesRecording(audio_filename + ".wav", "wav", 44100, channels)
    #    recording = True
    #    print "audio_recorder started recording"
    pass

def onWordRecognized(msg):
    global audio_filename, recording, audio_recorder, memory_service
    print "onWordRecognized=", msg
    # stop the microphone and send to google
    if recording:
        #stop the microphone
        audio_recorder.stopMicrophonesRecording()
        recording = False
        print "audio_recorder stopped recording"

        #send to google
        memory_service.raiseEvent("GoogleRequest", audio_filename)

def onGoogleResponse(msg):
    global response
    print "onGoogleResponse=", msg
    response = msg

def actionThread_exec (params):
    global response, recording, audio_recorder, asr_service, memory_service, audio_filename
    t = threading.currentThread()

    memory_service  = getattr(t, "mem_serv", None)

    #reset memory value
    memory_service.insertData("googleasrresponse", "")

    #establishing test vocabulary
    vocabulary = ["grape juice", "orange juice", "chocolate drink", "sprite", "coke", "Alex",\
        "Charlie", "Elizabeth", "Francis", "Jennifer", "Linda", "Mary", "Patricia",\
        "Robin", "Skyler", "James", "John", "Michael", "Robert", "William", "yes", "no"] #add verbs

    asr_service.pause(True)
    asr_service.removeAllContext()
    try:
        asr_service.setVocabulary(vocabulary, True) # put multiple possibilities
    except:
        print "Error setting vocabulary"
    asr_service.pause(False)

    # start the microphone
    file_basename = "SPQRel_rec_"
    audio_filename = os.path.join("/tmp", file_basename + str(time.time()))
    audio_recorder.startMicrophonesRecording(audio_filename + ".wav", "wav", 44100, channels)
    recording = True
    print "audio_recorder started recording"

    response = None
    #let it run
    while response is None:
        print "Waiting for trascription..."
        time.sleep(0.5)

    #save into memory
    memory_service.insertData("googleasrresponse", response)

    asr_service.pause(True)

    #stop recording
    if recording:
        audio_recorder.stopMicrophonesRecording()
        recording = False

    # action end
    action_success(actionName,params)

def init(session):
    global asr_service, asr_service_name, subWordRecognized, idSubWordRecognized, subSpeechDetected, idSubSpeechDetected, audio_recorder, subGoogleResponse, idSubGoogleResponse
    print actionName+" init"
    action_base.init(session, actionName, actionThread_exec)

    #Starting services
    asr_service = session.service("ALSpeechRecognition")
    asr_service.setLanguage("English")

    audio_recorder = session.service("ALAudioRecorder")

    memory_service = session.service("ALMemory")

    audio_recorder.stopMicrophonesRecording()
    recording = False
    ## Start the speech recognition engine with user Test_ASR
    #asr_service_name = "Test_ASR" + str(time.time())
    #asr_service.subscribe(asr_service_name)


    #subscribe to event WordRecognized
    subWordRecognized = memory_service.subscriber("WordRecognized")
    idSubWordRecognized = subWordRecognized.signal.connect(onWordRecognized)
    #subscribe to event SpeechDetected
    subSpeechDetected = memory_service.subscriber("SpeechDetected")
    idSubSpeechDetected = subSpeechDetected.signal.connect(onSpeechDetected)
    #subscribe to event GoogleResponse
    subGoogleResponse = memory_service.subscriber("GoogleResponse")
    idSubGoogleResponse = subGoogleResponse.signal.connect(onGoogleResponse)

    asr_service.pause(True)

def quit():
    global subWordRecognized, idSubWordRecognized, subSpeechDetected, idSubSpeechDetected, audio_recorder, subGoogleResponse, idSubGoogleResponse
    print actionName+" quit"

    #stop recording
    if recording:
        audio_recorder.stopMicrophonesRecording()
        recording = False

    #Disconnecting callbacks and subscribers
    subWordRecognized.signal.disconnect(idSubWordRecognized)
    subSpeechDetected.signal.disconnect(idSubSpeechDetected)
    subGoogleResponse.signal.disconnect(idSubGoogleResponse)

    #asr_service.unsubscribe(asr_service_name)

    asr_service.pause(True)

    actionThread_exec.do_run = False




if __name__ == "__main__":

    app = action_base.initApp(actionName)

    init(app.session)

    #Program stays at this point until we stop it
    app.run()

    quit()
