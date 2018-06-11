import qi
import os
import argparse
import signal
from lu4r_client import LU4RClient
import slu_utils
import xml.etree.ElementTree as ET


class LanguageUnderstanding(object):
    PATH = ''
    RANKED_EVENT = "VRanked"

    def __init__(self, lip, lport, gpsrgen, app):
        super(LanguageUnderstanding, self).__init__()

        app.start()
        session = app.session

        self.__shutdown_requested = False
        signal.signal(signal.SIGINT, self.signal_handler)

        self.load_gpsr_xmls(gpsrgen)

        self.lu4r_client = LU4RClient(lip, lport)
        self.memory = session.service('ALMemory')

    def start(self):
        self.ranked_sub = self.memory.subscriber(LanguageUnderstanding.RANKED_EVENT)
        self.ranked_sub_id = self.ranked_sub.signal.connect(self.callback)

        print "[" + self.__class__.__name__ + "] Subscribers:", self.memory.getSubscribers(LanguageUnderstanding.RANKED_EVENT)

    def load_gpsr_xmls(self, gpsrgen):
        # NOTE only parsing the GPSR tasks definitions
        self.objectsxml = ET.parse(gpsrgen + "/GPSRCmdGen/Resources/Objects.xml").getroot()
        self.namesxml = ET.parse(gpsrgen + "/GPSRCmdGen/Resources/Names.xml").getroot()
        self.questionsxml = ET.parse(gpsrgen + "/GPSRCmdGen/Resources/Questions.xml").getroot()
        self.locationsxml = ET.parse(gpsrgen + "/GPSRCmdGen/Resources/Locations.xml").getroot()
        self.gesturesxml = ET.parse(gpsrgen + "/GPSRCmdGen/Resources/Gestures.xml").getroot()

    def quit(self):
        self.ranked_sub.signal.disconnect(self.ranked_sub_id)

    def callback(self, msg):
        transcriptions_dict = slu_utils.list_to_dict_w_probabilities(msg)
        best_transcription = slu_utils.pick_best(transcriptions_dict)
        print "[" + self.__class__.__name__ + "] User says: " + best_transcription
        lu4r_interpretation = str(self.lu4r_client.parse_sentence(best_transcription))

        ws_interpretation = self.doWordSpotting(best_transcription)

        print "[" + self.__class__.__name__ + "] LU4R Interpretation: " + str(lu4r_interpretation)
        print "[" + self.__class__.__name__ + "] Word spotting: " + str(ws_interpretation)
        interpretations = [lu4r_interpretation, ws_interpretation]
        self.memory.raiseEvent("CommandInterpretations", interpretations)

    def  doWordSpotting(self, transcription):
        # look for verbs
        vb_spotted = []
        for vbcat in self.verbs.keys():
            for vb in self.verbs[vbcat]:
                if vb in transcription:
                    vb_index = transcription.find(vb)
                    vb_spotted.append({"verbcat" : vbcat, "index": vb_index, "verb": vb})
        # look for objects
        obj_spotted = []
        for objcat in self.objectsxml.findall("category"):
            objcatname = objcat.get("name")
            for obj in objcat.findall("object"):
                objname = obj.get("name")
                if objname in transcription:
                    obj_index = transcription.find(objname)
                    obj_spotted.append({"objcat": objcatname, "index": obj_index, "obj": objname})
        # look for persons
        psn_spotted = []
        for nametag in self.namesxml.findall("name"):
            name = nametag.text
            if name in transcription:
                name_index = transcription.find(name)
                psn_spotted.append({"index": name_index, "person": name})
        # look for locations
        loc_spotted = []
        for room in self.locationsxml.findall("room"):
            roomname = room.get("name")
            for location in room.findall("location"):
                locname = location.get("name")
                if locname in transcription:
                    loc_index = transcription.find(locname)
                    loc_spotted.append({"room": roomname, "index": loc_index, "loc": locname})
        # look for gestures
        gest_spotted = []
        for gest in self.gesturesxml.findall("gesture"):
            gestname = gest.get("name")
            if gestname in transcription:
                gest_index = transcription.find(gestname)
                gest_spotted.append({"gest": gestname, "index": gest_index})
        # TODO look for questions?
        # look for whattosay
        wts_spotted = []
        for wts in self.whattosay:
            if wts in transcription:
                wts_index = transcription.find(wts)
                wts_spotted.append({"wts": wts, "index": wts_index})

        # sort the complete list by index
        complete_list = vb_spotted + obj_spotted + psn_spotted + loc_spotted + gest_spotted + wts_spotted
        complete_list = sorted(complete_list, key=lambda k: k['index'])

        return complete_list

    def signal_handler(self, signal, frame):
        print "[" + self.__class__.__name__ + "] Caught Ctrl+C, stopping."
        self.__shutdown_requested = True
        print "[" + self.__class__.__name__ + "] Good-bye"

    ## where possible uses the same categories of lu4r
    verbs = {
        "taking" : ["get", "grasp", "take", "retrieve", "pick up"],   #"$vbtake"
        "place" : ["put", "place", "leave", "set"],   #"$vbplace"
        "speak" : ["tell", "say"],   #"$vbspeak"
        "motion" : ["go to", "navigate to"],   #"$vbgopl"
        "motion" : ["go to", "navigate to", "enter"],   #"$vbgor"
        "locating" : ["find", "locate", "spot", "pinpoint", "look for"],   #"$vbfind"
        "guide" : ["guide", "escort", "take", "lead", "accompany", "conduct"],   #"$vbguide"
        "cotheme" : ["follow", "come behind", "go behind", "come after", "go after", "accompany"],   #"$vbfollow"
        "bringing" : ["bring", "deliver", "give", "hand", "hand over"]   #"$vbdeliver"
    }

    whattosay = [
     "something about yourself",
     "the time",
     "what day is today",
     "what day is tomorrow",
     "your team's name",
     "your team's country",
     "your team's affiliation",
     "the day of the week",
     "the day of the month",
     "a joke"
    ]

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--pip", type=str, default=os.environ['PEPPER_IP'],
                        help="Robot ip address")
    parser.add_argument("-p", "--pport", type=int, default=9559,
                        help="Robot port number")
    parser.add_argument("-l", "--luar-ip", type=str, default=os.environ['LU4R_IP'],
                        help="The LU4R ip address")
    parser.add_argument("-o", "--luar-port", type=int, default=9001,
                        help="The LU4R listening port")
    parser.add_argument("-g", "--gpsr-gen", type=str, default=os.environ['SPQREL_HOME'] + "/../GPSRCmdGen",
                        help="The GPSRCmdGen folder path")


    args = parser.parse_args()

    try:
        # Initialize qi framework.
        connection_url = "tcp://" + args.pip + ":" + str(args.pport)
        app = qi.Application(["dialogue_manager", "--qi-url=" + connection_url], autoExit=False)
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)

    lu = LanguageUnderstanding(
        lip=args.luar_ip,
        lport=args.luar_port,
        gpsrgen=args.gpsr_gen,
        app=app
    )

    lu.start()

    app.run()

    lu.quit()


if __name__ == "__main__":
    main()
