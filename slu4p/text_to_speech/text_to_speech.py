import os
import qi
import time
import argparse
import signal


class TextToSpeech(object):
    PATH = ''
    EVENT_NAME = "Veply"

    def __init__(self, body_language_mode, speed, pitch, app):
        super(TextToSpeech, self).__init__()

        app.start()
        session = app.session

        self.__shutdown_requested = False
        signal.signal(signal.SIGINT, self.signal_handler)

        self.memory = session.service("ALMemory")

        self.tts = session.service("ALTextToSpeech")
        self.tts.setParameter("speed", speed)
        self.tts.setParameter("pitchShift", pitch)
        #self.body_language_mode = body_language_mode
        #if self.body_language_mode != "disabled":
        #    self.breathing = ALProxy("ALMotion")
        #    self.breathing.setBreathEnabled('Arms', True)
        #    self.configuration = {"bodyLanguageMode": self.body_language_modess}

    def start(self):
        self.tts_sub = self.memory.subscriber(TextToSpeech.EVENT_NAME)
        self.tts_sub_id = self.tts_sub.signal.connect(self.callback)
        print "[" + self.__class__.__name__ + "] Subscribers:", self.memory.getSubscribers(TextToSpeech.EVENT_NAME)

    def quit(self):
        self.tts_sub.signal.disconnect(self.tts_sub_id)
        #self.broker.shutdown()

    def callback(self, msg):
        sentence = str(msg)
        print "Saying:", sentence
        self.tts.say(sentence)
        #self.tts.say(args[1], self.configuration)

    def signal_handler(self, signal, frame):
        print "[" + self.inst.__class__.__name__ + "] Caught Ctrl+C, stopping."
        self.__shutdown_requested = True
        print "[" + self.inst.__class__.__name__ + "] Good-bye"


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--pip", type=str, default=os.environ['PEPPER_IP'],
                        help="Robot ip address")
    parser.add_argument("-p", "--pport", type=int, default=9559,
                        help="Robot port number")
    parser.add_argument("-l", "--language-mode", type=str, default="contextual",
                        help="The body language modality while speaking",
                        choices=['contextual', 'random', 'disabled'])
    parser.add_argument("-s", "--speed", type=int, default=90,
                        help="The speaking speed")
    parser.add_argument("-t", "--pitch", type=float, default=0.9,
                        help="The speaking pitch")

    args = parser.parse_args()

    try:
        # Initialize qi framework.
        connection_url = "tcp://" + args.pip + ":" + str(args.pport)
        app = qi.Application(["text_to_speech", "--qi-url=" + connection_url], autoExit=False)
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)

    tts = TextToSpeech(
        body_language_mode=args.language_mode,
        speed=args.speed,
        pitch=args.pitch,
        app=app
    )

    tts.start()

    app.run()

    tts.quit()


if __name__ == "__main__":
    main()
