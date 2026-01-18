# 좌표계 정의

## 1. World 좌표계 (Gazebo)

Gazebo 표준 좌표계:
- **X**: 전방 (Forward)
- **Y**: 좌측 (Left)
- **Z**: 상방 (Up)

오른손 법칙 적용.

## 2. Camera 좌표계 (OpenCV)

OpenCV 표준 카메라 좌표계:
- **X**: 오른쪽 (Right, 이미지에서 오른쪽)
- **Y**: 아래쪽 (Down, 이미지에서 아래쪽)
- **Z**: 전방 (Forward, 카메라가 바라보는 방향)

## 3. World → Camera 변환

카메라가 World +X 방향을 바라볼 때:

### 축 변환
| World | Camera |
|-------|--------|
| X     | Z      |
| Y     | X      |
| Z     | -Y     |

### 회전 행렬
```
R = | 0  1  0 |
    | 0  0 -1 |
    | 1  0  0 |
```

### Quaternion
```
qx = -0.5, qy = 0.5, qz = -0.5, qw = 0.5
```

### ROS2 static_transform_publisher 예시

카메라가 World 원점에서 Z 방향 0.4m 위에 위치할 때:
```bash
ros2 run tf2_ros static_transform_publisher \
    --x 0 --y 0 --z 0.4 \
    --qx -0.5 --qy 0.5 --qz -0.5 --qw 0.5 \
    --frame-id world --child-frame-id camera_link
```

## 4. Gazebo World 설정

`pallet_test.world` 기준:
- 카메라 위치: `(0, 0, 0.4)` - World 원점에서 Z 방향 0.4m 위
- 카메라 방향: World +X 방향을 바라봄 (yaw = 0)
- 팔레트 위치: `(3.0, 0, 0)` - 카메라 전방 3m

## 5. 이미지 좌표계

- **u**: 이미지 가로 (왼쪽 → 오른쪽, 0 ~ width)
- **v**: 이미지 세로 (위쪽 → 아래쪽, 0 ~ height)
- 원점: 이미지 좌상단

### Camera 좌표 → 이미지 좌표
```
u = fx * (X/Z) + cx
v = fy * (Y/Z) + cy
```
