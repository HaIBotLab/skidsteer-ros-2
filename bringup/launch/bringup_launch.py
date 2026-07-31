import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource  
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.actions import TimerAction

def generate_launch_description():
    
    return LaunchDescription([
        IncludeLaunchDescription(
            FindPackageShare('low_control').find('low_control') + '/launch/low_level_control.launch.xml'
        ),
        IncludeLaunchDescription(
            FindPackageShare('microstrain_inertial_driver').find('microstrain_inertial_driver') + '/launch/microstrain_launch.py'
        ),
        IncludeLaunchDescription(
            FindPackageShare('velodyne').find('velodyne') + '/launch/velodyne-all-nodes-VLP16-launch.py'
        ),
        Node(
            package='odom',
            executable='odom',
            name='odom',
            parameters=[		
                {'left_wheel_topic': 'wheel_data_left'},
                {'right_wheel_topic': 'wheel_data_right'},
                {'odom_topic': 'odom'},
                {'wheel_base': 0.5},
                {'wheel_radius': 0.1}
            ]
        ),
        TimerAction(
            period=2.0,        #delay   
            actions=[
                Node(	
                    package='robot_localization',
                    executable='ekf_node',
                    name='ekf_filter_node',
                    output='screen',
                    parameters=[os.path.join(get_package_share_directory('ekf'), 'config', 'ekf.yaml')],
                ),
            ]
        ),
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='base_footprint_to_base_link',
            arguments=['0', '0', '0.15', '0', '0', '0', 'base_footprint', 'base_link']
        ),
         Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='base_link_to_velodyne_link',
            arguments=['0.1', '0', '0.48', '0', '0', '0', 'base_link', 'velodyne']
        ),
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='base_link_to_imu_link',
            arguments=['0', '0', '0.', '0', '0', '0', 'base_link', 'imu_link']
        ),
    ])
