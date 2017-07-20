#!/usr/bin/env python


import time 
from cv2 import startWindowThread, imencode, imread
from StringIO import StringIO

from json import dumps,loads
from math import pi
from util import Key, CognitiveFaceException
import person_group as PG
import person as PERSON
import face as CF

# big hack to stop annoying warnings
try:
    from requests.packages.urllib3 import disable_warnings
    disable_warnings()
except:
    pass
#

class CognitiveFace():

    def __init__(self):
        
        self._api_key = 'be062e88698e4777ac6196623d7230dd'
        self._topic_timeout = 10 
        #startWindowThread()
        Key.set(self._api_key)

        self._person_group_id = 'robocup_test' 
                                                
        self._init_person_group(self._person_group_id,False)
        
    def _init_person_group(self, gid, delete_first=False):
        person_group = None
        try:
            person_group = PG.get(gid)
            print('getting person group "%s"'
                          % person_group)
        except CognitiveFaceException as e:
            print('person group "%s" doesn\'t exist, needs creating.'
                          ' Exception: %s'
                          % (gid, e))
        try:
            # if we are expected to reinitialise this, and the group
            # already existed, delete it first
            if person_group is not None and delete_first:
                print('delete existing person group "%s"'
                              ' before re-creating it.' % gid)
                PG.delete(gid)
                person_group = None
            # if the group does not exist, we gotto create it
            if person_group is None:
                print('creating new person group "%s".'
                              % gid)
                PG.create(gid, user_data=dumps({
                    'created_by': 'Pepper'
                }))
            print('active person group is now "%s".' % gid)
            self._person_group_id = gid
        except CognitiveFaceException as e:
            print('Operation failed for person group "%s".'
                          ' Exception: %s'
                          % (gid, e))

    def _find_person_by_name(self, name):
        persons = PERSON.lists(self._person_group_id)
        for p in persons:
            if p['name'] == name:
                return p
        return None

    def _init_person(self, name, delete_first=False):
        gid = self._person_group_id
        person = self._find_person_by_name(name)
        try:
            # if we are expected to reinitialise this, and the group
            # already existed, delete it first
            if person is not None and delete_first:
                print('delete existing person "%s"'
                              ' before re-creating it.' % name)
                PERSON.delete(gid, person['personId'])
                person = None
            # if the group does not exist, we gotto create it
            if person is None:
                print('creating new person "%s".'
                              % name)
                PERSON.create(gid, name, user_data=dumps({
                    'created_by': 'Pepper'
                }))
                person = self._find_person_by_name(name)
        except CognitiveFaceException as e:
            print('Operation failed for person "%s".'
                          ' Exception: %s'
                          % (gid, e))
        return person

    def _convert_jpg(self, image_msg):

        retval, buf = imencode('.jpg', image_msg)
        return buf.tostring()

    def add_face_srv(self, req):
        img_msg = self._get_image(req)
        faces = self._detect(img_msg, False)
        target_face = None        
        
        # biggest face
        max_area = 0.0
        biggest_face = None
        for f in faces.faces:
            area = float(f.faceRectangle.width * f.faceRectangle.height)
            if area > max_area:
                max_area = area
                biggest_face = f
        biggest_face.person = req.person
        
        target_face=biggest_face


        self._add_face_target(img_msg,target_face)

        return target_face
            


    def _person_group_select(self, req):
        self._init_person_group(req.id, req.delete_group)
        return []

    def _get_image(self, req):
        if req.filename is not '':
            img = imread(req.filename)

        return img

    def detect_srv(self, image, identify=False):
        faces = []
        try:
            data = CF.detect(
                StringIO(self._convert_jpg(image)),
                
                landmarks=False,
                attributes='age,gender,headPose,smile,glasses,hair,facialhair,accessories')
            identities = {}
            if identify:
                print('trying to identify persons')
                ids = [f['faceId'] for f in data]
                print 'ids=',ids
                try:
                    identified = CF.identify(ids[0:10], self._person_group_id)
                    for i in identified:
                        if len(i['candidates']) > 0:
                            pid = i['candidates'][0]['personId']
                            person = PERSON.get(self._person_group_id, pid)
                            identities[i['faceId']] = person['name']
                    print('identified %d persons in this image: %s'
                                  % (len(identities), str(identities)))
                except CognitiveFaceException as e:
                    print('identification did not work: %s' %
                                  str(e))
            for f in data:
                
                faceId = f['faceId']
                if faceId in identities:
                    person = identities[faceId]
                else:
                    person = ''
                    
#                pose={'x':f['faceRectangle']['left'],'y':f['faceRectangle']['top'],'w':f['faceRectangle']['width'],'h':f['faceRectangle']['height']}

                gender = f['faceAttributes']['gender']
                age = f['faceAttributes']['age']
                smile = f['faceAttributes']['smile']
                
                facialhair = f['faceAttributes']['FacialHair']
                glasses= f['Glasses']
                accessories= f['Accessories']
                hair = f['faceAttributes']['Hair']
                
                # color with max confidence
                index_def_hair=None
                max_conf=0.0
                for i in range(len(hair['HairColor'])):
                    if hair['HairColor'][i]['Confidence']>max_conf:                        
                        max_conf=hair['HairColor'][i]['Confidence']
                        index_def_hair=i
                        
                def_hair=hair['HairColor'][i]
                
     
#                face.rpy.x = (f['faceAttributes']['headPose']['roll'] /
#                              180.0 * math.pi)
#                face.rpy.y = (f['faceAttributes']['headPose']['pitch'] /
#                              180.0 * math.pi)
#                face.rpy.z = (f['faceAttributes']['headPose']['yaw'] /
#                              180.0 * math.pi)
#     
                face_info='gender': gender, 'smile':smile, 'hair':def_hair,'facialhair':facialhair, 'glasses':glasses, 'accessories':accessories}                
                face={ 'name':person, 'faceinfo':face_info}                         
                
                faces.append(face)
            
        except Exception as e:
            print('failed to detect via the MS Face API: %s' %
                          str(e))
        return faces

#cfa = CognitiveFace()

