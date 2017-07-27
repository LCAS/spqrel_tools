#!/usr/bin/env python
# encoding=utf8

# encoding=utf8
import argparse
import sys
import requests

lu4r_ip = '127.0.0.1'
lu4r_port = '9001'
lu4r_url = 'http://' + lu4r_ip + ':' + str(lu4r_port) + '/service/nlu'

parser = argparse.ArgumentParser()
parser.add_argument('input_file', help='Full path of folder with audio files to be recognized')
parser.add_argument('output_file', help='Output file with transcriptions')
args = parser.parse_args()
file_out = open(args.output_file,'w')

HEADERS = {'content-type': 'application/json'}
f=open(args.input_file,'r')
for line in f:
	if line[0] == '#':
		continue
	line=line.strip()
	if line=="":
		continue
        data= '{\"hypotheses\":[{\"transcription\":\" ' + line  + '\", \"confidence\":0.9,\"rank\":0}]}'
        entities='{\"entities\":[]}'
        to_send = {'hypo': data, 'entities': entities}
        response = requests.post(lu4r_url, to_send, headers=HEADERS)
        print "LU4R response: ",response.text

        answer=response.text.strip()
        file_out.write(answer+'\n')
        


