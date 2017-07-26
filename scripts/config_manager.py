#!/usr/bin/env python
import yaml
from json import dumps, loads
from naoqi import *
import argparse


class config_manager(object):

    def __init__(self, pip, pport, filename):
        self.memProxy = ALProxy("ALMemory", pip, pport)

        try:
            data = self.load_config(filename)
        except Exception, e:
            print "error"
            print e
            exit(1)

        if type(data) is list:
            for i in data:
                self.decode_dict(i, '/')
        else:
            self.decode_dict(data, '/')

    def load_config(self, filename):
        with open(filename, 'r') as f:
            return yaml.load(f)

    def decode_dict(self, data, cstr):
        for i in data.keys():
            if type(data[i]) is not dict:
                if i.lower().startswith("$json:"):
                    key = i.split(':')[1]
                    self.memProxy.insertData(cstr + key, dumps(data[i]))
                else:
                    if type(data[i]) is str:
                        self.memProxy.insertData(cstr + i, str(data[i]))
                    elif type(data[i]) is int:
                        self.memProxy.insertData(cstr + i, int(data[i]))
                    elif type(data[i]) is float:
                        self.memProxy.insertData(cstr + i, float(data[i]))
                    elif type(data[i]) is list:
                        self.memProxy.insertData(cstr + i, list(data[i]))
                    else:
                        self.memProxy.insertData(cstr + i, dumps(data[i]))
            else:
                self.decode_dict(data[i], cstr + i + '/')


if __name__ == '__main__':
    """
    Main entry point

    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--pip", type=str, default=os.environ['PEPPER_IP'],
                        help="Robot IP address.  On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--pport", type=int, default=9559,
                        help="Naoqi port number")
    parser.add_argument("--file", type=str, default="spqrel-config.yaml",
                        help="path to config file")
    args = parser.parse_args()
    pip = args.pip
    pport = args.pport
    filename = args.file

    server = config_manager(pip, pport, filename)

    #myBroker = ALBroker("pythonBroker", "0.0.0.0", 0, pip, pport)
