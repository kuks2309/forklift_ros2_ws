#!/usr/bin/env python3
"""
Gazebo Pose Estimation Test
- Subscribe to Gazebo camera image
- Detect green pallet (color segmentation)
- Estimate pose using solvePnP
- Compare with Gazebo ground truth
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from gazebo_msgs.srv import GetEntityState
from cv_bridge import CvBridge
import cv2
import numpy as np
import math
import sys
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
sys.path.append('/home/amap/forklift_ros2_ws/src/AI/Palette/scripts')
from pose_estimation import estimate_pose_pnp, draw_pose_axes


class GazeboPoseEstimator(Node):
    def __init__(self):
        super().__init__('gazebo_pose_estimator')

        self.bridge = CvBridge()
        self.latest_image = None
        self.result_image = None

        # Camera subscriber
        self.image_sub = self.create_subscription(
            Image, '/camera/image_raw', self.image_callback, 10)

        # Gazebo state service client
        self.get_state_client = self.create_client(
            GetEntityState, '/gazebo/get_entity_state')

        # Result image publisher
        self.result_pub = self.create_publisher(Image, '/pose_result', 10)

        # Pallet parameters
        self.pallet_width = 1200.0   # mm
        self.pallet_height = 150.0   # mm
        self.pallet_name = 'pallet_0deg'

        self.get_logger().info('Gazebo Pose Estimator Started')
        self.get_logger().info('Press Ctrl+C to exit')

    def image_callback(self, msg):
        self.latest_image = self.bridge.imgmsg_to_cv2(msg, 'bgr8')

    def get_ground_truth(self):
        """Get pallet pose from Gazebo"""
        if not self.get_state_client.service_is_ready():
            return None

        request = GetEntityState.Request()
        request.name = self.pallet_name
        request.reference_frame = 'world'

        future = self.get_state_client.call_async(request)
        rclpy.spin_until_future_complete(self, future, timeout_sec=0.1)

        if future.result() is None:
            return None

        state = future.result().state

        # Extract position
        x = state.pose.position.x
        y = state.pose.position.y
        z = state.pose.position.z

        # Extract quaternion and convert to yaw
        qx = state.pose.orientation.x
        qy = state.pose.orientation.y
        qz = state.pose.orientation.z
        qw = state.pose.orientation.w

        # Quaternion to Euler (yaw only)
        siny_cosp = 2 * (qw * qz + qx * qy)
        cosy_cosp = 1 - 2 * (qy * qy + qz * qz)
        yaw_world = math.atan2(siny_cosp, cosy_cosp)

        # Convert to camera-relative yaw
        # World yaw 90deg (1.5708) = pallet facing camera = 0deg relative
        yaw_relative = math.degrees(yaw_world) - 90.0

        return {
            'x': x,
            'y': y,
            'z': z,
            'yaw_world': math.degrees(yaw_world),
            'yaw': yaw_relative  # Camera-relative yaw
        }

    def detect_pallet_quad(self, image):
        """Detect blue pallet front face using color segmentation"""
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Blue color range
        lower_blue = np.array([100, 100, 100])
        upper_blue = np.array([130, 255, 255])
        mask = cv2.inRange(hsv, lower_blue, upper_blue)

        # Morphology
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            return None

        # Get largest contour
        largest = max(contours, key=cv2.contourArea)

        if cv2.contourArea(largest) < 1000:
            return None

        # Approximate to quadrilateral
        epsilon = 0.02 * cv2.arcLength(largest, True)
        approx = cv2.approxPolyDP(largest, epsilon, True)

        if len(approx) == 4:
            pts = approx.reshape(4, 2)
            return self.order_points(pts)

        # If not 4 points, use bounding rect
        rect = cv2.minAreaRect(largest)
        box = cv2.boxPoints(rect)
        return self.order_points(box.astype(int))

    def order_points(self, pts):
        """Order points: top-left, top-right, bottom-right, bottom-left"""
        pts = np.array(pts, dtype=np.float32)

        # Sort by y (top to bottom)
        sorted_by_y = pts[np.argsort(pts[:, 1])]
        top_pts = sorted_by_y[:2]
        bottom_pts = sorted_by_y[2:]

        # Sort top by x (left to right)
        top_pts = top_pts[np.argsort(top_pts[:, 0])]
        bottom_pts = bottom_pts[np.argsort(bottom_pts[:, 0])]

        # P1(top-left), P2(top-right), P3(bottom-right), P4(bottom-left)
        return np.array([top_pts[0], top_pts[1], bottom_pts[1], bottom_pts[0]], dtype=np.float32)

    def process_frame(self):
        if self.latest_image is None:
            return

        image = self.latest_image.copy()
        h, w = image.shape[:2]

        # Get ground truth from Gazebo
        gt = self.get_ground_truth()

        # Detect pallet
        quad = self.detect_pallet_quad(image)

        if quad is None:
            cv2.putText(image, "No pallet detected", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            self.result_image = image
            return

        # Draw detected quadrilateral
        pts = quad.astype(int)
        cv2.polylines(image, [pts], True, (0, 255, 255), 2)
        for i, pt in enumerate(pts):
            cv2.circle(image, tuple(pt), 5, (0, 255, 0), -1)
            cv2.putText(image, f"P{i+1}", (pt[0]+5, pt[1]-5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        # Estimate pose
        pose = estimate_pose_pnp(quad, (w, h), self.pallet_width, self.pallet_height)

        if pose['success']:
            # Draw axes
            image = draw_pose_axes(image, quad, pose, axis_len=200)

            est_yaw = pose['yaw']
            est_x = pose['tvec'][2] / 1000.0  # Z in camera = X in world (forward)
            est_y = -pose['tvec'][0] / 1000.0  # X in camera = -Y in world (left/right)

            # Display results
            y_pos = 30

            # Estimated pose
            cv2.putText(image, f"[Estimated]", (10, y_pos),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            y_pos += 30
            cv2.putText(image, f"  Yaw: {est_yaw:.1f} deg", (10, y_pos),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            y_pos += 25
            cv2.putText(image, f"  Dist: {est_x:.2f} m", (10, y_pos),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            y_pos += 40

            # Ground truth
            if gt:
                cv2.putText(image, f"[Ground Truth]", (10, y_pos),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                y_pos += 30
                cv2.putText(image, f"  Yaw: {gt['yaw']:.1f} deg", (10, y_pos),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                y_pos += 25
                cv2.putText(image, f"  X: {gt['x']:.2f} m", (10, y_pos),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                y_pos += 40

                # Error
                yaw_err = est_yaw - gt['yaw']
                dist_err = est_x - gt['x']
                cv2.putText(image, f"[Error]", (10, y_pos),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                y_pos += 30
                cv2.putText(image, f"  Yaw: {yaw_err:+.1f} deg", (10, y_pos),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                y_pos += 25
                cv2.putText(image, f"  Dist: {dist_err:+.2f} m", (10, y_pos),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                # Console output
                print(f"Est Yaw: {est_yaw:+6.1f}° | GT Yaw: {gt['yaw']:+6.1f}° | Err: {yaw_err:+5.1f}°", end='\r')

        self.result_image = image

        # Publish to ROS topic
        result_msg = self.bridge.cv2_to_imgmsg(image, 'bgr8')
        self.result_pub.publish(result_msg)


def main():
    rclpy.init()
    node = GazeboPoseEstimator()

    # Matplotlib setup
    plt.ion()
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.axis('off')
    im = None

    print("Waiting for camera image...")

    try:
        while rclpy.ok():
            # Process ROS callbacks
            rclpy.spin_once(node, timeout_sec=0.05)

            # Process frame
            node.process_frame()

            # Update display
            if node.result_image is not None:
                rgb_image = cv2.cvtColor(node.result_image, cv2.COLOR_BGR2RGB)
                if im is None:
                    im = ax.imshow(rgb_image)
                    plt.tight_layout()
                else:
                    im.set_data(rgb_image)

                fig.canvas.draw_idle()
                fig.canvas.flush_events()

            plt.pause(0.01)

    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        plt.close('all')
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
