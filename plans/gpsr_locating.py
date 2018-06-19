import os
import sys

try:
    sys.path.insert(0, os.getenv('PNP_HOME')+'/PNPnaoqi/py')
except:
    print "Please set PNP_HOME environment variable to PetriNetPlans folder."
    sys.exit(1)

import pnp_cmd_naoqi
from pnp_cmd_naoqi import *


def gpsr_locating(p, req):
    try:
        return p.exec_action('say', 'locating')
    except:
        return p.exec_action('say', "sorry_I_can't_do_this_right_now")

if __name__ == '__main__':
    p = PNPCmd()

    p.begin()

    gpsr_locating(p, {
        'object': {
            'location': 'kitchen'
        }
    })

    p.end()