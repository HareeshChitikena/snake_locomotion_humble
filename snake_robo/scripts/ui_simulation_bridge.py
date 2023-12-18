#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import paho.mqtt.client as mqtt
import time
import socket

class ParamsPublisher(Node):
 
    def __init__(self):
        # Initialize Variables
        super().__init__('ui_simulation_bridge')
        self.params_publisher_pub           = self.create_publisher(String, 'snake_robot_params', 10)
        socket_port                         = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        soc_connection                      = socket_port.connect(("8.8.8.8", 80))
        self.ip_address                     = socket_port.getsockname()[0]
        self.mqtt_address                   = self.ip_address
        self.mqtt_user                      = 'snake'
        self.mqtt_passowrd                  = 'classic'
        self.params_data                    = String()


    def on_message(self, client, user_data, msg): 
 
        msg_string = str(msg.payload.decode())
        self.params_data.data = msg_string
        self.params_publisher_pub.publish(self.params_data)
        print(msg_string)
  

    def mosquitto_receiver(self):

        mqtt_client = mqtt.Client()
        mqtt_client.username_pw_set(self.mqtt_user, self.mqtt_passowrd)
        mqtt_client.connect(self.mqtt_address, 1883)
        mqtt_client.message_callback_add('snake_robot_params', self.on_message)
        mqtt_client.subscribe('snake_robot_params')
        mqtt_client.loop_start()
        time.sleep(0.5)
        mqtt_client.loop_stop()
    
    


def main(args=None):

    rclpy.init(args=args)

    run_instant = ParamsPublisher()
    while rclpy.ok():
        run_instant.mosquitto_receiver()
        rclpy.spin_once(run_instant, timeout_sec=0.05)

    run_instant.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
