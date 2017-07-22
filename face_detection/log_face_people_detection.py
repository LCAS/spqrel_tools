import qi
import os
import sys
import argparse

from naoqi import ALProxy

# To get the constants relative to the video.
import vision_definitions

# opencv
import numpy as np
import cv2
from cv2 import cv

# Python Image Library
import Image

import threading
import time
import datetime
from json import dumps


log_enabled=True
#global videoProxy
global imageWidget
global log_people
global log_face
global log_video

def onFaceDetection(facevalue):


    if(len(facevalue) > 0):

        detectionTimestamp=facevalue[0]
        cameraPose_InTorsoFrame=facevalue[2]
        cameraPose_InRobotFrame=facevalue[3]
        cameraId=facevalue[4]        
        
        currentimestamp={'secs':int(detectionTimestamp[0]),'nsecs':int(detectionTimestamp[1])}
        print "detectionTimestamp=",currentimestamp
        
        # CHANGES??
        # get the ALValue returned by the time filtered recognition:
        if(len(facevalue[1]) > 0): # just in case of the ALValue is not in the wrong format
        
            
            #    - [] when nothing new.
            #    - [4] when a face has been detected but not recognized during the first 8s.
            #    - [2, [faceName]] when one face has been recognized.
            #    - [3, [faceName1, faceName2, ...]] when several faces have been recognized.

            timeFilteredResult = facevalue[1][len(facevalue[1]) -1]  #value[1][1]
                        
            
            if( len(timeFilteredResult) == 1 ):
                # If a face has been detected for more than 8s but not recognized
                if(timeFilteredResult[0] == 4):
                    print 'detected unknow face for more than 8s'
                    pass
            elif( len(timeFilteredResult) == 2 ):
                # If one or several faces have been recognized
                if(timeFilteredResult[0] in [2, 3]):
                    for s in timeFilteredResult[1]:
                        print 'Recognized ',s
                        
         

            print '__________________'
        
        #FACES INFO
        faces_array=[]
        try:
            faceInfoArray=facevalue[1][0:len(facevalue[1]) -1] 
            for faceInfo in faceInfoArray:
                # First Field = Shape info.
                faceShapeInfo = faceInfo[0]
                # Second Field = Extra info .
                faceExtraInfo = faceInfo[1]
                print "  alpha %.3f - beta %.3f" % (faceShapeInfo[1], faceShapeInfo[2])
                print "  width %.3f - height %.3f" % (faceShapeInfo[3], faceShapeInfo[4])
                print '  ID:',faceExtraInfo[0],', score= ',round(faceExtraInfo[1],3),', label= ',faceExtraInfo[2]
                
                pose={'alpha': round(faceShapeInfo[1],2), 'beta': round(faceShapeInfo[2],2), 'width':round(faceShapeInfo[3],2), 'height': round(faceShapeInfo[4],2)}
                face={'timestamp':currentimestamp,'faceid': faceExtraInfo[0], 'user': faceExtraInfo[2], 'confidence':round(faceExtraInfo[1],3), 'pose': pose, 'camerapose_robot' :cameraPose_InRobotFrame,'camerapose_torso' :cameraPose_InTorsoFrame}
                json_face=dumps(face)
                print 'json_face:: ',json_face

                if log_enabled is True:            
                    log_face.write(json_face+'\n')                 
        except:
            print "faces detected, but it seems getData is invalid. ALValue ="
            print '__________________'




        
