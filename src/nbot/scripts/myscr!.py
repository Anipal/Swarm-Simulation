#!/usr/bin/env python



#    inc !!!!!!!!!!!!!!!!!!
import sys
import rospy
import math
from gazebo_msgs.srv import *
from geometry_msgs.msg import Twist
from tf.transformations import euler_from_quaternion

def x_t(xb,yb,xr,yr,yaw):
	return (xb-xr)*math.cos(yaw) + (yb-yr)*math.sin(yaw)

def y_t(xb,yb,xr,yr,yaw):
	return (yb-yr)*math.cos(yaw) - (xb-xr)*math.sin(yaw)

def process(a,b,y):
    rospy.wait_for_service('gazebo/get_model_state')
    try:
        ob = rospy.ServiceProxy('gazebo/get_model_state', GetModelState)	
	rospy.init_node('getModelState_and_move', anonymous=True)
	pub = rospy.Publisher('/cmd_vel', Twist, queue_size = 10)
	rate = rospy.Rate(10000000)

	for tt in range(1000):
		o=Twist()
		o.linear.x=0.0
       		o.linear.y=0
       		o.linear.z=0
       		o.angular.x=0
       		o.angular.y=0
       		o.angular.z=0.2
  		pub.publish(o)
		rate.sleep()
	
	resp1 = ob(a, y)
	resp2 = ob(b, y)

	orientation_q = resp1.pose.orientation
       	orientation_list = [orientation_q.x, orientation_q.y, orientation_q.z, orientation_q.w]
       	(roll, pitch, init_yaw) = euler_from_quaternion (orientation_list)

	
	xt=x_t(resp2.pose.position.x,resp2.pose.position.y,resp1.pose.position.x,resp1.pose.position.y,init_yaw)
	yt=y_t(resp2.pose.position.x,resp2.pose.position.y,resp1.pose.position.x,resp1.pose.position.y,init_yaw)
	
	print init_yaw
	print resp1.pose.position.x
	print resp1.pose.position.y
	print "\n"

	print xt
	print yt

	

	while (math.fabs(xt)>0.01 or math.fabs(yt)>0.01):	
	        
		while (angle >0.1):	
			o=Twist()
			resp1 = ob(a, y)
			xt=x_t(resp2.pose.position.x,resp2.pose.position.y,resp1.pose.position.x,resp1.pose.position.y,init_yaw)
			yt=y_t(resp2.pose.position.x,resp2.pose.position.y,resp1.pose.position.x,resp1.pose.position.y,init_yaw)
			angle=math.atan(yt/xt)*(180/3.142)
			if (xt < 0 and yt < 0):
				angle+=180
			if (xt < 0 and yt > 0):
				angle=math.fabs(angle)+90
			if (xt > 0 and yt < 0):
				angle= 360 + angle
			o.angular.z=0.2*angle
			pub.publish(o)

		if math.fabs(xt) > 1 and math.fabs(yt) >1:
			o.linear.x=0.2*math.fabs(xt*yt)
		if math.fabs(xt) > 1 and math.fabs(yt) <1:
			o.linear.x=0.2*math.fabs(xt)
		if math.fabs(xt) < 1 and math.fabs(yt) >1:
			o.linear.x=0.2*math.fabs(yt)
		if math.fabs(xt) < 1 and math.fabs(yt) <1:
			o.linear.x=0.01
                         
    		
		
		print "xt- "+str(xt)
		print "yt- "+ str(yt)
		print "linear v- "+str(o.linear.x)
		print "angular z-  "+str(o.linear.z)		
		rate.sleep()
	
	o=Twist()
	pub.publish(o)
	
		

    except rospy.ServiceException, e:
        print "Service call failed: %s"%e



if __name__ == "__main__":
    a='mybot'
    b='cylinder'
    y='world'
    process(a,b,y)
    
