import argparse
import yaml
import qi
import sys
from PIL import Image
import json
from base64 import encodestring

from os.path import dirname, realpath, join
from os import environ
from io import BytesIO


class MapBridge(object):

    def __init__(self, memory_service, mapprops, topomap):

        self.memory_service = memory_service

        self.props = self.read_map_properties(mapprops)

        self.mapprops_path = realpath(dirname(mapprops))
        imgpath = join(self.mapprops_path, self.props['image'])

        self.map_img = Image.open(imgpath)

    def read_map_properties(self, mapprops):
        with open(mapprops, 'r') as f:
            props = yaml.load(f)
        return props

    def publish_map(self):
        props_json = json.dumps(self.props)
        print props_json
        memory_service.insertData("/map/props", props_json)
        memory_service.raiseEvent("/map/props", props_json)
        io = BytesIO()
        self.map_img.save(io, "JPEG")
        base64 = encodestring(io.getvalue())
        memory_service.insertData("/map/jpg", base64)
        memory_service.raiseEvent("/map/jpg", base64)

if __name__ == '__main__':
    """
    Main entry point

    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--pip", type=str, default=environ['PEPPER_IP'],
                        help="Robot IP address." +
                        "On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--pport", type=int, default=9559,
                        help="Naoqi port number")
    parser.add_argument("--tmap", type=str, default="INB3123.tpg",
                        help="path to topological map")
    parser.add_argument("--map", type=str, default="INB3123.yaml",
                        help="run fake nav")
    args = parser.parse_args()
    pip = args.pip
    pport = args.pport

    try:
        connection_url = "tcp://" + pip + ":" + str(pport)
        print "Connecting to ", connection_url
        app = qi.Application(["SPQReLUI", "--qi-url=" + connection_url])
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" +
               pip + "\" on port " + str(pport) + ".\n"
               "Please check your script arguments. "
               "Run with -h option for help.")
        sys.exit(1)

    app.start()
    session = app.session
    memory_service = session.service("ALMemory")

    topomap_file = args.tmap
    map_file = args.map

    mb = MapBridge(memory_service, map_file, topomap_file)
    mb.publish_map()
    sys.exit(0)