import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CompressedImage
from cv_bridge import CvBridge
# from geometry_msgs.msg import Point
from std_msgs.msg import Float32
import cv2
import numpy as np

class Detector(Node):
    def __init__(self):
        super().__init__('detector')

        self.create_subscription(
            Image,
            '/image_raw',
            self.image_callback,
            1
        )
        self.angle_pub = self.create_publisher(
            Float32,
            '/object_angle',
            10
        )
        self.debug_camera_pub  = self.create_publisher(
            Image,
            '/camera/debug',
            10
        )

        self.bridge = CvBridge()
    
    def is_red_hsv(self, mean_hsv, s_min=80, v_min=60):
        h, s, v = mean_hsv
        if s < s_min or v < v_min:
            return False
        return (h <= 5) or (h >= 175)

    def mean_hsv_in_patch(self, hsv_img, cx, cy, r=6):
        h, w = hsv_img.shape[:2]
        x0 = max(cx - r, 0)
        x1 = min(cx + r + 1, w)
        y0 = max(cy - r, 0)
        y1 = min(cy + r + 1, h)
        patch = hsv_img[y0:y1, x0:x1]
        if patch.size == 0:
            return None
        return patch.reshape(-1, 3).mean(axis=0)

    def image_callback(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

        # resize once and use consistently
        resized = cv2.resize(frame, (80, 60))

        # grayscale for Hough, for circle detection
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        # denoise
        # gray = cv2.GaussianBlur(gray, (9, 9), 1.5)

        # gather hsv
        hsv = cv2.cvtColor(resized, cv2.COLOR_BGR2HSV)

        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT,dp=1.2,
            minDist=150, param1=180, param2=25, 
            minRadius=4,maxRadius=2000)
        red_circles = []
        if circles is not None:
            circles = np.round(circles[0]).astype(int)

            for (x, y, r) in circles:
                mean_hsv = self.mean_hsv_in_patch(hsv, x, y, r=3)
                if mean_hsv is None:
                    continue

                h_, s_, v_ = mean_hsv
                is_red = self.is_red_hsv(mean_hsv)
                if not is_red:
                    continue
                # # draw circle
                color = (0, 255, 0) if is_red else (0, 0, 255)
                cv2.circle(resized, (x, y), r, color, 2)
                cv2.circle(resized, (x, y), 4, (255, 255, 255), -1)

                # text position (to the right of circle)
                text_x = x + r + 10
                text_y = y

                cv2.putText(
                    resized,
                    f"H:{int(h_)} S:{int(s_)} V:{int(v_)}",
                    (text_x, text_y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    color,
                    2,
                    cv2.LINE_AA
                )
                red_circles.append([x,y,r])
            angle = Float32()
            if len(red_circles) == 0:
                angle.data = 0.0
            else:
                circles_sorted = sorted(red_circles, key=lambda c: c[2], reverse=True)
                main_circle = circles_sorted[0]
                angle.data = float(40 - main_circle[0]) * 0.542797397
            self.angle_pub.publish(angle)
            compressed_msg = self.bridge.cv2_to_imgmsg(resized, encoding='bgr8')
            self.debug_camera_pub.publish(compressed_msg)

def main(args=None):
    rclpy.init(args=args)
    node = Detector()
    rclpy.spin(node)
