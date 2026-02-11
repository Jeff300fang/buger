import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point
from geometry_msgs.msg import Twist

class Follower(Node):
    def __init__(self):
        super().__init__('follower')
        self.point_sub = self.create_subscription(
            Point,
            '/object_point',
            self.point_callback,
            10
        )
        self.vel_pub = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )
    
    def point_callback(self, msg):
        twist = Twist()
        if msg.y > 0:
            twist.angular.z = 0.4
        elif msg.y < 0:
            twist.angular.z = -0.4 
        else:
            twist.angular.z = 0.0
        self.vel_pub.publish(twist)

def main(args=None):
    rclpy.init(args=args)
    node = Follower()
    rclpy.spin(node)