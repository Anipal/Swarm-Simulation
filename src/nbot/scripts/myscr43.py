#!/usr/bin/env python

import sys
import rospy
import math
from gazebo_msgs.srv import *
from geometry_msgs.msg import Twist
from tf.transformations import euler_from_quaternion

def x_t(xb, yb, xr, yr, yaw):
    return (xb - xr) * math.cos(yaw) + (yb - yr) * math.sin(yaw)


def y_t(xb, yb, xr, yr, yaw):
    return (yb - yr) * math.cos(yaw) - (xb - xr) * math.sin(yaw)


def dist(a, b):
    return math.sqrt((a.x - b.x) * (a.x - b.x) + (a.y - b.y) * (a.y - b.y))

"""
def order(a, b):
    rospy.wait_for_service('gazebo/get_model_state')
    ob = rospy.ServiceProxy('gazebo/get_model_state', GetModelState)
    bot = ob(a, y)

    ball = ob(b[0], y)
    s_d = dist(bot.pose.position, ball.pose.position)
    pos = 0
    j =  1
    while j < len(b):
        ball = ob(b[j], y)
        t = dist(bot.pose.position, ball.pose.position)
        if t < s_d:
            s_d = t
            pos = j
        j += 1
    var = b[pos]
    del b[pos]
    rospy.set_param('/balls',b)
    return pos,var
"""

def order2(a, b):
    rospy.wait_for_service('gazebo/get_model_state')
    ob = rospy.ServiceProxy('gazebo/get_model_state', GetModelState)
    bot = ob(a, y)
	
    s_d = 1000
    for l1 in range(len(b)):
	for l2 in range(len(b[l1])):
		ball = ob(b[l1][l2], y)
		d = dist(bot.pose.position, ball.pose.position)
		print str(b[l1][l2]) + "  -  " + str(d)
		if d < s_d:
			s_d = d
			pos = l1

    var = b[pos]
    del b[pos]
    rospy.set_param('/balls',b)
    return pos,var
	
def sort(var, position):
	y = 'world'
	ob = rospy.ServiceProxy('gazebo/get_model_state', GetModelState)
	for l1 in range(len(var)):   	
		resp = ob(var[l1], y)
		l2 = l1 + 1
		s = var[l1]
		pos = l1
		while l2 < len(var):
			resp2 = ob (var[l2], y)
			if dist(position, resp2.pose.position) < dist(position,resp.pose.position):
				s = var[l2]
				pos = l2
			l2+=1
		t = var[l1]
		var[l1] = var[pos]
		var[pos] = t 
	print "sorted"
	print var






