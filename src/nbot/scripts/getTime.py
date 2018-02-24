#!/usr/bin/env python

import rospy

to=0
while True:
	t = rospy.get_param('obs')
	if t !=to :
		print t
	to=t
