#!/usr/bin/env python
import rospy
import qi
import argparse
import os
import sys
from std_msgs.msg import String


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
            self.memory_service, 'person_analysis_outcome'
        )
        self.trigger_tobi = Qi2RosStringTopic(
            self.memory_service, 'trigger_person_analysis'
        )

        self.ip = os.getenv("PEPPER_IP", default="127.0.0.1")
        self.website_pub = rospy.Publisher('/qi/webview/url',
                                           String, queue_size=1)

    def display_webview(self, uri=None):
        if uri is None:
            uri = 'http://%s:1036/' % self.ip
        self.website_pub.publish(uri)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--pip", type=str,
        default=os.environ['PEPPER_IP'],
        help="Robot IP address.  On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--pport", type=int, default=9559,
                        help="Naoqi port number")
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
               "Please check your arguments. Run with -h option for help.")
        sys.exit(1)

    app.start()

    rospy.init_node('spqrel_ros_bridge')

    ip = os.getenv("PEPPER_IP", default="127.0.0.1")
    rospy.set_param('PEPPER_IP', ip)

    bridge = SPQReLROSBridge(app.session)
    rospy.spin()
