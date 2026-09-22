from glob import glob
from setuptools import find_packages, setup

package_name = 'testbed_devices'
setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),

    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Testbed Maintainer',
    maintainer_email='maintainer@example.invalid',
    description='Adapter testbed starter package',
    license='UNLICENSED',
    entry_points={'console_scripts': ['amr_node = testbed_devices.amr.node:main']},
)
