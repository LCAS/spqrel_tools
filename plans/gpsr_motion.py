import os
import sys

try:
    sys.path.insert(0, os.getenv('PNP_HOME')+'/PNPnaoqi/py')
except:
    print "Please set PNP_HOME environment variable to PetriNetPlans folder."
    sys.exit(1)

import pnp_cmd_naoqi
from pnp_cmd_naoqi import *

from support.semantics_interpreter import SemanticResolver

def gpsr_motion(p, req):

    sr = SemanticResolver()
    result = sr.parse_requires(req)

    if result['wp'] is not None:
        try:
            return p.exec_action('navigateto', result['wp'],interrupt='aborted', recovery='restart_action')
        except:
            return p.exec_action('say', "sorry_I_can't_do_this_right_now")
    else:
        try:
            return p.exec_action('navigateto', 'wp6',interrupt='aborted', recovery='restart_action')
        except:
            return p.exec_action('say', "sorry_I_can't_do_this_right_now")


if __name__ == '__main__':
    p = PNPCmd()

    p.begin()

    gpsr_motion(p,'')

    p.end()