class ImageWidget():
    """
    Tiny widget to display camera images from Naoqi.
    """
    def __init__(self, IP, PORT, CameraID, parent=None):
        """
        Initialization.
        """

        self._image = None
        

        self._imgWidth = 320
        self._imgHeight = 240
        self._cameraID = CameraID


        # Proxy to ALVideoDevice.
        self._videoProxy = None

        # Our video module name.
        self._imgClient = ""

        # This will contain this alImage we get from Nao.
        self._alImage = None

        self._registerImageClient(IP, PORT)

        # Trigger 'timerEvent' every ms.
        self.delay=0.05
        
        self.output_path='./data/'+datetime.datetime.now().strftime('%Y_%m_%d_%H_%M')+'/'
        # Define the codec and create VideoWriter object
        self.enabledwriter=False
        self._fps=2.0
        self.outvideo=self.output_path+'log.avi'
        self._fourcc = cv2.cv.FOURCC(*'XVID')
        self._out =None
        self.numframe=0


    def _registerImageClient(self, IP, PORT):
        """
        Register our video module to the robot.
        """
        self._videoProxy = ALProxy("ALVideoDevice", IP, PORT)
        resolution = vision_definitions.kQVGA  # 320 * 240

        colorSpace = vision_definitions.kRGBColorSpace
        self._imgClient = self._videoProxy.subscribe("_client", resolution, colorSpace, 5)

        # Select camera.
        self._videoProxy.setParam(vision_definitions.kCameraSelectID,
                                  self._cameraID)


    def _unregisterImageClient(self):
        """
        Unregister our naoqi video module.
        """
        if self._imgClient != "":
            self._videoProxy.unsubscribe(self._imgClient)


    def _updateImage(self):
        """
        Retrieve a new image from Nao.
        [0]: width.
        [1]: height.
        [2]: number of layers.
        [3]: ColorSpace.
        [4]: time stamp from qi::Clock (seconds).
        [5]: time stamp from qi::Clock (microseconds).
        [6]: binary array of size height * width * nblayers containing image data.
        [7]: camera ID (kTop=0, kBottom=1).
        [8]: left angle (radian). 0.49
        [9]: topAngle (radian). 0.38
        [10]: rightAngle (radian). -0.49
        [11]: bottomAngle (radian). -0.38

        """
        

        self._alImage = self._videoProxy.getImageRemote(self._imgClient)

#        print 'timestamp (secs):: ',self._alImage[4]
#        print 'timestamp (usecs):: ',self._alImage[5]
#        print 'width:: ',self._alImage[0]
#        print 'height:: ',self._alImage[1]
#        print 'topAngle (radian):: ',self._alImage[9]
#        print 'bottomAngle (radian):: ',self._alImage[11]
#        print '--------'

#        # CV2
        img_str=str(self._alImage[6])

        nparr = np.fromstring(img_str, dtype=np.uint8).reshape( self._alImage[1],self._alImage[0], 3)
        open_cv_image = cv2.cvtColor(nparr, cv2.cv.CV_BGR2RGB)
        

        cv2.imshow('window_name', open_cv_image) # show frame on window
        
        if self.enabledwriter is True:
            self._out.write(open_cv_image)
            currentimestamp={'secs':int(self._alImage[4]),'nsecs':int(self._alImage[5]), 'numframe': self.numframe}
            self.numframe+=1
            json_timestamp=dumps(currentimestamp)
            if log_enabled is True:
                log_video.write(json_timestamp+'\n')
#        #key=cv2.waitKey(0)

    def save_frame(self,frame,timestamp):
        
        path_image=self.output_path+'frames'
        if not os.path.exists(path_image):
            os.makedirs(path_image)
            
        cv2.imwrite(path_image+'/'+str(timestamp)+'.png',frame)

        
    def save_roi(self,frame,rect_target,faceid,timestamp):
   
        ymin=rect_target.y_offset
        ymax=rect_target.y_offset+rect_target.height
        xmin=rect_target.x_offset
        xmax=rect_target.x_offset+rect_target.width
        
        roi_new_user=frame[ymin:ymax,xmin:xmax]
        
        path_image=path_image=self.output_path+'faceid'
        if not os.path.exists(path_image):
            os.makedirs(path_image)
            
        cv2.imwrite(path_image+'/'+str(timestamp)+'.png',roi_new_user)
                
        
    def timerEvent(self):
        """
        Called periodically. Retrieve a nao image, and update the widget.
        """
        self._updateImage()
        #time.sleep(self.delay)


    def __del__(self):
        """
        When the widget is deleted, we unregister our naoqi video module.
        """
        self._unregisterImageClient()

    def initWriter(self):
        
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)
        self._out = cv2.VideoWriter(self.outvideo, self._fourcc, self._fps, (self._imgWidth,self._imgHeight))
        self.enabledwriter=True

    def close(self):
        """
        When the widget is deleted, we unregister our naoqi video module.
        """
        self._unregisterImageClient()
        self._out.release()
        cv2.destroyAllWindows()


