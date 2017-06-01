#!/usr/bin/env python

# -*- encoding: UTF-8 -*-
# Get an image from NAO. Display it and save it using PIL.
import os
import sys
import time

import argparse


# Python Image Library
import Image

from naoqi import ALProxy


def showNaoImage(IP, PORT):
  """
  First get an image from Nao, then show it on the screen with PIL.
  """

  camProxy = ALProxy("ALVideoDevice", IP, PORT)
  resolution = 2    # VGA
  colorSpace = 11   # RGB

  videoClient = camProxy.subscribe("python_client", resolution, colorSpace, 5)

  t0 = time.time()

  # Get a camera image.
  # image[6] contains the image data passed as an array of ASCII chars.
  naoImage = camProxy.getImageRemote(videoClient)

  t1 = time.time()

  # Time the image transfer.
  print "acquisition delay ", t1 - t0

  camProxy.unsubscribe(videoClient)


  # Now we work with the image returned and save it as a PNG  using ImageDraw
  # package.

  # Get the image size and pixel array.
  imageWidth = naoImage[0]
  imageHeight = naoImage[1]
  array = naoImage[6]

  # Create a PIL Image from our pixel array.
  im = Image.fromstring("RGB", (imageWidth, imageHeight), array)

  # Save the image.
  im.save("camImage.png", "PNG")

  im.show()



if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument("--pip", type=str, default=os.environ['PEPPER_IP'],
                    help="Robot IP address.  On robot or Local Naoqi: use '127.0.0.1'.")
  parser.add_argument("--pport", type=int, default=9559,
                    help="Naoqi port number")
  parser.add_argument("--camera", type=int, default=0,
                    help="Robot camera ID address. 0 by default")

  args = parser.parse_args()
  IP = args.pip
  PORT = args.pport


  naoImage = showNaoImage(IP, PORT)

