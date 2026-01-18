#!/usr/bin/env python3
"""
Bird's Eye View Calibration Module
- Checkerboard camera calibration (intrinsic parameters)
- Camera axis parallel to ground plane (pitch=0, roll=0)
- Bird's eye view transformation
"""

import cv2
import numpy as np
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt


def calibrate_camera_checkerboard(image_paths, board_size=(9, 6), square_size=25.0):
    """
    Calibrate camera using checkerboard images

    Args:
        image_paths: list of checkerboard image paths
        board_size: (cols, rows) inner corners of checkerboard
        square_size: size of each square in mm

    Returns:
        dict with camera_matrix, dist_coeffs, image_size, calibration_error
    """
    # Prepare object points (0,0,0), (1,0,0), (2,0,0) ...
    objp = np.zeros((board_size[0] * board_size[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:board_size[0], 0:board_size[1]].T.reshape(-1, 2)
    objp *= square_size

    obj_points = []  # 3D points in world
    img_points = []  # 2D points in image
    image_size = None

    print(f"Processing {len(image_paths)} images...")
    print(f"Checkerboard: {board_size[0]}x{board_size[1]}, square size: {square_size}mm")

    for img_path in image_paths:
        img = cv2.imread(str(img_path))
        if img is None:
            print(f"  Skip: {img_path} (cannot read)")
            continue

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        image_size = gray.shape[::-1]

        # Find checkerboard corners
        ret, corners = cv2.findChessboardCorners(gray, board_size, None)

        if ret:
            # Refine corners
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
            corners = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)

            obj_points.append(objp)
            img_points.append(corners)
            print(f"  OK: {Path(img_path).name}")
        else:
            print(f"  Skip: {Path(img_path).name} (corners not found)")

    if len(obj_points) < 3:
        print("Error: Need at least 3 valid checkerboard images")
        return None

    print(f"\nCalibrating with {len(obj_points)} images...")

    # Calibrate camera
    ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(
        obj_points, img_points, image_size, None, None
    )

    # Calculate reprojection error
    total_error = 0
    for i in range(len(obj_points)):
        img_points_proj, _ = cv2.projectPoints(
            obj_points[i], rvecs[i], tvecs[i], camera_matrix, dist_coeffs
        )
        error = cv2.norm(img_points[i], img_points_proj, cv2.NORM_L2) / len(img_points_proj)
        total_error += error
    mean_error = total_error / len(obj_points)

    print(f"Calibration done!")
    print(f"  Reprojection error: {mean_error:.4f} pixels")
    print(f"  Focal length: fx={camera_matrix[0,0]:.1f}, fy={camera_matrix[1,1]:.1f}")
    print(f"  Principal point: cx={camera_matrix[0,2]:.1f}, cy={camera_matrix[1,2]:.1f}")

    return {
        'camera_matrix': camera_matrix,
        'dist_coeffs': dist_coeffs,
        'image_size': image_size,
        'calibration_error': mean_error,
        'num_images': len(obj_points)
    }


def save_calibration(calib_result, output_path):
    """Save calibration result to JSON file"""
    data = {
        'camera_matrix': calib_result['camera_matrix'].tolist(),
        'dist_coeffs': calib_result['dist_coeffs'].tolist(),
        'image_size': list(calib_result['image_size']),
        'calibration_error': calib_result['calibration_error'],
        'num_images': calib_result['num_images']
    }
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Saved calibration to: {output_path}")


def load_calibration(calib_path):
    """Load calibration from JSON file"""
    with open(calib_path, 'r') as f:
        data = json.load(f)
    return {
        'camera_matrix': np.array(data['camera_matrix'], dtype=np.float32),
        'dist_coeffs': np.array(data['dist_coeffs'], dtype=np.float32),
        'image_size': tuple(data['image_size']),
        'calibration_error': data['calibration_error'],
        'num_images': data['num_images']
    }


def compute_bird_eye_transform(camera_matrix, camera_height, image_size,
                                output_scale=10.0, output_size=None):
    """
    Compute bird's eye view transformation matrix

    Assumes camera axis parallel to ground (pitch=0, roll=0)

    Args:
        camera_matrix: 3x3 camera intrinsic matrix
        camera_height: camera height from ground (mm)
        image_size: (width, height) of input image
        output_scale: mm per pixel in output image
        output_size: (width, height) of output image, None for auto

    Returns:
        dict with transform_matrix, inverse_matrix, output_size, params
    """
    fx = camera_matrix[0, 0]
    fy = camera_matrix[1, 1]
    cx = camera_matrix[0, 2]
    cy = camera_matrix[1, 2]
    w, h = image_size

    # For camera parallel to ground:
    # Image Y corresponds to ground Z (depth)
    # Image X corresponds to ground X (lateral)

    # Ground plane in camera coordinates: Y = -camera_height (below camera)
    # For each image pixel (u, v), the 3D ray is:
    #   X = (u - cx) / fx * Z
    #   Y = (v - cy) / fy * Z
    # When Y = -camera_height:
    #   Z = -camera_height * fy / (v - cy)

    if output_size is None:
        # Auto size based on field of view
        output_size = (int(w * 1.5), int(h * 2))

    out_w, out_h = output_size
    out_cx, out_cy = out_w // 2, out_h

    # Build homography: image -> bird's eye view
    # Source points (image corners + center bottom)
    src_pts = np.float32([
        [0, h],           # bottom-left
        [w, h],           # bottom-right
        [w, h // 2],      # middle-right
        [0, h // 2]       # middle-left
    ])

    # Compute ground coordinates for source points
    dst_pts = []
    for u, v in src_pts:
        if v <= cy:
            # Above horizon, skip
            v = cy + 1
        z = -camera_height * fy / (v - cy)
        x = (u - cx) / fx * z
        # Convert to output pixels
        out_x = out_cx + x / output_scale
        out_y = out_cy - z / output_scale  # Y increases upward in bird's eye
        dst_pts.append([out_x, out_y])

    dst_pts = np.float32(dst_pts)

    # Compute homography
    H, _ = cv2.findHomography(src_pts, dst_pts)
    H_inv = np.linalg.inv(H)

    return {
        'transform_matrix': H,
        'inverse_matrix': H_inv,
        'output_size': output_size,
        'output_scale': output_scale,
        'camera_height': camera_height,
        'output_center': (out_cx, out_cy)
    }


def apply_bird_eye_view(image, transform):
    """Apply bird's eye view transformation to image"""
    H = transform['transform_matrix']
    out_size = transform['output_size']
    return cv2.warpPerspective(image, H, out_size)


def image_to_ground(points, transform, camera_matrix, camera_height):
    """
    Convert image points to ground coordinates (mm)

    Args:
        points: Nx2 array of image points
        transform: bird eye transform dict
        camera_matrix: 3x3 camera intrinsic matrix
        camera_height: camera height from ground (mm)

    Returns:
        Nx2 array of ground coordinates (x, z) in mm
    """
    fx = camera_matrix[0, 0]
    fy = camera_matrix[1, 1]
    cx = camera_matrix[0, 2]
    cy = camera_matrix[1, 2]

    points = np.array(points, dtype=np.float32)
    if points.ndim == 1:
        points = points.reshape(1, 2)

    ground_pts = []
    for u, v in points:
        if v <= cy:
            # Above horizon
            ground_pts.append([np.nan, np.nan])
            continue
        z = -camera_height * fy / (v - cy)
        x = (u - cx) / fx * z
        ground_pts.append([x, -z])  # z is distance forward

    return np.array(ground_pts)


def draw_perspective_lines(image, quad_pts, camera_matrix, camera_height,
                           line_length=500, color=(255, 0, 0), thickness=2):
    """
    Draw perspective lines from quad corners toward vanishing point

    For camera parallel to ground, vanishing point is at principal point (cx, cy)

    Args:
        image: input image
        quad_pts: 4 quad points (P1, P2, P3, P4)
        camera_matrix: 3x3 camera intrinsic matrix
        camera_height: camera height (mm)
        line_length: length to extend lines (pixels)
        color: line color (BGR)
        thickness: line thickness

    Returns:
        image with perspective lines drawn
    """
    vis_img = image.copy()
    cx = camera_matrix[0, 2]
    cy = camera_matrix[1, 2]
    vanishing_point = np.array([cx, cy])

    pts = np.array(quad_pts, dtype=np.float32)

    for pt in pts:
        # Direction toward vanishing point
        direction = vanishing_point - pt
        length = np.linalg.norm(direction)
        if length > 0:
            direction = direction / length

        # Extend line
        end_pt = pt + direction * line_length
        cv2.line(vis_img, tuple(pt.astype(int)), tuple(end_pt.astype(int)),
                color, thickness)

    return vis_img


def draw_coordinate_axes(image, quad_pts, axis_length=80, thickness=2, yaw_offset=0.0):
    """
    Draw XYZ coordinate axes at quad center (World coordinate system)

    Yaw 회전: Z축(수직) 기준으로 X,Y가 수평면(지면)에서 회전

    World 좌표계 (Gazebo):
    - X (red): 전방 (Forward) - 지면과 평행
    - Y (green): 좌측 (Left) - 지면과 평행, X에 수직
    - Z (blue): 상방 (Up) - 항상 고정

    카메라 시점 (World +X 방향을 바라봄):
    - World X → 깊이 방향 (이미지에서 위쪽으로 줄어듦, 소실점 방향)
    - World Y → 이미지 왼쪽 방향
    - World Z → 이미지 위쪽 방향

    Yaw 회전 효과:
    - Yaw=0: X축이 전방(깊이), Y축이 왼쪽
    - Yaw=+90: X축이 왼쪽, Y축이 뒤쪽(깊이 반대)
    - Yaw=-90: X축이 오른쪽, Y축이 전방(깊이)

    Args:
        image: input image
        quad_pts: 4 quad points (P1, P2, P3, P4)
        axis_length: axis length in pixels
        thickness: line thickness
        yaw_offset: yaw rotation in degrees (for testing)

    Returns:
        image with coordinate axes, yaw_deg
    """
    vis_img = image.copy()
    pts = np.array(quad_pts, dtype=np.float32)

    # Origin: center of quad
    center = np.mean(pts, axis=0)
    cx, cy = int(center[0]), int(center[1])

    # Yaw 회전 (Z축 기준)
    yaw_rad = np.radians(yaw_offset)
    cos_yaw = np.cos(yaw_rad)
    sin_yaw = np.sin(yaw_rad)

    # World 좌표계에서 3D 축 방향 (단위 벡터)
    # Yaw 회전 적용: X,Y만 회전, Z는 고정
    # R_z(yaw) = [[cos, -sin, 0], [sin, cos, 0], [0, 0, 1]]
    x_world = np.array([cos_yaw, sin_yaw, 0])   # X축 (전방)
    y_world = np.array([-sin_yaw, cos_yaw, 0])  # Y축 (좌측)
    z_world = np.array([0, 0, 1])               # Z축 (상방, 고정)

    # World → Image 투영
    # 카메라가 World +X 방향을 바라보고 있다고 가정
    # World X → Camera Z (depth) → 이미지에서 위쪽(-Y)으로 줄어듦
    # World Y → Camera -X → 이미지에서 왼쪽(-X)
    # World Z → Camera -Y → 이미지에서 위쪽(-Y)

    # 깊이 스케일: 전방으로 갈수록 작아짐 (원근 효과)
    depth_scale = 0.5  # 깊이 방향 축소 비율

    # 이미지 좌표로 변환
    # World X (전방) → 이미지 위쪽(-Y)으로 향하면서 축소
    # World Y (좌측) → 이미지 왼쪽(-X)
    # World Z (상방) → 이미지 위쪽(-Y)

    x_img = np.array([
        -x_world[1] * axis_length,          # World Y성분 → Image -X
        -x_world[0] * axis_length * depth_scale  # World X성분 → Image -Y (깊이, 축소)
    ], dtype=np.float32)

    y_img = np.array([
        -y_world[1] * axis_length,          # World Y성분 → Image -X
        -y_world[0] * axis_length * depth_scale  # World X성분 → Image -Y
    ], dtype=np.float32)

    # Z축 (상방): 항상 이미지에서 위쪽
    z_img = np.array([0, -axis_length], dtype=np.float32)

    # Calculate end points
    x_end = center + x_img
    y_end = center + y_img
    z_end = center + z_img

    # Draw Z-axis (blue) - Up (always fixed) - 먼저 그려서 뒤에 위치
    cv2.arrowedLine(vis_img, (cx, cy), (int(z_end[0]), int(z_end[1])),
                    (255, 0, 0), thickness, tipLength=0.2)

    # Draw Y-axis (green) - Left
    cv2.arrowedLine(vis_img, (cx, cy), (int(y_end[0]), int(y_end[1])),
                    (0, 255, 0), thickness, tipLength=0.2)

    # Draw X-axis (red) - Forward
    cv2.arrowedLine(vis_img, (cx, cy), (int(x_end[0]), int(x_end[1])),
                    (0, 0, 255), thickness, tipLength=0.2)

    # Display yaw info on image
    yaw_text = f"Yaw: {yaw_offset:.1f} deg"
    cv2.putText(vis_img, yaw_text, (cx - 60, cy + 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 3)
    cv2.putText(vis_img, yaw_text, (cx - 60, cy + 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    return vis_img, yaw_offset


def visualize_calibration(image, calib_result, camera_height):
    """Visualize calibration with grid overlay"""
    camera_matrix = calib_result['camera_matrix']
    dist_coeffs = calib_result['dist_coeffs']

    # Undistort image
    undistorted = cv2.undistort(image, camera_matrix, dist_coeffs)

    # Compute bird's eye transform
    h, w = image.shape[:2]
    transform = compute_bird_eye_transform(
        camera_matrix, camera_height, (w, h),
        output_scale=5.0
    )

    # Apply bird's eye view
    bird_eye = apply_bird_eye_view(undistorted, transform)

    # Draw grid on bird's eye view
    out_w, out_h = transform['output_size']
    out_cx, out_cy = transform['output_center']
    scale = transform['output_scale']

    # Draw 1m grid
    grid_mm = 1000  # 1 meter
    grid_px = int(grid_mm / scale)

    for x in range(0, out_w, grid_px):
        cv2.line(bird_eye, (x, 0), (x, out_h), (50, 50, 50), 1)
    for y in range(0, out_h, grid_px):
        cv2.line(bird_eye, (0, y), (out_w, y), (50, 50, 50), 1)

    # Draw center lines
    cv2.line(bird_eye, (out_cx, 0), (out_cx, out_h), (0, 255, 0), 2)
    cv2.line(bird_eye, (0, out_cy), (out_w, out_cy), (0, 255, 0), 2)

    return undistorted, bird_eye


def main():
    parser = argparse.ArgumentParser(description='Bird Eye View Camera Calibration')
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Calibrate command
    calib_parser = subparsers.add_parser('calibrate', help='Calibrate camera with checkerboard')
    calib_parser.add_argument('--images', type=str, required=True,
                              help='Path to checkerboard images (folder or glob pattern)')
    calib_parser.add_argument('--board', type=str, default='9x6',
                              help='Checkerboard size (cols x rows inner corners)')
    calib_parser.add_argument('--square', type=float, default=25.0,
                              help='Square size in mm')
    calib_parser.add_argument('--output', type=str, default='camera_calib.json',
                              help='Output calibration file')

    # Test command
    test_parser = subparsers.add_parser('test', help='Test calibration with image')
    test_parser.add_argument('--calib', type=str, required=True,
                             help='Calibration JSON file')
    test_parser.add_argument('--image', type=str, required=True,
                             help='Test image path')
    test_parser.add_argument('--height', type=float, default=1500.0,
                             help='Camera height from ground (mm)')

    args = parser.parse_args()

    if args.command == 'calibrate':
        # Parse board size
        cols, rows = map(int, args.board.split('x'))
        board_size = (cols, rows)

        # Get image paths
        images_path = Path(args.images)
        if images_path.is_dir():
            image_paths = list(images_path.glob('*.png')) + \
                         list(images_path.glob('*.jpg')) + \
                         list(images_path.glob('*.jpeg'))
        else:
            image_paths = list(Path('.').glob(args.images))

        if not image_paths:
            print(f"No images found: {args.images}")
            return

        # Calibrate
        result = calibrate_camera_checkerboard(image_paths, board_size, args.square)

        if result:
            save_calibration(result, args.output)

    elif args.command == 'test':
        # Load calibration
        calib = load_calibration(args.calib)
        print(f"Loaded calibration: {args.calib}")
        print(f"  Image size: {calib['image_size']}")
        print(f"  Focal length: fx={calib['camera_matrix'][0,0]:.1f}, fy={calib['camera_matrix'][1,1]:.1f}")

        # Load test image
        image = cv2.imread(args.image)
        if image is None:
            print(f"Cannot read image: {args.image}")
            return

        # Visualize
        undistorted, bird_eye = visualize_calibration(image, calib, args.height)

        # Display
        plt.figure(figsize=(15, 5))
        plt.subplot(131)
        plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        plt.title('Original')
        plt.axis('off')

        plt.subplot(132)
        plt.imshow(cv2.cvtColor(undistorted, cv2.COLOR_BGR2RGB))
        plt.title('Undistorted')
        plt.axis('off')

        plt.subplot(133)
        plt.imshow(cv2.cvtColor(bird_eye, cv2.COLOR_BGR2RGB))
        plt.title('Bird Eye View')
        plt.axis('off')

        plt.tight_layout()
        plt.show()

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
