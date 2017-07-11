# SLU4P - Spoken Language Understanding 4 Pepper

This document provides a description of **SLU4P** - *Spoken Language
Understanding 4 Pepper*

*SLU4P* is composed of a complete collection of
modules that enable a fast design, development and deployment
of effective interactions through Natural Language with the Pepper robot.



It provides the following modules:
 
 * **Speech-To-Text** -> ``speech_to_text``
 * **Speech Re-Ranking** -> ``speech_reranking``
 * **Language Understanding** -> ``language_understanding``
 * **Dialogue Management** -> ``dialogue_management``
 * **Text-To-Speech** -> ``text_to_speech``

The modules are self-contained, so that there is no need to install other libraries.

##Requirements
 * `Python (2.7)`
 * `pynaoqi (> 2.5)`
 * `Pepper robot`
 
##Setup

To setup the `SLU4P` packages, the whole folder has to be uploaded directly on the Pepper (e.g. in the `/home/nao` folder).
Then, navigate to the `slu4p` folder and run the `setup.sh`:

```
$ cd /home/nao/slu4p
$ ./setup.sh
```

Notice that you may need to change the execution permissions of the bash file with:

```
$ chmod +x setup.sh
```

##Running
The system can be lauched by individually running each module (see below).

###Speech-To-Text

This module enables the speech-to-text capability on the Pepper robot.
The key feature here is that the recognition of speech is performed through two ASRs. In fact, the free-form Google ASR and the internal vocabulary-based Nuance ASR can be used simultaneously. While the Google ASR provides transcriptions without any restriction on the lexicon, the Nuance ASR needs the definition of a vocabulary of keywords/sentences that are domain-specific.
The Google ASR requires access to the Internet; however, the functionality of the module is guaranteed even when no Internet connection is provided, thanks to the Nuance ASR.

The `Speech-To-Text`module implements a continuous ASR: once the module is started, it keeps listening to new sentences. Then, whenever a new sentence is uttered, it tries to recognize the speech.

The recognition process is obtained as follows.
During initialization, two `ALProxy` instances are created: the `ALSpeechRecognition` and the `ALAudioRecorder` proxy. While the former is an interface to the internl Nuance ASR, the latter is required to record an audio file, enabling the Google ASR. At the same time, the module subscribes two event: the `WordRecognized` and the `ALTextToSpeech/TextDone` event. At the very beginning, the Nuance ASR is started, as well as the audio file recording. Whenever a `WordRecognized` event is thrown, the microphone recording is stopped, the `wav`file is converted to `flac` to reduce the data size and sent to Google for the recognition. The results are collected into a Python `dictionary`, where the keys are `GoogleASR` and `NuanceASR` and the values are the corresponding list of transcription. Finally, the event `VordRecognized` is raised, containing the above structure as value.
Whenever no results are available from Google (e.g. the service is not reachable), its corresponding list will be empty. This guarantees the system functionality even when the Internet connection is not available. Moreover, the audio recording is reset every 30 seconds, to prevent sizeable audio files.

The subscription to the `ALTextToSpeech/TextDone` event is essential to avoid possible overlaps between *listening* and *speaking*. Whenever the value is `0`, it means the robot is speaking and the listening is stopped. On the contrary, if its value is `1` the listening is started.

As the Speech Recognition is the entry point of the SLU process, it requires a mechanism to pause the recognition. This is essential when, for example, the robot is moving and does not require to listen for possible sentences. In order to pause the ASR, this module is subscribed to the `ASRPause` event. Whenever the value is `1`, the ASR will be shutdown and the listening is not triggered. To re-activate the ASR, the value needs to be set again to `0`.

 * **Resources**
    * *Nuance grammar*: a text file that contains, for each line, a keyword/sentence to be recognized by Nuance ASR.
    * *GoogleAPI keys*: a text file where, in each line, a Google key is provided.

####Running

```
$ python speech_to_text/speech_recognition.py -v resources/nuance_grammar.txt -k resources/google_keys.txt
```
####Usage

