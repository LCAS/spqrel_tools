import os
import urllib
import json
import slu_utils
import pyaudio
import wave


class AudioRecorder:
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    CHUNK = 1024
    recording = True

    def __init__(self, language, key_file):
        self.audio = pyaudio.PyAudio()

    def startMicrophonesRecording(self, file_path):
        # start Recording
        self.stream = self.audio.open(format=self.FORMAT, channels=self.CHANNELS,
                                      rate=self.RATE, input=True,
                                      frames_per_buffer=self.CHUNK)
        print "recording..."
        frames = []

        while self.recording:
            data = self.stream.read(self.CHUNK)
            frames.append(data)
        print "finished recording"



    def stopMicrophonesRecording(self):
        # stop Recording
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()

        waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        waveFile.setnchannels(CHANNELS)
        waveFile.setsampwidth(audio.get_sample_size(FORMAT))
        waveFile.setframerate(RATE)
        waveFile.writeframes(b''.join(frames))
        waveFile.close()


def main():



if __name__ == "__main__":
    main()
