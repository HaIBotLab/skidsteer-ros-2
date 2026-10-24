#!/usr/bin/env python3

import os

from launch import LaunchDescription
from launch.actions import ExecuteProcess, LogInfo, TimerAction
from launch.substitutions import EnvironmentVariable


def generate_launch_description():
    # Thu muc chua cac script Python cua camera
    script_dir = os.path.dirname(os.path.abspath(__file__))

    depth_relay_script = os.path.join(
        script_dir,
        'depth_relay.py'
    )

    # ---------------------------------------------------------
    # 1. Khoi dong driver Astra Pro
    # ---------------------------------------------------------
    camera_driver = ExecuteProcess(
        cmd=[
            'ros2', 'component', 'standalone',
            'astra_camera',
            'astra_camera::OBCameraNodeFactory',
            '-n', 'camera',
            '--node-namespace', '/camera',

            # RGB
            '-p', 'color_width:=640',
            '-p', 'color_height:=480',
            '-p', 'color_fps:=30',
            '-p', 'enable_color:=true',

            # IR: khong su dung
            '-p', 'ir_width:=640',
            '-p', 'ir_height:=480',
            '-p', 'ir_fps:=30',
            '-p', 'enable_ir:=false',

            # Depth
            '-p', 'depth_width:=640',
            '-p', 'depth_height:=480',
            '-p', 'depth_fps:=30',
            '-p', 'enable_depth:=true',
            '-p', 'depth_align:=true',
            '-p', 'depth_scale:=1',

            # Chon camera RGB/UVC
            '-p', 'uvc_camera.enable:=true',
            '-p', 'uvc_camera.vid:=0x2bc5',
            '-p', 'uvc_camera.pid:=0x0501',
            '-p', 'uvc_camera.format:=mjpeg',

            # TF
            '-p', 'publish_tf:=true',
            '-p', 'tf_publish_rate:=10.0',

            # Ket noi lai khi camera mat ket noi
            '-p', 'reconnect_timeout:=6.0',

            # So luong thiet bi
            '-p', 'number_of_devices:=1',
            '-p', 'serial_number:=',
        ],
        output='screen',
        emulate_tty=True,
    )

    # ---------------------------------------------------------
    # 2. Relay Depth image va CameraInfo de xu ly QoS
    # ---------------------------------------------------------
    depth_relay = ExecuteProcess(
        cmd=[
            '/usr/bin/python3',
            depth_relay_script,
        ],
        output='screen',
        emulate_tty=True,
    )

    # ---------------------------------------------------------
    # 3. Tao point cloud tu Depth image
    # Chay sau 2 giay de driver camera co thoi gian khoi dong
    # ---------------------------------------------------------
    point_cloud = ExecuteProcess(
        cmd=[
            'ros2', 'run',
            'depth_image_proc',
            'point_cloud_xyz_node',
            '--ros-args',

            '-r', 'image_rect:=/camera/depth/image_raw_relay',
            '-r', 'camera_info:=/camera/depth/camera_info_relay',
            '-r', 'points:=/camera/depth/points',
        ],
        output='screen',
        emulate_tty=True,
    )

    return LaunchDescription([
        LogInfo(
            msg='Dang khoi dong camera Astra Pro bang ROS 2 Launch...'
        ),

        # Khoi dong driver camera
        camera_driver,

        # Khoi dong relay
        depth_relay,

        # Cho driver khoi dong roi tao point cloud
        TimerAction(
            period=2.0,
            actions=[
                point_cloud,
            ],
        ),

        LogInfo(
            msg=(
                'RGB: /camera/color/image_raw | '
                'Depth: /camera/depth/image_raw | '
                'Point cloud: /camera/depth/points'
            )
        ),
    ])
