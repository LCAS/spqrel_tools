#!/usr/bin/env python

import argparse
import conditions
from conditions import set_condition

from threading import Timer

from naoqi import *

myBroker = None
check_loc = 0

# create python module
class MyModule(ALModule):
    """python class MyModule test auto documentation : comment needed to create a new python module"""

    def closest_node_callback(self, str_var_name, value):
        """callback when data change"""
        print "New goal", str_var_name, " ", value, " "
        global check_loc
        check_loc = 1

    def current_node_callback(self, str_var_name, value):
        print "GOAL REACHED: ", str_var_name, " ", value, " "
        global check_loc
        check_loc = 1

class TopologicalConditions(object):

    def __init__(self, pip, pport):
        self.cancelled = False
        self.preclon='none'
        self.precurn='none'
        self.memProxy = ALProxy("ALMemory", pip, pport)
        self.list_of_nodes = self.memProxy.getData("TopologicalNav/Nodes")        
        self._initialise_conditions()
        self.local_timer = Timer(0.5, self._local_timer)
        self.local_timer.start()
        signal.signal(signal.SIGINT, self._on_shutdown)
        signal.pause()

    def _initialise_conditions(self):
        for i in self.list_of_nodes:
            cond_name= 'closeto_' + i
            set_condition(memory_service,cond_name,'false')
            cond_name= 'currentnode_' + i
            set_condition(memory_service,cond_name,'false')

    def _local_timer(self):
        global check_loc
        if check_loc:
            curn = self.memProxy.getData("TopologicalNav/CurrentNode")
            clon = self.memProxy.getData("TopologicalNav/ClosestNode")
            if clon != 'none':
                cond_name= 'closeto_' + clon
                set_condition(memory_service,cond_name,'true')
            if self.preclon != 'none' and self.preclon != clon:
                cond_name= 'closeto_' + self.preclon
                set_condition(memory_service,cond_name,'false')
            self.preclon=clon
            if curn != 'none':
                cond_name= 'currentnode_' + curn
                set_condition(memory_service,cond_name,'true')
            if self.precurn != 'none' and self.precurn != curn:
                cond_name= 'currentnode_' + self.precurn
                set_condition(memory_service,cond_name,'false')
            self.precurn=curn
            check_loc=0
        self.local_timer = Timer(0.5, self._local_timer)
        self.local_timer.start()


    def _on_shutdown(self, signal, frame):
        print('You pressed Ctrl+C!')
        global myBroker
        self.cancelled = True
        myBroker.shutdown()
        self.local_timer.cancel()
        sys.exit(0)


if __name__ == '__main__':
    """
    Main entry point

    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--pip", type=str, default=os.environ['PEPPER_IP'],
                        help="Robot IP address.  On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--pport", type=int, default=9559,
                        help="Naoqi port number")

    args = parser.parse_args()
    pip = args.pip
    pport = args.pport


    myBroker = ALBroker("pythonBroker", "0.0.0.0", 0, pip, pport)
    try:
        pythonModule = MyModule("pythonModule")
        prox = ALProxy("ALMemory")
        prox.subscribeToEvent("TopologicalNav/CurrentNode", "pythonModule", "closest_node_callback")
        prox.subscribeToEvent("TopologicalNav/ClosestNode", "pythonModule", "current_node_callback")
    except Exception, e:
        print "error"
        print e
        exit(1)

    server = TopologicalConditions(pip, pport)