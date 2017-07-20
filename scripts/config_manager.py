#!/usr/bin/env python
import sys
import yaml
import json
from naoqi import *
import argparse



class config_manager(object):
    
    def __init__(self, pip, pport, filename):
        self.memProxy = ALProxy("ALMemory", pip, pport)

        try:
            data = self.load_config(filename) 
            print data
        except Exception, e:
            print "error"
            print e
            exit(1)
    
        if type(data) is list:
            print "list"
            for i in data:
                self.decode_dict(i, '/')
        else:
            print "not list"
            self.decode_dict(data, '/')

    
    def load_config(self,filename):
        print "loading " + filename
        with open(filename, 'r') as f:
            return yaml.load(f)
    
    def decode_dict(self, data, cstr):
        for i in data.keys():
            cstr=cstr + i
            if type(data[i]) is not dict:
                 print "inserting:", cstr, data[i]
                 self.memProxy.insertData(cstr, data[i])
            else:
                cstr=cstr + '/'
                self.decode_dict(data[i], cstr)
    
    

if __name__ == '__main__':
    """
    Main entry point

    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--pip", type=str, default=os.environ['PEPPER_IP'],
                        help="Robot IP address.  On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--pport", type=int, default=9559,
                        help="Naoqi port number")
    parser.add_argument("--file", type=str, default="config.yaml",
                        help="path to config file")
    args = parser.parse_args()
    pip = args.pip
    pport = args.pport
    filename = args.file

    server = config_manager(pip, pport, filename)

    #myBroker = ALBroker("pythonBroker", "0.0.0.0", 0, pip, pport)
