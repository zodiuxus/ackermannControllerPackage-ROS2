import rclpy
from rclpy.node import Node
from ackermann_msgs.msg import AckermannDriveStamped, AckermannDrive
import math
import sys
import os

if sys.platform == 'win32':
    import msvcrt
else:
    import tty
    import termios

    
def getKey(settings):
    if sys.platform == 'win32':
        # getwch() returns a string on Windows
        key = msvcrt.getwch()
    else:
        tty.setraw(sys.stdin.fileno())
        # sys.stdin.read() returns a string on Linux
        key = sys.stdin.read(1)
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

message = """
Ackermann Control Node
---------------------------
Moving around:
             ^
            w/i 
   < a/j    s/k    d/l >
---------------------------
w/i : increase speed
s/k : decrease speed
a/j : turn left
d/l : turn right
r/o : steering angle to 0
q   : to stop and quit
"""

class ackermannControl(Node):
    def __init__(self):
        super().__init__('Ackermann_Control')
        self.publisher_ego_ = self.create_publisher(AckermannDriveStamped, '/drive', 10) 
        self.publisher_opp_ = self.create_publisher(AckermannDriveStamped, '/opp_drive', 10) 
        timer_period = 0.1
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.speed = 0.0
        self.steering_angle = 0.0
        self.lines = []
        self.opp_speed = 0.0
        self.opp_steering_angle = 0.0


    def timer_callback(self):
        msg = AckermannDriveStamped()
        msg_opp = AckermannDriveStamped()
        msg_opp.header.stamp = self.get_clock().now().to_msg()
        msg_opp.drive.steering_angle_velocity = math.pi/72
        msg_opp.drive.acceleration = 0.5
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.drive.steering_angle_velocity = math.pi/72
        msg.drive.acceleration = 0.5
        key = getKey(settings=termios.tcgetattr(sys.stdin.fileno()))
        
        if key.lower() == 'w':
            self.speed = self.speed + 1.0
        elif key.lower() == 'a':
            self.steering_angle = self.steering_angle + math.pi/36
        elif key.lower() == 's':
            self.speed = self.speed - 1.0
        elif key.lower() == 'd':
            self.steering_angle = self.steering_angle - math.pi/36
        elif key.lower() == 'r':
            self.steering_angle = 0.0

        elif key.lower() == 'i':
            self.opp_speed = self.opp_speed + 1.0
        elif key.lower() == 'j':
            self.opp_steering_angle = self.opp_steering_angle + math.pi/36
        elif key.lower() == 'k':
            self.opp_speed = self.opp_speed - 1.0
        elif key.lower() == 'l':
            self.opp_steering_angle = self.opp_steering_angle - math.pi/36
        elif key.lower() == 'o':
            self.opp_steering_angle = 0.0

        elif key.lower() == 'q':
            self.speed = 0.0
            self.steering_angle = 0.0
            self.opp_speed = 0.0
            self.opp_steering_angle = 0.0
            msg_opp.drive.steering_angle = self.opp_steering_angle
            msg.drive.steering_angle = self.steering_angle
            msg_opp.drive.speed = self.opp_speed
            msg.drive.speed = self.speed
            self.publisher_ego_.publish(msg)
            self.publisher_opp_.publish(msg)
            messages = "speed: " + str(self.speed) + " steering_angle: " + str(self.steering_angle)
            print(messages)
            sys.exit(0)
        messages = "speed: " + str(self.speed) + " steering_angle: " + str(self.steering_angle)
        print(messages)
        self.lines.append(messages)
        
        msg_opp.drive.steering_angle = self.opp_steering_angle
        msg.drive.steering_angle = self.steering_angle
        msg_opp.drive.speed = self.opp_speed
        msg.drive.speed = self.speed
        self.publisher_ego_.publish(msg)
        self.publisher_opp_.publish(msg_opp)

        if len(self.lines) > 8:
            self.lines.clear()
            clear_screen()
            print(messages)


def main(args=None):
    rclpy.init(args=args)
    drive = ackermannControl()
    rclpy.spin(drive)
    drive.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