```
usage: speech_recognition.py [-h] [-i PIP] [-p PPORT] [-l LANG]
                             [--word-spotting] [--no-audio] [--no-visual]
                             [-v VOCABULARY] [-k KEYS]

optional arguments:
  -h, --help            show this help message and exit
  -i PIP, --pip PIP     Robot ip address
  -p PPORT, --pport PPORT
                        Robot port number
  -l LANG, --lang LANG  Use one of the supported languages (only English at
                        the moment)
  --word-spotting       Run in word spotting mode
  --no-audio            Turn off bip sound when recognition starts
  --no-visual           Turn off blinking eyes when recognition starts
  -v VOCABULARY, --vocabulary VOCABULARY
                        A txt file containing the list of sentences composing
                        the vocabulary
  -k KEYS, --keys KEYS  A txt file containing the list of the keys for the
                        Google ASR
```

#####TODO

 * Check the availability of the network connection (Google requirement): if not, deactivate Google ASR
 * Catch the requests limit error

###Speech Re-Ranking

The ranking provided by the ASR takes into account only the acoustic information of the spoken sentence. The domain, instead, plays a key role in determining the correct hypothesis and should be considered to improve the robusness of the recognition. This module enables a re-ranking process, by relying on evidences provided by the application domain. The process is based on approach proposed in [1].

Re-ranking is performed through as follows. While the prior distribution reflects the initial ranking provided by the ASR, the posterior distributions inject the following evidences into the ranking process:

 * **Domain-dependent nouns**: each sentence, containing a noun of the domain, is rewarded;
 * **Domain-dependent verbs**: each sentence, containing a verb invoking an action the robot is able to perform, is rewarded;
 * **Grammar-based reward**: each sentence provided by the free-form ASR, if it is contained into the Nuance ASR vocabulary, then the sentence is rewarded;
 * **Overlap reward**: whenever a sentence is recognized by both the ASRs, then it is rewarded.

The module subscribes the `VordRecognized` event and, once the new ranking has been computed, raises the event `VRanked`, where the value is a dictionary containing, for each sentence, its corresponding confidence value.



 * **Resources**
    * *Domain-dependent noun dictionary*: a text file containing a list of domain-dependent nouns;
    * *Domain-dependent verb dictionary*: a text file containing a list of domain-dependent verbs;
    * *Nuance grammar*: a text file that contains, for each line, a keyword/sentence to be recognized by Nuance ASR.

 * **Dependencies**
    * `Speech Recognition`

####Running

```
$ python speech_reranking/reranker.py --noun-dictionary resources/noun_dictionary.txt --verb-dictionary resources/verb_dictionary.txt --nuance-grammar resources/nuance_grammar.txt
```

####Usage

```
usage: reranker.py [-h] [-i PIP] [-p PPORT] [-a ALPHA] [-n NOUN_COST]
                   [-v VERB_COST] [-g GRAMMAR_COST] [-o OVERLAP_COST]
                   [--noun-dictionary NOUN_DICTIONARY]
                   [--verb-dictionary VERB_DICTIONARY]
                   [--nuance-grammar NUANCE_GRAMMAR]

optional arguments:
  -h, --help            show this help message and exit
  -i PIP, --pip PIP     Robot ip address
  -p PPORT, --pport PPORT
                        Robot port number
  -a ALPHA, --alpha ALPHA
                        Alpha parameter for the additive smoothing of the
                        prior distribution
  -n NOUN_COST, --noun-cost NOUN_COST
                        Cost for the noun posterior distribution
  -v VERB_COST, --verb-cost VERB_COST
                        Cost for the verb posterior distribution
  -g GRAMMAR_COST, --grammar-cost GRAMMAR_COST
                        Cost for the grammar posterior distribution
  -o OVERLAP_COST, --overlap-cost OVERLAP_COST
                        Cost for the overlap posterior distribution
  --noun-dictionary NOUN_DICTIONARY
                        A txt file containing the list of domain nouns
  --verb-dictionary VERB_DICTIONARY
                        A txt file containing the list of domain verbs
  --nuance-grammar NUANCE_GRAMMAR
                        A txt file containing the list of sentences composing
                        the vocabulary
```

