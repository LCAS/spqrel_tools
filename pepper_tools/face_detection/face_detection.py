
#http://doc.aldebaran.com/2-5/naoqi/peopleperception/alfacedetection.html

import qi
import argparse
import sys
import time
import threading



def onDetection(value):
#    
#    print "onDetection ::value=",value
    
    if(len(value) > 0):

        detectionTimestamp=value[0]
        cameraPose_InTorsoFrame=value[2]
        cameraPose_InRobotFrame=value[3]
        cameraId=value[4]        
        
        
        
        if(len(value[1]) > 0): # just in case of the ALValue is in the wrong format

            #Detecting changes

            # get the ALValue returned by the time filtered recognition:
            #    - [] when nothing new.
            #    - [4] when a face has been detected but not recognized during the first 8s.
            #    - [2, [faceName]] when one face has been recognized.
            #    - [3, [faceName1, faceName2, ...]] when several faces have been recognized.
            timeFilteredResult = value[1][len(value[1]) -1]
            if( len(timeFilteredResult) == 1 ):
                # If a face has been detected for more than 8s but not recognized # TODO: Try to learn face??
                if(timeFilteredResult[0] == 4):
                    pass
                
            elif( len(timeFilteredResult) == 2 ):
                # If one or several faces have been recognized
                if(timeFilteredResult[0] in [2, 3]):
                    for s in timeFilteredResult[1]:
                        print 'persons recognized : ',s

            # TODO: extract data for each face detected  value[1][..]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pip", type=str, default=os.environ['PEPPER_IP'],
                        help="Robot IP address.  On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--pport", type=int, default=9559,
                        help="Naoqi port number")
    args = parser.parse_args()
    pip = args.pip
    pport = args.pport

    #Starting application
    try:
        connection_url = "tcp://" + pip + ":" + str(pport)
        app = qi.Application(["PeopleDetection", "--qi-url=" + connection_url ])
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + pip + "\" on port " + str(pport) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)

    app.start()
    session = app.session

    #Starting services
    memory_service  = session.service("ALMemory")

    #Testing some functions from the ALWavingDetection module
    service = session.service("ALFaceDetection")
    
    # list of faces currently trained
    learnedlist = service.getLearnedFacesList()
    print 'learnedlist=',learnedlist

    print 'RecognitionEnabled=',service.isRecognitionEnabled()
    service.setRecognitionEnabled(True) 
    
    # Connect the event callback.
    anyDetection = memory_service.subscriber("FaceDetected")
    idAnyDetection = anyDetection.signal.connect(onDetection)
      

    #Program stays at this point until we stop it
    app.run()

    #Disconnecting callbacks and Threads
    anyDetection.signal.disconnect(idAnyDetection)
    monitorThread.do_run = False
    
    print "Finished"


if __name__ == "__main__":
    main()
