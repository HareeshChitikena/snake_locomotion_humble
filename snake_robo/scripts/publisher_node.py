#!/usr/bin/env python3
import rclpy 
from rclpy.node import Node
from builtin_interfaces.msg import Duration
from std_msgs.msg import Float64MultiArray, String, Float64 
from sensor_msgs.msg import JointState
import math, os, sys
import numpy as np
from datetime import datetime

FeedBack = np.empty(9,dtype=float)  
Vel_FeedBack = np.empty(9,dtype=float)
set_point = np.empty(9,dtype=float)  
U_Value = np.empty(9,dtype=float)
Velocity = np.empty(9,dtype=float)
Acceleration = np.empty(9,dtype=float)

class 	EffortPublisher(Node): 
    def __init__(self):                                     
        super().__init__('effort_Pub')                       
                                                            
        self.get_logger().set_level(rclpy.logging.LoggingSeverity.DEBUG)
        timer_period = 0.1
        self.shutdownnodeafter = 200 # in seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.shutdownnode = self.create_timer(self.shutdownnodeafter, self.shutdown_callback)
        self.Effort_publisher = self.create_publisher(Float64MultiArray,"/effort_controllers/commands", 10)
        self.subscription = self.create_subscription(JointState, 'joint_states', self.PID_callback, 10)
        self.params       = self.create_subscription(String, 'snake_robot_params', self.paramters_from_ui, 10)
        self.dir_path       = os.path.expanduser('~/dev_ws/snake_robo/scripts/logs/')
        self.error_data = Float64()
        self.subscription
        self.timer_timer = 0 
        self.default_kd = 0.8
        self.default_kp = 1#0.42 
        self.default_a = 65
        self.default_w = 0.45
        self.default_d = 0.78
        self.default_phi0 = 0
        self.default_phi1 = 0
        self.k_d = self.default_kd
        self.k_p = self.default_kp 
        self.var_a = self.default_a
        self.var_w = self.default_w
        self.var_d = self.default_d
        self.var_phi0 = self.default_phi0
        self.var_phi1 = self.default_phi1
        self.write_title = True
        self.filename = self.dir_path + 'poseinformation' + datetime.now().strftime("%d_%m_%Y_%H_%M_%S")

    def paramters_from_ui(self, params):
        param_string = params.data.split(',')
        self.get_logger().debug(f'variable {param_string[0]} value {param_string[1]}')
        self.k_d = float(param_string[1]) if param_string[0] == 'k_d' else self.k_d # Update K_d
        self.k_p = float(param_string[1]) if param_string[0] == 'k_p' else self.k_p  # Update K_p
        self.var_a = float(param_string[1]) if param_string[0] == 'a' else self.var_a # Update a
        self.var_w = float(param_string[1]) if param_string[0] == 'w' else self.var_w # Update w
        self.var_d = float(param_string[1]) if param_string[0] == 'd' else self.var_d # Update d
        self.var_phi0 = float(param_string[1]) if param_string[0] == 'phi0' else self.var_phi0 # Update phi0
        self.var_phi1 = float(param_string[1]) if param_string[0] == 'phi1' else self.var_phi1 # Update phi1

    def PID_callback(self, msg): 
        feedback_temp = np.empty(9,dtype=float)
        velocity_temp = np.empty(9,dtype=float)   
        for i in range(0,9):
            feedback_temp[i] = msg.position[i]  
            velocity_temp[i] = msg.velocity[i]
            
            FeedBack[i] = feedback_temp[i]
            Vel_FeedBack[i] = velocity_temp[i]

    def phi_angle_generator_at_t(self, timer):
        N = 10
        a = self.var_a                            # Alpha value of the equation
        w = self.var_w                   # Freq_w of the equation of the angle
        d = self.var_d                       # Delta, which is the value of the phase shift in the equation of the angle 0.698132 
        phi0 = self.var_phi0                 # Offset angle in positive dir
        phi1 = self.var_phi1                 # Offset angle in negative dir
        temp_JA = np.empty(9,dtype=float)
        temp_JA_d = np.empty(9,dtype=float)
        temp_JA_dd = np.empty(9,dtype=float)
        temp_huge_arr = np.array([])
        for i in range(0,N - 1):
            temp_JA[i] = ( a * np.sin(w * timer + i * d) + phi0 - phi1)
            temp_JA_d[i] = ( a * w * np.cos(w * timer + i * d))
            temp_JA_dd[i] = ( -1 * a * w ** 2 * np.sin(w * timer + i * d))
        temp_huge_arr= np.array([ temp_JA, temp_JA_d, temp_JA_dd])   
        return temp_huge_arr

    def timer_callback(self):
        global U_Value 
        set_point, Velocity , Acceleration  = self.phi_angle_generator_at_t(self.timer_timer)
        for i in range(0,9):
            U_Value[i] = 1*((Acceleration[i] + self.k_d * ( set_point[i] - FeedBack[i] ) + self.k_p * (Velocity[i] - Vel_FeedBack[i])))
            self.error_data.data = (set_point[i])#*(3.14/180) 
            self.create_publisher(Float64, 'position'+str(i), 10).publish(self.error_data)

            self.error_data.data =(FeedBack[i])*(180/3.14)
            self.create_publisher(Float64, 'position_feedback_'+str(i), 10).publish(self.error_data)

            #self.error_data.data = (set_point[i] - FeedBack[i]*(180/3.14))
            #self.create_publisher(Float64, 'position_error_'+str(i), 10).publish(self.error_data)



            self.error_data.data = Velocity[i] 
            self.create_publisher(Float64, 'velocity'+str(i), 10).publish(self.error_data)

            #self.error_data.data = Velocity[i] - Vel_FeedBack[i]
            #self.create_publisher(Float64, 'velocity_error_'+str(i), 10).publish(self.error_data)
            self.error_data.data = Vel_FeedBack[i]
            self.create_publisher(Float64, 'velocity_feedback_'+str(i), 10).publish(self.error_data)
           # self.error_data.data = Acceleration[i]
            #self.create_publisher(Float64, 'Acceleration'+str(i), 10).publish(self.error_data)
            with open(self.filename + '_j_' + str(i) + '.txt', 'a') as file:
                if self.write_title:
                    file.write(f'Time,Acceleration,PositionSetpoint,PositionSetpointError,VelocitySetpoint,VelocitySetpointError\n')
                    self.write_title = False
                file.write(f'{self.timer_timer},{Acceleration[i]},{set_point[i]},{set_point[i] - FeedBack[i]},{Velocity[i]},{Velocity[i] - Vel_FeedBack[i]}\n')
        # creating an array of values to be sent to the joints
        
        value1 = U_Value[0] 
        value2 = U_Value[1] 
        value3 = U_Value[2] 
        value4 = U_Value[3]
        value5 = U_Value[4]
        value6 = U_Value[5]
        value7 = U_Value[6]
        value8 = U_Value[7]
        value9 = U_Value[8]

        msg = Float64MultiArray()
        msg.data = [value1,value2,value3,value4,value5,value6,value7,value8,value9]
        self.Effort_publisher.publish(msg)
        print(set_point)
        self.timer_timer = self.timer_timer + 1
        if self.timer_timer >10000: 
            self.timer_timer = 0
            
    def shutdown_callback(self):
        #stop the node
        pass
        self.get_logger().info('Shutting down...')
        self.destroy_node()
        sys.exit()
            

def main(args=None):
     
    rclpy.init(args=args)
    effort_Pub = EffortPublisher()
    rclpy.spin(effort_Pub)
    effort_Pub.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
