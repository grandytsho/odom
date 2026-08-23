#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import serial

class SerialBridge(Node):
    def __init__(self):
        super().__init__('serial_bridge')
        self.port = '/dev/ttyACM0' 
        self.baud = 115200
        
        try:
            self.ser = serial.Serial(self.port, self.baud, timeout=0.1)
            self.get_logger().info(f"Connected to STM32 on {self.port} at {self.baud} baud.")
        except Exception as e:
            self.get_logger().error(f"Failed to open serial port {self.port}: {e}")
            return

        self.sub = self.create_subscription(String, 'mcu/out', self.cb_serial, 10)

    def cb_serial(self, msg: String):
        if hasattr(self, 'ser') and self.ser.is_open:
            # Append \r\n instead of just \n
            data_to_send = (msg.data + '\r\n').encode('utf-8')
            self.ser.write(data_to_send)
            self.ser.flush()  # Force OS buffer to flush immediately to hardware

def main(args=None):
    rclpy.init(args=args)
    node = SerialBridge()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()