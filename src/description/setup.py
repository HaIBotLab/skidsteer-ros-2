import os
from glob import glob
from setuptools import setup

package_name = 'simulation'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        
        # --- THÊM 3 DÒNG NÀY VÀO ĐỂ COPY FILE URDF, MESHES VÀ LAUNCH ---
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*.urdf')),
        (os.path.join('share', package_name, 'meshes/visual'), glob('meshes/visual/*.STL')),
        # --------------------------------------------------------------
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='weed',
    maintainer_email='weed@todo.todo',
    description='Skidsteer Robot Simulation Package',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            # Sau này bạn viết code Python điều khiển AI thì khai báo vào đây
        ],
    },
)
