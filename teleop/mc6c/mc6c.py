#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.duration import Duration
from sensor_msgs.msg import Joy
from std_msgs.msg import Float64MultiArray
import time

class RCTeleopFromLogicNode(Node):
    def __init__(self):
        super().__init__('rc_teleop_from_logic_node')

        # === Các tham số này mô phỏng lại các giá trị trong file config.h ===
        self.declare_parameter('input_topic', 'joy')
        self.declare_parameter('output_topic', 'kine_to_ZLA8015D')
        
        # Chỉ số trục trên tay cầm (cần kiểm tra bằng 'ros2 topic echo /joy')
        self.declare_parameter('throttle_axis', 1)  # Trục tiến/lùi
        self.declare_parameter('steer_axis', 2)     # Trục lái trái/phải

        # Các giá trị PWM thô từ tay cầm của bạn
        # Lấy từ file config.h để mô phỏng chính xác
        self.declare_parameter('rc.throttle_forward_min', 1580)
        self.declare_parameter('rc.throttle_forward_max', 1810)
        self.declare_parameter('rc.throttle_stop_min', 1490)
        self.declare_parameter('rc.throttle_stop_max', 1570)
        self.declare_parameter('rc.throttle_backward_min', 1280)
        self.declare_parameter('rc.throttle_backward_max', 1480)
        
        self.declare_parameter('rc.steer_left_min', 1180) # Các giá trị này có vẻ ngược trong code C++,
        self.declare_parameter('rc.steer_left_max', 1390) # ta sẽ điều chỉnh trong logic
        self.declare_parameter('rc.steer_right_min', 1500)
        self.declare_parameter('rc.steer_right_max', 1680)

        # Các tham số điều khiển từ file config.h
        self.declare_parameter('control.move_range', 150.0)
        self.declare_parameter('control.rotate_in_place_divisor', 9.0)
        self.declare_parameter('control.move_and_turn_divisor', 4.0)

        # Lấy giá trị các tham số
        # ... (Bạn có thể thêm code get_parameter ở đây nếu muốn) ...

        # === Tạo Publisher và Subscriber ===
        output_topic = self.get_parameter('output_topic').get_parameter_value().string_value
        input_topic = self.get_parameter('input_topic').get_parameter_value().string_value
        self.command_pub = self.create_publisher(Float64MultiArray, output_topic, 10)
        self.joy_sub = self.create_subscription(Joy, input_topic, self.joy_callback, 10)

        self.get_logger().info("RC Teleop Node (dựa trên logic C++) đã khởi động.")

    def _map_value(self, x, in_min, in_max, out_min, out_max):
        """Hàm map tương đương trong Python"""
        # Tránh chia cho 0
        if in_max == in_min:
            return out_min
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    def joy_callback(self, msg):
        # Đọc giá trị từ các trục (giả sử joy_node đã chuẩn hóa về -1.0 đến 1.0)
        # Chúng ta cần chuyển nó về thang đo PWM của bạn (ví dụ 1000 đến 2000)
        # Giả sử tâm của joy là 0, min là -1, max là 1
        # Và tâm của RC là ~1500, min ~1000, max ~2000
        raw_throttle = msg.axes[self.get_parameter('throttle_axis').get_parameter_value().integer_value]
        raw_steer = msg.axes[self.get_parameter('steer_axis').get_parameter_value().integer_value]
        
        # Chuyển đổi giá trị joy (-1 đến 1) sang thang đo PWM (1000 đến 2000)
        # Đây là bước mô phỏng lại tín hiệu `pw` trong code C++
        pw2 = self._map_value(raw_throttle, -1.0, 1.0, 1000, 2000)
        pw4 = self._map_value(raw_steer, -1.0, 1.0, 1000, 2000)

        # === SAO CHÉP LOGIC TỪ CODE C++ CỦA BẠN VÀO ĐÂY ===
        
        # Lấy các giá trị ngưỡng và điều khiển từ tham số
        p = self.get_parameter
        t_fwd_min = p('rc.throttle_forward_min').get_parameter_value().integer_value
        t_fwd_max = p('rc.throttle_forward_max').get_parameter_value().integer_value
        t_stop_min = p('rc.throttle_stop_min').get_parameter_value().integer_value
        t_stop_max = p('rc.throttle_stop_max').get_parameter_value().integer_value
        t_bwd_min = p('rc.throttle_backward_min').get_parameter_value().integer_value
        t_bwd_max = p('rc.throttle_backward_max').get_parameter_value().integer_value
        
        s_left_min = p('rc.steer_left_min').get_parameter_value().integer_value
        s_left_max = p('rc.steer_left_max').get_parameter_value().integer_value
        s_right_min = p('rc.steer_right_min').get_parameter_value().integer_value
        s_right_max = p('rc.steer_right_max').get_parameter_value().integer_value

        move_range = p('control.move_range').get_parameter_value().double_value
        rotate_divisor = p('control.rotate_in_place_divisor').get_parameter_value().double_value
        move_turn_divisor = p('control.move_and_turn_divisor').get_parameter_value().double_value

        rpm_left_cmd = 0.0
        rpm_right_cmd = 0.0
        turn_divisor = 1.0

        # Logic cho tiến/lùi
        if t_fwd_min < pw2 < t_fwd_max:
            base_rpm = self._map_value(pw2, t_fwd_min, t_fwd_max, 0, move_range)
            rpm_left_cmd = base_rpm
            rpm_right_cmd = base_rpm
            turn_divisor = move_turn_divisor
        elif t_bwd_min < pw2 < t_bwd_max:
            base_rpm = self._map_value(pw2, t_bwd_min, t_bwd_max, 0, -move_range)
            rpm_left_cmd = base_rpm
            rpm_right_cmd = base_rpm
            turn_divisor = move_turn_divisor
        elif t_stop_min < pw2 < t_stop_max:
            turn_divisor = rotate_divisor
        
        # Logic cho rẽ (đã được sửa lại cho đúng với robot vi sai)
        # rẽ trái -> giảm tốc bánh trái, tăng tốc bánh phải
        # rẽ phải -> tăng tốc bánh trái, giảm tốc bánh phải
        if s_left_min < pw4 < s_left_max: # Rẽ trái
            turn_rpm = self._map_value(pw4, s_left_max, s_left_min, 0, move_range) / turn_divisor
            rpm_left_cmd -= turn_rpm
            rpm_right_cmd += turn_rpm
        elif s_right_min < pw4 < s_right_max: # Rẽ phải
            turn_rpm = self._map_value(pw4, s_right_min, s_right_max, 0, move_range) / turn_divisor
            rpm_left_cmd += turn_rpm
            rpm_right_cmd -= turn_rpm

        # Ràng buộc giá trị cuối cùng
        rpm_left_cmd = max(min(rpm_left_cmd, move_range), -move_range)
        rpm_right_cmd = max(min(rpm_right_cmd, move_range), -move_range)

        # Tạo và publish tin nhắn lệnh
        command_msg = Float64MultiArray()
        # Chú ý: ESP32 của bạn nhận lệnh bánh phải là số âm, ta sẽ điều chỉnh ở đây
        # hoặc để node ESP32 tự xử lý. Ở đây, ta sẽ gửi đi giá trị dương,
        # và để ESP32 xử lý dấu trừ.
        command_msg.data = [rpm_left_cmd, rpm_right_cmd] 
        self.command_pub.publish(command_msg)


def main(args=None):
    rclpy.init(args=args)
    node = RCTeleopFromLogicNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
