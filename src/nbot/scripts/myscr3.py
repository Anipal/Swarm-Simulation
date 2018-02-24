#!/usr/bin/env python

import sys
import rospy
import math
from gazebo_msgs.srv import *
from geometry_msgs.msg import Twist
from tf.transformations import euler_from_quaternion

def clean(b):
	lb=len(b)
	i=0
	while i<len(b):
		if b[i][0]!='s':
			del b[i]
			i=i-1
		i+=1
	return b

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
    return pos


def process(a, b, y):

    rospy.wait_for_service('gazebo/get_model_state')
    try:
        ob = rospy.ServiceProxy('gazebo/get_model_state', GetModelState)
        rospy.init_node('getModelState_and_move', anonymous=True)
        pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
        rate = rospy.Rate(10000000)

        resp1 = ob(a, y)
        resp2 = ob(b, y)

        orientation_q = resp1.pose.orientation
        orientation_list = [orientation_q.x, orientation_q.y, orientation_q.z, orientation_q.w]
        (roll, pitch, init_yaw) = euler_from_quaternion(orientation_list)

        xt = x_t(resp2.pose.position.x, resp2.pose.position.y, resp1.pose.position.x, resp1.pose.position.y, init_yaw)
        yt = y_t(resp2.pose.position.x, resp2.pose.position.y, resp1.pose.position.x, resp1.pose.position.y, init_yaw)

        while (math.fabs(xt) > 0.09 or math.fabs(yt) > 0.09):

            o = Twist()
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
            #print "xt- " + str(xt)
            #print "yt- " + str(yt)
            #print "angle- " + str(A)
            #print "linear v- " + str(o.linear.x)
            #print "angular z-  " + str(o.linear.z)
            rate.sleep()

        obj = rospy.ServiceProxy('gazebo/delete_model', DeleteModel)
        obj(b)
        o = Twist()
        pub.publish(o)
        rospy.wait_for_service('gazebo/delete_model')


    except rospy.ServiceException, e:
        print "Service call failed: %s" % e


if __name__ == "__main__":
    a = 'mybot'
    rospy.wait_for_service('gazebo/get_world_properties')
    obj = rospy.ServiceProxy('gazebo/get_world_properties', GetWorldProperties)
    resp = obj()
    b = resp.model_names
    b = clean(b)
    y = 'world'
    
    #sys.exit(1)
    for i in range(len(b)):
	print i
        pos = order(a, b)
	print pos
        process(a,b[pos],y)
        del b[pos]
        #print b

