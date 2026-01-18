#!/usr/bin/env python3
"""
Pallet 좌표를 카메라 이미지로 투영하는 스크립트

World 좌표계에서 Pallet 위치의 XYZ 축을 Camera 좌표계로 변환 후 이미지에 투영
"""

import numpy as np
import cv2
import math

# 카메라 파라미터
IMAGE_WIDTH = 1280
IMAGE_HEIGHT = 720
HFOV = 1.047  # horizontal field of view (radians, 60 degrees)

# Camera intrinsic matrix 계산
fx = IMAGE_WIDTH / (2 * math.tan(HFOV / 2))
fy = fx  # square pixels
cx = IMAGE_WIDTH / 2
cy = IMAGE_HEIGHT / 2

# World → Camera 변환
# World X → Camera Z (forward)
# World Y → Camera -X (left in image)
# World Z → Camera -Y (up in image)
R_world_to_cam = np.array([
    [0, -1, 0],
    [0, 0, -1],
    [1, 0, 0]
], dtype=np.float64)

# 카메라 위치 (World 좌표계)
camera_pos_world = np.array([0, 0, 0.4])  # Z 방향 0.4m


def world_to_camera(point_world):
    """World 좌표를 Camera 좌표로 변환"""
    relative = point_world - camera_pos_world
    point_cam = R_world_to_cam @ relative
    return point_cam


def camera_to_image(point_cam):
    """Camera 좌표를 이미지 좌표로 투영"""
    if point_cam[2] <= 0:
        return None

    x, y, z = point_cam
    u = fx * (x / z) + cx
    v = fy * (y / z) + cy
    return np.array([u, v])


def draw_world_axes_at_pallet(x, y, yaw_deg, save_path=None):
    """Pallet 위치에서 Pallet 좌표축을 이미지에 투영 (Yaw 회전 적용)"""
    # 빈 이미지 생성
    image = np.zeros((IMAGE_HEIGHT, IMAGE_WIDTH, 3), dtype=np.uint8)
    image[:] = (50, 50, 50)  # 어두운 회색 배경

    # Pallet 위치 (World 좌표계)
    pallet_origin = np.array([x, y, 0.0])

    # 축 길이 (0.5m)
    axis_length = 0.5

    # Yaw 회전 행렬 (Z축 기준 회전)
    yaw_rad = math.radians(yaw_deg)
    cos_yaw = math.cos(yaw_rad)
    sin_yaw = math.sin(yaw_rad)
    R_yaw = np.array([
        [cos_yaw, -sin_yaw, 0],
        [sin_yaw, cos_yaw, 0],
        [0, 0, 1]
    ])

    # Pallet 로컬 좌표축 (Yaw 회전 적용)
    local_x = np.array([axis_length, 0, 0])
    local_y = np.array([0, axis_length, 0])
    local_z = np.array([0, 0, axis_length])

    # World 좌표로 변환
    x_axis_end = pallet_origin + R_yaw @ local_x
    y_axis_end = pallet_origin + R_yaw @ local_y
    z_axis_end = pallet_origin + R_yaw @ local_z

    # World → Camera → Image 변환
    origin_cam = world_to_camera(pallet_origin)
    x_end_cam = world_to_camera(x_axis_end)
    y_end_cam = world_to_camera(y_axis_end)
    z_end_cam = world_to_camera(z_axis_end)

    origin_img = camera_to_image(origin_cam)
    x_end_img = camera_to_image(x_end_cam)
    y_end_img = camera_to_image(y_end_cam)
    z_end_img = camera_to_image(z_end_cam)

    # 축 그리기
    if origin_img is not None:
        origin_pt = tuple(origin_img.astype(int))

        # X축 (빨강) - World X → Camera Z (forward, shrinks toward center)
        if x_end_img is not None:
            x_pt = tuple(x_end_img.astype(int))
            cv2.arrowedLine(image, origin_pt, x_pt, (0, 0, 255), 3, tipLength=0.1)
            cv2.putText(image, "X", (x_pt[0] + 10, x_pt[1]),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        # Y축 (초록) - World Y → Camera -X (left in image)
        if y_end_img is not None:
            y_pt = tuple(y_end_img.astype(int))
            cv2.arrowedLine(image, origin_pt, y_pt, (0, 255, 0), 3, tipLength=0.1)
            cv2.putText(image, "Y", (y_pt[0] + 10, y_pt[1]),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        # Z축 (파랑) - World Z → Camera -Y (up in image)
        if z_end_img is not None:
            z_pt = tuple(z_end_img.astype(int))
            cv2.arrowedLine(image, origin_pt, z_pt, (255, 0, 0), 3, tipLength=0.1)
            cv2.putText(image, "Z", (z_pt[0] + 10, z_pt[1]),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)

        # 원점 표시
        cv2.circle(image, origin_pt, 8, (255, 255, 255), -1)

    # 정보 표시
    info_lines = [
        f"Pallet Position (World): X={x}m, Y={y}m, Yaw={yaw_deg}deg",
        f"Camera Position (World): (0, 0, 0.4)m",
        f"Axis Length: {axis_length}m",
        "",
        "World -> Camera Transform:",
        "  World X (red)   -> Camera Z (forward)",
        "  World Y (green) -> Camera -X (left)",
        "  World Z (blue)  -> Camera -Y (up)",
        "",
        "Projected Coordinates:",
        f"  Origin: World({x:.1f}, {y:.1f}, 0) -> Cam({origin_cam[0]:.2f}, {origin_cam[1]:.2f}, {origin_cam[2]:.2f})",
    ]

    if x_end_img is not None:
        info_lines.append(f"  X-end:  World({x+axis_length:.1f}, {y:.1f}, 0) -> Cam({x_end_cam[0]:.2f}, {x_end_cam[1]:.2f}, {x_end_cam[2]:.2f})")
    if y_end_img is not None:
        info_lines.append(f"  Y-end:  World({x:.1f}, {y+axis_length:.1f}, 0) -> Cam({y_end_cam[0]:.2f}, {y_end_cam[1]:.2f}, {y_end_cam[2]:.2f})")
    if z_end_img is not None:
        info_lines.append(f"  Z-end:  World({x:.1f}, {y:.1f}, {axis_length}) -> Cam({z_end_cam[0]:.2f}, {z_end_cam[1]:.2f}, {z_end_cam[2]:.2f})")

    y_offset = 30
    for line in info_lines:
        cv2.putText(image, line, (10, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
        y_offset += 18

    if save_path:
        cv2.imwrite(save_path, image)
        print(f"Saved: {save_path}")

    return image


def main():
    # Pallet 위치: World X=3m, Y=1m, Yaw=45도
    x = 3.0
    y = 1.0
    yaw_deg = 45.0

    save_path = "/home/amap/forklift_ros2_ws/teach/pallet_projection.png"
    image = draw_world_axes_at_pallet(x, y, yaw_deg, save_path)

    print(f"\n=== World Axes Projection at Pallet Position ===")
    print(f"Pallet: X={x}m, Y={y}m")
    print(f"Camera: (0, 0, 0.4)m, looking +X direction")
    print(f"\nImage saved to: {save_path}")


if __name__ == '__main__':
    main()
