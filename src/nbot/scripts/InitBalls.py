#!/usr/bin/env python
import rospy
import math
from gazebo_msgs.srv import *

def clean(b):
	#lb=len(b)
	i=0
	while i<len(b):
		if b[i][0]!='s':
			del b[i]
			i=i-1
		i+=1
	return b

def dist(a, b):
    return math.sqrt((a.x - b.x) * (a.x - b.x) + (a.y - b.y) * (a.y - b.y))

"""
def cluster(b):
	c = []
	t = []
	y = 'world'
	#lb = len(b)
	rospy.wait_for_service('gazebo/get_model_state')
   	ob = rospy.ServiceProxy('gazebo/get_model_state', GetModelState)
    	#bot = ob(a, y)
        #ball = ob(b[0], y)
	#s_d = dist(bot.pose.position, ball.pose.position)
	i = 0
	while i < len(b):
		balli = ob(b[i], y)
		t.append(b[i])
		j = i+1
		while j < len(b):
			ballj = ob(b[j], y)
			d = dist(balli.pose.position, ballj.pose.position)
			if d <= 1 :
				t.append(b[j])
				del b[j]
			j+=1	
		c.append(t)
		t = []
		i+=1
	return c
"""

def func(b):
	c = []
	i = 0
	while i<len(b):
		#print "b - " + str(b)
		#print "c - " + str(c)
		t = b[i]
		#print "\nt -" +str(t)
		del b[i]
		c.append([t] + group(t,b))
		#i+=1
	return c

def group(t, b):
	#print "2nd t - " + str(t)
	y = 'world'
	if not b:
		return []
	rospy.wait_for_service('gazebo/get_model_state')
   	ob = rospy.ServiceProxy('gazebo/get_model_state', GetModelState)
	ballt = ob(t, y)
	i = 0
	temp = []
	while i < len(b):
		balli = ob(b[i], y)
		d = dist(ballt.pose.position, balli.pose.position)
		#print " b[i] - " + str(b[i]) +"   ---- " + str(d) #+ "  ballt - "+ str(ballt.pose.position) + "  balli - "+ str(balli.pose.position) 
		if d <= 1.1:
			store = b[i]
			del b[i]
			#i-=1
			i=-1
			#print "calling group"
			temp+= [store] + group(store,b)
			#print "here t is "+ str(t)
		i+=1
	return temp
			


if __name__ == "__main__":
    rospy.wait_for_service('gazebo/get_world_properties')
    obj = rospy.ServiceProxy('gazebo/get_world_properties', GetWorldProperties)
    resp = obj()
    b = resp.model_names
    clean(b)
    print b
    c = func(b)
    print c
    rospy.set_param('/balls',c)
    rospy.set_param('/lock', '0')