def process(a, b, y):

    rospy.wait_for_service('gazebo/get_model_state')
    try:
        ob = rospy.ServiceProxy('gazebo/get_model_state', GetModelState)
        pub = rospy.Publisher(a+'/cmd_vel', Twist, queue_size=10)
        rate = rospy.Rate(1000)

        resp1 = ob(a, y)
        resp2 = ob(b, y)

        orientation_q = resp1.pose.orientation
        orientation_list = [orientation_q.x, orientation_q.y, orientation_q.z, orientation_q.w]
        (roll, pitch, init_yaw) = euler_from_quaternion(orientation_list)

        xt = x_t(resp2.pose.position.x, resp2.pose.position.y, resp1.pose.position.x, resp1.pose.position.y, init_yaw)
        yt = y_t(resp2.pose.position.x, resp2.pose.position.y, resp1.pose.position.x, resp1.pose.position.y, init_yaw)

        while (math.fabs(xt) > 0.1 or math.fabs(yt) > 0.1):

            o = Twist()
	    to=rospy.get_time()
	    t = rospy.get_param(a+'/obs')
	    #print t
	    if math.fabs(t-to)<0.5 :
			#print t-to
			pub.publish(o)
			continue

            angle = math.atan(yt / xt) * (180 / 3.142)
            A = 0
            if (xt < 0 and yt < 0):
                A = angle + 180
            elif (xt < 0 and yt > 0):
                A = math.fabs(angle) + 90
            elif (xt > 0 and yt < 0):
                A = 360 + angle
            elif (xt > 0 and yt > 0):
                A = angle
            elif xt < 0 and yt == 0:
                A = 180
            elif xt == 0 and yt > 0:
                A = 90
            elif xt == 0 and yt < 0:
                A = 270

            if A > 0 and A <= 180:
                A = A
            elif A > 180 and A <= 360:
                A = A - 360
	    
	    o.angular.z = 2.0 * A * (3.142 / 180)
		

	    while A>10 or A<-10:
		#print "tuning"+str(A)
		o.angular.z = 2.0 * A * (3.142 / 180)
		pub.publish(o)
		resp1 = ob(a, y)
            	orientation_q = resp1.pose.orientation
            	orientation_list = [orientation_q.x, orientation_q.y, orientation_q.z, orientation_q.w]
            	(roll, pitch, init_yaw) = euler_from_quaternion(orientation_list)
            	xt = x_t(resp2.pose.position.x, resp2.pose.position.y, resp1.pose.position.x, resp1.pose.position.y,init_yaw)
        	yt = y_t(resp2.pose.position.x, resp2.pose.position.y, resp1.pose.position.x, resp1.pose.position.y,init_yaw)
		angle = math.atan(yt / xt) * (180 / 3.142)
           	A = 0
           	if (xt < 0 and yt < 0):
           	     A = angle + 180
           	elif (xt < 0 and yt > 0):
           	     A = math.fabs(angle) + 90
           	elif (xt > 0 and yt < 0):
           	     A = 360 + angle
            	elif (xt > 0 and yt > 0):
                	A = angle
            	elif xt < 0 and yt == 0:
            	    A = 180
            	elif xt == 0 and yt > 0:
            	    A = 90
            	elif xt == 0 and yt < 0:
            	    A = 270
	
            	if A > 0 and A <= 180:
            	    A = A
            	elif A > 180 and A <= 360:
            	    A = A - 360
	
            if xt > 0:
            	o.linear.x = 0.5 * math.sqrt(xt * xt + yt * yt)
	    	if math.sqrt(xt**2 +yt**2) < 0.5 :
			o.linear.x = 0.1
	    
            #else:
            #    o.linear.x = 0.0

           
            pub.publish(o)
            resp1 = ob(a, y)
            orientation_q = resp1.pose.orientation
            orientation_list = [orientation_q.x, orientation_q.y, orientation_q.z, orientation_q.w]
            (roll, pitch, init_yaw) = euler_from_quaternion(orientation_list)
            xt = x_t(resp2.pose.position.x, resp2.pose.position.y, resp1.pose.position.x, resp1.pose.position.y,
                     init_yaw)
            yt = y_t(resp2.pose.position.x, resp2.pose.position.y, resp1.pose.position.x, resp1.pose.position.y,
                     init_yaw)
            rate.sleep()
	
	rospy.wait_for_service('gazebo/delete_model')
        obj = rospy.ServiceProxy('gazebo/delete_model', DeleteModel)
        obj(b)
        #rospy.wait_for_service('gazebo/delete_model')


    except rospy.ServiceException, e:
        print "Service call failed: %s" % e

