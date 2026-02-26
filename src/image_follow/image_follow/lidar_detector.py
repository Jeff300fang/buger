import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import PoseStamped
from message_filters import Subscriber, ApproximateTimeSynchronizer
from std_msgs.msg import Float32MultiArray
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy, HistoryPolicy
import math

lidar_qos = QoSProfile(
    reliability=ReliabilityPolicy.BEST_EFFORT,
    durability=DurabilityPolicy.VOLATILE,
    history=HistoryPolicy.KEEP_LAST,
    depth=5
)

class LidarDetector(Node):
    def __init__(self):
        super().__init__('lidar_detector')
        scan_subscription = Subscriber(self, LaserScan, '/scan', qos_profile=lidar_qos)
        angle_subscritipn = Subscriber(self, PoseStamped, '/object_angle')
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

    def synced_callback(self, scan: LaserScan, angle: PoseStamped):
        obj_angle = angle.pose.orientation.z
        if obj_angle < 0:
            obj_angle += 2 * math.pi    
        index = int((obj_angle - scan.angle_min) / scan.angle_increment)
        self.get_logger().info(f"{index}")
        window = scan.ranges[index - 3:index + 4]
        valid_ranges = [r for r in window if not math.isinf(r) and not math.isnan(r)]
        if not valid_ranges:
            return
        distance = min(valid_ranges)
        object_pose = Float32MultiArray()
        object_pose.data = [distance, angle.pose.orientation.z]
        self.obj_pub.publish(object_pose)

def main(args=None):
    rclpy.init(args=args)
    node = LidarDetector()
    rclpy.spin(node)
