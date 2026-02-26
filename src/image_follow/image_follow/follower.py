import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray
from geometry_msgs.msg import Twist

KP_ANGLE = 1.0
KD_ANGLE = 0.1

KP_DISTANCE = 1.0
KD_DISTANCE = 0.1

class Follower(Node):
    def __init__(self):
        super().__init__('follower')
        self.point_sub = self.create_subscription(
            Float32MultiArray,
            '/object_detect',
            self.position_callback,
            10
        )
        self.vel_pub = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )
        self.previous_angle = 0.0
        self.previous_distrance = 0.0

        self.create_timer()

    def position_callback(self, msg):
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