#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
import math
from slamtec import SlamtecMapper
import time

class SlamtecPublisher(Node):
    def __init__(self):
        super().__init__('slamtec_publisher')
        
        # Create publisher
        self.publisher_ = self.create_publisher(LaserScan, 'scan', 10)
        
        # Initialize Slamtec
        self.slamtec = SlamtecMapper(host='192.168.11.1', port=1445)
        
        # Create timer
        self.timer = self.create_timer(0.1, self.timer_callback)  # 10Hz
        self.frame_id = 'laser_frame'

    def timer_callback(self):
        # Get laser scan data
        scan_data = self.slamtec.get_laser_scan(valid_only=True)
        
        # Create LaserScan message
        msg = LaserScan()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = self.frame_id
        
        # Convert data
        angles = []
        ranges = []
        for angle, distance, valid in scan_data:
            angles.append(angle)
            ranges.append(distance)
        
        msg.angle_min = min(angles)
        msg.angle_max = max(angles)
        msg.angle_increment = (msg.angle_max - msg.angle_min) / len(angles)
        msg.time_increment = 0.0
        msg.scan_time = 0.1
        msg.range_min = 0.15  # From Slamtec specs
        msg.range_max = 8.0   # From Slamtec specs
        msg.ranges = ranges
        
        # Publish
        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    publisher = SlamtecPublisher()
    rclpy.spin(publisher)
    publisher.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()