import requests
import json


class LU4RClient:
    ip = '127.0.0.1'  # class variable shared by all instances
    port = 9001
    chain_type = ''
    output_type = ''
    language = ''
    HEADERS = {'content-type': 'application/json'}

    LU4R_STATUS_URL = ''
    LU4R_INFO_URL = ''
    LU4R_PARSE_URL = ''

    json_entities = ''

    def __init__(self, lip, lport):
        self.ip = lip
        self.port = lport

        self.LU4R_STATUS_URL = 'http://' + self.ip + ':' + str(self.port) + '/init/status'
        self.LU4R_INFO_URL = 'http://' + self.ip + ':' + str(self.port) + '/init/info'
        self.LU4R_PARSE_URL = 'http://' + self.ip + ':' + str(self.port) + '/service/slu'

        self.status()

        info = json.loads(self.info())
        self.chain_type = info['chain_type']
        self.output_type = info['output_type']
        self.language = info['language']

    def status(self):
        try:
            response = requests.post(self.LU4R_STATUS_URL, {}, headers=self.HEADERS)
            print "[" + self.inst.__class__.__name__ + "]" + response.text
            return 1
        except requests.exceptions.RequestException as e:
            print "[" + self.inst.__class__.__name__ + "] [STATUS]ERROR! LU4R is not running. Launch it and retry."
            return 0

    def info(self):
        try:
            response = requests.post(self.LU4R_INFO_URL, {}, headers=self.HEADERS)
            return response.text
        except requests.exceptions.RequestException as e:
            print "[" + self.inst.__class__.__name__ + "] [INFO]ERROR! LU4R is not running. Launch it and retry."
            return 0

    def parse_sentence(self, sentence):
        try:
            json_hypo = '{\"hypotheses\":[{\"transcription\":\"' + sentence + '\", \"confidence\":"1.0\",\"rank\":\"1\"}]}'
            to_send = {'hypo': json_hypo, 'entities': '{\"entities\":[' + self.json_entities + ']}'}
            response = requests.post(self.LU4R_PARSE_URL, to_send, headers=self.HEADERS)
            return response.text
        except requests.exceptions.RequestException as e:
            print "[" + self.inst.__class__.__name__ + "] [PARSE]ERROR! LU4R cannot to parse."

    def parse_sentences(self, sentences):
        sentences_dict = []
        counter = 1;
        for sentence in sentences:
            hypothesis = dict()
            hypothesis['transcription'] = sentence
            hypothesis['confidence'] = str(1 - (float(counter) / float(len(sentences))))
            hypothesis['rank'] = str(counter)
            sentences_dict.append(hypothesis)
            counter = counter + 1
        try:
            json_hypo = '{\"hypotheses\":' + json.dumps(sentences_dict) + '}'
            to_send = {'hypo': json_hypo, 'entities': '{\"entities\":[' + self.json_entities + ']}'}
            response = requests.post(self.LU4R_PARSE_URL, to_send, headers=self.HEADERS)
            return response.text
        except requests.exceptions.RequestException as e:
            print "[" + self.inst.__class__.__name__ + "] [PARSE]ERROR! LU4R cannot to parse."

    def parse_sentence_perceptual(self, sentence, entities):
        if self.chain_type != 'SIMPLE':
            print "[" + self.inst.__class__.__name__ + "] [WARNING]BASIC chain active. Perceptual information will be neglected."
        self.json_entities = entities
        return self.parse_sentence(sentence)
