#!/usr/bin/env python3
"""
Gazebo launch file for pallet pose estimation testing
"""

import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess, DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    # Paths
    gazebo_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    world_file = os.path.join(gazebo_dir, 'worlds', 'pallet_test.world')
    models_dir = os.path.join(gazebo_dir, 'models')

    # Set GAZEBO_MODEL_PATH
    gazebo_model_path = os.environ.get('GAZEBO_MODEL_PATH', '')
    if gazebo_model_path:
        gazebo_model_path = models_dir + ':' + gazebo_model_path
    else:
        gazebo_model_path = models_dir

    return LaunchDescription([
        # Launch Gazebo with world file
        ExecuteProcess(
            cmd=['gazebo', '--verbose', world_file,
                 '-s', 'libgazebo_ros_init.so',
                 '-s', 'libgazebo_ros_factory.so'],
            output='screen',
            additional_env={'GAZEBO_MODEL_PATH': gazebo_model_path}
        ),
    ])
