from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'micro_ros_bringup'

setup(
    name=package_name,
    version='1.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # Quan trọng: cài launch files vào share để FindPackageShare tìm được
        (os.path.join('share', package_name, 'launch'),
            glob('launch/*.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Pham Duc Duy',
    maintainer_email='lechien220205@gmail.com',
    description='Launch package for micro-ROS agent',
    license='MIT',
    entry_points={'console_scripts': []},
)
