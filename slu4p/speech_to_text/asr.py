#http://doc.aldebaran.com/2-5/naoqi/audio/alspeechrecognition-api.html
import qi
import argparse
import sys
from os.path import expanduser
import os
import time



class SpeechRecognition(object):
    USE_GOOGLE = True
    CHANNELS = [1, 1, 1, 1]
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
            #self.asr_service.setParameter("Sensitivity", 0.1)
            self.asr_service.setParameter("NbHypotheses", 3)
        except:
            print "error setting vocabulary"
        self.asr_service.pause(False)

        # Start the speech recognition engine with user Test_ASR
        self.asr_service.subscribe("Test_ASR")
        print 'Speech recognition engine started'

        #subscribe to event WordRecognized
        self.subWordRecognized = self.memory_service.subscriber("WordRecognized")
        #self.idSubWordRecognized = self.subWordRecognized.signal.connect(self.onWordRecognized)

        # speech detected
        self.subSpeechDet = self.memory_service.subscriber("SpeechDetected")
        #self.idSubSpeechDet = self.subSpeechDet.signal.connect(self.onSpeechDetected)

        # enable
        self.subEnable = self.memory_service.subscriber("ASR_enable")
        self.idSubEnable = self.subEnable.signal.connect(self.onEnable)

        #subscribe to google asr transcription
        if self.USE_GOOGLE:
	    self.audio_recorder.stopMicrophonesRecording()
            self.googleAsrRecognized = self.memory_service.subscriber("GoogleAsrRecognized")
            self.idGoogleAsrRecognized = self.googleAsrRecognized.signal.connect(self.onGoogleASR)

            self.audio_recorder.startMicrophonesRecording("utterance" + ".wav", "wav", 44100, [1, 1, 1, 1])
            print 'Audio recorder engine started'

	self.is_enabled = False

    def quit(self):
        #Disconnecting callbacks and subscribers
        self.asr_service.unsubscribe("Test_ASR")
        if self.idSubWordRecognized is not None:
	    self.subWordRecognized.signal.disconnect(self.idSubWordRecognized)
        if self.idSubSpeechDet is not None:
	    self.subSpeechDet.signal.disconnect(self.idSubSpeechDet)
        if self.idSubEnable is not None:
	    self.subEnable.signal.disconnect(self.idSubEnable)
        if self.USE_GOOGLE:
            self.googleAsrRecognized.signal.disconnect(self.idGoogleAsrRecognized)

    def onSpeechDetected(self, value):
        print "speechdetected=", value
        self.audio_recorder.stopMicrophonesRecording()
        print "Audio recorder stopped recording"

        if self.USE_GOOGLE:
            self.memory_service.raiseEvent("GoogleRequest", self.AUDIO_FILE)


    def onWordRecognized(self, value):
        print "value=",value
        self.audio_recorder.stopMicrophonesRecording()
        print "Audio recorder stopped recording"

        if self.USE_GOOGLE:
            self.memory_service.raiseEvent("GoogleRequest", self.AUDIO_FILE)

    def onGoogleASR(self, value):
        print "googleasr=", value

    def onEnable(self, value):
        print "enable=", value
        if value == "0":
            if self.is_enabled:
                self.is_enabled = False
                if self.USE_GOOGLE:
                    self.audio_recorder.stopMicrophonesRecording()
                if self.subWordRecognized is not None:
                    self.subWordRecognized.signal.disconnect(self.idSubWordRecognized)
                if self.subSpeechDet is not None:
                    self.subSpeechDet.signal.disconnect(self.idSubSpeechDet)
                print "ASR disabled"
            else:
                print "ASR already disabled"
        else:
            if not self.is_enabled:
                if self.USE_GOOGLE:
                    #try:
                    #    self.AUDIO_FILE_DIR = self.memory_proxy.getData("NAOqibag/CurrentLogFolder") + "/asr_logs/"
                    #except:
                    self.AUDIO_FILE_DIR = expanduser('~') + '/bags/no_data/asr_logs/'
                    if not os.path.exists(self.AUDIO_FILE_DIR):
                        os.makedirs(self.AUDIO_FILE_DIR)
                    self.AUDIO_FILE_PATH = self.AUDIO_FILE_DIR + 'SPQReL_mic_'

                    self.audio_recorder.stopMicrophonesRecording()
                    self.AUDIO_FILE = self.AUDIO_FILE_PATH + str(time.time())
                    self.audio_recorder.startMicrophonesRecording(self.AUDIO_FILE + ".wav", "wav", 44100, self.CHANNELS)

                self.is_enabled = True
                self.idSubWordRecognized = self.subWordRecognized.signal.connect(self.onWordRecognized)
                self.idSubSpeechDet = self.subSpeechDet.signal.connect(self.onSpeechDetected)

                # TODO move it here!!
                #self.subscribe(
                #    event=SpeechRecognition.WR_EVENT,
                #    callback=self.word_recognized_callback
                #)
                print "ASR enabled"
            else:
                print "ASR already enabled"

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

    sr.quit()

if __name__ == "__main__":
    main()
