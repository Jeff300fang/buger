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
        self.last_msg_time = self.get_clock().now()

        self.create_timer(0.05, self.timer_callback)
        self.current_position = Float32MultiArray()
        self.current_position.data = [0.0, 0.0]

    def position_callback(self, msg):
        self.current_position = msg.data
        self.last_msg_time = self.get_clock().now()


    def timer_callback(self):
        dt = (self.last_msg_time - self.get_clock().now()).nanoseconds * 1e-9
        if dt > 0.1:
            self.current_position = Float32MultiArray()
            self.current_position.data = [0.0, 0.0]
        twist = Twist()
        twist.angular.z = KP_ANGLE * self.current_position.data[1]
        twist.linear.x = KP_DISTANCE * self.current_position.data[0]
        self.vel_pub.publish(twist)

def main(args=None):
    rclpy.init(args=args)
    node = Follower()
    rclpy.spin(node)