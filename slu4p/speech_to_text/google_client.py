import requests
import json
import slu_utils
import base64

class GoogleClient(object):
    timeout = 20
    url = ''
    headers = {"Content-Type": "application/json"}

    def __init__(self, language, key_file):
        super(GoogleClient, self).__init__()

        app.start()
        session = app.session

        self.memory_service = session.service("ALMemory")

        keys = slu_utils.lines_to_list(key_file)
        self.language = language
        key = keys[0]
        self.url = "https://speech.googleapis.com/v1/speech:recognize?key=%s" % key

        self.subGR = self.memory_service.subscriber("GoogleRequest")
        self.idsubGR = self.subGR.signal.connect(self.onGoogleRequest)

    def quit(self):
        self.subGR.signal.disconnect(self.idsubGR)
        

    def onGoogleRequest(self, value):
        print "onGoogleRequest:", value
        file_path = str(value) + ".wav"

        transcriptions = self.recognize_file(file_path)

        print transcriptions

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
    parser = argparse.ArgumentParser()
    parser.add_argument("--pip", type=str, default=os.environ['PEPPER_IP'],
                        help="Robot IP address.  On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--pport", type=int, default=9559,
                        help="Naoqi port number")

    args = parser.parse_args()
    pip = args.pip
    pport = args.pport


    #Starting application
    try:
        connection_url = "tcp://" + pip + ":" + str(pport)
        app = qi.Application(["google_client", "--qi-url=" + connection_url ])
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + pip + "\" on port " + str(pport) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)

    gc = GoogleClient(
        "en-US",
        "resources/cloud_google_keys.txt",
        app
    )

    app.run()

    gc.quit()


if __name__ == "__main__":
    main()
