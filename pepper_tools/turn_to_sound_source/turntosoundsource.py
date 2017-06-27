import qi
import argparse
import sys
import functools
import os
import threading
import time
import math


def rhMonitorThread (memory_service):
    t = threading.currentThread()
    print "Monitoring Sound Detection"
    while getattr(t, "do_run", True):
        sound_value =  memory_service.getData("ALSoundLocalization/SoundLocated")
        if sound_value:
            print "Sound:", sound_value
        time.sleep(.2)

    print "Monitoring Sound Detection Finished"
    print "Exiting Thread"


class TurnToSoundsource:
    def __init__(self, session):
        self.session = session

        self.HEAD_PITCH_MAX = 0.6371 * 0.75
        self.HEAD_PITCH_MIN = -0.7068 * 0.75
        self.HEAD_YAW_MAX = 2.0857 * 0.75
        self.HEAD_YAW_MIN = -2.0857 * 0.75
        self.MAX_SPEED_FRACTION = 0.2
        self.NAMES = ["HeadYaw", "HeadPitch"]

    def onSoundLocalized(self, motion, value):
        """
        :param motion: motion service
        :param value: output of sounddetected
                        [ [time(sec), time(usec)],
                        [azimuth(rad), elevation(rad), confidence, energy],
                        [Head Position[6D]] in FRAME_TORSO
                        [Head Position[6D]] in FRAME_ROBOT
                        ]
        :return:
        """

        confidence = value[1][2]
        # print confidence

        if confidence > 0.7:
            sound_azimuth = value[1][0]
            sound_elevation = value[1][1]
            x = math.sin(sound_elevation) * math.cos(sound_azimuth)
            y = math.sin(sound_elevation) * math.sin(sound_azimuth)
            z = math.cos(sound_elevation)
            head_pitch = value[2][4]
            head_yaw = value[2][5]
            azimuth = sound_azimuth + head_yaw
            elevation = sound_elevation + head_pitch
            turn = 0
            if azimuth > self.HEAD_YAW_MAX:
                turn = azimuth
                azimuth = 0.
            if azimuth < self.HEAD_YAW_MIN:
                turn = azimuth
                azimuth = 0.
            if elevation > self.HEAD_PITCH_MAX:
                elevation = self.HEAD_PITCH_MAX
            if elevation < self.HEAD_PITCH_MIN:
                elevation = self.HEAD_PITCH_MIN
            target_angles = [azimuth, 0]  # [azimuth, elevation]
            print "Current Head Yaw: ", head_yaw, "Current Head Pitch", head_pitch
            print "Sound Detected Azimuth: ", sound_azimuth, "Sound Detected Elevation: ", sound_elevation
            print "Sound Detected Coordinate: ", [x, y, z]
            print "Target Head Yaw: ", azimuth, "Target Head Pitch: ", elevation
            print "Turn: ", turn
            print "------------------------------------------------------------------"
            motion.angleInterpolationWithSpeed(self.NAMES, target_angles, self.MAX_SPEED_FRACTION)
            if math.fabs(turn) > 0.01:
                motion.moveTo(0, 0, turn)
            # print a


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
        app = qi.Application(["LookAtSoundSource", "--qi-url=" + connection_url ])
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + pip + "\" on port " + str(pport) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)

    app.start()
    session = app.session

    turn_to_sound = TurnToSoundsource(session)

    #Starting services
    memory_service = session.service("ALMemory")
    motion_service = session.service("ALMotion")
    sound_service = session.service("ALSoundLocalization")
    motion_service.setStiffnesses("Head", 1.0)

    # subscribe to any change on "SoundLocalized"
    sound_service.subscribe("SoundService")
    sound_localized = memory_service.subscriber("ALSoundLocalization/SoundLocated")
    id_sound_localized = sound_localized.signal.connect(functools.partial(turn_to_sound.onSoundLocalized, motion_service))

    # create a thead that monitors directly the signal, optional
    # monitorThread = threading.Thread(target=rhMonitorThread, args=(memory_service,))
    # monitorThread.start()

    # Program stays at this point until we stop it
    app.run()

    motion_service.stopMove()

    # Disconnecting callbacks, services and Threads
    sound_localized.signal.disconnect(id_sound_localized)
    sound_service.unsubscribe("SoundService")

    # monitorThread.do_run = False

    print "Finished"


if __name__ == "__main__":
    main()