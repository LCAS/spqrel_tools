from Tkinter import *

jointsNames = ["HeadYaw", "HeadPitch",
               "LShoulderPitch", "LShoulderRoll", "LElbowYaw", "LElbowRoll", "LWristYaw",
               "RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", "RWristYaw"]

#joint limits taken from http://doc.aldebaran.com/2-5/family/pepper_technical/joints_pep.html
jointLimits ={'HeadYaw': (-2.0857, 2.0857),
              'HeadPitch': (-0.7068, 0.6371),
              'LShoulderPitch': (-2.0857, 2.0857),
              'LShoulderRoll': (0.0087, 1.5620),
              'LElbowYaw': (-2.0857, 2.0857),
              'LElbowRoll': (-1.5620, -0.0087),
              'LWristYaw': (-1.8239, 1.8239),
              'RShoulderPitch': (-2.0857, 2.0857),
              'RShoulderRoll': (-1.5620, -0.0087),
              'RElbowYaw': (-2.0857, 2.0857),
              'RElbowRoll': (0.0087,1.5620),
              'RWristYaw': (-1.8239, 1.8239)}

class JointAnglesGUI:

    def __init__(self, master, motion_service):
        self.master = master
        master.title("Joint Angles GUI")
        self.motion_service = motion_service

        useSensors = True
        
        self.labels = []
        self.scalewidgets = []
        for j, jointname in enumerate(jointsNames):
            print (j, jointname)

            currentSensorAngle = self.motion_service.getAngles(jointname, useSensors)
            print str(currentSensorAngle)

            self.labels.append(Label(text=jointname))
            self.labels[j].grid(row=j, column=1)
            self.scalewidgets.append(Scale(master, from_=jointLimits[jointname][0], to=jointLimits[jointname][1], resolution=0.1, orient="horizontal", length=200))
            self.scalewidgets[j].set(float(currentSensorAngle[0]))
            self.scalewidgets[j].bind("<ButtonRelease-1>", lambda event, widget = self.scalewidgets[j], jointname = jointsNames[j]: self.updateValue(event, widget, jointname))
            self.scalewidgets[j].grid(row=j, column=2)

    def updateValue(self, event, widget, jointname):
        print "setting", jointname, "to: ", widget.get()
        angles = widget.get()
        fractionMaxSpeed = 0.1
        self.motion_service.setAngles(jointname,angles,fractionMaxSpeed)
        time.sleep(0.5)


#from naoqi import ALBroker
#from naoqi import ALProxy
import qi
import argparse
import sys
import time
import os

class AngleController:
    def __init__(self,master):
        self.master = master
        parser = argparse.ArgumentParser()
        parser.add_argument("--pip", type=str, default=os.environ['PEPPER_IP'],
                            help="Robot IP address.  On robot or Local Naoqi: use '127.0.0.1'.")
        parser.add_argument("--pport", type=int, default=9559,
                            help="Naoqi port number")
        args = parser.parse_args()
        pip = args.pip
        pport = args.pport

        session = qi.Session()
        try:
            session.connect("tcp://" + pip + ":" + str(pport))
        except RuntimeError:
            print ("Can't connect to Naoqi at ip \"" + pip + "\" on port " + str(pport) +".\n"
                   "Please check your script arguments. Run with -h option for help.")
            sys.exit(1)

        self.motion_service  = session.service("ALMotion")

        gui = JointAnglesGUI(self.master, self.motion_service)
        master.mainloop()
       
    
if __name__ == "__main__":
    master = Tk()
    ac = AngleController(master)
