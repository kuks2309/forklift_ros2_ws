#!/usr/bin/env python3
"""
Pallet Pose Estimation Module
- 6DoF pose estimation using solvePnP (roll, pitch, yaw)
- Can estimate roughly without camera calibration
"""

import cv2
import numpy as np


# Default pallet size (mm) - 1200x1000x150 pallet front face (forklift entry side)
DEFAULT_PALLET_WIDTH = 1200.0   # mm (width)
DEFAULT_PALLET_HEIGHT = 150.0   # mm (height, front face visible height)


def estimate_pose_pnp(quad_pts, image_size,
                      pallet_width=DEFAULT_PALLET_WIDTH,
                      pallet_height=DEFAULT_PALLET_HEIGHT,
                      camera_matrix=None):
    """
    6DoF pose estimation using solvePnP

    Args:
        quad_pts: 4 2D image coordinates (P1, P2, P3, P4)
                  P1(top-left), P2(top-right), P3(bottom-right), P4(bottom-left)
        image_size: (width, height) image size
        pallet_width: pallet width (mm)
        pallet_height: pallet height (mm)
        camera_matrix: camera intrinsic parameters (None uses estimated values)

    Returns:
        dict: {
            'roll': float - X-axis rotation (degrees)
            'pitch': float - Y-axis rotation (degrees)
            'yaw': float - Z-axis rotation (degrees)
            'tvec': np.array - translation vector [x, y, z]
            'rvec': np.array - rotation vector
            'success': bool - success flag
        }
    """
    # 3D object coordinates (pallet local coordinate system)
    # Pallet center at origin
    # X: right (P1->P2 direction)
    # Y: up (P4->P1 direction, opposite to image Y-axis)
    # Z: camera direction (normal, from pallet to camera)
    half_w = pallet_width / 2
    half_h = pallet_height / 2

    # P1(top-left), P2(top-right), P3(bottom-right), P4(bottom-left) order
    # OpenCV coordinate system: X-right, Y-down, Z-from camera to object
    # Small Y in image (top) = small Y in 3D
    # Large Y in image (bottom) = large Y in 3D
    object_points = np.array([
        [-half_w, -half_h, 0],  # P1: top-left (X-, Y-)
        [half_w, -half_h, 0],   # P2: top-right (X+, Y-)
        [half_w, half_h, 0],    # P3: bottom-right (X+, Y+)
        [-half_w, half_h, 0]    # P4: bottom-left (X-, Y+)
    ], dtype=np.float32)

    # 2D image coordinates
    image_points = np.array(quad_pts, dtype=np.float32)

    # Camera matrix (use estimated values if not provided)
    if camera_matrix is None:
        w, h = image_size
        # FOV 60 degrees: focal_length = w / (2 * tan(fov/2))
        fov_deg = 60
        focal_length = w / (2 * np.tan(np.radians(fov_deg / 2)))
        camera_matrix = np.array([
            [focal_length, 0, w / 2],
            [0, focal_length, h / 2],
            [0, 0, 1]
        ], dtype=np.float32)

    # Distortion coefficients (none)
    dist_coeffs = np.zeros(4)

    # Run solvePnP
    success, rvec, tvec = cv2.solvePnP(
        object_points, image_points, camera_matrix, dist_coeffs,
        flags=cv2.SOLVEPNP_ITERATIVE
    )

    if not success:
        return {
            'roll': 0, 'pitch': 0, 'yaw': 0,
            'tvec': np.zeros(3), 'rvec': np.zeros(3),
            'success': False
        }

    # Convert rotation vector to rotation matrix
    R, _ = cv2.Rodrigues(rvec)

    # Extract Euler angles from rotation matrix (roll, pitch, yaw)
    # OpenCV coordinate system: X-right, Y-down, Z-forward (camera direction)
    roll, pitch, yaw = rotation_matrix_to_euler(R)

    return {
        'roll': np.degrees(roll),
        'pitch': np.degrees(pitch),
        'yaw': np.degrees(yaw),
        'tvec': tvec.flatten(),
        'rvec': rvec.flatten(),
        'R': R,
        'success': True,
        'camera_matrix': camera_matrix
    }


