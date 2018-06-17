#http://doc.aldebaran.com/2-5/naoqi/audio/alspeechrecognition-api.html
import qi
import argparse
import sys
import os

USE_GOOGLE = False

audio_recorder = None

def onWordRecognized(value):
    global audio_recorder
    print "value=",value
    audio_recorder.stopMicrophonesRecording()
    print "Audio recorder stopped reconrding"


def onGoogleASR(value):
    print "googleasr=", value

def main():
    global audio_recorder
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
        app = qi.Application(["ReactToTouch", "--qi-url=" + connection_url ])
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + pip + "\" on port " + str(pport) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)

    app.start()
    session = app.session

    #Starting services
    asr_service = session.service("ALSpeechRecognition")
    asr_service.setLanguage("English")

    audio_recorder = session.service("ALAudioRecorder")

    memory_service  = session.service("ALMemory")

    #establishing test vocabulary
    #vocabulary = ["yes", "no", "please", "hello", "goodbye", "hi, there", "go to the kitchen"]
    with open(vocab) as f:
        content = f.readlines()
    # you may also want to remove whitespace characters like `\n` at the end of each line
    vocabulary = [x.strip() for x in content]
    print "Vocabulary read", vocabulary

    asr_service.pause(True)
    asr_service.removeAllContext()
    try:
        asr_service.setVocabulary(vocabulary, False)
        asr_service.setParameter("Sensitivity", 0.1)
    except:
        print "error setting vocabulary"
    asr_service.pause(False)

    # Start the speech recognition engine with user Test_ASR
    asr_service.subscribe("Test_ASR")
    print 'Speech recognition engine started'


    audio_recorder.startMicrophonesRecording("utterance" + ".wav", "wav", 44100, [1, 1, 1, 1])
    print 'Audio recorder engine started'

    #subscribe to event WordRecognized
    subWordRecognized = memory_service.subscriber("WordRecognized")
    idSubWordRecognized = subWordRecognized.signal.connect(onWordRecognized)

    #subscribe to google asr transcription
    if USE_GOOGLE:
        googleAsrRecognized = memory_service.subscriber("GoogleAsrRecognized")
        idGoogleAsrRecognized = googleAsrRecognized.signal.connect(onGoogleASR)


    #let it run
    app.run()

    #Disconnecting callbacks and subscribers
    asr_service.unsubscribe("Test_ASR")
    subWordRecognized.signal.disconnect(idSubWordRecognized)
    if USE_GOOGLE:
        googleAsrRecognized.signal.disconnect(idGoogleAsrRecognized)

if __name__ == "__main__":
    main()
