# Forklift Simulation Models 조사

조사 일자: 2026-01-15
업데이트: 2026-01-16

## 개요

ROS/ROS2 기반 Gazebo 및 Isaac Sim forklift 시뮬레이션 모델들을 조사하여 정리한 문서입니다.

---

## 현재 설치 현황

| 항목 | 상태 | 설치 위치 |
|------|------|----------|
| Isaac Sim (GitHub 소스 빌드) | ✅ 설치됨 | `/home/amap/isaacsim/` |
| IsaacSim-Autonomous-Forklift | ✅ 설치됨 | `/home/amap/IsaacSim-Autonomous-Forklift/` |

---

## 1. ROS2-Forklift-Simulation (삭제됨)

- **GitHub**: https://github.com/cangozpi/ROS2-Forklift-Simulation
- **ROS 버전**: ROS2 Humble
- **상태**: 삭제됨 (환경이 너무 단순함)

### 특징
- ROS2 + Gazebo 기반 forklift 시뮬레이션
- URDF 모델 포함
- Deep Reinforcement Learning을 통한 자율 주행 학습
- 팔레트 근처로 자율 네비게이션 구현

### 시스템 요구사항
- Ubuntu 22.04.3
- Python 3.10.12
- Gazebo 11.10.2
- CUDA-capable GPU (학습 시 권장)

### 주요 의존성
- PyTorch
- stable-baselines3
- gymnasium
- tensorboard

### 프로젝트 구조
```
src/
├── forklift_robot/          # URDF 모델, ROS 컨트롤러
│   ├── urdf/                # Forklift 모델 정의
│   ├── config/              # 컨트롤러 설정
│   └── launch/              # ROS launch 파일
├── ros_gazebo_plugins/      # 커스텀 충돌 감지 플러그인
└── forklift_gym_env/        # 학습 환경
    ├── config/              # YAML 설정 파일
    ├── rl/                  # DDPG, TD3, sb3 구현
    └── envs/                # Gym 환경 (ForkliftEnv)
```

### 실행 방법

```bash
# 빌드
make clean_build

# 수동 조작 (GUI + 시뮬레이션)
make manual_launch

# RL 학습
make train_DDPG      # DDPG 알고리즘
make train_sb3       # Stable-baselines3 (PPO, DDPG 등)

# TensorBoard 모니터링
make start_tensorboard
make start_tensorboard_sb3

# Gazebo 프로세스 정리
make kill_gazebo_processes
```

### 지원 RL 알고리즘
- Custom PyTorch: DDPG, TD3, DDPG+HER
- Stable-Baselines3: PPO, DDPG, TQC, HER

---

## 2. gazeboforkliftsimulation

- **GitHub**: https://github.com/valentinbarral/gazeboforkliftsimulation
- **ROS 버전**: ROS1

### 특징
- 다양한 센서가 장착된 forklift 모델
- 위치 측정 테스트용으로 설계
- launch 파일 제공
- gazebo2ros 패키지로 토픽 퍼블리시

### 실행 방법
```bash
roslaunch gtec_gazeboforkliftsimulation forklift_gazebo_simulation.launch
```

---

## 3. aeksiri/forklift

- **GitHub**: https://github.com/aeksiri/forklift
- **ROS 버전**: ROS1

### 특징
- 메타 패키지 (플러그인, 차량 모델, 월드 포함)
- Gazebo + RViz 연동
- 실제 트럭(CitiTrucks)과 시뮬레이션 모두 지원하는 인터페이스

---

## 4. smalik007/forklift_gazebo

- **GitHub**: https://github.com/smalik007/forklift_gazebo
- **ROS 버전**: ROS1

### 특징
- 기본적인 forklift Gazebo 모델
- 간단한 구조

---

## 5. IsaacSim-Autonomous-Forklift

- **GitHub**: https://github.com/iminolee/IsaacSim-Autonomous-Forklift
- **플랫폼**: Isaac Sim / Gazebo

### 특징
- NVIDIA Isaac Sim 기반 (Gazebo도 지원)
- 자율 주행 기능
- 팔레트 감지 및 도킹 기능
- 창고 환경 시뮬레이션
- 실시간 모니터링 및 상호작용

---

## 비교 요약

| 프로젝트 | ROS 버전 | RL 지원 | 센서 | 특이사항 |
|---------|---------|--------|------|---------|
| ROS2-Forklift-Simulation | ROS2 Humble | O (DDPG, PPO 등) | 기본 | 강화학습 중심 |
| gazeboforkliftsimulation | ROS1 | X | 다양함 | 위치 측정 테스트 |
| aeksiri/forklift | ROS1 | X | 기본 | 실제 트럭 연동 |
| smalik007/forklift_gazebo | ROS1 | X | 기본 | 간단한 모델 |
| IsaacSim-Autonomous-Forklift | ROS1/2 | O | 다양함 | Isaac Sim 기반 |

---

## 권장 사항

- **ROS2 사용 시**: `ROS2-Forklift-Simulation` 권장 (현재 설치됨)
- **ROS1 사용 시**: `gazeboforkliftsimulation` 또는 `smalik007/forklift_gazebo`
- **고급 시뮬레이션 필요 시**: `IsaacSim-Autonomous-Forklift`
