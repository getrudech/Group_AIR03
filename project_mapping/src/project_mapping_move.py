#!/usr/bin/env python
import rospy
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
import random

class AutoMapper:
    def __init__(self):
        rospy.init_node('auto_mapper')
        self.pub = rospy.Publisher('/cmd_vel', Twist, queue_size=1)
        self.front = 10.0
        self.left = 10.0
        self.right = 10.0
        self.got_data = False
        rospy.Subscriber('/scan', LaserScan, self.cb)

    def cb(self, msg):
        r = msg.ranges
        n = len(r)
        rmin = msg.range_min
        rmax = msg.range_max

        def safe_min(start, end):
            s = [r[i] for i in range(start, min(end, n)) if rmin < r[i] < rmax]
            return min(s) if s else 10.0

        # FRONT is around index 180 (not 0!)
        self.front = safe_min(160, 200)
        # LEFT is around index 270
        self.left = safe_min(250, 290)
        # RIGHT is around index 90
        self.right = safe_min(70, 110)

        self.got_data = True

    def run(self):
        rospy.sleep(2)
        while not self.got_data and not rospy.is_shutdown():
            rospy.sleep(0.5)
        rospy.loginfo("Auto mapper started!")

        twist = Twist()
        rate = rospy.Rate(10)

        while not rospy.is_shutdown():
            rospy.loginfo("F:%.2f L:%.2f R:%.2f", self.front, self.left, self.right)

            if self.front < 0.8:
                # WALL AHEAD - stop, back up, turn
                rospy.loginfo("WALL DETECTED! Turning.")
                # stop
                twist.linear.x = 0.0
                twist.angular.z = 0.0
                self.pub.publish(twist)
                rospy.sleep(0.3)

                # back up
                twist.linear.x = -0.2
                twist.angular.z = 0.0
                for i in range(15):
                    self.pub.publish(twist)
                    rate.sleep()

                # turn 90 degrees (away from closest side)
                turn_dir = 0.6 if self.left > self.right else -0.6
                twist.linear.x = 0.0
                twist.angular.z = turn_dir
                for i in range(26):
                    self.pub.publish(twist)
                    rate.sleep()

                # stop
                twist.linear.x = 0.0
                twist.angular.z = 0.0
                self.pub.publish(twist)
                rospy.sleep(0.3)

            else:
                # clear path - go forward at 0.6
                twist.linear.x = 0.6
                twist.angular.z = random.uniform(-0.1, 0.1)
                self.pub.publish(twist)

            rate.sleep()

if __name__ == '__main__':
    am = AutoMapper()
    am.run()
