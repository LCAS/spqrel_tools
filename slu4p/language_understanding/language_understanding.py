import qi
import os
import argparse
import signal
from lu4r_client import LU4RClient
import slu_utils
import xml.etree.ElementTree as ET
import pprint as pp


class LanguageUnderstanding(object):
    PATH = ''
    UNDERSTAND_EVENT = "UnderstandCommand"
    SEMANTIC_INFO_MEM = "/semantic_info"

    def __init__(self, lip, lport, app):
        super(LanguageUnderstanding, self).__init__()

        app.start()
        session = app.session

        self.__shutdown_requested = False
        signal.signal(signal.SIGINT, self.signal_handler)

        self.memory = session.service('ALMemory')

        self.load_gpsr_xmls()

        self.lu4r_client = LU4RClient(lip, lport)

    def start(self):
        self.ranked_sub = self.memory.subscriber(LanguageUnderstanding.UNDERSTAND_EVENT)
        self.ranked_sub_id = self.ranked_sub.signal.connect(self.callback)

        print "[" + self.__class__.__name__ + "] Subscribers:", self.memory.getSubscribers(LanguageUnderstanding.UNDERSTAND_EVENT)

    def load_gpsr_xmls(self):
        # NOTE only parsing the GPSR tasks definitions
        self.gpsr_tasks_definition = eval( self.memory.getData( self.SEMANTIC_INFO_MEM + "/gpsr_tasks_definition") )
        self.spr_tasks_definition = eval( self.memory.getData( self.SEMANTIC_INFO_MEM + "/spr_tasks_definition") )
        self.objects = eval( self.memory.getData( self.SEMANTIC_INFO_MEM + "/objects") )
        self.names = eval( self.memory.getData( self.SEMANTIC_INFO_MEM + "/names") )
        self.locations = eval( self.memory.getData( self.SEMANTIC_INFO_MEM + "/locations") )
        self.questions = eval( self.memory.getData( self.SEMANTIC_INFO_MEM + "/questions") )
        print "Semantic info loaded!"

    def quit(self):
        self.ranked_sub.signal.disconnect(self.ranked_sub_id)

    def callback(self, msg):
        print "callback=", msg
        msg = msg.lower()
        google_transcription = self.memory.getData("googleasrresponse")[0].lower()
        print "analysing google transcription:", google_transcription
        if msg == "spr":
            print google_transcription
            #get ws interpretation
            ws_interpretation = self.doWordSpotting(google_transcription, "spr")

            print "[" + self.__class__.__name__ + "] Word spotting: " + str(ws_interpretation)

            self.memory.raiseEvent("CommandInterpretation", ws_interpretation)
            self.memory.insertData("CommandInterpretation", ws_interpretation)
        elif msg == "gpsr":
            #transcriptions_dict = slu_utils.list_to_dict_w_probabilities(google_transcription)
            best_transcription = google_transcription
            print "[" + self.__class__.__name__ + "] User says: " + best_transcription

            # get lu4r interpretation
            lu4r_interpretation = str(self.lu4r_client.parse_sentence(best_transcription))
            print "[" + self.__class__.__name__ + "] LU4R Interpretation: " + str(lu4r_interpretation)

            # get ws interpretation
            ws_interpretation = self.doWordSpotting(best_transcription, "gpsr")
            print "[" + self.__class__.__name__ + "] Word spotting: " + str(ws_interpretation)

            # merge interpretations TODO
            #merged_interpretation = self.mergeInterpretations(lu4r_interpretation, ws_interpretation)


            #print "[" + self.__class__.__name__ + "] Merged: " + str(merged_interpretation)

            interpretations = [lu4r_interpretation, ws_interpretation]
            self.memory.raiseEvent("CommandInterpretation", interpretations)
        elif msg == "question":
            pass

    def mergeInterpretations(self, lu4r_interpretation, ws_interpretation):
        lu4rDict = self.generateLu4rDict(lu4r_interpretation)

        for task in ws_interpretation:
            for lu4r_name in task["lu4r_name"]:
                for lu4rkey in lu4rDict.keys():
                    if lu4r_name == lu4rkey:
                        print "found match:", lu4r_name, lu4rkey
                        mergedTask = self.mergeLu4rWsTasks(lu4rDict[lu4rkey], task)

    def mergeLu4rWsTasks(self, lu4rTask, wsTask):
        for requirement in task["requires"]:
            for lnreq in requirement["lu4r_name"]:
                for lu4rArg in lu4rTask:
                    if lu4rArg.keys()[0] == lnreq:
                        print "aaaaaaaaaaa:", lu4rArg.keys()[0], lnreq
                ##TODO
                ##TODO


    def generateLu4rDict(self, inter, depth=1):
        frames_dict = {}

        start_fi = inter.find(" / ") + 3
        end_fi = inter.find("\n")
        frame, rest = inter[start_fi:end_fi], inter[end_fi:]

        if frame == "and":
            ops = rest.split("\n" + "\t"*depth + ":op")[1:]
            frame_ops_list = []
            for op in ops:
                frame_ops_list.append(self.generateLu4rDict(op, depth+1))

            frames_dict.update({frame: frame_ops_list})
        else:
            frame = frame.split("-")[1]
            args = rest.split("\n" + "\t"*depth + ":")[1:]
            args_list = []
            for arg in args:
                end_ani = arg.find(" (")
                start_avi = arg.find(" / ") + 3
                arg_name, arg_value = arg[:end_ani], arg[start_avi:]
                if ":mod" in arg_value:
                    splitted = arg_value.split("\t"*(depth+1) + ":mod")
                    print splitted, arg_value
                    arg_value = splitted[0][:splitted[0].find("\n")]
                    mod_list = []
                    for split in splitted[1:]:
                        start_mi, end_mi = split.find(" / ") + 3, split.find(")")
                        arg_value = split[start_mi:end_mi] + arg_value
                    args_list.append({arg_name: arg_value})
                else:
                    arg_value = arg_value[:arg_value.find(")")]
                    args_list.append({arg_name : arg_value})

            frames_dict.update({frame: args_list})

        return frames_dict

    def doWordSpotting(self, transcription, test):
        spotted_tasks = []

        if test == "spr":
            tasks_definition = self.spr_tasks_definition
        elif test == "gpsr":
            tasks_definition = self.gpsr_tasks_definition

        # look for verbs
        for task in tasks_definition.keys():
            for vb in tasks_definition[task]["possible_verbs"]:
                if vb in transcription:
                    vb_index = transcription.find(vb)
                    spotted_tasks.append({"task": task, "index": vb_index, "verb": vb, "requires": tasks_definition[task]["requires"]})
        # look for objects
        obj_spotted = []
        objcat_spotted = []
        for objcat in self.objects:
            objcatname = objcat["name"]
            if objcatname in transcription:
                objcat_index = transcription.find(objcatname)
                objcat_spotted.append({"objcat": objcatname, "index": objcat_index})
            for obj in objcat["objectList"]:
                objname = obj["name"]
                if objname in transcription:
                    obj_index = transcription.find(objname)
                    obj_spotted.append({"objcat": objcatname, "index": obj_index, "obj": objname})
        for obj in self.objects_to_guess:
            if obj in transcription:
                obj_index = transcription.find(obj)
                obj_spotted.append({"obj": obj, "index": obj_index, "toguess": "object"})
        # look for persons
        psn_spotted = []
        for nametag in self.names:
            name = nametag["name"]
            if name in transcription:
                name_index = transcription.find(name)
                psn_spotted.append({"index": name_index, "person": name})
        for name in self.names_to_guess:
            if name in transcription:
                name_index = transcription.find(name)
                psn_spotted.append({"person": name, "index": name_index, "toguess": "name"})
        # look for locations
        loc_spotted = []
        room_spotted = []
        for room in self.locations:
            roomname = room["name"]
            if roomname in transcription:
                room_index = transcription.find(roomname)
                room_spotted.append({"room": roomname, "index": room_index})
            for location in room["locationList"]:
                locname = location["name"]
                if locname in transcription:
                    loc_index = transcription.find(locname)
                    loc_spotted.append({"room": roomname, "index": loc_index, "loc": locname})
        # look for gestures
        #gest_spotted = []
        #for gest in self.gesturesxml.findall("gesture"):
        #    gestname = gest.get("name")
        #    if gestname in transcription:
        #        gest_index = transcription.find(gestname)
        #        gest_spotted.append({"gest": gestname, "index": gest_index})
        # TODO look for questions?
        # look for whattosay
        wts_spotted = []
        for wts in self.whattosay:
            if wts in transcription:
                wts_index = transcription.find(wts)
                wts_spotted.append({"wts": wts, "index": wts_index})

        quest_spotted = []
        max_quest_spotted = {}
        for q in self.questions:
            qstring = q["q"].replace("?", "").replace("!", "").replace(",", "").replace(".", "")
            qsplit = qstring.split(" ")
            tsplit = transcription.split(" ")
            equalwords = sum([1 for qw in qsplit if qw in transcription])
            #print q, equalwords, len(tsplit)
            if equalwords > len(tsplit)*0.7:
                quest_spotted.append({"question": q, "equals": equalwords})
        maxeq = 0
        for quest in quest_spotted:
            if quest["equals"] > maxeq:
                max_quest_spotted = quest["question"]
                maxeq = quest["equals"]

        print maxeq



        # sort the complete list by index
        #complete_list = obj_spotted + psn_spotted + loc_spotted + wts_spotted
        #complete_list = sorted(complete_list, key=lambda k: k['index'])

        # complete dict
        attr_spotted = {
                    "object": obj_spotted,
                    "name": psn_spotted,
                    "location": loc_spotted,
                    "whattosay": wts_spotted,
                    "room": room_spotted,
                    "category": objcat_spotted
                    }

        # look for other things listed under "possible_names"
        for i in range(len(spotted_tasks)):
            n_req = 0
            for requirement in spotted_tasks[i]["requires"]:
                name_requirement = requirement.keys()[0]


        # fill the requirements with the complete spotted list
        vb_indexes = sorted([t["index"] for t in spotted_tasks])
        # for attcat in attr_spotted.keys():
        #     for att in attr_spotted[attcat]:
        #         if att["index"]


        for i in range(len(spotted_tasks)):
            n_req = 0
            for requirement in spotted_tasks[i]["requires"]:
                name_requirement = requirement.keys()[0]
                if "possible_names" in requirement[name_requirement]:
                    for poss_name in requirement[name_requirement]["possible_names"]:
                        if poss_name in transcription:
                            if "spotted" in spotted_tasks[i]["requires"][n_req].keys():
                                spotted_tasks[i]["requires"][n_req]["spotted"].append(poss_name)
                            else:
                                spotted_tasks[i]["requires"][n_req].update({"spotted":poss_name})

                else:
                    for attr in attr_spotted[name_requirement]:
                        #if attr["index"] > vb_indexes[i] and len(vb_indexes) > i and attr["index"] < vb_indexes[i + 1]:
                        if "spotted" in spotted_tasks[i]["requires"][n_req].keys():
                            spotted_tasks[i]["requires"][n_req]["spotted"].append(attr)
                        else:
                            spotted_tasks[i]["requires"][n_req].update({"spotted":attr})
                n_req += 1

        spotted_tasks.append(max_quest_spotted)

        pp.pprint (spotted_tasks)

        return spotted_tasks

    def signal_handler(self, signal, frame):
        print "[" + self.__class__.__name__ + "] Caught Ctrl+C, stopping."
        self.__shutdown_requested = True
        print "[" + self.__class__.__name__ + "] Good-bye"

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

    objects_to_guess = [
        " it "
    ]

    names_to_guess = [
        " me ",
        " him ",
        " her "
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
        app=app
    )

    lu.start()

    app.run()

    lu.quit()


if __name__ == "__main__":
    main()
