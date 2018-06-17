import qi
import argparse
import signal
import os
from google_client import *
from event_abstract import *
from os.path import expanduser


class SpeechRecognition(object):
    WR_EVENT = "WordRecognized"
    TD_EVENT = "ALTextToSpeech/TextDone"
    SD_EVENT = "SpeechDetected"
    ASR_ENABLE = "ASR_enable"
    FLAC_COMM = 'flac -f '
    CHANNELS = [0, 0, 1, 0]
    timeout = 0

    busy = False

    USE_GOOGLE = False

    def __init__(self, language, sensitivity, word_spotting, num_hypo, audio, visual, vocabulary_file, google_keys, asr_logging, app):
        super(self.__class__, self).__init__()

        app.start()
        session = app.session

        self.__shutdown_requested = False
        signal.signal(signal.SIGINT, self.signal_handler)

        vocabulary = slu_utils.lines_to_list(vocabulary_file)
        if (language == 'en') or (language == 'eng') or (language == 'english') or (language == 'English'):
            nuance_language = 'English'
            google_language = "en-US"

        self.logging = asr_logging

        #dialogP = session.service("ALDialog")
        #try:
        #    print dialogP.getAllLoadedTopics()
        #    print dialogP.getActivatedTopics()
        #    dialogP.unloadTopic("modifiable_grammar") # hack to avoid error on ALSpeechRecognition
        #except:
        #    print "Topic modifable_grammar not set, trying with resetAll"
        #    try:
        #        dialogP.resetAll()
        #    except:
        #        print "Error while  resetAll"
        # or change language and put it back

        self.nuance_asr = session.service("ALSpeechRecognition")

        if self.USE_GOOGLE:
            self.audio_recorder = session.service("ALAudioRecorder")

            self.google_asr = GoogleClient(google_language, google_keys)

        self.memory = session.service("ALMemory")

        self.configure(
            sensitivity=sensitivity,
            vocabulary=vocabulary,
            nuance_language=nuance_language,
            word_spotting=word_spotting,
            num_hypo=num_hypo,
            audio=audio,
            visual=visual
        )

    def start(self):
        self.td_sub = self.memory.subscriber(SpeechRecognition.TD_EVENT)
        self.td_sub_id = self.td_sub.signal.connect(self.text_done_callback)


        self.enable_sub = self.memory.subscriber(SpeechRecognition.ASR_ENABLE)
        self.enable_sub_id = self.enable_sub.signal.connect(self.enable_callback)

        self.wr_sub = self.memory.subscriber(SpeechRecognition.WR_EVENT)
        self.wr_sub_id = self.wr_sub.signal.connect(self.word_recognized_callback)
        #self.wr_sub_id = None
        time.sleep(3)

        print "[" + self.__class__.__name__ + "] Subscribers:", self.memory.getSubscribers(
            SpeechRecognition.WR_EVENT)
        print "[" + self.__class__.__name__ + "] Subscribers:", self.memory.getSubscribers(
            SpeechRecognition.TD_EVENT)
        print "[" + self.__class__.__name__ + "] Subscribers:", self.memory.getSubscribers(
            SpeechRecognition.ASR_ENABLE)

        self.is_enabled = True

        #print "[" + self.__class__.__name__ + "] ASR disabled"

        if self.USE_GOOGLE:
            if self.logging:
                self.AUDIO_FILE_DIR = expanduser('~') + '/bags/asr_logs/'
            else:
                self.AUDIO_FILE_DIR = '/tmp/asr_logs/'
            if not os.path.exists(self.AUDIO_FILE_DIR):
                os.makedirs(self.AUDIO_FILE_DIR)
            self.AUDIO_FILE_PATH = self.AUDIO_FILE_DIR + 'SPQReL_mic_'

        #if self.is_enabled:
        #    self.unsubscribe(SpeechRecognition.WR_EVENT)
        #self.unsubscribe(SpeechRecognition.TD_EVENT)
        #self.unsubscribe(SpeechRecognition.ASR_ENABLE)
        #self.broker.shutdown()

    def stop(self):
        if self.USE_GOOGLE:
            self.audio_recorder.stopMicrophonesRecording()
        self.is_enabled = False
        self.__shutdown_requested = True
        print '[' + self.__class__.__name__ + '] Good-bye'

    def configure(self, sensitivity, word_spotting, num_hypo, nuance_language, audio, visual, vocabulary):
        self.nuance_asr.pause(True)
        print "pause"
        self.nuance_asr.setParameter("Sensitivity", sensitivity)
        self.nuance_asr.setParameter("NbHypotheses", num_hypo)
        self.nuance_asr.setVocabulary(vocabulary, word_spotting)
        self.nuance_asr.setLanguage(nuance_language)
        self.nuance_asr.setAudioExpression(audio)
        self.nuance_asr.setVisualExpression(visual)
        self.nuance_asr.pause(False)
        print "un-pause"

    def collect_google_asr(self):
        res = []
        """
        Convert Wave file into Flac file
        """
        if os.path.exists(self.AUDIO_FILE + '.wav'):
            if os.path.getsize(self.AUDIO_FILE + '.wav') > 0:
                os.system(self.FLAC_COMM + self.AUDIO_FILE + '.wav')
                f = open(self.AUDIO_FILE + '.flac', 'rb')
                flac_cont = f.read()
                f.close()
                res = [r.encode('ascii', 'ignore').lower() for r in self.google_asr.recognize_data(flac_cont)]
        return res

    def speech_detected_callback(self, msg):
        print "speech detected"
        if self.USE_GOOGLE:
            self.audio_recorder.stopMicrophonesRecording()
            self.nuance_asr.pause(True)
            print "pause"
        if self.busy:
            return
        self.busy = True
        results = {'GoogleASR': [], 'NuanceASR': []}
        if self.USE_GOOGLE:
            google_asr = self.collect_google_asr()

            results['GoogleASR'] = google_asr

        print "[" + self.__class__.__name__ + "] " + str(results)
        self.memory.raiseEvent("LocalVordRecognized", results)
        self.timeout = 0

        if self.USE_GOOGLE:
            self.nuance_asr.pause(False)
            print "un-pause"
            self.audio_recorder.stopMicrophonesRecording()
            self.AUDIO_FILE = self.AUDIO_FILE_PATH + str(time.time())
            self.audio_recorder.startMicrophonesRecording(self.AUDIO_FILE + ".wav", "wav", 44100, self.CHANNELS)
        self.busy = False

    def word_recognized_callback(self, msg):
        print "word recognized"
        if self.USE_GOOGLE:
            self.audio_recorder.stopMicrophonesRecording()
            self.nuance_asr.pause(True)
            print "pause"
        if self.busy:
            return
        self.busy = True
        results = {'GoogleASR': [], 'NuanceASR': []}
        if self.USE_GOOGLE:
            google_asr = self.collect_google_asr()

            results['GoogleASR'] = google_asr

        results['NuanceASR'] = [msg[0].lower()]
        print "[" + self.__class__.__name__ + "] " + str(results)
        self.memory.raiseEvent("LocalVordRecognized", results)
        self.timeout = 0

        if self.USE_GOOGLE:
            self.nuance_asr.pause(False)
            print "un-pause"
            self.audio_recorder.stopMicrophonesRecording()
            self.AUDIO_FILE = self.AUDIO_FILE_PATH + str(time.time())
            self.audio_recorder.startMicrophonesRecording(self.AUDIO_FILE + ".wav", "wav", 44100, self.CHANNELS)
        self.busy = False

    def text_done_callback(self, msg):
        try:
            if self.is_enabled:
                if msg == 0:
                    if self.USE_GOOGLE:
                        self.audio_recorder.stopMicrophonesRecording()
                    self.nuance_asr.pause(True)
                    print "pause"
                else:
                    if self.USE_GOOGLE:
                        self.audio_recorder.stopMicrophonesRecording()
                        self.AUDIO_FILE = self.AUDIO_FILE_PATH + str(time.time())
                        self.audio_recorder.startMicrophonesRecording(self.AUDIO_FILE + ".wav", "wav", 44100, self.CHANNELS)
                    self.nuance_asr.pause(False)
                    print "un-pause"
        except Exception as e:
            print e.message

    def enable_callback(self, msg):
        if msg == "0":
            if self.is_enabled:
                self.is_enabled = False
                if self.USE_GOOGLE:
                    self.audio_recorder.stopMicrophonesRecording()
                if self.wr_sub_id is not None:
                    self.wr_sub_id.disconnect()
                print "[" + self.__class__.__name__ + "] ASR disabled"
            else:
                print "[" + self.__class__.__name__ + "] ASR already disabled"
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
                self.is_enabled = True

                if self.USE_GOOGLE:
                    self.audio_recorder.stopMicrophonesRecording()
                    self.AUDIO_FILE = self.AUDIO_FILE_PATH + str(time.time())
                    self.audio_recorder.startMicrophonesRecording(self.AUDIO_FILE + ".wav", "wav", 44100, self.CHANNELS)

                #self.subscribe(
                #    event=SpeechRecognition.WR_EVENT,
                #    callback=self.word_recognized_callback
                #)
                print "[" + self.__class__.__name__ + "] ASR enabled"
            else:
                print "[" + self.__class__.__name__ + "] ASR already enabled"

    def reset(self):
        if self.is_enabled:
            print "[" + self.__class__.__name__ + "] Reset recording.."
            if self.USE_GOOGLE:
                self.audio_recorder.stopMicrophonesRecording()
                try:
                    os.remove(self.AUDIO_FILE + ".wav")
                except:
                    print "No such file: " + self.AUDIO_FILE + ".wav"
                self.AUDIO_FILE = self.AUDIO_FILE_PATH + str(time.time())
                self.audio_recorder.startMicrophonesRecording(self.AUDIO_FILE + ".wav", "wav", 44100, self.CHANNELS)

    #def _spin(self, *args):
    #    while not self.__shutdown_requested:
    #        for f in args:
    #            f()
    #        time.sleep(.1)
    #        self.timeout = self.timeout + 1
    #        if self.timeout > 300:
    #            self.timeout = 0
    #            self.reset()

    def signal_handler(self, signal, frame):
        print "[" + self.__class__.__name__ + "] Caught Ctrl+C, stopping."
        if self.USE_GOOGLE:
            self.audio_recorder.stopMicrophonesRecording()
        self.__shutdown_requested = True
        print "[" + self.__class__.__name__ + "] Good-bye"


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--pip", type=str, default=os.environ['PEPPER_IP'],
                        help="Robot ip address")
    parser.add_argument("-p", "--pport", type=int, default=9559,
                        help="Robot port number")
    parser.add_argument("-l", "--lang", type=str, default="en",
                        help="Use one of the supported languages (only English at the moment)")
    parser.add_argument("-s", "--sensitivity", type=float, default=0.8,
                        help="Sets the sensitivity of the speech recognizer")
    parser.add_argument("--word-spotting", type=bool, default=True,
                        help="Run in word spotting mode")
    parser.add_argument("--num-hypotesys", type=int, default=10,
                        help="Number of hypotesys returned by nuance")
    parser.add_argument("--no-audio", type=bool, default=False,
                        help="Turn off bip sound when recognition starts")
    parser.add_argument("--no-visual", type=bool, default=False,
                        help="Turn off blinking eyes when recognition starts")
    parser.add_argument("-v", "--vocabulary", type=str, default="resources/nuance_grammar.txt",
                        help="A txt file containing the list of sentences composing the vocabulary")
    parser.add_argument("-k", "--keys", type=str, default="resources/cloud_google_keys.txt",
                        help="A txt file containing the list of the keys for the Google ASR")
    parser.add_argument("-o", "--asr-logging", type=bool, default=False,
                        help="Logs the audio files")
    args = parser.parse_args()

    try:
        # Initialize qi framework.
        connection_url = "tcp://" + args.pip + ":" + str(args.pport)
        app = qi.Application(["local_speech_recognition", "--qi-url=" + connection_url])
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)


    sr = SpeechRecognition(
        language=args.lang,
        sensitivity=args.sensitivity,
        word_spotting=args.word_spotting,
        num_hypo=args.num_hypotesys,
        audio=not args.no_audio,
        visual=not args.no_visual,
        vocabulary_file=args.vocabulary,
        google_keys=args.keys,
        asr_logging=args.asr_logging,
        app=app
    )

    sr.start()

    app.run()

    sr.quit()


if __name__ == "__main__":
    main()
