```python
import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    GroupAction,
    IncludeLaunchDescription,
    TimerAction,
)
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    # =========================================================
    # 1. ROBOT DESCRIPTION -> ROBOT STATE PUBLISHER
    # =========================================================
    urdf_path = os.path.join(
        get_package_share_directory('simulation'),
        'urdf',
        'skid_robot_v3.urdf'
    )

    with open(urdf_path, 'r', encoding='utf-8') as f:
        robot_desc = f.read()

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_desc,
            'use_sim_time': False,
        }]
    )

    # =========================================================
    # 2. LAUNCH ARGUMENTS
    # =========================================================
    arg_velodyne = DeclareLaunchArgument(
        'velodyne',
        default_value='true',
        description='Bat/tat Velodyne VLP-16'
    )

    arg_imu = DeclareLaunchArgument(
        'imu',
        default_value='true',
        description='Bat/tat IMU Microstrain'
    )

    arg_kinematic = DeclareLaunchArgument(
        'kinematic',
        default_value='true',
        description='Bat/tat kinematic, odometry va EKF'
    )

    arg_micro_ros = DeclareLaunchArgument(
        'micro_ros',
        default_value='true',
        description='Bat/tat micro-ROS agent cho ESP32'
    )

    arg_joy = DeclareLaunchArgument(
        'joy',
        default_value='true',
        description='Bat/tat joystick'
    )

    arg_camera = DeclareLaunchArgument(
        'camera',
        default_value='true',
        description='Bat/tat camera Astra Pro RGB-D'
    )

    use_velodyne = LaunchConfiguration('velodyne')
    use_imu = LaunchConfiguration('imu')
    use_kinematic = LaunchConfiguration('kinematic')
    use_micro_ros = LaunchConfiguration('micro_ros')
    use_joy = LaunchConfiguration('joy')
    use_camera = LaunchConfiguration('camera')

    # =========================================================
    # 3. VELODYNE VLP-16
    # =========================================================
    velodyne_launch = GroupAction(
        condition=IfCondition(use_velodyne),
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    PathJoinSubstitution([
                        FindPackageShare('velodyne'),
                        'launch',
                        'velodyne-all-nodes-VLP16-launch.py'
                    ])
                )
            ),
        ]
    )

    # =========================================================
    # 4. IMU MICROSTRAIN
    # =========================================================
    imu_launch = GroupAction(
        condition=IfCondition(use_imu),
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    PathJoinSubstitution([
                        FindPackageShare('microstrain_inertial_driver'),
                        'launch',
                        'microstrain_launch.py'
                    ])
                )
            ),
        ]
    )

    # =========================================================
    # 5. ASTRA PRO RGB-D CAMERA
    #
    # Khong chay start_astra_pro_camera.sh o day.
    # Launch file nay se tu khoi dong camera va cac node relay.
    # =========================================================
    astra_launch_path = os.path.expanduser(
        '~/Desktop/skid_robot_v2/src/hardware/'
        'astra_orbbec_pro_cam/scripts/'
        'astra_pro_camera.launch.py'
    )

    astra_camera_launch = GroupAction(
        condition=IfCondition(use_camera),
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    astra_launch_path
                )
            ),
        ]
    )

    # =========================================================
    # 6. KINEMATIC
    # =========================================================
    kinematic_node = Node(
        condition=IfCondition(use_kinematic),
        package='low_control',
        executable='differential_kinematics_node',
        name='differential_kinematics_node',
        output='screen',
        parameters=[
            {'wheel_radius': 0.1},
            {'wheel_separation': 0.5},
        ]
    )

    # =========================================================
    # 7. ODOMETRY
    # =========================================================
    odom_node = Node(
        condition=IfCondition(use_kinematic),
        package='odom',
        executable='odom',
        name='odom',
        output='screen',
        parameters=[
            {'odom_topic': 'odom'},
            {'wheel_base': 0.5},
            {'wheel_radius': 0.1},
        ]
    )

    # =========================================================
    # 8. EKF
    # =========================================================
    ekf_node = TimerAction(
        period=2.0,
        actions=[
            Node(
                condition=IfCondition(use_kinematic),
                package='robot_localization',
                executable='ekf_node',
                name='ekf_filter_node',
                output='screen',
                parameters=[
                    os.path.join(
                        get_package_share_directory('ekf'),
                        'config',
                        'ekf.yaml'
                    )
                ],
            ),
        ]
    )

    # =========================================================
    # 9. MICRO-ROS AGENT
    # =========================================================
    micro_ros_launch = GroupAction(
        condition=IfCondition(use_micro_ros),
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    PathJoinSubstitution([
                        FindPackageShare('micro_ros_bringup'),
                        'launch',
                        'micro_ros.launch.py'
                    ])
                )
            ),
        ]
    )

    # =========================================================
    # 10. JOYSTICK
    # =========================================================
    joy_hw_node = Node(
        condition=IfCondition(use_joy),
        package='joy',
        executable='joy_node',
        name='joy_node',
        output='screen',
        parameters=[
            {'device_id': 0},
            {'autorepeat_rate': 20.0},
        ]
    )

    # =========================================================
    # 11. ASSEMBLE LAUNCH DESCRIPTION
    # =========================================================
    return LaunchDescription([

        # Launch arguments
        arg_velodyne,
        arg_imu,
        arg_kinematic,
        arg_micro_ros,
        arg_joy,
        arg_camera,

        # Robot TF
        robot_state_publisher,

        # LiDAR va IMU
        velodyne_launch,
        imu_launch,

        # Camera Astra Pro
        astra_camera_launch,

        # Micro-ROS
        micro_ros_launch,

        # Delay cac node dieu khien va odometry
        TimerAction(
            period=5.0,
            actions=[
                kinematic_node,
                odom_node,
                ekf_node,
                joy_hw_node,
            ]
        ),
    ])
```
