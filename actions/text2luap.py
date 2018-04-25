#!/usr/bin/env python
# encoding=utf8

# encoding=utf8
import argparse
import sys
import requests
import execplan
import qi
import os
import traceback

lu4r_ip = '192.168.127.16'
lu4r_port = '9001'
lu4r_url = 'http://' + lu4r_ip + ':' + str(lu4r_port) + '/service/nlu'


def to_plan(asr, frame):
    return execplan.LU4R_to_plan(frame, asr, memory_service)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('input_file', type=str, help='Full path of folder with audio files to be recognized')
    parser.add_argument('output_file', type=str, help='Output file with transcriptions')

    args = parser.parse_args()

    # Starting application
    try:
        connection_url = "tcp://" + os.environ['PEPPER_IP'] + ":" + str(9559)
        print "Connecting to ", connection_url
        app = qi.Application(["lua4rtest", "--qi-url=" + connection_url])
    except RuntimeError:
        sys.exit(1)

    app.start()
    memory_service = app.session.service("ALMemory")

    file_out = open(args.output_file, 'w')

HEADERS = {'content-type': 'application/json'}
f = open(args.input_file, 'r')
for line in f:
    if line[0] == '#':
        continue
    line = line.strip()
    if line == "":
        continue
    data = '{\"hypotheses\":[{\"transcription\":\" ' + line + '\", \"confidence\":0.9,\"rank\":0}]}'
    entities = '{\"entities\":[]}'
    to_send = {'hypo': data, 'entities': entities}
    response = requests.post(lu4r_url, to_send, headers=HEADERS)
    answer = response.text.strip()
    try:
        print "+++ Utterance: " , line
        plan = to_plan(line, answer)
        print "+++ LU4R response: ", response.text.replace('\n', '')
        print '+++ Final plan: ', plan

        #file_out.write(plan + '\n')
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print "*** utterance '%s' cannot be translated. " % line
        print "*** exception: %s" % str(e)
        print "  * traceback: %s" % traceback.extract_tb(exc_traceback)
    print "\n"
