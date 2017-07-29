#!/usr/bin/env python
import rospy
import qi
import argparse
import os
import json
import sys
from std_msgs.msg import String
from sensor_msgs.msg import Image, CameraInfo
from ms_face_api.srv import Detect, DetectRequest

class Qi2RosStringTopic(object):

    def _on_event(self, data):
        self._pub.publish(data)

    def __init__(self, memory_service, memory_key, latch=False, prefix='/qi/'):
        self.memory_service = memory_service
        try:
            self._pub = rospy.Publisher(prefix + memory_key,
                                        String, latch=latch,
                                        queue_size=1)
            self._sub = self.memory_service.subscriber(memory_key)
            self._sub.signal.connect(self._on_event)
            if latch:
                hist = self.memory_service.getEventHistory(memory_key)
                if len(hist) > 0:
                    try:
                        self._on_event(hist[-1][0])
                    except Exception:
                        pass
            rospy.loginfo('subscribed to %s on Qi' % memory_key)
        except Exception as e:
            rospy.logwarn("Cannot set up for %s: %s" % (memory_key, str(e)))


class Ros2QiStringTopic():

    def _on_event(self, data):
        self.memory_service.raiseEvent(self.memory_key, data.data)
        self.memory_service.insertData(self.memory_key, data.data)

    def __init__(self, memory_service, topic_name, prefix='/ros/'):
        self.memory_service = memory_service
        self.memory_key = prefix + topic_name
        try:
            self.memory_service.declareEvent(self.memory_key)
            self._sub = rospy.Subscriber(topic_name,
                                         String,
                                         self._on_event,
                                         queue_size=1)
            rospy.loginfo('subscribed to %s on ROS' % topic_name)
        except Exception as e:
            rospy.logwarn("Cannot set up for %s: %s" % (topic_name, str(e)))


class SPQReLROSBridge():

    def __init__(self, session):
        self.session = session
        self.memory_service = session.service("ALMemory")
        self.veply_q2r = Qi2RosStringTopic(
            self.memory_service, 'Veply', latch=True
        )
        self.person_ana_r2q = Ros2QiStringTopic(
            self.memory_service, '/person_analysis_outcome'
        )
        self.trigger_tobi = Qi2RosStringTopic(
            self.memory_service, 'trigger_person_analysis'
        )

        self.ip = os.getenv("PEPPER_IP", default="127.0.0.1")
        self.website_pub = rospy.Publisher('/qi/webview/url',
                                           String, queue_size=1)

        self.trigger_tobi_sub = rospy.Subscriber(
            '/qi/trigger_person_analysis',
            String, self._trigger_tobi)
        self.trigger_tobi_sub = rospy.Subscriber(
            '/detect_people/fusion',
            String, self._stop_tobi)

        self._image_pub = rospy.Publisher(
            '/spqrel/camera/image_raw',
            Image, queue_size=1)
        self._depth_pub = rospy.Publisher(
            '/spqrel/depth/image_raw',
            Image, queue_size=1)
        self._depth_info_pub = rospy.Publisher(
            '/spqrel/depth/camera_info',
            CameraInfo, queue_size=1)

        self._image_counter = 0
        self._depth_counter = 0
        self._THROTTLE = 5

    def _image_cb(self, img):
        self._image_counter += 1
        if self._image_counter > self._THROTTLE:
            rospy.logdebug('publish image')
            self._image_pub.publish(img)
            self._image_counter = 0

    def _depth_cb(self, img):
        self._depth_counter += 1
        if self._depth_counter > self._THROTTLE:
            rospy.logdebug('publish depth')
            self._depth_pub.publish(img)
            self._depth_counter = 0

    def _depth_info_cb(self, info):
        rospy.logdebug('publish depth info')
        self._depth_info_pub.publish(info)

    def _stop_tobi(self, _):
        rospy.loginfo('stop tobi')
        if self._cam_sub:
            self._cam_sub.unregister()
            self._cam_sub = None
        if self._depth_sub:
            self._depth_sub.unregister()
            self._depth_sub = None
        if self._depth_info_sub:
            self._depth_info_sub.unregister()
            self._depth_info_sub = None

    def _trigger_tobi(self, data):
        rospy.loginfo('trigger tobi')
        self._cam_sub = rospy.Subscriber(
            'spqrel_pepper/camera/front/camera/image_raw',
            Image, self._image_cb
        )
        self._depth_sub = rospy.Subscriber(
            'spqrel_pepper/camera/depth/camera/image_raw',
            Image, self._depth_cb
        )
        self._depth_info_sub = rospy.Subscriber(
            '/spqrel_pepper/camera/depth/camera/camera_info',
            CameraInfo, self._depth_info_cb
        )

        # d = rospy.ServiceProxy('/ms_face_api/detect', Detect)
        # r = DetectRequest()
        # r.topic = 'spqrel_pepper/camera/front/camera/image_raw'
        # res = d.call(r)
        # res_faces = []
        # for f in
        # res_dict = {
        #     'age': res.age,
        #     'gender': res.gender,
        #     'smile': res.smile
        # }
        # print json.dumps(res)

    def display_webview(self, uri=None):
        if uri is None:
            uri = 'http://%s:1036/' % self.ip
        self.website_pub.publish(uri)


if __name__ == "__main__":

    pip = os.environ['PEPPER_IP']
    pport = 9559

    try:
        connection_url = "tcp://" + pip + ":" + str(pport)
        print "Connecting to ", connection_url
        app = qi.Application(["SPQReLUI", "--qi-url=" + connection_url])
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" +
               pip + "\" on port " + str(pport) + ".\n"
               "Please check your arguments. Run with -h option for help.")
        sys.exit(1)

    app.start()

    rospy.init_node('spqrel_ros_bridge')

    ip = os.getenv("PEPPER_IP", default="127.0.0.1")
    rospy.set_param('PEPPER_IP', ip)

    bridge = SPQReLROSBridge(app.session)
    bridge.display_webview()
    rospy.spin()
