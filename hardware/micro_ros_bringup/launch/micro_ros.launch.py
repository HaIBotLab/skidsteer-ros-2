from launch import LaunchDescription
from launch.actions import ExecuteProcess


def generate_launch_description():
    """
    Launch micro-ROS agent kết nối ESP32 qua serial.
    Dùng đường dẫn tuyệt đối + set ROS_DOMAIN_ID=30
    để khớp với domain của ROS 2 workspace.

    Port : /dev/ttyUSB0
    Baud : 115200
    """

    micro_ros_agent = ExecuteProcess(
        cmd=[
            '/home/chienle/Desktop/micro_ros_ws/install/micro_ros_agent'
            '/lib/micro_ros_agent/micro_ros_agent',
            'serial',
            '-D', '/dev/ttyUSB0',
            '-b', '115200',
        ],
        #additional_env={'ROS_DOMAIN_ID': '30'},
        output='screen'
    )

    return LaunchDescription([
        micro_ros_agent,
    ])
