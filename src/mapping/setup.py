from setuptools import find_packages, setup

package_name = 'mapping'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/cartographer_velodyne_launch.py']),
    ],
    install_requires=['setuptools',
    		      'cartographer_ros',
    		      'rviz2',
    		      'sensor_msgs',
    		      'geometry_msgs',
    		      'tf2_ros',],
    zip_safe=True,
    maintainer='binh',
    maintainer_email='binh85980344@gmail.com',
    description='TODO: Package description',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
          
        ],
    },
)
