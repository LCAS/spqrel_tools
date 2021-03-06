import os
import sys

try:
    sys.path.insert(0, os.getenv('PNP_HOME')+'/PNPnaoqi/py')
except:
    print "Please set PNP_HOME environment variable to PetriNetPlans folder."
    sys.exit(1)

import pnp_cmd_naoqi
from pnp_cmd_naoqi import *


def gpsr_guide(p, req):
    try:
        return p.exec_action('say', 'guide')
    except:
        return p.exec_action('say', "sorry_I_can't_do_this_right_now")

if __name__ == '__main__':
    p = PNPCmd()

    p.begin()

    gpsr_guide(p, {
        'whattosay': {
            'text': 'test text'
        }
    })

    p.end()