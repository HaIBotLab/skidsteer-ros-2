import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    # 1. Khai báo các đường dẫn
    pkg_name = 'simulation' # <--- Hãy chắc chắn tên package đúng (v1, v2 hay v3)
    bringup_dir = get_package_share_directory(pkg_name)
    
    urdf_file_name = 'skid_robot_v3.urdf' 
    urdf_path = os.path.join(bringup_dir, 'urdf', urdf_file_name)
    
    # Đường dẫn file World (Nếu muốn mở world có sẵn)
    world_path = os.path.join(bringup_dir, 'world', 'depot.sdf')

    # 2. Cấu hình biến môi trường để Gazebo tìm thấy model
    # (Quan trọng để load mesh STL)
    install_dir = get_package_share_directory(pkg_name).split('/share')[0]
    gazebo_model_path = SetEnvironmentVariable(
        name='GAZEBO_MODEL_PATH',
        value=[os.path.join(install_dir, 'share'), 
               ':', os.environ.get('GAZEBO_MODEL_PATH', '')]
    )

    # 3. Khởi chạy Gazebo Classic Server (gzserver)
    # Load world trống hoặc world depot của bạn
    gzserver = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={
            #'world': world_path,  # Hoặc bỏ dòng này để load empty world
            'verbose': 'true',
            'pause': 'false'
        }.items()
    )

    # 4. Robot State Publisher (Đọc URDF)
    # Đọc file và xử lý chuỗi
    with open(urdf_path, 'r') as infp:
        robot_desc = infp.read()

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='both',
        parameters=[{
            'use_sim_time': True,
            'robot_description': robot_desc
        }]
    )

    # 5. Spawn Entity (Đưa robot vào Gazebo Classic)
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-topic', 'robot_description',
            '-entity', 'my_robot',
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.5' # Thả cao một chút để không kẹt đất
        ],
        output='screen'
    )

    # 6. Joint State Publisher (Tùy chọn)
    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        parameters=[{'use_sim_time': True}],
        output='screen'
    )
    
    # 7. TF Static (Map -> Odom)
    #tf_map = Node(
    #   package='tf2_ros',
    #    executable='static_transform_publisher',
    #    arguments=['0', '0', '0', '0', '0', '0', 'map', 'odom']
    #)

    return LaunchDescription([
        gazebo_model_path,
        gzserver,
        robot_state_publisher,
        spawn_entity,
        joint_state_publisher,
        #tf_map
    ])
