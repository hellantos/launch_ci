
from launch_ci.actions import Package, System
from launch import LaunchDescription
from launch.actions import RegisterEventHandler, TimerAction
from launch.event_handlers import OnExecutionComplete
from launch_ci.actions.build_system import BuildSystem
from launch_ci.actions.clean_package import CleanPackage
from launch_ci.actions.clone_system import CloneSystem
from launch_ci.actions.install_system_deps import InstallSystemDeps


def generate_launch_description():
    ld = LaunchDescription()
    sys = System(
        name="TestSystem",
        workspace="/home/christoph/ws_ros2/temp/",
        packages=[
            Package(
                name="rclcpp_cascade_lifecycle",
                type="distro",
                version="galactic",
                system="TestSystem"
            ),
            Package(
                name="angles",
                type="distro",
                version="galactic",
                system="TestSystem"
            )
        ]
    )

    ls = CloneSystem(
        system_name="TestSystem",
    )

    isd = InstallSystemDeps(
        system_name="TestSystem",
    )

    cp = CleanPackage(
        system_name="TestSystem",
        package_name="angles",
    )

    bs = BuildSystem(
        system_name="TestSystem"
    )

    ld.add_action(sys)
    ld.add_action(ls)
    ld.add_action(isd)
    ld.add_action(cp)
    ld.add_action(bs)
    return ld
