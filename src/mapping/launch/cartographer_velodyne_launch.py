from launch import LaunchDescription
from launch_ros.actions import Node

CONFIG_DIR = "/home/chienle/Desktop/skid_robot_v2/src/mapping/config"
RVIZ_CONFIG = "/home/chienle/Desktop/skid_robot_v2/src/mapping/config/rviz2_cartographer.rviz"

def generate_launch_description():

    cartographer = Node(
        package='cartographer_ros',
        executable='cartographer_node',
        name='cartographer_node',
        output='screen',
        arguments=[
            '-configuration_directory', CONFIG_DIR,
            '-configuration_basename', 'slam_2d.lua'
        ],
        remappings=[
            ('scan', '/scan')
        ]
    )

    occupancy_grid = Node(
        package='cartographer_ros',
        executable='cartographer_occupancy_grid_node',
        name='cartographer_occupancy_grid_node',
        output='screen'
    )

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=[
            '-d',
            RVIZ_CONFIG
        ]
    )

    return LaunchDescription([
        cartographer,
        occupancy_grid,
        rviz
    ])
