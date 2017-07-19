import argparse
import signal
from naoqi import ALProxy, ALBroker, ALModule
from google_client import *
from event_abstract import *
from os.path import expanduser


class SpeechRecognition(EventAbstractClass):
    WR_EVENT = "WordRecognized"
    TD_EVENT = "ALTextToSpeech/TextDone"
    ASR_ENABLE = "ASR_enable"
    FLAC_COMM = 'flac -f '
    CHANNELS = [0, 0, 1, 0]
    timeout = 0

    def __init__(self, ip, port, language, word_spotting, audio, visual, vocabulary_file, google_keys, asr_logging):
        super(self.__class__, self).__init__(self, ip, port)

        self.__shutdown_requested = False
        signal.signal(signal.SIGINT, self.signal_handler)

        vocabulary = slu_utils.lines_to_list(vocabulary_file)
        if (language == 'en') or (language == 'eng') or (language == 'english') or (language == 'English'):
            nuance_language = 'English'
            google_language = "en-US"

        self.logging = asr_logging

        self.nuance_asr = ALProxy("ALSpeechRecognition")

        self.audio_recorder = ALProxy("ALAudioRecorder")

        self.google_asr = GoogleClient(google_language, google_keys)

        self.memory_proxy = ALProxy("ALMemory")

        self.configure(
            vocabulary=vocabulary,
            nuance_language=nuance_language,
            word_spotting=word_spotting,
            audio=audio,
            visual=visual
        )

    def start(self, *args, **kwargs):
        self.subscribe(
            event=SpeechRecognition.TD_EVENT,
            callback=self.text_done_callback
        )

        self.subscribe(
            event=SpeechRecognition.ASR_ENABLE,
            callback=self.enable_callback
        )

        print "[" + self.inst.__class__.__name__ + "] Subscribers:", self.memory.getSubscribers(
            SpeechRecognition.WR_EVENT)
        print "[" + self.inst.__class__.__name__ + "] Subscribers:", self.memory.getSubscribers(
            SpeechRecognition.TD_EVENT)
        print "[" + self.inst.__class__.__name__ + "] Subscribers:", self.memory.getSubscribers(
            SpeechRecognition.ASR_ENABLE)

        self.is_enabled = False

        print "[" + self.inst.__class__.__name__ + "] ASR disabled"

        if self.logging:
            self.AUDIO_FILE_DIR = expanduser('~') + '/bags/asr_logs/'
        else:
            self.AUDIO_FILE_DIR = '/tmp/asr_logs/'
        if not os.path.exists(self.AUDIO_FILE_DIR):
            os.makedirs(self.AUDIO_FILE_DIR)
        self.AUDIO_FILE_PATH = self.AUDIO_FILE_DIR + 'SPQReL_mic_'

        self._spin()

        if self.is_enabled == True:
            self.unsubscribe(SpeechRecognition.WR_EVENT)
        self.unsubscribe(SpeechRecognition.TD_EVENT)
        self.unsubscribe(SpeechRecognition.ASR_ENABLE)
        self.broker.shutdown()

    def stop(self):
        self.audio_recorder.stopMicrophonesRecording()
        self.is_enabled = False
        self.__shutdown_requested = True
        print '[' + self.inst.__class__.__name__ + '] Good-bye'

    def configure(self, word_spotting, nuance_language, audio, visual, vocabulary):
        self.nuance_asr.pause(True)
        self.nuance_asr.setVocabulary(vocabulary, word_spotting)
        self.nuance_asr.setLanguage(nuance_language)
        self.nuance_asr.setAudioExpression(audio)
        self.nuance_asr.setVisualExpression(visual)
        self.nuance_asr.pause(False)

    def word_recognized_callback(self, *args, **kwargs):
        self.audio_recorder.stopMicrophonesRecording()
        self.nuance_asr.pause(True)
        """
        Convert Wave file into Flac file
        """
        os.system(self.FLAC_COMM + self.AUDIO_FILE + '.wav')
        f = open(self.AUDIO_FILE + '.flac', 'rb')
        flac_cont = f.read()
        f.close()

        results = {}
        results['GoogleASR'] = [r.encode('ascii', 'ignore').lower() for r in self.google_asr.recognize_data(flac_cont)]
        results['NuanceASR'] = [args[1][0].lower()]
        print "[" + self.inst.__class__.__name__ + "] " + str(results)
        self.timeout = 0
        self.nuance_asr.pause(False)
        self.audio_recorder.stopMicrophonesRecording()
        self.AUDIO_FILE = self.AUDIO_FILE_PATH + str(time.time())
        self.audio_recorder.startMicrophonesRecording(self.AUDIO_FILE + ".wav", "wav", 44100, self.CHANNELS)
        self.memory.raiseEvent("VordRecognized", results)

    def text_done_callback(self, *args, **kwargs):
        try:
            if self.is_enabled:
                if args[1] == 0:
                    self.audio_recorder.stopMicrophonesRecording()
                    self.nuance_asr.pause(True)
                else:
                    self.audio_recorder.stopMicrophonesRecording()
                    self.AUDIO_FILE = self.AUDIO_FILE_PATH + str(time.time())
                    self.audio_recorder.startMicrophonesRecording(self.AUDIO_FILE + ".wav", "wav", 44100, self.CHANNELS)
                    self.nuance_asr.pause(False)
        except Exception as e:
            print e.message

    def enable_callback(self, *args, **kwargs):
        if args[1] == "0":
            if self.is_enabled:
                self.is_enabled = False
                self.audio_recorder.stopMicrophonesRecording()
                self.unsubscribe(SpeechRecognition.WR_EVENT)
                print "[" + self.inst.__class__.__name__ + "] ASR disabled"
            else:
                print "[" + self.inst.__class__.__name__ + "] ASR already disabled"
        else:
            if not self.is_enabled:
                #try:
                #    self.AUDIO_FILE_DIR = self.memory_proxy.getData("NAOqibag/CurrentLogFolder") + "/asr_logs/"
                #except:
                self.AUDIO_FILE_DIR = expanduser('~') + '/bags/no_data/asr_logs/'
                if not os.path.exists(self.AUDIO_FILE_DIR):
                    os.makedirs(self.AUDIO_FILE_DIR)
                self.AUDIO_FILE_PATH = self.AUDIO_FILE_DIR + 'SPQReL_mic_'
                self.is_enabled = True
                self.audio_recorder.stopMicrophonesRecording()
                self.AUDIO_FILE = self.AUDIO_FILE_PATH + str(time.time())
                self.audio_recorder.startMicrophonesRecording(self.AUDIO_FILE + ".wav", "wav", 44100, self.CHANNELS)
                self.subscribe(
                    event=SpeechRecognition.WR_EVENT,
                    callback=self.word_recognized_callback
                )
                print "[" + self.inst.__class__.__name__ + "] ASR enabled"
            else:
                print "[" + self.inst.__class__.__name__ + "] ASR already enabled"

    def reset(self):
        if self.is_enabled:
            print "[" + self.inst.__class__.__name__ + "] Reset recording.."
            self.audio_recorder.stopMicrophonesRecording()
            try:
                os.remove(self.AUDIO_FILE + ".wav")
            except:
                print "No such file: " + self.AUDIO_FILE + ".wav"
            self.AUDIO_FILE = self.AUDIO_FILE_PATH + str(time.time())
            self.audio_recorder.startMicrophonesRecording(self.AUDIO_FILE + ".wav", "wav", 44100, self.CHANNELS)

    def _spin(self, *args):
        while not self.__shutdown_requested:
            for f in args:
                f()
            time.sleep(.1)
            self.timeout = self.timeout + 1
            if self.timeout > 300:
                self.timeout = 0
                self.reset()

    def signal_handler(self, signal, frame):
        print "[" + self.inst.__class__.__name__ + "] Caught Ctrl+C, stopping."
        self.audio_recorder.stopMicrophonesRecording()
        self.__shutdown_requested = True
        print "[" + self.inst.__class__.__name__ + "] Good-bye"


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--pip", type=str, default="127.0.0.1",
                        help="Robot ip address")
    parser.add_argument("-p", "--pport", type=int, default=9559,
                        help="Robot port number")
    parser.add_argument("-l", "--lang", type=str, default="en",
                        help="Use one of the supported languages (only English at the moment)")
    parser.add_argument("--word-spotting", action="store_true",
                        help="Run in word spotting mode")
    parser.add_argument("--no-audio", action="store_true",
                        help="Turn off bip sound when recognition starts")
    parser.add_argument("--no-visual", action="store_true",
                        help="Turn off blinking eyes when recognition starts")
    parser.add_argument("-v", "--vocabulary", type=str, default="resources/nuance_grammar.txt",
                        help="A txt file containing the list of sentences composing the vocabulary")
    parser.add_argument("-k", "--keys", type=str, default="resources/google_keys.txt",
                        help="A txt file containing the list of the keys for the Google ASR")
    parser.add_argument("-o", "--asr-logging", type=bool, default=False,
                        help="Logs the audio files")
    args = parser.parse_args()

    sr = SpeechRecognition(
        ip=args.pip,
        port=args.pport,
        language=args.lang,
        word_spotting=args.word_spotting,
        audio=not args.no_audio,
        visual=not args.no_visual,
        vocabulary_file=args.vocabulary,
        google_keys=args.keys,
        asr_logging=args.asr_logging
    )
    sr.update_globals(globals())
    sr.start()


if __name__ == "__main__":
    main()
