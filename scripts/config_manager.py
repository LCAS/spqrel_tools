#!/usr/bin/env python
import os
import yaml
from json import dumps, loads
from naoqi import *
import argparse
import xml.etree.ElementTree as ET
import pprint as pp

class config_manager(object):

    def __init__(self, pip, pport, app):
        app.start()

        self.memProxy = app.session.service("ALMemory")

        config_folder = os.path.join(os.environ["SPQREL_TOOLS"], "config")

        # open dictionary file
        dictionary_file = os.path.join(os.path.join(os.environ["SPQREL_TOOLS"], "slu4p/resources"), "nuance_dictionary.txt")
        self.nuance_dictionary = open(dictionary_file, "w")
        print "Saving to Nuance dictionary in:", dictionary_file

        # load semantic info
        memory_keys = []
        for config_file in os.listdir(config_folder):
            [config_name, ext] = config_file.split(".")
            if ext == "xml":
                memory_key = "/semantic_info/"+ config_name.lower()
                print "Loading config for", config_file, "into [" + memory_key + "] ...",
                try:
                    xml_root = ET.parse(os.path.join(config_folder, config_file)).getroot()
                    info = self.decode_xml(xml_root, config_name)
                    self.memProxy.insertData(memory_key, str(info))
                    memory_keys.append(memory_key)
                    print "DONE"
                except Exception, e:
                    print "Error parsing xml file", config_file
                    print e
                    exit(1)
            elif ext == "yaml":
                memory_key = "/semantic_info/"+ config_name.lower()
                print "Loading config for", config_file, "into [" + memory_key + "] ...",
                try:
                    yf = open(os.path.join(config_folder, config_file))
                    info = self.decode_yaml(yf, config_name)
                    self.memProxy.insertData(memory_key, str(info))
                    memory_keys.append(memory_key)
                    print "DONE"
                except Exception, e:
                    print "Error parsing xml file", config_file
                    print e
                    exit(1)

        # Close the dictionary file
        self.nuance_dictionary.close()

        #for key in memory_keys:
        #    print key, ":"
        #    pp.pprint(eval(self.memProxy.getData(key)))

    def inDictionary(self, values):
        for value in values:
            self.nuance_dictionary.write(value + "\n")

    def decode_yaml(self, yaml_file, config_name):
        content = yaml.load(yaml_file)

        # put the verbs in the dictionary
        for task in content:
            self.inDictionary(content[task]["possible_verbs"])

        return content

    def decode_xml(self, xml_root, config_name):
        config_name = config_name.lower()
        if config_name == "objects":
            categories = []
            for objcat in xml_root.findall("category"):
                objcatname = objcat.get("name")
                # put in dictionary
                self.inDictionary([objcatname])
                objcatlocation = objcat.get("defaultLocation")
                objcatroom = objcat.get("room")
                objects = []
                for obj in objcat.findall("object"):
                    objname = obj.get("name")
                    # put in dictionary
                    self.inDictionary([objname])
                    objects.append({"name": objname}) # TODO other parameters here
                categories.append({"name": objcatname, "defaultLocation": objcatlocation, "room": objcatroom, "objectList": objects})
            return categories
        elif config_name == "locations":
            rooms = []
            for locroom in xml_root.findall("room"):
                locroomname = locroom.get("name")
                locroomwp = locroom.get("waypoint")
                # put in dictionary
                self.inDictionary([locroomname])
                locations = []
                for loc in locroom.findall("location"):
                    locname = loc.get("name")
                    locwp = loc.get("waypoint")
                    # put in dictionary
                    self.inDictionary([locname])
                    locations.append({
                        "name": locname,
                        "waypoint": locwp
                    })
                rooms.append({
                    "name": locroomname,
                    "waypoint": locroomwp,
                    "locationList": locations})
            return rooms
        elif config_name == "names":
            names = []
            for name in xml_root.findall("name"):
                namename = name.text
                # put in dictionary
                self.inDictionary([namename])
                names.append({"name": namename, "gender": name.get("gender")})
            return names
        elif config_name == "questions":
            questions = []
            for question in xml_root.findall("question"):
                questionstring = question.find("q").text
                # put in dictionary
                self.inDictionary([questionstring])
                questions.append({"q": questionstring, "a": question.find("a").text})
            return questions
        else:
            return []

    #def load_config(self, filename):
    #    with open(filename, 'r') as f:
    #        return yaml.load(f)

    #def decode_dict(self, data, cstr):
    #    for i in data.keys():
    #        if type(data[i]) is not dict:
    #            if i.lower().startswith("$json:"):
    #                key = i.split(':')[1]
    #                self.memProxy.insertData(cstr + key, dumps(data[i]))
    #            else:
    #                if type(data[i]) is str:
    #                    self.memProxy.insertData(cstr + i, str(data[i]))
    #                elif type(data[i]) is int:
    #                    self.memProxy.insertData(cstr + i, int(data[i]))
    #                elif type(data[i]) is float:
    #                    self.memProxy.insertData(cstr + i, float(data[i]))
    #                elif type(data[i]) is list:
    #                    self.memProxy.insertData(cstr + i, list(data[i]))
    #                else:
    #                    self.memProxy.insertData(cstr + i, dumps(data[i]))
    #        else:
    #            self.decode_dict(data[i], cstr + i + '/')


if __name__ == '__main__':
    """
    Main entry point

    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--pip", type=str, default=os.environ['PEPPER_IP'],
                        help="Robot IP address.  On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--pport", type=int, default=9559,
                        help="Naoqi port number")
    #parser.add_argument("--file", type=str, default="spqrel-config.yaml",
    #                    help="path to config file")
    args = parser.parse_args()
    pip = args.pip
    pport = args.pport
    #filename = args.file

    try:
        # Initialize qi framework.
        connection_url = "tcp://" + args.pip + ":" + str(args.pport)
        app = qi.Application(["config_manager", "--qi-url=" + connection_url])
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)

    server = config_manager(pip, pport, app)

    #myBroker = ALBroker("pythonBroker", "0.0.0.0", 0, pip, pport)
