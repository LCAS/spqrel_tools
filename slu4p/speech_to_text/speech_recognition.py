import argparse
import signal
from naoqi import ALProxy, ALBroker, ALModule
from google_client import *
from event_abstract import *


class SpeechRecognition(EventAbstractClass):
    WR_EVENT = "WordRecognized"
    TD_EVENT = "ALTextToSpeech/TextDone"
    ASR_ENABLE = "ASR_enable"
    FLAC_COMM = 'flac -f '
    FILE_PATH = '/tmp/recording'
    CHANNELS = [0, 0, 1, 0]
    timeout = 0

    def __init__(self, ip, port, language, word_spotting, audio, visual, vocabulary_file, google_keys):
        super(self.__class__, self).__init__(self, ip, port)

        self.__shutdown_requested = False
        signal.signal(signal.SIGINT, self.signal_handler)

        vocabulary = slu_utils.lines_to_list(vocabulary_file)
        if (language == 'en') or (language == 'eng') or (language == 'english') or (language == 'English'):
            nuance_language = 'English'
            google_language = "en-US"

        self.nuance_asr = ALProxy("ALSpeechRecognition")

        self.audio_recorder = ALProxy("ALAudioRecorder")

        self.google_asr = GoogleClient(google_language, google_keys)

        self.configure(
            vocabulary=vocabulary,
            nuance_language=nuance_language,
            word_spotting=word_spotting,
            audio=audio,
            visual=visual
        )

    def start(self, *args, **kwargs):
        self.subscribe(
            event=SpeechRecognition.WR_EVENT,
            callback=self.word_recognized_callback
        )
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

        self.is_enabled = True

        self.audio_recorder.stopMicrophonesRecording()
        self.audio_recorder.startMicrophonesRecording(self.FILE_PATH + ".wav", "wav", 16000, self.CHANNELS)

        self._spin()

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
        os.system(self.FLAC_COMM + self.FILE_PATH + '.wav')
        f = open(self.FILE_PATH + '.flac', 'rb')
        flac_cont = f.read()
        f.close()

        results = {}
        results['GoogleASR'] = [r.encode('ascii', 'ignore').lower() for r in self.google_asr.recognize_data(flac_cont)]
        results['NuanceASR'] = [args[1][0].lower()]
        print "[" + self.inst.__class__.__name__ + "] " + str(results)
        self.timeout = 0
        self.nuance_asr.pause(False)
        self.audio_recorder.stopMicrophonesRecording()
        self.audio_recorder.startMicrophonesRecording(self.FILE_PATH + ".wav", "wav", 16000, self.CHANNELS)
        self.memory.raiseEvent("VordRecognized", results)

    def text_done_callback(self, *args, **kwargs):
        if self.is_enabled:
            if args[1] == 0:
                self.audio_recorder.stopMicrophonesRecording()
                self.nuance_asr.pause(True)
            else:
                self.audio_recorder.stopMicrophonesRecording()
                self.audio_recorder.startMicrophonesRecording(self.FILE_PATH + ".wav", "wav", 16000, self.CHANNELS)
                self.nuance_asr.pause(False)

    def enable_callback(self, *args, **kwargs):
        if args[1] == 1:
            self.audio_recorder.stopMicrophonesRecording()
            self.unsubscribe(SpeechRecognition.WR_EVENT)
            self.is_enabled = False
        else:
            self.audio_recorder.stopMicrophonesRecording()
            self.audio_recorder.startMicrophonesRecording(self.FILE_PATH + ".wav", "wav", 16000, self.CHANNELS)
            self.subscribe(
                event=SpeechRecognition.WR_EVENT,
                callback=self.word_recognized_callback
            )
            self.is_enabled = True

    def reset(self):
        if self.is_enabled:
            print "[" + self.inst.__class__.__name__ + "] Reset recording.."
            self.audio_recorder.stopMicrophonesRecording()
            self.audio_recorder.startMicrophonesRecording(self.FILE_PATH + ".wav", "wav", 16000, self.CHANNELS)

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
    args = parser.parse_args()

    sr = SpeechRecognition(
        ip=args.pip,
        port=args.pport,
        language=args.lang,
        word_spotting=args.word_spotting,
        audio=not args.no_audio,
        visual=not args.no_visual,
        vocabulary_file=args.vocabulary,
        google_keys=args.keys
    )
    sr.update_globals(globals())
    sr.start()


if __name__ == "__main__":
    main()
