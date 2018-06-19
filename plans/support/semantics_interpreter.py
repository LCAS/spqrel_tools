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
    sr = SemanticResolver()
    sr.augment_entities()
    logger.info(pformat(sr.entities))

    print sr.resolve_wp('tableware')


if __name__ == '__main__':
    main()
