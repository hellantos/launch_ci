import os
from ros2_package_assessment.actions import LoadPackage, Package
import pytest


def test_get_index():
    lp = LoadPackage(package_name="rclcpp")
    index = lp._get_index()
    assert "galactic" in index.distributions.keys()

def test_get_distro_name():
    lp = LoadPackage(package_name="rclcpp")
    distro_name = lp._get_distro_env()
    assert distro_name == "galactic"

def test_get_distro():
    lp = LoadPackage(package_name="rclcpp")
    index = lp._get_index()
    distro_name = lp._get_distro_env()
    distro = lp._get_distro(index, distro_name)

    assert distro.name == "galactic"
    assert len(distro.release_packages) > 0

def test_fetch_distro_package():
    p = Package(name="rclcpp", type="distro", version="galactic", local_path=os.path.join(os.path.dirname(__file__),"temp"))
    lp = LoadPackage(package_name="rclcpp")
    lp._fetch_from_distro()
    assert p.version == "galactic"
    

