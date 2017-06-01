import qi
import argparse
import json
import sys
from speech.google_client import GoogleClient

def main():

	with open('vocabulary.txt') as f:
	    content = f.readlines()
	# you may also want to remove whitespace characters like `\n` at the end of each line
	content = [x.strip() for x in content]
	print content
	
	#AIzaSyAONQ_K4NOIGfRWXmiuXonThf2rs3XzKPY
	#AIzaSyDya-9naDiG0Dm8MVVKhQw50HmsvfZeZfE
	client = GoogleClient('en-US', 'AIzaSyAONQ_K4NOIGfRWXmiuXonThf2rs3XzKPY')

	filepath = 'File16.wav'
	
	print client.recognize(filepath)

if __name__ == "__main__":
	main()