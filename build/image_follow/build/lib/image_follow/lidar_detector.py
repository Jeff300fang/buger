import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Float32
from message_filters import Subscriber, ApproximateTimeSynchronizer
from std_msgs.msg import Float32MultiArray

class LidarDetector(Node):
    def __init__(self):
        super().__init__('lidar_detector')
        scan_subscription = Subscriber(self, LaserScan, '/scan')
        angle_subscritipn = Subscriber(self, Float32, '/object_angle')
        self.sync = ApproximateTimeSynchronizer(
            [scan_subscription, angle_subscritipn],
            10,
            0.05,
        )
        self.sync.registerCallback(self.synced_callback)
        self.obj_pub = self.create_publisher(
            Float32MultiArray,
            '/object_detect',
            1,
        )

    def synced_callback(self, scan: LaserScan, angle: Float32):
        index = int((angle.data - scan.angle_min) / scan.angle_increment)
        distance = min(scan.ranges[index - 3:index + 4])
        object_pose = Float32MultiArray()
        object_pose.data = [distance, angle.data]
        self.obj_pub.publish(object_pose)

def main(args=None):
    rclpy.init(args=args)
    node = LidarDetector()
    rclpy.spin(node)
