#!/usr/bin/env python3
"""
Keyboard teleop for pallet position control in Gazebo
Arrow keys: move pallet (X/Y)
Q/E: rotate yaw
W/S: move forward/backward (Z for testing)
R: reset to initial position
ESC: quit
"""

import rclpy
from rclpy.node import Node
from gazebo_msgs.srv import SetEntityState
from gazebo_msgs.msg import EntityState
from geometry_msgs.msg import Pose, Point, Quaternion
import sys
import termios
import tty
import math
import select


def euler_to_quaternion(roll, pitch, yaw):
    """Convert Euler angles to quaternion"""
    cy = math.cos(yaw * 0.5)
    sy = math.sin(yaw * 0.5)
    cp = math.cos(pitch * 0.5)
    sp = math.sin(pitch * 0.5)
    cr = math.cos(roll * 0.5)
    sr = math.sin(roll * 0.5)

    q = Quaternion()
    q.w = cr * cp * cy + sr * sp * sy
    q.x = sr * cp * cy - cr * sp * sy
    q.y = cr * sp * cy + sr * cp * sy
    q.z = cr * cp * sy - sr * sp * cy
    return q


class PalletTeleop(Node):
    def __init__(self):
        super().__init__('pallet_teleop')

        # Service client for setting model state
        self.set_state_client = self.create_client(
            SetEntityState, '/gazebo/set_entity_state')

        while not self.set_state_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for /gazebo/set_entity_state service...')

        # Initial pallet pose
        self.pallet_name = 'pallet_0deg'
        self.x = 3.0
        self.y = 0.0
        self.z = 0.0
        self.yaw = math.pi / 2  # 90 degrees (1200mm side facing camera)

        # Movement increments
        self.linear_step = 0.1   # 10cm
        self.angular_step = 0.05  # ~3 degrees

        self.get_logger().info('Pallet Teleop Ready!')
        self.print_instructions()

    def print_instructions(self):
        msg = """
------------------------------------------
  Pallet Teleop Control (Gazebo ground truth)
------------------------------------------
  Arrow Keys:
    ↑ : Move forward (+X, closer)
    ↓ : Move backward (-X, farther)
    ← : Move left (+Y)
    → : Move right (-Y)

  Rotation:
    Q : Rotate CCW (Yaw+)
    E : Rotate CW (Yaw-)

  Other:
    R : Reset to initial position
    P : Print current pose
    ESC/Ctrl+C : Quit
------------------------------------------
"""
        print(msg)

    def print_current_pose(self):
        yaw_deg = math.degrees(self.yaw) - 90  # Subtract 90 to show relative to camera
        print(f"\n[Ground Truth] X={self.x:.2f}m, Y={self.y:.2f}m, Yaw={yaw_deg:.1f}°")

    def set_pallet_pose(self):
        """Send pose update to Gazebo"""
        request = SetEntityState.Request()
        request.state = EntityState()
        request.state.name = self.pallet_name
        request.state.pose = Pose()
        request.state.pose.position = Point(x=self.x, y=self.y, z=self.z)
        request.state.pose.orientation = euler_to_quaternion(0, 0, self.yaw)
        request.state.reference_frame = 'world'

        future = self.set_state_client.call_async(request)
        rclpy.spin_until_future_complete(self, future, timeout_sec=0.5)

        if future.result() is not None:
            yaw_deg = math.degrees(self.yaw) - 90
            print(f"Pose: X={self.x:.2f}, Y={self.y:.2f}, Yaw={yaw_deg:.1f}°", end='\r')
        else:
            self.get_logger().error('Failed to set pallet pose')

    def reset_pose(self):
        """Reset to initial position"""
        self.x = 3.0
        self.y = 0.0
        self.yaw = math.pi / 2
        self.set_pallet_pose()
        print("\n[Reset] Pallet returned to initial position")

    def process_key(self, key):
        """Process keyboard input"""
        if key == '\x1b[A':  # Up arrow - move closer
            self.x -= self.linear_step
        elif key == '\x1b[B':  # Down arrow - move farther
            self.x += self.linear_step
        elif key == '\x1b[D':  # Left arrow
            self.y += self.linear_step
        elif key == '\x1b[C':  # Right arrow
            self.y -= self.linear_step
        elif key.lower() == 'q':  # Rotate CCW
            self.yaw += self.angular_step
        elif key.lower() == 'e':  # Rotate CW
            self.yaw -= self.angular_step
        elif key.lower() == 'r':  # Reset
            self.reset_pose()
            return True
        elif key.lower() == 'p':  # Print pose
            self.print_current_pose()
            return True
        elif key == '\x1b' or key == '\x03':  # ESC or Ctrl+C
            return False
        else:
            return True

        self.set_pallet_pose()
        return True


def get_key(timeout=0.1):
    """Get keyboard input"""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        rlist, _, _ = select.select([sys.stdin], [], [], timeout)
        if rlist:
            key = sys.stdin.read(1)
            if key == '\x1b':  # Escape sequence
                key += sys.stdin.read(2)
            return key
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return None


def main():
    rclpy.init()
    node = PalletTeleop()

    try:
        while rclpy.ok():
            key = get_key()
            if key is not None:
                if not node.process_key(key):
                    break
    except KeyboardInterrupt:
        pass
    finally:
        print("\nShutting down...")
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
