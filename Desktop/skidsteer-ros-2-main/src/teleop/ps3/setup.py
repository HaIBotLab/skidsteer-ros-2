from setuptools import find_packages, setup

package_name = 'ps3'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/ps3.launch.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ttminh',
    maintainer_email='trantuanminh14022003@gmail.com',
    description='TODO: Package description',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
    	'console_scripts': [
            	'ps3_teleop_node = ps3.ps3:main',
        ],
    },
)
