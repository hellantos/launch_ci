from ros2_package_assessment.actions import Package, LoadPackage
from launch import LaunchDescription
from launch.actions import RegisterEventHandler
from launch.event_handlers import OnExecutionComplete


def generate_launch_description():
    ld = LaunchDescription()
    pkg = Package(
        name="rclcpp_cascade_lifecycle",
        type="distro",
        version="galactic",
        local_path="/home/christoph/ws_ros2/temp/",
        )
    lp = LoadPackage(package_name="rclcpp_cascade_lifecycle")

    event_handler = OnExecutionComplete(
        target_action=pkg,
        on_completion=lp
    )

    reg_vent = RegisterEventHandler(event_handler=event_handler)

    
    ld.add_action(pkg)
    ld.add_action(lp)
    return ld