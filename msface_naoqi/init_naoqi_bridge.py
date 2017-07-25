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


import threading
import time
import datetime
from json import dumps
import functools

from  face_api_naoqi import CognitiveFace

global imageWidget


thread_rate=4 
       
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
        self.delay=0.1
        
        self.opencvframe=None
        # Show opencv image
        self.showvideo=False
        
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
        resolution = vision_definitions.kQVGA  # kQVGA =320 * 240  ,kVGA =640x480

        colorSpace = vision_definitions.kRGBColorSpace
        self._imgClient = self._videoProxy.subscribe("msface_naoqi_client", resolution, colorSpace, 5)

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
        

        alImage = self._videoProxy.getImageRemote(self._imgClient)

        self._imgWidth = alImage[0]
        self._imgHeight = alImage[1]
#        # CV2
        img_str=str(alImage[6])

        nparr = np.fromstring(img_str, dtype=np.uint8).reshape( alImage[1],alImage[0], 3)
        open_cv_image = cv2.cvtColor(nparr, cv2.cv.CV_BGR2RGB)
        self.opencvframe=open_cv_image
        if self.showvideo is True:
            cv2.imshow('window_name', open_cv_image) # show frame on window
        
        if self.enabledwriter is True:
            self._out.write(open_cv_image)


    def save_frame(self,frame,timestamp):
        
        path_image=self.output_path+'frames'
        if not os.path.exists(path_image):
            os.makedirs(path_image)
            
        cv2.imwrite(path_image+'/'+str(timestamp)+'.png',frame)
         
        
    def timerEvent(self):
        """
        Called periodically. Retrieve a nao image, and update the widget.
        """
        self._updateImage()
        time.sleep(self.delay)


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


def onEvent(value ):
    
    print ' onEvent :',value
    global camera_enabled
    global imageWidget
    command=value.split('_')
    
    if command[0]== 'camera' :
        if command[1]== 'start' :
            camera_enabled = 1
            
            imageWidget = ImageWidget(args.pip,args.pport ,args.camera)
            imageWidget.initWriter()
            
            #create a thread that monitors directly the signal
            imageThread = threading.Thread(target = rhImageThread, )
            imageThread.start()
            
        elif command[1]== 'stop' :
            camera_enabled = 0
            
            imageThread.do_run = False
        
    elif command[0]== 'addface' :
        
        json_person=cognitiveface.add_face_srv(imageWidget.frame,command[1]) # (image, name)
        ## Write data in ALMemory
        str_person=json.dumps(json_person)
        memory_service.insertData('Actions/FaceRecognition/Recognition', str_person)
        time.sleep(0.5)
        memory_service.insertData('Actions/FaceRecognition/Recognition', '')
        
    elif command[0]== 'detect' :
        
        json_person=cognitiveface.detect_face_srv(imageWidget.frame,command[1]) #command[1]==True recognition
        ## Write data in ALMemory
        str_person=json.dumps(json_person)
        memory_service.insertData('Actions/FaceRecognition/Recognition', str_person)
        time.sleep(0.5)
        memory_service.insertData('Actions/FaceRecognition/Recognition', '')

    elif command[0]== 'initgroup' : #change group without clear persons
        
        res=cognitiveface.init_group_srv(command[1]) #command[1]==name grup
        
    elif command[0]== 'deleteperson' :
        
        res=cognitiveface.delete_person_srv(command[1]) #command[1]==name recognition

    elif command[0]== 'deleteallpersons' :
        
        res=cognitiveface.delete_allpersons_srv(command[1]) #command[1]==name grup        
        

    
def rhImageThread ():
    
    t = threading.currentThread()
        

    
    
    while getattr(t, "do_run", True):
        
            
        imageWidget.timerEvent()
 
        
    print "Exiting Thread"
    imageWidget.close()


def quit():
    
    memory_service.insertData('Actions/FaceRecognition/Enabled', 'false')    
    
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
    parser.add_argument("--group_recognition", type=str, default='robocup_test',
                        help="Name of group for recognition robocup_test")  
    parser.add_argument("--delete_group_first", type=bool, default=False,
                        help="Initialization of the group deleting all persons  ")                          
    global args
    args = parser.parse_args()
    #Starting application
    try:
        connection_url = "tcp://" + args.pip + ":" + str(args.pport)
        app = qi.Application(["MSFACE_naoqi", "--qi-url=" + connection_url ])
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + args.pip + "\" on port " + str(args.pport) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)

    app.start()
    session = app.session


    global cognitiveface
    cognitiveface=CognitiveFace(args.group_recognition, args.delete_group_first)


    global memory_service
    
    #Starting services
    memory_service  = session.service("ALMemory")

    #subscribe to any change 
    subscriber = memory_service.subscriber("Actions/FaceRecognition/Command")
#    idEvent = subscriber.signal.connect(functools.partial(onEvent, args.pip, args.pport,args.camera ))
    idEvent = subscriber.signal.connect(onEvent)            
    memory_service.insertData('Actions/FaceRecognition/Enabled', 'true')
    
    #Program stays at this point until we stop it
    app.run()

    imageThread.do_run = False
      

    print "Finished"            

if __name__ == "__main__":
    main()
