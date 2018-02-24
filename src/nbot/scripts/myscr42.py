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


def process(a, b, y):

    rospy.wait_for_service('gazebo/get_model_state')
    try:
        ob = rospy.ServiceProxy('gazebo/get_model_state', GetModelState)
        pub = rospy.Publisher(a+'/cmd_vel', Twist, queue_size=10)
        rate = rospy.Rate(1000000)

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
	    if math.fabs(t-to)<1 :
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

            if xt > 0:
                o.linear.x = 0.1 * math.sqrt(xt * xt + yt * yt)
            else:
                o.linear.x = 0.0

            o.angular.z = 2 * A * (3.142 / 180)
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
	print "deleted"
    except rospy.ServiceException, e:
        print "Service call failed: %s" % e


if __name__ == "__main__":
    a = sys.argv[1]
    y = 'world'
    rospy.init_node('Control', anonymous=True)
    b = rospy.get_param('/balls')
    print b
    try:
    	while b:
    			for i in range(len(b)):
        			pos,var = order(a, b)
				print var
				process(a,var,y)
				b = rospy.get_param('/balls')
				print b
    except:
	print "Done"
    pub = rospy.Publisher(a+'/cmd_vel', Twist, queue_size=10)
    o = Twist()
    o.angular.z =0
    o.linear.z =0
    pub.publish(o)