###Language Understanding

WIP

 * **Resources**
    * [LU4R](http://sag.art.uniroma2.it/lu4r.html)

 * **Dependencies**
    * `Speech Recognition`

###Dialogue Management

Whenever a sentence is recognized, a reply has to be generated. This module enables such capability into the Pepper. The interaction patterns are specified through the AIML language. Hence, in order to run the module, an AIML Knowledge Base has to be provided. The AIML interpreter is based on [PyAIML](https://pypi.python.org/pypi/aiml/0.8.6). As NaoQi does not allow to install packages through the `pip` command, the source code of the interpreter has been embedded into the module.

Whenever the Re-Ranking module raises the `VRanked` event, this module picks the best hypothesis from the list and raises the event `Veply`, containing the response generated by the AIML interpreter.

 * **Resources**
    * *AIML Knowledge Base*: a collection of `.aiml` files, defining the behavior of the dialogue agent

 * **Dependencies**
    * `Speech Recognition`

####Running

```
$ python dialogue_management/dialogue_manager.py -a resources/aiml_kbs/alice
```

####Usage

```
usage: dialogue_manager.py [-h] [-i PIP] [-p PPORT] [-a AIML_PATH]

optional arguments:
  -h, --help            show this help message and exit
  -i PIP, --pip PIP     Robot ip address
  -p PPORT, --pport PPORT
                        Robot port number
  -a AIML_PATH, --aiml-path AIML_PATH
                        Path to the root folder of AIML Knowledge Base
```

###Text-To-Speech

This module is the end of the processing chain. Its purpose is to generate a speech, given a text representing the sentence. During initialization, it creates `ALAnimatedSpeech` and `ALMotion` proxies. While the former is used to produce the audio given the text, the latter is used to recover to the breathing behavior after the animated speech finishes. The module subscribes the `Veply` event and, whenever it is triggered, generates the corresponding speech.

 * **Dependencies**
    * `Speech Recognition`
    * `Dialogue Management`

####Running

```
$ python text_to_speech/text_to_speech.py
```

####Usage

```
usage: text_to_speech.py [-h] [-i PIP] [-p PPORT]
                         [-l {contextual,random,disabled}]

optional arguments:
  -h, --help            show this help message and exit
  -i PIP, --pip PIP     Robot ip address
  -p PPORT, --pport PPORT
                        Robot port number
  -l {contextual,random,disabled}, --language-mode {contextual,random,disabled}
                        The body language modality while speaking
```

##Author

* **Andrea Vanzo** - [andrea.vanzo1@gmail.com](mailto:andrea.vanzo1@gmail.com)

##Acknowledgements

##References
[1] Andrea Vanzo, Danilo Croce, Emanuele Bastianelli, Roberto Basili, Daniele Nardi, *"Robust Spoken Language Understanding for House Service Robots"*, In Proceedings of the 17th International Conference on Intelligent Text Processing and Computational Linguistics CICLing 2016, Konya, Turkey, 2016.

##FAQ

* **When I try to run one of the modules, I get the following error**:

```
Traceback (most recent call last):
  File "speech_to_text/speech_recognition.py", line 4, in <module>
    from google_client import *
  File "/data/home/nao/slu4p/speech_to_text/google_client.py", line 5, in <module>
    import slu_utils
ImportError: No module named slu_utils
```
This error occurs because Python cannot find the `slu_utils` module as the `PYTHONPATH` variable for the current session does not contain `/home/nao/slu4p`. Even though you previously run the `setup.sh` script, whenever a new connection with Pepper is open (through, for example `ssh nao@pepper.local`) it seems that the new session does not source the `.bashrc`.

To solve the issue, you just need to run

```
$ source ~/.bashrc
```
on the new terminal.

