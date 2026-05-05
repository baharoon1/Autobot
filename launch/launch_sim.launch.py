import os
import xacro

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory('autobot')
    ros_gz_share = get_package_share_directory('ros_gz_sim')

    xacro_file = os.path.join(pkg_share, 'description', 'robot.urdf.xacro')
    robot_description_xml = xacro.process_file(xacro_file).toxml()

    rsp = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[
            {'robot_description': robot_description_xml},
            {'use_sim_time': True}
        ]
    )

    world_file = os.path.join(pkg_share, 'worlds', 'empty_with_sensors.sdf')
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros_gz_share, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': f'{world_file} -r'}.items()
    )

    spawn = TimerAction(
        period=5.0,
        actions=[
            Node(
                package='ros_gz_sim',
                executable='create',
                arguments=[
                    '-world', 'empty',
                    '-string', robot_description_xml,
                    '-name', 'my_bot',
                    '-z', '0.1'
                ],
                output='screen'
            )
        ]
    )

    joint_state_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model',
        ],
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    tf_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/tf@tf2_msgs/msg/TFMessage@gz.msgs.Pose_V',
        ],
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    odom_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/odom@nav_msgs/msg/Odometry@gz.msgs.Odometry',
        ],
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    cmd_vel_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
        ],
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    lidar_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
        ],
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    static_lidar_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        arguments=[
            '--x', '0.1',
            '--y', '0',
            '--z', '0.175',
            '--roll', '0',
            '--pitch', '0',
            '--yaw', '0',
            '--frame-id', 'chassis',
            '--child-frame-id', 'my_bot/base_link/laser'
        ],
        output='screen'
    )

    image_bridge = Node(
        package="ros_gz_image",
        executable='image_bridge',
        arguments=[
            '/camera/image_raw'
        ],
        

    )

    camera_bridge = Node(
        package= 'ros_gz_bridge',
        executable='parameter_bridge',
        arguments= [
            '/camera/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo'
        ],
        
    )

    return LaunchDescription([
        rsp,
        gazebo,
        spawn,
        joint_state_bridge,
        tf_bridge,
        odom_bridge,
        cmd_vel_bridge,
        lidar_bridge,
        static_lidar_tf,
        image_bridge,
        camera_bridge

    ])