def rotation_matrix_to_euler(R):
    """
    Convert rotation matrix to Euler angles

    Coordinate system:
    - Roll: X-axis rotation (pallet left-right tilt)
    - Pitch: Z-axis rotation (pallet tilt within plane, clockwise/counter-clockwise)
    - Yaw: Y-axis rotation (horizontal direction - pallet facing left/right)
           Yaw+ = pallet faces right, Yaw- = pallet faces left

    Returns:
        (roll, pitch, yaw) in radians
    """
    sy = np.sqrt(R[0, 0] ** 2 + R[1, 0] ** 2)

    singular = sy < 1e-6

    if not singular:
        roll = np.arctan2(R[2, 1], R[2, 2])    # X-axis rotation
        y_rot = np.arctan2(-R[2, 0], sy)       # Y-axis rotation (raw)
        z_rot = np.arctan2(R[1, 0], R[0, 0])   # Z-axis rotation
    else:
        roll = np.arctan2(-R[1, 2], R[1, 1])
        y_rot = np.arctan2(-R[2, 0], sy)
        z_rot = 0

    # Remap to user convention:
    # - Yaw (horizontal direction) = -Y-axis rotation
    #   Yaw+ means pallet faces right, which requires -Y rotation
    # - Pitch (plane tilt) = Z-axis rotation
    yaw = -y_rot
    pitch = z_rot

    return roll, pitch, yaw


