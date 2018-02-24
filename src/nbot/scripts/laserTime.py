#!/usr/bin/env python

import sys
import rospy
import math
from gazebo_msgs.srv import *
from sensor_msgs.msg import LaserScan



def scan_handler(msg):
	for i in range(len(msg.ranges)):
		if (msg.ranges[i]<2):
			#print str(msg.ranges[i]) + " -> " + str(i)
			seconds = rospy.get_time()
			rospy.set_param('obs', seconds)
			break

print "start"
rospy.init_node('laser', anonymous=True)
#seconds = rospy.get_time()
rospy.set_param('obs', 100)
scan_sub = rospy.Subscriber('laser/scan', LaserScan, scan_handler)
rospy.spin()



