#!/usr/bin/env python

import qi
import argparse
import sys
import time
import os


def do_init():
    os.system("date >> /home/nao/init.log")    

    #ff = open('/home/nao/init.log','a')
    #ff.close()

    os.system('/home/nao/bin/tmux -2 new-session -d -s init')
    os.system('/home/nao/bin/tmux select-window -t init:0')
    os.system('/home/nao/bin/tmux rename-window \'modim\'')   # window 0 - modim
    os.system('/home/nao/bin/tmux send-keys "cd /home/nao/modim/src/GUI" C-m')
    os.system('/home/nao/bin/tmux send-keys "python ws_server.py -robot pepper" C-m')

    os.system('/home/nao/bin/tmux new-window -t init:1 -n \'blockly\'')    # window 1 - blockly server
    os.system('/home/nao/bin/tmux send-keys "cd /home/nao/pepper_tools/cmd_server/" C-m')
    os.system('/home/nao/bin/tmux send-keys "python websocket_pepper.py -robot pepper" C-m')

    os.system('/home/nao/bin/tmux new-window -t init:2 -n \'tablet\'')    # window 2 - tablet manager
    os.system('/home/nao/bin/tmux send-keys "cd /home/nao/spqrel_launch/scripts/" C-m')
    os.system('/home/nao/bin/tmux send-keys "python tabletmanager.py" C-m')




def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pip", type=str, default=os.getenv('PEPPER_IP'),
                        help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--pport", type=int, default=9559,
                        help="Naoqi port number")

    args = parser.parse_args()
    pip = args.pip
    pport = args.pport

    try:
        connection_url = "tcp://" + pip + ":" + str(pport)
        print "Connecting to ",	connection_url
        app = qi.Application(["Init", "--qi-url=" + connection_url ])
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + pip + "\" on port " + str(pport) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)

    app.start()
    session = app.session

    do_init()


if __name__ == "__main__":
    main()

