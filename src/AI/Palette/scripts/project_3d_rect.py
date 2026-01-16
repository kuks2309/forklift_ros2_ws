#!/usr/bin/env python3
"""
Project 3D rectangle to 2D image
- Uses camera intrinsic and extrinsic parameters for 3D -> 2D projection
- Code to understand the inverse process of solvePnP
"""

import cv2
import numpy as np


def create_camera_matrix(image_size, fov_deg=60):
    """
    Create camera intrinsic parameter matrix

    Args:
        image_size: (width, height)
        fov_deg: horizontal field of view (degrees)

    Returns:
        camera_matrix: 3x3 camera intrinsic parameter matrix
    """
    w, h = image_size
    # focal length = image_width / (2 * tan(fov/2))
    focal_length = w / (2 * np.tan(np.radians(fov_deg / 2)))

    camera_matrix = np.array([
        [focal_length, 0, w / 2],
        [0, focal_length, h / 2],
        [0, 0, 1]
    ], dtype=np.float32)

    return camera_matrix


def create_rect_3d(width, height):
    """
    Create 4 vertices of a rectangle on the XY plane (Z=0) in 3D space
    Center is at origin

    Args:
        width: rectangle width
        height: rectangle height

    Returns:
        4x3 numpy array: P1(top-left), P2(top-right), P3(bottom-right), P4(bottom-left)
    """
    half_w = width / 2
    half_h = height / 2

    # OpenCV camera coordinate system:
    # X: right (+)
    # Y: down (+)
    # Z: camera viewing direction (+)

    # Rectangle on Z=0 plane
    # P1(top-left): X-, Y-
    # P2(top-right): X+, Y-
    # P3(bottom-right): X+, Y+
    # P4(bottom-left): X-, Y+
    rect_3d = np.array([
        [-half_w, -half_h, 0],  # P1: top-left
        [half_w, -half_h, 0],   # P2: top-right
        [half_w, half_h, 0],    # P3: bottom-right
        [-half_w, half_h, 0]    # P4: bottom-left
    ], dtype=np.float32)

    return rect_3d


def euler_to_rotation_matrix(roll, pitch, yaw):
    """
    Convert Euler angles to rotation matrix

    User convention:
    - Roll: X-axis rotation (pallet left-right tilt)
    - Pitch: Z-axis rotation (pallet tilt within plane)
    - Yaw: horizontal direction (pallet facing left/right)
           Yaw+ = faces right, Yaw- = faces left

    Args:
        roll: X-axis rotation (radians)
        pitch: Z-axis rotation (radians) - plane tilt
        yaw: horizontal direction (radians) - left/right facing

    Returns:
        3x3 rotation matrix
    """
    # Convert user convention to actual axis rotations
    y_rot = -yaw    # Yaw (horizontal) = -Y-axis rotation
    z_rot = pitch   # Pitch (plane tilt) = Z-axis rotation

    # X-axis rotation (Roll)
    Rx = np.array([
        [1, 0, 0],
        [0, np.cos(roll), -np.sin(roll)],
        [0, np.sin(roll), np.cos(roll)]
    ])

    # Y-axis rotation (from Yaw)
    Ry = np.array([
        [np.cos(y_rot), 0, np.sin(y_rot)],
        [0, 1, 0],
        [-np.sin(y_rot), 0, np.cos(y_rot)]
    ])

    # Z-axis rotation (from Pitch)
    Rz = np.array([
        [np.cos(z_rot), -np.sin(z_rot), 0],
        [np.sin(z_rot), np.cos(z_rot), 0],
        [0, 0, 1]
    ])

    # Apply in ZYX order: R = Rz * Ry * Rx
    R = Rz @ Ry @ Rx
    return R.astype(np.float32)


def project_3d_to_2d(points_3d, rvec, tvec, camera_matrix, dist_coeffs=None):
    """
    Project 3D points to 2D image coordinates

    Args:
        points_3d: Nx3 3D coordinates
        rvec: rotation vector (3x1)
        tvec: translation vector (3x1)
        camera_matrix: camera intrinsic parameters
        dist_coeffs: distortion coefficients (None means 0)

    Returns:
        Nx2 2D image coordinates
    """
    if dist_coeffs is None:
        dist_coeffs = np.zeros(4)

    points_2d, _ = cv2.projectPoints(points_3d, rvec, tvec, camera_matrix, dist_coeffs)
    return points_2d.reshape(-1, 2)


