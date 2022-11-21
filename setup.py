from setuptools import find_packages
from setuptools import setup

package_name = 'launch_ci'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=["test", "launch"]),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch/', ['launch/launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Christoph Hellmann Santos',
    maintainer_email='christoph.hellmann.santos@ipa.fraunhofer.de',
    description='Advanced build and test tool based on launch',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
        ],
    },
)
