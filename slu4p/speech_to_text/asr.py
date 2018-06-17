#http://doc.aldebaran.com/2-5/naoqi/audio/alspeechrecognition-api.html
import qi
import argparse
import sys
import os

USE_GOOGLE = False



class SpeechRecognition(object):

    audio_recorder = None

    def __init__(self, vocab, app):
        super(SpeechRecognition, self).__init__()

        app.start()
        session = app.session

        #Starting services
        self.asr_service = session.service("ALSpeechRecognition")
        self.asr_service.setLanguage("English")

        self.audio_recorder = session.service("ALAudioRecorder")

        self.memory_service  = session.service("ALMemory")

        #establishing test vocabulary
        #vocabulary = ["yes", "no", "please", "hello", "goodbye", "hi, there", "go to the kitchen"]
        with open(vocab) as f:
            content = f.readlines()
        # you may also want to remove whitespace characters like `\n` at the end of each line
        vocabulary = [x.strip() for x in content]
        print "Vocabulary read", vocabulary

        self.asr_service.pause(True)
        self.asr_service.removeAllContext()
        try:
            self.asr_service.setVocabulary(vocabulary, True)
            self.asr_service.setParameter("Sensitivity", 0.1)
            self.asr_service.setParameter("NbHypotheses", 3)
        except:
            print "error setting vocabulary"
        self.asr_service.pause(False)

        # Start the speech recognition engine with user Test_ASR
        self.asr_service.subscribe("Test_ASR")
        print 'Speech recognition engine started'

        #subscribe to event WordRecognized
        self.subWordRecognized = self.memory_service.subscriber("WordRecognized")
        idSubWordRecognized = self.subWordRecognized.signal.connect(self.onWordRecognized)

        # speech detected
        self.subSpeechDet = self.memory_service.subscriber("SpeechDetected")
        self.id_sd = self.subSpeechDet.signal.connect(self.onSpeechDetected)


        #subscribe to google asr transcription
        if USE_GOOGLE:
            self.googleAsrRecognized = self.memory_service.subscriber("GoogleAsrRecognized")
            self.idGoogleAsrRecognized = self.googleAsrRecognized.signal.connect(self.onGoogleASR)

            self.audio_recorder.startMicrophonesRecording("utterance" + ".wav", "wav", 44100, [1, 1, 1, 1])
            print 'Audio recorder engine started'


    def quit(self):
        #Disconnecting callbacks and subscribers
        self.asr_service.unsubscribe("Test_ASR")
        self.subWordRecognized.signal.disconnect(self.idSubWordRecognized)
        self.subSpeechDet.signal.disconnect(self.id_sd)
        if USE_GOOGLE:
            self.googleAsrRecognized.signal.disconnect(self.idGoogleAsrRecognized)

    def onSpeechDetected(self, value):
        print "speech detected!", value


    def onWordRecognized(self, value):
        print "value=",value
        self.audio_recorder.stopMicrophonesRecording()
        print "Audio recorder stopped reconrding"


    def onGoogleASR(self, value):
        print "googleasr=", value

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pip", type=str, default=os.environ['PEPPER_IP'],
                        help="Robot IP address.  On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--pport", type=int, default=9559,
                        help="Naoqi port number")
    parser.add_argument("--vocab", type=str, default="resources/Allsenteces_1.txt",
                        help="The nuance vocabulary")

    args = parser.parse_args()
    pip = args.pip
    pport = args.pport
    vocab = args.vocab

    #Starting application
    try:
        connection_url = "tcp://" + pip + ":" + str(pport)
        app = qi.Application(["asr", "--qi-url=" + connection_url ])
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + pip + "\" on port " + str(pport) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)

    sr = SpeechRecognition(
        vocab=vocab,
        app=app
    )


    #let it run
    app.run()


if __name__ == "__main__":
    main()
