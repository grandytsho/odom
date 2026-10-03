#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Joy

class CustomTeleopTwistJoy(Node):
    def __init__(self):
        super().__init__('custom_teleop_twist_joy')
        
        # Publishers and Subscribers
        self.publisher_ = self.create_publisher(Twist, 'cmd_vel', 10)
        self.subscription = self.create_subscription(Joy, 'joy', self.joy_callback, 10)

        # ---- YOUR CONFIGURATION ----
        self.enable_axis = 2       # Left Trigger (LT)
        self.axis_linear_x = 1     # Left Stick Up/Down
        self.axis_linear_y = 0     # Left Stick Left/Right
        self.axis_angular_yaw = 3  # Right Stick Left/Right
        
        self.scale_linear_x = 0.09
        self.scale_linear_y = 0.09
        self.scale_angular_yaw = 0.5

        # ---- DIAGONAL BUTTON CONFIG ----
        # xpadneo button mappings: 0=A, 1=B, 2=X, 3=Y, 4=LB, 5=RB
        self.diagonal_button = 3   # Set to 'Y' button
        # --------------------------------

    def joy_callback(self, msg):
        twist = Twist()

        # xpadneo triggers rest at -1.0 and go to 1.0 when pulled. 
        # Any value > 0.0 means the trigger is being pulled (deadman active)
        deadman_active = msg.axes[self.enable_axis] > 0.0

        if not deadman_active:
            # Deadman switch not pulled: stop the robot (publish all zeros)
            self.publisher_.publish(twist)
            return

        # Check if our custom diagonal button is being held down
        if msg.buttons[self.diagonal_button] == 1:
            # Override with your custom diagonal values
            twist.linear.x = 0.5
            twist.linear.y = 0.5
            twist.linear.z = 0.0
            twist.angular.x = 0.0
            twist.angular.y = 0.0
            twist.angular.z = 0.0
        else:
            # Standard driving mode (from your YAML config)
            twist.linear.x = msg.axes[self.axis_linear_x] * self.scale_linear_x
            twist.linear.y = msg.axes[self.axis_linear_y] * self.scale_linear_y
            twist.angular.z = msg.axes[self.axis_angular_yaw] * self.scale_angular_yaw

        self.publisher_.publish(twist)

def main(args=None):
    rclpy.init(args=args)
    node = CustomTeleopTwistJoy()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()