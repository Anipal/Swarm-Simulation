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
        rospy.init_node('getModelState_and_move', anonymous=True)
        pub = rospy.Publisher(a+'/cmd_vel', Twist, queue_size=10)
        rate = rospy.Rate(1000000)

        resp1 = ob(a, y)
        resp2 = ob(b, y)

        orientation_q = resp1.pose.orientation
        orientation_list = [orientation_q.x, orientation_q.y, orientation_q.z, orientation_q.w]
        (roll, pitch, init_yaw) = euler_from_quaternion(orientation_list)

        xt = x_t(resp2.pose.position.x, resp2.pose.position.y, resp1.pose.position.x, resp1.pose.position.y, init_yaw)
        yt = y_t(resp2.pose.position.x, resp2.pose.position.y, resp1.pose.position.x, resp1.pose.position.y, init_yaw)
	#xo=0
	#yo=0
	#f = 0
	
        while (math.fabs(xt) > 0.1 or math.fabs(yt) > 0.1):

            o = Twist()
	    to=rospy.get_time()
	    
	    t = rospy.get_param('a1/obs')
	    #print t
	    if math.fabs(t-to)<0.5 :
		if math.sqrt(xt*xt+yt*yt)>0.8:
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
		

	    """ Select final settings for 42 as well """
            if xt > 0:
                o.linear.x = 0.1 * math.sqrt(xt * xt + yt * yt)
            else:
               o.linear.x = 0.05
	    
            if o.linear.x > 0.8:
		 o.linear.x = 0.8
	    elif o.linear.x < 0.05:
		 o.linear.x= 0.05

	    #print "Linear "+str(o.linear.x)

            o.angular.z = 2 * A * (3.142 / 180)

	    if o.angular.z >0.7:
		o.linear.x = 0

            pub.publish(o)
	    

            resp1 = ob(a, y)
            orientation_q = resp1.pose.orientation
            orientation_list = [orientation_q.x, orientation_q.y, orientation_q.z, orientation_q.w]
            (roll, pitch, init_yaw) = euler_from_quaternion(orientation_list)
            xt = x_t(resp2.pose.position.x, resp2.pose.position.y, resp1.pose.position.x, resp1.pose.position.y,
                     init_yaw)
            yt = y_t(resp2.pose.position.x, resp2.pose.position.y, resp1.pose.position.x, resp1.pose.position.y,
                     init_yaw)
	   # print xo-resp1.pose.position.x
	   # print yo-resp1.pose.position.y
	    """
	    if math.fabs(xo - resp1.pose.position.x) < 0.0001   and math.fabs(yo - resp1.pose.position.y) < 0.0001:
		f+=1
		print f
		if f==100:
			for q in range(10000):
				o.linear.x=-0.1
				o.angular.z=0
				pub.publish(o)
				print "pub"
				f = 0
	    
            xo = resp1.pose.position.x
	    yo = resp1.pose.position.y
	    """
            rate.sleep()

        obj = rospy.ServiceProxy('gazebo/delete_model', DeleteModel)
        obj(b)
        #rospy.wait_for_service('gazebo/delete_model') ######################


    except rospy.ServiceException, e:
        print "Service call failed: %s" % e


if __name__ == "__main__":
    a = sys.argv[1]
    y = 'world'
    b = rospy.get_param('/balls')
    while b:
    		for i in range(len(b)):
        		pos,var = order(a, b)
			print var
			process(a,var,y)
			b = rospy.get_param('/balls')

    pub = rospy.Publisher(a+'/cmd_vel', Twist, queue_size=10)
    o = Twist()
    o.angular.z =0
    o.linear.z =0
    pub.publish(o)

