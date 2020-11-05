#! /usr/bin/python

import rospy
import time
import signal
import random

from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from turtlesim.srv import Spawn, Kill
from math import pow, atan2, sqrt, pi

turtle_name = 'chaser'

#def ctrl_c_handler():
#    rospy.wait_for_service('/kill') 
#    kill_func = rospy.ServiceProxy('/kill', Kill)
#    kill_func(turtle_name)


class TurtleChaser:
    def __init__(self):
        rospy.init_node(turtle_name)
        self.goal_pose_subscriber = rospy.Subscriber('/turtle1/pose', Pose, self.update_goal_pose)
        self.self_pose_subscriber = rospy.Subscriber('/chaser/pose', Pose, self.update_self_pose)
        self.velocity_publisher = rospy.Publisher('/chaser/cmd_vel', Twist, queue_size=10)

        self.goal_pose = Pose()
        self.distance_tolerance = 0.5
        self.pose = Pose()
        self.pose.x = random.random() * 10
        self.pose.y = random.random() * 10
        
        rospy.wait_for_service('/spawn')
        spawn_func = rospy.ServiceProxy('/spawn', Spawn)
        spawn_func(self.pose.x, self.pose.y, 0, turtle_name)
        
        self.rate = rospy.Rate(100)

    def euclidean_distance(self, goal_pose):
        return sqrt(pow((goal_pose.x - self.pose.x), 2) +
                    pow((goal_pose.y - self.pose.y), 2))

    def linear_vel(self, goal_pose, constant=1.5):
        return constant if self.euclidean_distance(goal_pose) > constant else self.euclidean_distance(goal_pose)

    def steering_angle(self, goal_pose):
        return atan2(goal_pose.y - self.pose.y, goal_pose.x - self.pose.x)

    def angular_vel(self, goal_pose, constant=4, private_space=1):
        return constant * (self.steering_angle(goal_pose) - self.pose.theta)

    def update_goal_pose(self, data):
        self.goal_pose = data
        self.goal_pose.x = round(self.goal_pose.x, 4)
        self.goal_pose.y = round(self.goal_pose.y, 4)

    def update_self_pose(self, data):
        self.pose = data
        self.pose.x = round(self.pose.x, 4)
        self.pose.y = round(self.pose.y, 4)

    def move2goal(self):
        vel_msg = Twist()
        
        while True:
            while self.euclidean_distance(self.goal_pose) >= self.distance_tolerance:
                vel_msg.linear.x = self.linear_vel(self.goal_pose)
                vel_msg.linear.y = 0
                vel_msg.linear.z = 0

                vel_msg.angular.x = 0
                vel_msg.angular.y = 0
                vel_msg.angular.z = self.angular_vel(self.goal_pose)

                self.velocity_publisher.publish(vel_msg)
                self.rate.sleep()

            vel_msg.linear.x = 0
            vel_msg.angular.z = 0
            self.velocity_publisher.publish(vel_msg)

            print("Ha-ha, gotcha! You have 5 second to run!")
            rospy.sleep(5)

try:
    chaser = TurtleChaser()
    chaser.move2goal()
except rospy.ROSInterruptException:
    pass

print("Kukukuku")

# signal.signal(signal.SIGINT, ctrl_c_handler)