def home(a,y,X,Y):
    rospy.wait_for_service('gazebo/get_model_state')
    try:
        ob = rospy.ServiceProxy('gazebo/get_model_state', GetModelState)
        pub = rospy.Publisher(a+'/cmd_vel', Twist, queue_size=10)
        rate = rospy.Rate(1000)

        resp1 = ob(a, y)

        orientation_q = resp1.pose.orientation
        orientation_list = [orientation_q.x, orientation_q.y, orientation_q.z, orientation_q.w]
        (roll, pitch, init_yaw) = euler_from_quaternion(orientation_list)

        xt = x_t(X, Y, resp1.pose.position.x, resp1.pose.position.y, init_yaw)
        yt = y_t(X, Y, resp1.pose.position.x, resp1.pose.position.y, init_yaw)
	
	f=0
        while (math.fabs(xt) > 0.7 or math.fabs(yt) > 0.7):

            o = Twist()
	    to= rospy.get_time()
	    t = rospy.get_param(a+'/obs')
	    #print t
	    if math.fabs(t-to)<0.5 :
			#print t-to
			pub.publish(o)
			continue	

            angle = math.atan(yt / xt) * (180 / 3.142)
            A = 0
            if (xt < 0 and yt < 0):
                A = angle + 180
            elif (xt < 0 and yt > 0):
                A = math.fabs(angle) + 90
            elif (xt > 0 and yt < 0):
                A = 360 + angle
            elif (xt > 0 and yt > 0):
                A = angle
            elif xt < 0 and yt == 0:
                A = 180
            elif xt == 0 and yt > 0:
                A = 90
            elif xt == 0 and yt < 0:
                A = 270

            if A > 0 and A <= 180:
                A = A
            elif A > 180 and A <= 360:
                A = A - 360
	    
	    o.angular.z = 2.0 * A * (3.142 / 180)
		

	    while A>15 or A<-15:
		#print "tuning"+str(A)
		o.angular.z = 2.0 * A * (3.142 / 180)
		pub.publish(o)
		resp1 = ob(a, y)
            	orientation_q = resp1.pose.orientation
            	orientation_list = [orientation_q.x, orientation_q.y, orientation_q.z, orientation_q.w]
            	(roll, pitch, init_yaw) = euler_from_quaternion(orientation_list)
            	xt = x_t(X,Y, resp1.pose.position.x, resp1.pose.position.y,init_yaw)
        	yt = y_t(X,Y, resp1.pose.position.x, resp1.pose.position.y,init_yaw)
		angle = math.atan(yt / xt) * (180 / 3.142)
           	A = 0
           	if (xt < 0 and yt < 0):
           	     A = angle + 180
           	elif (xt < 0 and yt > 0):
           	     A = math.fabs(angle) + 90
           	elif (xt > 0 and yt < 0):
           	     A = 360 + angle
            	elif (xt > 0 and yt > 0):
                	A = angle
            	elif xt < 0 and yt == 0:
            	    A = 180
            	elif xt == 0 and yt > 0:
            	    A = 90
            	elif xt == 0 and yt < 0:
            	    A = 270
	
            	if A > 0 and A <= 180:
            	    A = A
            	elif A > 180 and A <= 360:
            	    A = A - 360
	
            if xt > 0:
            	o.linear.x = 0.5* math.sqrt(xt * xt + yt * yt)
	    	
           # else:
            #    o.linear.x = 0.0

           
            pub.publish(o)
            resp1 = ob(a, y)
            orientation_q = resp1.pose.orientation
            orientation_list = [orientation_q.x, orientation_q.y, orientation_q.z, orientation_q.w]
            (roll, pitch, init_yaw) = euler_from_quaternion(orientation_list)
            xt = x_t(X,Y, resp1.pose.position.x, resp1.pose.position.y,
                     init_yaw)
            yt = y_t(X,Y,resp1.pose.position.x, resp1.pose.position.y,
                     init_yaw)
            rate.sleep()
	
    except rospy.ServiceException, e:
        print "Service call failed: %s" % e




if __name__ == "__main__":
    a = sys.argv[1]
    y = 'world'
    rospy.init_node('Control', anonymous=True)
    ob = rospy.ServiceProxy('gazebo/get_model_state', GetModelState)
    resp1 = ob(a, y)
    b = ['a']
    try:
    	while b:
				while rospy.get_param('/lock') == '1':
					print "waiting"
				rospy.set_param('/lock','1')
				b = rospy.get_param('/balls')	
        			pos,var = order2(a, b)
				rospy.set_param('/lock', '0')
				sort(var,resp1.pose.position)
				for l1 in var:
					process(a,l1,y)
    except:
	rospy.set_param('/lock', '0')
	print "Done"
    finally :
	    home(a,y,resp1.pose.position.x,resp1.pose.position.y)
	    pub = rospy.Publisher(a+'/cmd_vel', Twist, queue_size=10)
	    o = Twist()
	    o.angular.z =0
	    o.linear.z =0
	    pub.publish(o)







