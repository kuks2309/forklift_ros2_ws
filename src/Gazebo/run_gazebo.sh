#!/bin/bash
# Run Gazebo with pallet test world

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Set model path
export GAZEBO_MODEL_PATH="$SCRIPT_DIR/models:$GAZEBO_MODEL_PATH"

# Source ROS2
source /opt/ros/humble/setup.bash

echo "Starting Gazebo with pallet test world..."
echo "Model path: $GAZEBO_MODEL_PATH"
echo ""
echo "Pallet pose: x=3.0m, y=0, z=0, yaw=0"
echo "Camera at origin, height=0.4m (RealSense), looking forward (+X)"
echo ""

# Run Gazebo
gazebo --verbose "$SCRIPT_DIR/worlds/pallet_test.world" \
    -s libgazebo_ros_init.so \
    -s libgazebo_ros_factory.so
