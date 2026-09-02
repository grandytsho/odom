#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import String
import json
import time

class CmdvelToMcu(Node):
    def __init__(self):
        super().__init__('cmdvel_to_mcu')
        self.declare_parameter('wheel_L', 0.265)#half the length of base #305
        self.declare_parameter('wheel_W', 0.2555)#half the width of base #2175
        self.declare_parameter('min_pwm_threshold_normal', 16)
        self.declare_parameter('min_pwm_threshold_strafe', 16)
        self.declare_parameter('max_pwm', 19)        
        self.declare_parameter('idle_timeout', 0.05)
        self.declare_parameter('cmd_vel_in_topic', 'cmd_vel_out')
        self.declare_parameter('mcu_out_topic', 'mcu/out')
        self.declare_parameter('brake_duration', 0.30)     #in seconds
        self.declare_parameter('brake_pwm', 20)           # Standard brake PWM
        self.declare_parameter('brake_pwm_rotation', 13)  # Smaller brake PWM for point turns
        self.L = float(self.get_parameter('wheel_L').get_parameter_value().double_value)
        self.W = float(self.get_parameter('wheel_W').get_parameter_value().double_value)
        self.max_pwm = int(self.get_parameter('max_pwm').get_parameter_value().integer_value)
        self.min_normal = int(self.get_parameter('min_pwm_threshold_normal').get_parameter_value().integer_value)
        self.min_strafe = int(self.get_parameter('min_pwm_threshold_strafe').get_parameter_value().integer_value)
        self.brake_duration = float(self.get_parameter('brake_duration').get_parameter_value().double_value)
        self.brake_pwm = int(self.get_parameter('brake_pwm').get_parameter_value().integer_value)
        self.brake_pwm_rotation = int(self.get_parameter('brake_pwm_rotation').get_parameter_value().integer_value)

        cmd_topic = self.get_parameter('cmd_vel_in_topic').get_parameter_value().string_value
        mcu_out_topic = self.get_parameter('mcu_out_topic').get_parameter_value().string_value

        self.pub_mcu_out = self.create_publisher(String, mcu_out_topic, 10)
        self.sub_cmd = self.create_subscription(Twist, cmd_topic, self.cb_cmdvel, 20)

    def send_pwm(self, pwms):  
        msg = {
            "pwm1": int(pwms[0]),
            "pwm2": int(pwms[1]),
            "pwm3": int(pwms[2]),
            "pwm4": int(pwms[3])
        }
        out = String()
        out.data = json.dumps(msg)
        self.pub_mcu_out.publish(out)

    def cb_cmdvel(self, msg: Twist):
        self.last_cmd_time = time.time() 
        vx=raw_vx = float(msg.linear.x)
        vy=raw_vy = float(msg.linear.y)
        geom=self.L+self.W
        wz = -float(msg.angular.z)
        target_speeds_ms = [
                    vx - vy - wz * geom,
                    vx + vy + wz * geom,
                    vx + vy - wz * geom,
                    vx - vy + wz * geom
            ]
        target_pwms = []  
        is_moving_command = False  
        NAV2_MAX_SPEED_MS = 0.09 
    

        for speed_ms in target_speeds_ms:
            abs_speed = abs(speed_ms)
            if abs_speed < 0.01: 
                target_pwms.append(0)
                continue
            if abs_speed < 0.02: abs_speed = 0.02

            speed_ratio = (abs_speed - 0.02) / (NAV2_MAX_SPEED_MS - 0.02)#linear scale
            speed_ratio = max(0.0, min(1.0, speed_ratio)) #clipping the speed


            pwm_range = self.max_pwm - self.min_normal
            pwm_mag = self.min_normal + (speed_ratio * pwm_range)

            final_pwm = int(pwm_mag) if speed_ms > 0 else -int(pwm_mag) #sign also. f the original speed_ms was positive, keep the PWM positive; if it was negative, make the PWM negative too
            target_pwms.append(final_pwm)   


        if is_moving_command:
            # turn detection goes here

            # Cancel braking if we get a new move command
            if self.is_braking:
                self.is_braking = False

            self.current_pwms = [ #mapping
                -target_pwms[1], 
                target_pwms[2],
                target_pwms[0],
                -target_pwms[3]
            ]
            self.send_pwm(self.current_pwms)     
       


def main(args=None):
    rclpy.init(args=args)
    node = CmdvelToMcu()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.send_pwm([0,0,0,0])
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
        
        
    
