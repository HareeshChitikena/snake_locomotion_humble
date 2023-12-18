import os
from launch.actions import ExecuteProcess, IncludeLaunchDescription, RegisterEventHandler
from ament_index_python.packages import get_package_share_directory
from ament_index_python.packages import get_package_share_path
from launch_ros.substitutions import FindPackageShare
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import Command, LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
     

    
    package_name='my_bot' 
    
    
    world_relative_path = 'worlds'
    world_filename = 'empty.world' 
    
    
    pkg_share = FindPackageShare(package='my_bot').find('my_bot')   
    
    default_rviz_config_path = os.path.join(pkg_share, 'rviz/snake.rviz')   
        

    
    
    rviz_arg = DeclareLaunchArgument(name='rvizconfig', default_value=default_rviz_config_path,
                                     description='Absolute path to rviz config file')
                                     
    
    

    
    DeclareLaunchArgument(
            'world',
            default_value=[os.path.join(
            pkg_share, world_relative_path, world_filename)],
            description='SDF world file')
                                      

    rsp = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory(package_name),'launch','rsp.launch.py'
                )]), launch_arguments={'use_sim_time': 'true'}.items()
       ) 
       
     

    gazebo = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py')]),
             )


    spawn_entity = Node(package='gazebo_ros', executable='spawn_entity.py',
                        arguments=['-topic', 'robot_description',
                                   '-entity', 'snake_robot'],
                        output='screen')
    
    
    
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', LaunchConfiguration('rvizconfig')],
     )
    
    
    joint_broad_spawner = Node(
    package="controller_manager",
    executable="spawner",
    arguments=["joint_state_broadcaster"],
     )
     
     
    effort_spawner = Node(
    package="controller_manager",
    executable="spawner",
    arguments=["effort_controllers"],
     )     
     
 
         

    # Launch them all!
    return LaunchDescription([
        rviz_arg,    
        rsp,
        gazebo,
        spawn_entity,
        rviz_node,
        joint_broad_spawner,
        effort_spawner
       

        
              ])
