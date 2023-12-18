# Snake_locomotion_humble
This code is set for ROS2 humble.

The files are properly configured to run snake robot locomotion control.

snake_robo consists of different folders with the package name my_bot.

You need to clone snake_robo and colcon build to identify the package.

Then Run following commands:

ros2 launch my_bot launch_sim.launch.py 

ros2 run my_bot publisher_node.py
