import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    pkg_name = 'dead'
    urdf_file = 'robot.urdf'

    urdf_path = os.path.join(
        get_package_share_directory(pkg_name),
        'urdf',
        urdf_file
    )

    config_path = os.path.join(
            get_package_share_directory(pkg_name),
            'config',
            'ekf.yaml'
        )

    with open(urdf_path, 'r') as infp:
        robot_desc = infp.read()

    rsp_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_desc}]
    )
    brain_node=Node(
            package='dead',
            executable='Otransform',
            name='brain',
            output='screen'
        )
    
    data_node=Node(
            package='dead',
            executable='data',
            name='data',
            output='screen'
        )
    
    jsp_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher'
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen'
    )

    ekf_node = Node(
            package='robot_localization',
            executable='ekf_node',
            name='ekf',
            output='screen', 
            parameters=[config_path]
        )
    
    openloop_controller = Node(
    package = 'dead', 
    executable='open_loop',
    name='open_loop1',
    output='screen',
    )

    open_loop=Node(
    package = 'motor',
    executable='open_loop',
    name='open_loop1',
    output='screen',
    )
    static_tf_node = Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            arguments=['0.0000', '0.0000', '0.0000', '0.0000', '0.0000', '0.0000', 'base_link', 'imu_link']
        )

    return LaunchDescription([
        rsp_node,
        brain_node,
        jsp_node,
        rviz_node,
        data_node,
        ekf_node,
        static_tf_node,
        # openloop_controller,
        # open_loop,
    ])