def draw_pose_axes(img, quad_pts, pose_result, axis_len=200):
    """
    Draw 3D coordinate axes using solvePnP + projectPoints (OpenCV standard method)

    Args:
        img: input image
        quad_pts: quadrilateral vertices (P1, P2, P3, P4)
        pose_result: estimate_pose_pnp() result
        axis_len: axis length (mm)
    """
    vis_img = img.copy()

    if not pose_result.get('success', False):
        return vis_img

    rvec = pose_result['rvec'].reshape(3, 1)
    tvec = pose_result['tvec'].reshape(3, 1)
    camera_matrix = pose_result['camera_matrix']

    # 3D axis endpoints (pallet local coordinate system)
    # X: P1->P2 direction (right)
    # Y: P1->P4 direction (down)
    # Z: pallet front normal (pointing toward camera when facing front)
    axis_3d = np.float32([
        [0, 0, 0],              # origin
        [axis_len, 0, 0],       # X-axis (red) - right (P1->P2)
        [0, -axis_len, 0],      # Y-axis (green) - up (rotated 180 around X)
        [0, 0, -axis_len]       # Z-axis (blue) - into pallet (rotated 180 around X)
    ])

    # 3D -> 2D projection
    axis_2d, _ = cv2.projectPoints(axis_3d, rvec, tvec, camera_matrix, np.zeros(4))
    axis_2d = axis_2d.reshape(-1, 2).astype(int)

    origin = tuple(axis_2d[0])
    x_end = tuple(axis_2d[1])
    y_end = tuple(axis_2d[2])
    z_end = tuple(axis_2d[3])

    # Draw axes
    cv2.arrowedLine(vis_img, origin, x_end, (0, 0, 255), 3, tipLength=0.2)  # X: red
    cv2.arrowedLine(vis_img, origin, y_end, (0, 255, 0), 3, tipLength=0.2)  # Y: green
    cv2.arrowedLine(vis_img, origin, z_end, (255, 0, 0), 3, tipLength=0.2)  # Z: blue

    cv2.putText(vis_img, 'X', (x_end[0]+5, x_end[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)
    cv2.putText(vis_img, 'Y', (y_end[0]+5, y_end[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
    cv2.putText(vis_img, 'Z', (z_end[0]+5, z_end[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,0,0), 2)

    return vis_img


def estimate_rough_pose(quad_pts):
    """
    Rough pose estimation from geometric properties of quadrilateral

    Args:
        quad_pts: 4 2D image coordinates (P1, P2, P3, P4)
                  P1(top-left), P2(top-right), P3(bottom-right), P4(bottom-left)

    Returns:
        dict: {
            'center': (cx, cy) - center point
            'angle': float - rotation angle (degrees)
            'width': float - top width (pixels)
            'height_left': float - left height (pixels)
            'height_right': float - right height (pixels)
            'perspective': float - perspective ratio (top_width/bottom_width, <1 means farther)
            'tilt': float - left-right tilt (degrees)
        }
    """
    pts = np.array(quad_pts, dtype=np.float32)

    # Center point
    center = np.mean(pts, axis=0)

    # P1(top-left), P2(top-right), P3(bottom-right), P4(bottom-left)
    p1, p2, p3, p4 = pts[0], pts[1], pts[2], pts[3]

    # Top/bottom width
    top_width = np.linalg.norm(p2 - p1)
    bottom_width = np.linalg.norm(p3 - p4)

    # Left/right height
    height_left = np.linalg.norm(p4 - p1)
    height_right = np.linalg.norm(p3 - p2)

    # Rotation angle (angle of top edge)
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    angle = np.degrees(np.arctan2(dy, dx))

    # Perspective ratio (<1 means top is narrower = pallet is farther)
    perspective = top_width / bottom_width if bottom_width > 0 else 1.0

    # Left-right tilt (positive if left is higher)
    tilt = np.degrees(np.arctan2(height_left - height_right, (top_width + bottom_width) / 2))

    return {
        'center': tuple(center.astype(int)),
        'angle': angle,
        'width_top': top_width,
        'width_bottom': bottom_width,
        'height_left': height_left,
        'height_right': height_right,
        'perspective': perspective,
        'tilt': tilt
    }


def get_pose_direction(pose_info):
    """
    Generate direction text from pose info

    Returns:
        str: direction description string
    """
    angle = pose_info['angle']
    perspective = pose_info['perspective']
    tilt = pose_info['tilt']

    # Rotation direction
    if abs(angle) < 5:
        rotation_str = "Front"
    elif angle > 0:
        rotation_str = f"Right {abs(angle):.1f} deg"
    else:
        rotation_str = f"Left {abs(angle):.1f} deg"

    # Distance/perspective
    if perspective < 0.85:
        distance_str = "Far"
    elif perspective > 1.15:
        distance_str = "Close"
    else:
        distance_str = "Middle"

    # Tilt
    if abs(tilt) < 3:
        tilt_str = "Level"
    elif tilt > 0:
        tilt_str = f"Left high {abs(tilt):.1f} deg"
    else:
        tilt_str = f"Right high {abs(tilt):.1f} deg"

    return f"{rotation_str} | {distance_str} | {tilt_str}"


def draw_pose_info(img, quad_pts, pose_info):
    """
    Display pose info on image

    Args:
        img: input image
        quad_pts: quadrilateral vertices
        pose_info: estimate_rough_pose() result

    Returns:
        img: image with pose info drawn
    """
    vis_img = img.copy()
    cx, cy = pose_info['center']

    # Mark center point
    cv2.circle(vis_img, (cx, cy), 8, (0, 255, 255), -1)
    cv2.circle(vis_img, (cx, cy), 8, (0, 0, 0), 2)

    # Direction arrow (reflecting rotation angle)
    angle_rad = np.radians(pose_info['angle'])
    arrow_len = 60
    end_x = int(cx + arrow_len * np.cos(angle_rad))
    end_y = int(cy + arrow_len * np.sin(angle_rad))
    cv2.arrowedLine(vis_img, (cx, cy), (end_x, end_y), (0, 255, 255), 3, tipLength=0.3)

    # Pose info text
    direction = get_pose_direction(pose_info)

    # Text background
    text_y = 30
    info_lines = [
        f"Angle: {pose_info['angle']:.1f} deg",
        f"Perspective: {pose_info['perspective']:.2f}",
        f"Tilt: {pose_info['tilt']:.1f} deg",
        direction
    ]

    for i, line in enumerate(info_lines):
        y = text_y + i * 25
        cv2.putText(vis_img, line, (10, y), cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, (0, 0, 0), 3)
        cv2.putText(vis_img, line, (10, y), cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, (0, 255, 255), 1)

    return vis_img


def euler_to_rotation_matrix(roll, pitch, yaw):
    """
    Convert Euler angles to rotation matrix

    User convention:
    - Roll: X-axis rotation (pallet left-right tilt)
    - Pitch: Z-axis rotation (pallet tilt within plane)
    - Yaw: horizontal direction (pallet facing left/right)
           Yaw+ = faces right, Yaw- = faces left

    Internally converts to actual axis rotations:
    - Roll -> X-axis
    - Pitch -> Z-axis
    - Yaw -> -Y-axis

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


def create_camera_matrix(image_size, fov_deg=60):
    """Create camera intrinsic matrix"""
    w, h = image_size
    focal_length = w / (2 * np.tan(np.radians(fov_deg / 2)))
    camera_matrix = np.array([
        [focal_length, 0, w / 2],
        [0, focal_length, h / 2],
        [0, 0, 1]
    ], dtype=np.float32)
    return camera_matrix


def project_pose_to_2d(roll, pitch, yaw, tx, ty, tz, pallet_width, pallet_height, camera_matrix):
    """
    Project 3D pallet pose to 2D image coordinates

    Args:
        roll, pitch, yaw: rotation angles (radians)
        tx, ty, tz: translation (mm)
        pallet_width, pallet_height: pallet size (mm)
        camera_matrix: camera intrinsic matrix

    Returns:
        4x2 numpy array of projected 2D points
    """
    half_w = pallet_width / 2
    half_h = pallet_height / 2

    # 3D rectangle points
    rect_3d = np.array([
        [-half_w, -half_h, 0],  # P1: top-left
        [half_w, -half_h, 0],   # P2: top-right
        [half_w, half_h, 0],    # P3: bottom-right
        [-half_w, half_h, 0]    # P4: bottom-left
    ], dtype=np.float32)

    # Rotation matrix
    R = euler_to_rotation_matrix(roll, pitch, yaw)
    rvec, _ = cv2.Rodrigues(R)
    tvec = np.array([[tx], [ty], [tz]], dtype=np.float32)

    # Project to 2D
    points_2d, _ = cv2.projectPoints(rect_3d, rvec, tvec, camera_matrix, np.zeros(4))
    return points_2d.reshape(-1, 2)


def compute_quad_iou(quad1, quad2, image_size):
    """
    Compute IoU between two quadrilaterals using mask overlap

    Args:
        quad1, quad2: 4x2 numpy arrays of quadrilateral vertices
        image_size: (width, height)

    Returns:
        float: IoU score (0~1)
    """
    w, h = image_size

    # Create masks
    mask1 = np.zeros((h, w), dtype=np.uint8)
    mask2 = np.zeros((h, w), dtype=np.uint8)

    pts1 = quad1.astype(np.int32)
    pts2 = quad2.astype(np.int32)

    cv2.fillPoly(mask1, [pts1], 255)
    cv2.fillPoly(mask2, [pts2], 255)

    # Compute IoU
    intersection = np.logical_and(mask1, mask2).sum()
    union = np.logical_or(mask1, mask2).sum()

    if union == 0:
        return 0.0

    return intersection / union


def compute_point_distance(quad1, quad2):
    """
    Compute average point distance between two quadrilaterals

    Args:
        quad1, quad2: 4x2 numpy arrays

    Returns:
        float: average Euclidean distance
    """
    return np.mean(np.linalg.norm(quad1 - quad2, axis=1))


def generate_quad_candidates(quad_pts, pixel_offsets=[-5, -3, -1, 0, 1, 3, 5]):
    """
    Generate quadrilateral candidates by perturbing each point

    Args:
        quad_pts: 4x2 original quadrilateral points
        pixel_offsets: list of pixel offsets to try

    Returns:
        list of candidate quadrilaterals
    """
    quad_pts = np.array(quad_pts, dtype=np.float32)
    candidates = [quad_pts.copy()]  # Include original

    # Perturb each point independently
    for i in range(4):  # For each point
        for dx in pixel_offsets:
            for dy in pixel_offsets:
                if dx == 0 and dy == 0:
                    continue
                candidate = quad_pts.copy()
                candidate[i, 0] += dx
                candidate[i, 1] += dy
                candidates.append(candidate)

    # Also try uniform shifts of all points
    for dx in pixel_offsets:
        for dy in pixel_offsets:
            if dx == 0 and dy == 0:
                continue
            candidate = quad_pts.copy()
            candidate[:, 0] += dx
            candidate[:, 1] += dy
            candidates.append(candidate)

    return candidates


def refine_pose_by_quad_perturbation(quad_pts, image_size,
                                      pallet_width=DEFAULT_PALLET_WIDTH,
                                      pallet_height=DEFAULT_PALLET_HEIGHT,
                                      pixel_offsets=[-5, -3, -1, 0, 1, 3, 5]):
    """
    Refine pose by perturbing 2D quad coordinates and finding best match

    Method:
    1. Generate multiple candidate quads by perturbing original points
    2. For each candidate, compute pose using solvePnP
    3. Project pose back to 2D
    4. Select pose with highest IoU between projected quad and original quad

    Args:
        quad_pts: 4x2 array of quadrilateral points from YOLO
        image_size: (width, height)
        pallet_width, pallet_height: pallet size (mm)
        pixel_offsets: pixel offsets to try for perturbation

    Returns:
        dict: best pose result with projected_quad
    """
    original_quad = np.array(quad_pts, dtype=np.float32)
    camera_matrix = create_camera_matrix(image_size)

    # Generate candidate quads
    candidates = generate_quad_candidates(original_quad, pixel_offsets)

    best_score = -1
    best_pose = None
    best_projected = None

    for candidate_quad in candidates:
        # Compute pose for this candidate
        pose = estimate_pose_pnp(candidate_quad, image_size, pallet_width, pallet_height, camera_matrix)

        if not pose.get('success', False):
            continue

        # Project pose back to 2D
        projected = project_pose_to_2d(
            np.radians(pose['roll']),
            np.radians(pose['pitch']),
            np.radians(pose['yaw']),
            pose['tvec'][0], pose['tvec'][1], pose['tvec'][2],
            pallet_width, pallet_height, camera_matrix
        )

        # Compute IoU with original quad
        iou = compute_quad_iou(projected, original_quad, image_size)

        if iou > best_score:
            best_score = iou
            best_pose = pose
            best_projected = projected

    if best_pose is None:
        return {
            'roll': 0, 'pitch': 0, 'yaw': 0,
            'tvec': np.zeros(3), 'rvec': np.zeros(3),
            'success': False
        }

    # Add IoU and projected quad to result
    best_pose['iou'] = best_score
    best_pose['projected_quad'] = best_projected

    return best_pose


def refine_pose_iterative(quad_pts, image_size,
                          pallet_width=DEFAULT_PALLET_WIDTH,
                          pallet_height=DEFAULT_PALLET_HEIGHT,
                          max_iterations=3):
    """
    Iteratively refine pose by perturbing quad coordinates

    Method:
    1. Start with original quad
    2. Find best pose using perturbation
    3. Use projected quad as new reference
    4. Repeat until convergence

    Args:
        quad_pts: 4x2 array of quadrilateral points from YOLO
        image_size: (width, height)
        pallet_width, pallet_height: pallet size (mm)
        max_iterations: maximum refinement iterations

    Returns:
        dict: refined pose result
    """
    current_quad = np.array(quad_pts, dtype=np.float32)
    original_quad = current_quad.copy()

    best_pose = None
    best_iou = -1

    # Coarse to fine pixel offsets
    offset_levels = [
        [-10, -5, 0, 5, 10],      # Coarse
        [-3, -2, -1, 0, 1, 2, 3],  # Medium
        [-2, -1, 0, 1, 2],         # Fine
    ]

    for iteration in range(max_iterations):
        offsets = offset_levels[min(iteration, len(offset_levels) - 1)]

        pose = refine_pose_by_quad_perturbation(
            current_quad, image_size,
            pallet_width, pallet_height,
            pixel_offsets=offsets
        )

        if not pose.get('success', False):
            break

        # Check if this is better than previous best
        # Compare projected quad with ORIGINAL quad
        camera_matrix = create_camera_matrix(image_size)
        projected = project_pose_to_2d(
            np.radians(pose['roll']),
            np.radians(pose['pitch']),
            np.radians(pose['yaw']),
            pose['tvec'][0], pose['tvec'][1], pose['tvec'][2],
            pallet_width, pallet_height, camera_matrix
        )

        iou = compute_quad_iou(projected, original_quad, image_size)

        if iou > best_iou:
            best_iou = iou
            best_pose = pose
            best_pose['iou'] = iou
            best_pose['projected_quad'] = projected

        # Use projected quad as new reference for next iteration
        if pose.get('projected_quad') is not None:
            current_quad = pose['projected_quad']

    if best_pose is None:
        # Fallback to simple solvePnP
        return estimate_pose_pnp(quad_pts, image_size, pallet_width, pallet_height)

    return best_pose


# Test
if __name__ == '__main__':
    # Example quadrilateral coordinates
    test_pts = np.array([
        [200, 300],  # P1: top-left
        [500, 310],  # P2: top-right
        [520, 450],  # P3: bottom-right
        [180, 440]   # P4: bottom-left
    ])

    pose = estimate_rough_pose(test_pts)

    print("="*50)
    print("Rough Pose Estimation Result")
    print("="*50)
    print(f"Center: {pose['center']}")
    print(f"Rotation angle: {pose['angle']:.1f} deg")
    print(f"Top width: {pose['width_top']:.1f} px")
    print(f"Bottom width: {pose['width_bottom']:.1f} px")
    print(f"Perspective ratio: {pose['perspective']:.2f}")
    print(f"Tilt: {pose['tilt']:.1f} deg")
    print()
    print(f"Direction: {get_pose_direction(pose)}")
