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

    # ─────────────────────────────────────────────
    # Arguments
    # ─────────────────────────────────────────────
    arg_velodyne = DeclareLaunchArgument(
        'velodyne', default_value='true',
        description='Khởi động Velodyne VLP-16 (true/false)'
    )
    arg_imu = DeclareLaunchArgument(
        'imu', default_value='true',
        description='Khởi động IMU Microstrain /dev/ttyACM0 (true/false)'
    )
    arg_kinematic = DeclareLaunchArgument(
        'kinematic', default_value='true',
        description='Khởi động kinematic + odom + EKF + TF (true/false)'
    )
    arg_micro_ros = DeclareLaunchArgument(
        'micro_ros', default_value='true',
        description='Khởi động micro-ROS agent ESP32 /dev/ttyUSB0 (true/false)'
    )
    arg_joy = DeclareLaunchArgument(
        'joy', default_value='true',
        description='Khởi động joy_node + ps3 teleop (true/false)'
    )

    use_velodyne  = LaunchConfiguration('velodyne')
    use_imu       = LaunchConfiguration('imu')
    use_kinematic = LaunchConfiguration('kinematic')
    use_micro_ros = LaunchConfiguration('micro_ros')
    use_joy       = LaunchConfiguration('joy')

    # ─────────────────────────────────────────────
    # 1. VELODYNE VLP-16
    # ─────────────────────────────────────────────
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

    # ─────────────────────────────────────────────
    # 2. IMU – Microstrain (/dev/ttyACM0)
    # ─────────────────────────────────────────────
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

    # ─────────────────────────────────────────────
    # 3. KINEMATIC + ODOM + EKF + TF
    #
    #  Luồng AUTO:
    #    /cmd_vel
    #      → differential_kinematics_node → /wheel_rpm [rpm_left, -rpm_right]
    #      → micro-ROS agent → ESP32
    #      → Modbus RS485/MAX485 → ZLAC8015D × 2 → 4 bánh
    #
    #  Luồng feedback encoder:
    #    ESP32 → /zlac_encoder [fb_rpm_left, fb_rpm_right]
    #      → odom node → /odom
    #      → EKF (+ /imu/data) → /odometry/filtered
    #
    #  zlac8015D_pub ĐÃ BỎ: ESP32 đảm nhận toàn bộ Modbus
    # ─────────────────────────────────────────────

    kinematic_node = Node(
        condition=IfCondition(use_kinematic),
        package='low_control',
        executable='differential_kinematics_node',
        name='differential_kinematics_node',
        output='screen',
        parameters=[
            {'wheel_radius':     0.1},
            {'wheel_separation': 0.5},
        ]
    )

    odom_node = Node(
        condition=IfCondition(use_kinematic),
        package='odom',
        executable='odom',
        name='odom',
        output='screen',
        parameters=[
            {'odom_topic':   'odom'},
            {'wheel_base':   0.5},
            {'wheel_radius': 0.1},
        ]
    )

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
                        'config', 'ekf.yaml'
                    )
                ],
            ),
        ]
    )

    tf_footprint_to_base = Node(
        condition=IfCondition(use_kinematic),
        package='tf2_ros',
        executable='static_transform_publisher',
        name='base_footprint_to_base_link',
        arguments=['0', '0', '0.15', '0', '0', '0', 'base_footprint', 'base_link']
    )
    tf_base_to_velodyne = Node(
        condition=IfCondition(use_kinematic),
        package='tf2_ros',
        executable='static_transform_publisher',
        name='base_link_to_velodyne_link',
        arguments=['0.1', '0', '0.48', '0', '0', '0', 'base_link', 'velodyne']
    )
    tf_base_to_imu = Node(
        condition=IfCondition(use_kinematic),
        package='tf2_ros',
        executable='static_transform_publisher',
        name='base_link_to_imu_link',
        arguments=['0', '0', '0', '0', '0', '0', 'base_link', 'imu_link']
    )

    # ─────────────────────────────────────────────
    # 4. MICRO-ROS AGENT
    #    Include từ pkg micro_ros_bringup
    #    (src/hardware/micro_ros_bringup/launch/micro_ros.launch.py)
    #
    #    Port : /dev/ttyUSB0 → ESP32
    #    Baud : 115200
    #    ESP32 tự lo Modbus RS485 → ZLAC8015D
    # ─────────────────────────────────────────────
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

    # ─────────────────────────────────────────────
    # 5. JOY
    #    joy_node : đọc phần cứng MC6C/PS3 → /joy
    #    ps3      : /joy → /cmd_vel
    #
    #    AUTO thuần  : joy:=false  (nav2 làm chủ /cmd_vel)
    #    Override tay: joy:=true   (mặc định)
    # ─────────────────────────────────────────────
    joy_hw_node = Node(
        condition=IfCondition(use_joy),
        package='joy',
        executable='joy_node',
        name='joy_node',
        output='screen',
        parameters=[
            {'device_id':       0},
            {'autorepeat_rate': 20.0},
        ]
    )
	# run ps3 at new terminal
    #ps3_node = Node(
       # condition=IfCondition(use_joy),
        #package='ps3',
        #executable='ps3_teleop_node',
        #name='ps3_teleop_node',
        #output='screen',
    #)

# ─────────────────────────────────────────────
    # Assemble
    # ─────────────────────────────────────────────
    return LaunchDescription([
        # Arguments
        arg_velodyne,
        arg_imu,
        arg_kinematic,
        arg_micro_ros,
        arg_joy,

        # 1. Velodyne & IMU (Chạy độc lập)
        velodyne_launch,
        imu_launch,
        
        tf_footprint_to_base,
        tf_base_to_velodyne,
        tf_base_to_imu,


        # 2. micro-ROS (Khởi chạy đầu tiên để nắm giữ cổng USB và kết nối ZLAC)
        micro_ros_launch,
        
        # 3. Các node khác khởi chạy trễ hơn 5s sau khi micro-ROS đã ổn định
        TimerAction(
            period=5.0, 
            actions=[
                kinematic_node,
                odom_node,
                ekf_node,
                joy_hw_node,
                #ps3_node,
            ]
        ),
    ])
