import os
import yaml
from json import dumps, loads
import argparse
import xml.etree.ElementTree as ET
from pprint import pformat

import coloredlogs
import logging

logger = logging.Logger(__file__)
coloredlogs.install(level='INFO', logger=logger)


class SemanticResolver:

    TESTSTR = """
[{'object': {'lu4r_name': ['theme'], 'necessary': 1},
                'spotted': [{'category': 'cutlery',
                             'index': 12,
                             'text': 'fork'},
                            {'index': 41,
                             'text': ' it ',
                             'toguess': 'object'}]},
               {'location': {'lu4r_name': ['source'], 'necessary': 0},
                'spotted': [{'index': 26,
                             'room': 'bedroom',
                             'text': 'chair'},
                            {'index': 26,
                             'room': 'dining room',
                             'text': 'chair'},
                            {'index': 52,
                             'room': 'living room',
                             'text': 'bookcase'}]}]
    """

    def __init__(self):
        self.categories = {}
        self.objects = {}
        self.rooms = {}
        self.entities = {}
        self.locations = {}

        self.load_locations()
        self.load_objects()
        self.augment_entities()

    def load_locations(self):
        config_folder = os.path.join(os.environ["SPQREL_TOOLS"], "config")
        config_file = config_folder + '/Locations.xml'
        xml_root = ET.parse(
            config_file).getroot()

        for locroom in xml_root.findall("room"):
            room = {
                'waypoint': locroom.get("waypoint"),
                'locations': [],
                'type': 'room',
            }
            self.entities[locroom.get("name")] = room
            self.rooms[locroom.get("name")] = room
            for loc in locroom.findall("location"):
                locname = loc.get("name")
                locwp = loc.get("waypoint")
                location = {
                    "name": locname,
                    "waypoint": locwp,
                    'type': 'location',
                }
                self.entities[locname] = location
                self.locations[locname] = location
                room['locations'].append(location)
        return self.entities

    def load_objects(self):
        config_folder = os.path.join(os.environ["SPQREL_TOOLS"], "config")
        config_file = config_folder + '/Objects.xml'
        xml_root = ET.parse(
            config_file).getroot()

        for loc_category in xml_root.findall("category"):
            category = {
                'location': loc_category.get("defaultLocation"),
                'room': loc_category.get("room"),
                'objects': [],
                'type': 'category'
            }
            self.categories[loc_category.get("name")] = category
            self.entities[loc_category.get("name")] = category

            for loc_object in loc_category.findall("object"):
                objectname = loc_object.get("name")
                obj = {
                    "name": objectname,
                    "category": loc_category.get("name"),
                    'room': loc_category.get("room"),
                    'location': loc_category.get("defaultLocation"),
                    'type': 'object',
                }
                self.objects[objectname] = obj
                self.entities[objectname] = obj
                category['objects'].append(obj)
        return self.objects

    def augment_entities(self):
        for (k, v) in self.entities.items():
            if 'waypoint' not in v:
                logger.debug('no waypoint in %s' % k)
                if 'location' in v:
                    v['waypoint'] = self.locations[v['location']]['waypoint']
                else:
                    logger.warning('still no wp in %s' % k)

    def resolve(self, semantic):
        try:
            return self.entities[semantic]
        except Exception:
            return None

    def resolve_wp(self, semantic):
        try:
            return self.entities[semantic]['waypoint']
        except Exception:
            return None

    def parse_requires(self, d):
        # [{'index': 0,
        #   'requires': [{'object': {'lu4r_name': ['theme'], 'necessary': 1},
        #                 'spotted': [{'category': 'cutlery',
        #                              'index': 12,
        #                              'text': 'fork'},
        #                             {'index': 41,
        #                              'text': ' it ',
        #                              'toguess': 'object'}]},
        #                {'location': {'lu4r_name': ['source'], 'necessary': 0},
        #                 'spotted': [{'index': 26,
        #                              'room': 'bedroom',
        #                              'text': 'chair'},
        #                             {'index': 26,
        #                              'room': 'dining room',
        #                              'text': 'chair'},
        #                             {'index': 52,
        #                              'room': 'living room',
        #                              'text': 'bookcase'}]}],
        #   'task': 'taking',
        #   'verb': 'pick up'},
        #  {'index': 36,
        #   'requires': [{'object': {'lu4r_name': [], 'necessary': 1},
        #                 'spotted': [{'category': 'cutlery',
        #                              'index': 12,
        #                              'text': 'fork'},
        #                             {'index': 41,
        #                              'text': ' it ',
        #                              'toguess': 'object'}]},
        #                {'location': {'lu4r_name': [], 'necessary': 1},
        #                 'spotted': [{'index': 26,
        #                              'room': 'bedroom',
        #                              'text': 'chair'},
        #                             {'index': 26,
        #                              'room': 'dining room',
        #                              'text': 'chair'},
        #                             {'index': 52,
        #                              'room': 'living room',
        #                              'text': 'bookcase'}]}],
        #   'task': 'placing',
        #   'verb': 'place'}]
        obj = None
        location = None
        text = None
        room = None
        name = None
        try:
            for r in d:
                #logging.info('\nR: ' + pformat(r))
                if 'spotted' in r:
                    try:
                        for s in r['spotted']:
                            if 'text' in s:
                                text = s['text']
                            if 'room' in s:
                                room = s['room']
                            if 'name' in s:
                                name = s['name']
                            break
                        if 'object' in r:
                            obj = text
                        if 'location' in r:
                            location = text
                    except Exception as e:
                        logger.warning('exception %s' % e)
        except Exception as e:
            logger.warning('exception %s' % e)
        res = {
            'room': room,
            'location': location,
            'obj': obj,
            'text': text,
            'name': name,
            'wp': None
        }

        if obj is not None and res['wp'] is None:
            res['wp'] = self.resolve_wp(obj)
        elif location is not None and res['wp'] is None:
            res['wp'] = self.resolve_wp(location)
        elif room is not None and res['wp'] is None:
            res['wp'] = self.resolve_wp(room)
        logger.info(pformat(res))
        return res

    def load(self):
        config_folder = os.path.join(os.environ["SPQREL_TOOLS"], "config")
        files_to_load = [config_folder + '/Locations.xml']
        for config_file in files_to_load:
            [config_name, ext] = config_file.split(".")
            if ext == "xml":
                logger.info("Loading XML config for %s" % config_file)
                try:
                    xml_root = ET.parse(
                        config_file).getroot()
                    logger.info("Info: %s" % pformat(xml_root))
                    info = self.decode_xml(xml_root, "locations")
                    logger.info("Info: %s" % pformat(info))
                except Exception, e:
                    logger.info("Error parsing xml file %s: %s" % (
                        config_file, e)
                    )
                    print e
                    exit(1)
            elif ext == "yaml":
                logger.info("Loading config for %s" % config_file)
                try:
                    yf = open(os.path.join(config_folder, config_file))
                    info = self.decode_yaml(yf, config_name)
                    logger.info("Info: %s" % str(info))
                except Exception, e:
                    logger.info("Error parsing yaml file %s: %s" % (
                        config_file, e)
                    )
                    print e
                    exit(1)


def main():

    with open("/tmp/test.yaml", 'r') as stream:
        test=yaml.load(stream)
    #logger.info(pformat(test[0]['requires']))
    sr = SemanticResolver()
    sr.augment_entities()

    sr.parse_requires(yaml.load(SemanticResolver.TESTSTR))
    sr.parse_requires(test[1]['requires'])
    #logger.info(pformat(sr.entities))

    #print sr.resolve_wp('tableware')


if __name__ == '__main__':
    main()
