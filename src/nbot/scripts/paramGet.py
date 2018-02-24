#!/usr/bin/env python

import sys
import rospy
import math
if __name__ == "__main__":
	try:
		A = rospy.get_param('/obs')
		print A
	except:
		print "non"
