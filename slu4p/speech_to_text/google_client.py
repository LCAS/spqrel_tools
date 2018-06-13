import requests
import json
import slu_utils
import base64

class GoogleClient:
    timeout = 20
    url = ''
    headers = {"Content-Type": "application/json"}

    def __init__(self, language, key_file):
        keys = slu_utils.lines_to_list(key_file)
        self.language = language
        key = keys[0]
        self.url = "https://speech.googleapis.com/v1/speech:recognize?key=%s" % key

    def recognize_file(self, file_path):
        try:
            print "[" + self.__class__.__name__ + "] [GOOGLE] Recognizing file.."
            transcriptions = []
            data = open(file_path, "rb").read()
            base64_data = base64.b64encode(data)
            audio_json = {"content": base64_data}
            config_json = {"languageCode": self.language}
            json_data = {"config": config_json, "audio": audio_json}
            response = requests.post(self.url, json=json_data, headers=self.headers, timeout=self.timeout)
            json_res = json.loads(response.text)
            if "results" in json_res.keys() and "alternatives" in json_res["results"][0].keys():
                for alternative in json_res["results"][0]["alternatives"]:
                    transcriptions.append(alternative["transcript"].lower())
            return transcriptions
        except ValueError as ve:
            print ve.message
            print "[" + self.__class__.__name__ + "] [RECOGNIZE]ERROR! Google APIs are temporary unavailable. Returning empty list.."
            return []
        except requests.exceptions.RequestException as e:
            print e.message
            print "[" + self.__class__.__name__ + "] [RECOGNIZE]ERROR! Unable to reach Google. Returning empty list.."
            return []

    def recognize_data(self, data):
        try:
            print "[" + self.__class__.__name__ + "] [GOOGLE] Recognizing data.."
            transcriptions = []
            base64_data = base64.b64encode(data)
            audio_json = {"content": base64_data}
            config_json = {"languageCode": self.language}
            json_data = {"config": config_json, "audio": audio_json}
            response = requests.post(self.url, json=json_data, headers=self.headers, timeout=self.timeout)
            json_res = json.loads(response.text)
            print json_res
            if "results" in json_res.keys() and "alternatives" in json_res["results"][0].keys():
                for alternative in json_res["results"][0]["alternatives"]:
                    transcriptions.append(alternative["transcript"].lower())
            return transcriptions
        except ValueError as ve:
            print ve.message
            print "[" + self.__class__.__name__ + "] [RECOGNIZE]ERROR! Google APIs are temporary unavailable. Returning empty list.."
            return []
        except requests.exceptions.RequestException as e:
            print e.message
            print "[" + self.__class__.__name__ + "] [RECOGNIZE]ERROR! Unable to reach Google. Returning empty list.."
            return []


def main():
    g = GoogleClient("en-US", "resources/cloud_google_keys.txt")
    while True:
        print g.recognize_file('resources/recording.flac')


if __name__ == "__main__":
    main()