def visualize_projection(image_size, rect_2d, title="Projection", roll=0, pitch=0, yaw=0, tx=0, ty=0, tz=0,
                         rvec=None, tvec=None, camera_matrix=None):
    """
    Visualize projected rectangle

    Args:
        image_size: (width, height)
        rect_2d: 4x2 2D coordinates
        title: window title
        roll, pitch, yaw: rotation angles (radians)
        tx, ty, tz: translation vector (mm)
        rvec, tvec, camera_matrix: for drawing 3D axes

    Returns:
        visualization image
    """
    w, h = image_size
    img = np.zeros((h, w, 3), dtype=np.uint8) + 50

    # Draw rectangle
    pts = rect_2d.astype(int)
    cv2.polylines(img, [pts], True, (0, 255, 0), 2)

    # Mark vertices
    point_colors = [(0, 0, 255), (0, 128, 255), (0, 255, 255), (255, 255, 0)]
    point_names = ['P1(TL)', 'P2(TR)', 'P3(BR)', 'P4(BL)']

    for i, (pt, color, name) in enumerate(zip(pts, point_colors, point_names)):
        cv2.circle(img, tuple(pt), 8, color, -1)
        cv2.putText(img, f'P{i+1}', (pt[0]+10, pt[1]-5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    # Draw 3D coordinate axes (at rectangle center)
    if rvec is not None and tvec is not None and camera_matrix is not None:
        axis_len = 200  # mm
        # 3D axis definition (pallet local coordinate system)
        # X: right (+) (P1->P2 direction)
        # Y: down (+) (P1->P4 direction)
        # Z: pallet front normal (+) (pointing toward camera when facing front)
        axis_3d = np.float32([
            [0, 0, 0],              # origin
            [axis_len, 0, 0],       # X-axis (red) - right
            [0, axis_len, 0],       # Y-axis (green) - down
            [0, 0, axis_len]        # Z-axis (blue) - pallet front normal (toward camera)
        ])

        # 3D -> 2D projection
        axis_2d, _ = cv2.projectPoints(axis_3d, rvec, tvec, camera_matrix, np.zeros(4))
        axis_2d = axis_2d.reshape(-1, 2).astype(int)

        origin = tuple(axis_2d[0])
        x_end = tuple(axis_2d[1])
        y_end = tuple(axis_2d[2])
        z_end = tuple(axis_2d[3])

        # Draw axes
        cv2.arrowedLine(img, origin, x_end, (0, 0, 255), 3, tipLength=0.2)  # X: red
        cv2.arrowedLine(img, origin, y_end, (0, 255, 0), 3, tipLength=0.2)  # Y: green
        cv2.arrowedLine(img, origin, z_end, (255, 0, 0), 3, tipLength=0.2)  # Z: blue

        cv2.putText(img, 'X', (x_end[0]+5, x_end[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        cv2.putText(img, 'Y', (y_end[0]+5, y_end[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(img, 'Z', (z_end[0]+5, z_end[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

    # Display coordinate info (top-left)
    for i, (pt, color) in enumerate(zip(pts, point_colors)):
        text = f'P{i+1}: [{pt[0]}, {pt[1]}]'
        cv2.putText(img, text, (10, 30 + i*25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    # Display Roll, Pitch, Yaw (top-right)
    pose_info = [
        (f"Roll: {np.degrees(roll):.1f} deg", (0, 0, 255)),    # red
        (f"Pitch: {np.degrees(pitch):.1f} deg", (0, 255, 0)),  # green
        (f"Yaw: {np.degrees(yaw):.1f} deg", (255, 0, 0)),      # blue
        (f"Z: {tz/1000:.2f} m", (255, 255, 255))               # white
    ]

    for i, (text, color) in enumerate(pose_info):
        cv2.putText(img, text, (w - 220, 30 + i*25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 3)
        cv2.putText(img, text, (w - 220, 30 + i*25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    cv2.putText(img, title, (10, h-20),
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    return img


def main():
    # Image size
    image_size = (1280, 720)

    # Camera intrinsic parameters
    camera_matrix = create_camera_matrix(image_size, fov_deg=60)
    print("=" * 60)
    print("Camera Intrinsic Parameters:")
    print(f"  focal length: {camera_matrix[0, 0]:.1f}")
    print(f"  principal point: ({camera_matrix[0, 2]:.1f}, {camera_matrix[1, 2]:.1f})")
    print(f"  camera_matrix:\n{camera_matrix}")

    # 3D rectangle (pallet size: 1100mm x 300mm)
    rect_width = 1100.0  # mm
    rect_height = 300.0  # mm
    rect_3d = create_rect_3d(rect_width, rect_height)
    print("\n" + "=" * 60)
    print(f"3D Rectangle (size: {rect_width} x {rect_height} mm):")
    for i, pt in enumerate(rect_3d):
        print(f"  P{i+1}: {pt}")

    # Test cases - diverse Roll, Pitch, Yaw combinations
    # New convention:
    # - Roll: X-axis rotation (pallet left-right tilt)
    # - Pitch: Z-axis rotation (pallet tilt within plane, clockwise/counter-clockwise)
    # - Yaw: horizontal direction (pallet facing left/right)
    #        Yaw+ = faces right (P2 lower in image), Yaw- = faces left (P1 lower)
    test_cases = [
        # Basic cases
        {'name': 'Front (no rotation)', 'roll': 0, 'pitch': 0, 'yaw': 0, 'tx': 0, 'ty': 0, 'tz': 3000},

        # Yaw only (horizontal direction - pallet faces left/right)
        {'name': 'Yaw +10 deg', 'roll': 0, 'pitch': 0, 'yaw': np.radians(10), 'tx': 0, 'ty': 0, 'tz': 3000},
        {'name': 'Yaw +20 deg', 'roll': 0, 'pitch': 0, 'yaw': np.radians(20), 'tx': 0, 'ty': 0, 'tz': 3000},
        {'name': 'Yaw +30 deg', 'roll': 0, 'pitch': 0, 'yaw': np.radians(30), 'tx': 0, 'ty': 0, 'tz': 3000},
        {'name': 'Yaw -15 deg', 'roll': 0, 'pitch': 0, 'yaw': np.radians(-15), 'tx': 0, 'ty': 0, 'tz': 3000},
        {'name': 'Yaw -25 deg', 'roll': 0, 'pitch': 0, 'yaw': np.radians(-25), 'tx': 0, 'ty': 0, 'tz': 3000},

        # Pitch only (pallet tilt within plane)
        {'name': 'Pitch +5 deg', 'roll': 0, 'pitch': np.radians(5), 'yaw': 0, 'tx': 0, 'ty': 0, 'tz': 3000},
        {'name': 'Pitch +15 deg', 'roll': 0, 'pitch': np.radians(15), 'yaw': 0, 'tx': 0, 'ty': 0, 'tz': 3000},
        {'name': 'Pitch -10 deg', 'roll': 0, 'pitch': np.radians(-10), 'yaw': 0, 'tx': 0, 'ty': 0, 'tz': 3000},
        {'name': 'Pitch -20 deg', 'roll': 0, 'pitch': np.radians(-20), 'yaw': 0, 'tx': 0, 'ty': 0, 'tz': 3000},

        # Roll only (X-axis rotation)
        {'name': 'Roll +5 deg', 'roll': np.radians(5), 'pitch': 0, 'yaw': 0, 'tx': 0, 'ty': 0, 'tz': 3000},
        {'name': 'Roll +10 deg', 'roll': np.radians(10), 'pitch': 0, 'yaw': 0, 'tx': 0, 'ty': 0, 'tz': 3000},
        {'name': 'Roll -8 deg', 'roll': np.radians(-8), 'pitch': 0, 'yaw': 0, 'tx': 0, 'ty': 0, 'tz': 3000},
        {'name': 'Roll -15 deg', 'roll': np.radians(-15), 'pitch': 0, 'yaw': 0, 'tx': 0, 'ty': 0, 'tz': 3000},

        # Combined rotations
        {'name': 'R=5, P=10, Y=15', 'roll': np.radians(5), 'pitch': np.radians(10), 'yaw': np.radians(15), 'tx': 0, 'ty': 0, 'tz': 3000},
        {'name': 'R=-5, P=15, Y=20', 'roll': np.radians(-5), 'pitch': np.radians(15), 'yaw': np.radians(20), 'tx': 0, 'ty': 0, 'tz': 3000},
        {'name': 'R=8, P=-10, Y=25', 'roll': np.radians(8), 'pitch': np.radians(-10), 'yaw': np.radians(25), 'tx': 0, 'ty': 0, 'tz': 3000},
        {'name': 'R=-10, P=-15, Y=-20', 'roll': np.radians(-10), 'pitch': np.radians(-15), 'yaw': np.radians(-20), 'tx': 0, 'ty': 0, 'tz': 3000},
        {'name': 'R=3, P=8, Y=-12', 'roll': np.radians(3), 'pitch': np.radians(8), 'yaw': np.radians(-12), 'tx': 0, 'ty': 0, 'tz': 3000},
        {'name': 'R=-7, P=5, Y=18', 'roll': np.radians(-7), 'pitch': np.radians(5), 'yaw': np.radians(18), 'tx': 0, 'ty': 0, 'tz': 3000},

        # Different distances
        {'name': 'Z=2m, Y=15', 'roll': 0, 'pitch': 0, 'yaw': np.radians(15), 'tx': 0, 'ty': 0, 'tz': 2000},
        {'name': 'Z=4m, Y=15', 'roll': 0, 'pitch': 0, 'yaw': np.radians(15), 'tx': 0, 'ty': 0, 'tz': 4000},
        {'name': 'Z=5m, R=5, P=10, Y=20', 'roll': np.radians(5), 'pitch': np.radians(10), 'yaw': np.radians(20), 'tx': 0, 'ty': 0, 'tz': 5000},

        # Translation + rotation
        {'name': 'X+300, Y=20', 'roll': 0, 'pitch': 0, 'yaw': np.radians(20), 'tx': 300, 'ty': 0, 'tz': 3000},
        {'name': 'X-400, R=5, P=10', 'roll': np.radians(5), 'pitch': np.radians(10), 'yaw': 0, 'tx': -400, 'ty': 0, 'tz': 3000},
    ]

    print("\n" + "=" * 60)
    print("Projection Test:")

    for i, case in enumerate(test_cases):
        print(f"\n[{i+1}] {case['name']}")

        # Create rotation matrix
        R = euler_to_rotation_matrix(case['roll'], case['pitch'], case['yaw'])
        rvec, _ = cv2.Rodrigues(R)

        # Translation vector
        tvec = np.array([[case['tx']], [case['ty']], [case['tz']]], dtype=np.float32)

        print(f"    Roll={np.degrees(case['roll']):.1f}, Pitch={np.degrees(case['pitch']):.1f}, Yaw={np.degrees(case['yaw']):.1f}")
        print(f"    Translation: ({case['tx']}, {case['ty']}, {case['tz']}) mm")

        # 3D -> 2D projection
        rect_2d = project_3d_to_2d(rect_3d, rvec, tvec, camera_matrix)

        print("    Projected 2D coordinates:")
        for j, pt in enumerate(rect_2d):
            print(f"      P{j+1}: [{pt[0]:.1f}, {pt[1]:.1f}]")

        # Visualization
        title = f"{case['name']}"
        img = visualize_projection(image_size, rect_2d, title,
                                   roll=case['roll'], pitch=case['pitch'], yaw=case['yaw'],
                                   tx=case['tx'], ty=case['ty'], tz=case['tz'],
                                   rvec=rvec, tvec=tvec, camera_matrix=camera_matrix)

        # Save
        filename = f'/home/amap/forklift_ros2_ws/src/AI/Palette/scripts/projection_test_{i+1}.png'
        cv2.imwrite(filename, img)
        print(f"    Saved: projection_test_{i+1}.png")

    print("\n" + "=" * 60)
    print("Done!")


if __name__ == '__main__':
    main()
