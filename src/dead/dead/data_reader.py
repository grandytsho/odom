import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray
import serial
import json  

class SerialBridge(Node):
    def __init__(self):
        super().__init__('serial_bridge')
        self.publisher_ = self.create_publisher(Float64MultiArray, 'wheel_tick', 10)
        
        self.serial_port = '/dev/ttyACM0' 
        self.baud_rate = 115200
        
        try:
            self.ser = serial.Serial(self.serial_port, self.baud_rate, timeout=1.0)
            self.get_logger().info(f"Successfully connected to STM32 on {self.serial_port}")
        except Exception as e:
            self.get_logger().error(f"Failed to connect to STM32: {e}")
            return

        self.timer = self.create_timer(0.01, self.read_serial_data)

    def read_serial_data(self):
        if self.ser.in_waiting > 0:
            try:
                line = self.ser.readline().decode('utf-8').strip()
                
                if line.startswith('E{'):
                    clean_json_string = line[1:]
                    
                    data = json.loads(clean_json_string)

                    n1 = float(data['a'])
                    n2 = float(data['b'])
                    n3 = float(data['c'])
                    
                    msg = Float64MultiArray()
                    msg.data = [n1, n2, n3]
                    self.publisher_.publish(msg)
                    
            except Exception as e:
                pass 

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
#sudo cat /dev/ttyACM0