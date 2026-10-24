from setuptools import find_packages, setup

package_name = 'my_py_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    package_data={'': ['py.typed']},
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='jaemyeonglee',
    maintainer_email='leejm010517@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
    'console_scripts': [
        'forward_kinematics = my_py_pkg.forward_kinematics:main',
        'inverse_kinematics = my_py_pkg.inverse_kinematic:main',
        'joint_command_simulator = my_py_pkg.joint_command_simulator:main',
    ],
},
)