def rhMonitorThread (memory_service):
    
    t = threading.currentThread()
    
    while getattr(t, "do_run", True):
        imageWidget.timerEvent()
        facevalues =  memory_service.getData("FaceDetected")        
        peoplevalues =  memory_service.getData("PeoplePerception/PeopleDetected")
        peoplevisible =  memory_service.getData("PeoplePerception/VisiblePeopleList")
        if facevalues:
            onFaceDetection(facevalues)
        if peoplevisible:
            detectiontimestamp=peoplevalues[0]
            currentimestamp={'secs':int(detectiontimestamp[0]),'nsecs':int(detectiontimestamp[1])}
            
            for idperson in peoplevisible:
                #try:
                angles =memory_service.getData( "PeoplePerception/Person/" +str(idperson)+"/AnglesYawPitch")
                distance =memory_service.getData( "PeoplePerception/Person/" +str(idperson)+"/Distance")
                height =memory_service.getData( "PeoplePerception/Person/" +str(idperson)+"/RealHeight")
                shirtcolor =memory_service.getData( "PeoplePerception/Person/" +str(idperson)+"/ShirtColor")
                shirtcolorHSV =memory_service.getData( "PeoplePerception/Person/" +str(idperson)+"/ShirtColorHSV")
                PositionInRobotFrame =memory_service.getData( "PeoplePerception/Person/" +str(personid)+"/PositionInRobotFrame")
                print '0'
                personinfo={'height': round(height,2), 'shirtcolor': shirtcolor, 'shirtcolorHSV':shirtcolorHSV} 
                poseinrobotframe={}
                pose={'distance': round(distance,2), 'pitch': round(angles[1],2), 'yaw':round(angles[0],2), 'poseinrobotframe':PositionInRobotFrame}    
                
                person={'timestamp':currentimestamp,'personid': idperson, 'info': personinfo, 'pose': pose}
                json_people=dumps(person)
                if log_enabled is True:
                    log_people.write(json_people+'\n')
                #except:
                 #   print 'Exception::', idperson, 'not found' 
                    
        time.sleep(imageWidget.delay)
        key = cv2.waitKey(1) & 0xFF  
        if key == ord("q"):
            break
    print "Exiting Thread"
    imageWidget.close()
    cv2.destroyAllWindows()


def main():
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--pip", type=str, default=os.environ['PEPPER_IP'],
                        help="Robot IP address.  On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--pport", type=int, default=9559,
                        help="Naoqi port number")
    parser.add_argument("--camera", type=int, default=0,
                        help="Robot camera ID address. 0 by default")
    parser.add_argument("--outvideo", type=str, default='output.avi',
                        help="Output video name output.avi")                        
    args = parser.parse_args()
    pip = args.pip
    pport = args.pport    
    
    CameraID = args.camera   


    global imageWidget
    imageWidget = ImageWidget(args.pip, args.pport , args.camera)
    imageWidget.initWriter()
    
    if log_enabled:
        global log_face
        log_face = open('./data/'+datetime.datetime.now().strftime('%Y_%m_%d_%H_%M')+'/log_faces.csv', 'w')
        global log_people
        log_people = open('./data/'+datetime.datetime.now().strftime('%Y_%m_%d_%H_%M')+'/log_peolpe.csv', 'w')
        global log_video
        log_video = open('./data/'+datetime.datetime.now().strftime('%Y_%m_%d_%H_%M')+'/log_video.csv', 'w')
    #Starting application
    try:
        connection_url = "tcp://" + args.pip + ":" + str(args.pport)
        app = qi.Application(["FaceDetector", "--qi-url=" + connection_url ])
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + args.pip + "\" on port " + str(args.pport) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)

    app.start()
    session = app.session
    
    # Create a proxy to ALFaceDetection
    try:
      faceProxy = ALProxy("ALFaceDetection", args.pip, args.pport)
    except Exception, e:
      print "Error when creating face detection proxy:"
      print str(e)
      exit(1)
      

    #Starting services
    memory_service  = session.service("ALMemory")


    #create a thead that monitors directly the signal
    monitorThread = threading.Thread(target = rhMonitorThread, args = (memory_service,))
    monitorThread.start()

    #Program stays at this point until we stop it
    app.run()

    monitorThread.do_run = False
      

    print "Finished"            

if __name__ == "__main__":
    main()
