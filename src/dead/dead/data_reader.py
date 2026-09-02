import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray
import serial
import json  
from std_msgs.msg import String
class SerialBridge(Node):
    def __init__(self):
        super().__init__('serial_bridge')
        self.publisher_ = self.create_publisher(Float64MultiArray, 'wheel_tick', 10)
        
        self.serial_port = '/dev/ttyACM0' 
        self.baud_rate = 115200
        
        try:
            self.ser = serial.Serial(self.serial_port, self.baud_rate, timeout=0.1)
            self.get_logger().info(f"Successfully connected to STM32 on {self.serial_port}")
        except Exception as e:
            self.get_logger().error(f"Failed to connect to STM32: {e}")
            return

        self.timer = self.create_timer(0.01, self.read_serial_data)
        self.sub = self.create_subscription(String, 'mcu/out', self.cb_serial, 10)

    def read_serial_data(self):
        while self.ser.in_waiting > 0:
            try:
                line = self.ser.readline().decode('utf-8').strip()
                if line.startswith('E{'):
                    data = json.loads(line[1:])
                    n1, n2, n3 = float(data['a']), float(data['b']), float(data['c'])
                    msg = Float64MultiArray()
                    msg.data = [n1, n2, n3]
                    self.publisher_.publish(msg)
            except Exception:
                continue

    def cb_serial(self, msg: String):
            if hasattr(self, 'ser') and self.ser.is_open:
                data_to_send = (msg.data + '\r\n').encode('utf-8')
                self.ser.write(data_to_send)
                self.ser.flush()

def main(args=None):
    rclpy.init(args=args)
    node = SerialBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if hasattr(node, 'ser') and node.ser.is_open:
            node.ser.close()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()



#!/usr/bin/env python3

        
        

        

  
#sudo cat /dev/ttyACM0



# import rclpy
# from rclpy.node import Node
# import serial
# import json
# from std_msgs.msg import String

# class SerialJsonNode(Node):
#     def __init__(self):
#         super().__init__('serial_json_node')
#         self.publisher_ = self.create_publisher(String, 'mcu/in', 40)
#         self.serial_port = '/dev/ttyACM0'
#         self.baudrate = 115200
#         try:
#             self.ser = serial.Serial(self.serial_port, self.baudrate, timeout=1)
#             # self.get_logger().info(f"Opened serial port {self.serial_port}")
#         except serial.SerialException as e:
#             self.get_logger().error(f"Failed to open serial port: {e}")
#             raise e
#         self.timer = self.create_timer(0.01, self.timer_callback)

#     def timer_callback(self):
#         # send_data = {'a': 1, 'b': 2, 'c': 420, 'd': 100}
#         # try:
#         #     self.ser.write((json.dumps(send_data) + '\n').encode('utf-8'))
#         # except Exception as e:
#         #     self.get_logger().error(f"Failed to send data: {e}")
#         try:
#             while self.ser.in_waiting > 0:
#                 line = self.ser.readline().decode('utf-8').strip()
#                 # if line.startswith('E{'):
#                     # data = json.loads(line[1:])
#                     # # recv_data = json.loads(line)
#                     # self.get_logger().info(f"Received: {line}")
#                 if line.startswith('E{'):
#                     clean_line = line[1:]
#                     # self.get_logger().info(f"Received: {clean_line}")
#                     msg = String()
#                     msg.data = clean_line
#                     self.publisher_.publish(msg)
#         except json.JSONDecodeError:
#                             self.get_logger().warn("Received invalid JSON.")
#         except Exception as e:
#                             self.get_logger().error(f"Error reading from serial: {e}")

#     def destroy_node(self):
#         if hasattr(self, 'ser') and self.ser.is_open:
#             self.ser.close()
#         super().destroy_node()


# def main(args=None):
#     rclpy.init(args=args)
#     node = SerialJsonNode()
#     try:
#         rclpy.spin(node)
#     except KeyboardInterrupt:
#         pass
#     finally:
#         node.destroy_node()
#         rclpy.shutdown()

# if __name__ == '__main__':
#     main()