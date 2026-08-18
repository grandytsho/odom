import math
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TransformStamped
from std_msgs.msg import Float64MultiArray
from tf2_ros import TransformBroadcaster

def euler_to_quaternion(roll, pitch, yaw):
    """
    Converts euler roll, pitch, yaw to quaternion
    """
    qx = math.sin(roll/2) * math.cos(pitch/2) * math.cos(yaw/2) - math.cos(roll/2) * math.sin(pitch/2) * math.sin(yaw/2)
    qy = math.cos(roll/2) * math.sin(pitch/2) * math.cos(yaw/2) + math.sin(roll/2) * math.cos(pitch/2) * math.sin(yaw/2)
    qz = math.cos(roll/2) * math.cos(pitch/2) * math.sin(yaw/2) - math.sin(roll/2) * math.sin(pitch/2) * math.cos(yaw/2)
    qw = math.cos(roll/2) * math.cos(pitch/2) * math.cos(yaw/2) + math.sin(roll/2) * math.sin(pitch/2) * math.sin(yaw/2)
    return [qx, qy, qz, qw]


class Brain(Node):
    def __init__(self):
        super().__init__('smart_brain')

        # State variables
        self.x_ = 0.0
        self.y_ = 0.0
        self.th_ = 0.0
        self.n1 = 0.0
        self.n2 = 0.0
        self.n3 = 0.0
       
        # Robot constants
        self.l = 0.255
        self.b = 0.186
        self.r = 0.059 / 2.0
        self.c = 2.0 * math.pi * self.r / 2400.0

        # Publishers and Broadcasters
        self.odom_pub_ = self.create_publisher(Odometry, 'odom', 10)
        self.tf_broadcaster_ = TransformBroadcaster(self)
        self.last_time_ = self.get_clock().now()

        # Subscriptions
        self.wheel_sub_ = self.create_subscription(
            Float64MultiArray,
            'wheel_tick',
            self.wheel_callback,
            10
        )

    def wheel_callback(self, msg):
        current_time = self.get_clock().now()
        # dt = (current_time - self.last_time_).nanoseconds / 1e9  # Matches C++ dt calculation

        if len(msg.data) < 3:
            return

        dn1 = msg.data[2] - self.n1 #right
        dn2 = msg.data[0] - self.n2 #left
        dn3 = (msg.data[1]) - self.n3 #lateral

        
        dx = self.c * (dn1 + dn2) / 2.0
        dy = self.c * (dn3 - (dn2 - dn1) * self.b / self.l)
        dth = (self.c / self.l) * (dn2 - dn1)
       
        self.x_ = self.x_ + dx * math.cos(self.th_) - dy * math.sin(self.th_)
        self.y_ = self.y_ + dx * math.sin(self.th_) + dy * math.cos(self.th_)
        self.th_ = self.th_ + dth
        q = euler_to_quaternion(0, 0, self.th_)

        # Transform configuration
        t = TransformStamped()
        t.header.stamp = current_time.to_msg()
        t.header.frame_id = 'odom'
        t.child_frame_id = 'base_link'
        t.transform.translation.x = self.x_
        t.transform.translation.y = self.y_
        t.transform.translation.z = 0.0
        t.transform.rotation.x = q[0]
        t.transform.rotation.y = q[1]
        t.transform.rotation.z = q[2]
        t.transform.rotation.w = q[3]

        self.tf_broadcaster_.sendTransform(t)

        self.get_logger().info(f"x={self.x_ :.3f}, y={self.y_ :.3f}, th={self.th_ * 180 / math.pi:.3f}, ")#dn1={dn1:.3f}, dn2={dn2:.3f}, dn3={dn3:.3f}")
        
        self.last_time_ = current_time
        self.n1 = msg.data[2]
        self.n2 = msg.data[0]
        self.n3 = msg.data[1]


    

def main(args=None):
    rclpy.init(args=args)
    node = Brain()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()