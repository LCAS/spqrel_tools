#!/usr/bin/env python

import webnsock
from signal import signal, SIGINT

if __name__ == "__main__":

    webserver = webnsock.MyWebserver(webnsock.ControlServer())
    backend = webnsock.MyBackend()
    signal(SIGINT,
           lambda s, f: webnsock.signal_handler(webserver, backend, s, f))
    webserver.start()
    backend.talker()

