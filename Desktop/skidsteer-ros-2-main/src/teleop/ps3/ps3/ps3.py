#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""PS3 Teleoperation Node for ROS 2.

This module intercepts joypad inputs from a PS3 controller, maps them to linear
and angular velocity commands, scales them dynamically using the R2 trigger as
a throttle, and streams Twist packets to a mobile robot's base.

Author: Pham Duc Duy - https://github.com/phamduyaaaa

Version:
    1.1.0
"""

from typing import List, Optional, Tuple

from geometry_msgs.msg import Twist
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy


class PS3TeleopNode(Node):
    """ROS 2 Node that translates PS3 controller inputs into geometry_msgs/Twist.

    Features active state tracking to provide rich diagnostic logs containing
    exact button engagement and throttle percentages without clogging the I/O.

    Attributes:
        subscription (rclpy.subscription.Subscription): Joy topic subscriber.
        publisher (rclpy.publisher.Publisher): Twist command publisher.
        base_linear_vel (float): Unscaled forward/backward baseline speed (m/s).
        base_angular_vel (float): Unscaled turning baseline speed (rad/s).
        max_boost_multiplier (float): Maximum ceiling factor achieved at 100% R2.
        prev_log_key (tuple): Key hashing matrix utilized to prevent log spam.
    """

    def __init__(self) -> None:
        """Initializes constants, baseline parameters, and standard ROS interfaces."""
        super().__init__('ps3_teleop_node')

        # ---------------------------------------------------------
        # PS3 CONTROLLER MAPPING MATRIX
        # ---------------------------------------------------------
        self.BTN_X: int = 0          # Reverse motion
        self.BTN_TRIANGLE: int = 2   # Forward motion
        self.BTN_L1: int = 4         # Counter-clockwise rotation
        self.BTN_R1: int = 5         # Clockwise rotation
        self.BTN_L2: int = 6         # Safety brake button
        
        self.AXIS_R2_GA: int = 5     # Throttle trigger axis

        # ---------------------------------------------------------
        # VELOCITY PROFILES & SPEED CEILINGS
        # ---------------------------------------------------------
        self.base_linear_vel: float = 0.3      # m/s
        self.base_angular_vel: float = 0.8     # rad/s
        self.max_boost_multiplier: float = 3.0  # Caps out at 3x speed

        # ---------------------------------------------------------
        # SENIOR STATE TRACKING MECHANISM
        # ---------------------------------------------------------
        # Stores: (btn_pressed_name, is_braking, throttle_percent_rounded, is_moving)
        # Changes in this tuple trigger context-aware diagnostic logging.
        self.prev_log_key: Tuple[str, bool, int, bool] = ("", False, 0, False)

        # Initialize ROS communications
        self.subscription = self.create_subscription(
            Joy, 
            '/joy', 
            self.joy_callback, 
            10
        )
        self.publisher = self.create_publisher(
            Twist, 
            '/cmd_vel', 
            10
        )

        self.get_logger().info(
            "PS3 Teleop System online. Precision telemetry logging activated."
        )

    def joy_callback(self, msg: Joy) -> None:
        """Evaluates joystick arrays, packs kinematics commands, and generates telemetry.

        Args:
            msg (Joy): The raw joystick state containing axis and button arrays.
        """
        # Array size guard check to prevent runtime IndexErrors
        required_buttons = max(
            self.BTN_X, self.BTN_TRIANGLE, self.BTN_L1, self.BTN_R1, self.BTN_L2
        )
        if len(msg.buttons) <= required_buttons:
            return

        twist = Twist()
        v_linear: float = 0.0
        v_angular: float = 0.0
        
        # Human-readable string metadata tracker for log visibility
        active_direction_btn: str = "RELEASED"

        # =========================================================
        # 1. THROTTLE MULTIPLIER CALCULATION (R2 Trigger)
        # =========================================================
        ga_percent: float = 0.0
        if len(msg.axes) > self.AXIS_R2_GA:
            # R2 rests at 1.0, falls to -1.0 when fully depressed
            raw_ga: float = msg.axes[self.AXIS_R2_GA]
            ga_percent = (1.0 - raw_ga) / 2.0

        multiplier: float = 1.0 + (ga_percent * (self.max_boost_multiplier - 1.0))
        rounded_ga_int: int = int(ga_percent * 100)

        # =========================================================
        # 2. DIRECTIONAL ARRAYS & VELOCITY PACKING
        # =========================================================
        # Linear tracking
        if msg.buttons[self.BTN_TRIANGLE] == 1:
            v_linear = self.base_linear_vel * multiplier
            active_direction_btn = "TRIANGLE (FORW)"
        elif msg.buttons[self.BTN_X] == 1:
            v_linear = -self.base_linear_vel * multiplier
            active_direction_btn = "X (REV)"

        # Angular tracking (Can blend with linear motions safely)
        if msg.buttons[self.BTN_L1] == 1:
            v_angular = self.base_angular_vel * multiplier
            active_direction_btn = (
                "L1 (CCW)" if active_direction_btn == "RELEASED" 
                else f"{active_direction_btn} + L1"
            )
        elif msg.buttons[self.BTN_R1] == 1:
            v_angular = -self.base_angular_vel * multiplier
            active_direction_btn = (
                "R1 (CW)" if active_direction_btn == "RELEASED" 
                else f"{active_direction_btn} + R1"
            )

        # =========================================================
        # 3. SAFETY OVERRIDE / HARDBRAKE LOGIC
        # =========================================================
        is_l2_pressed: bool = (msg.buttons[self.BTN_L2] == 1)
        if is_l2_pressed:
            v_linear = 0.0
            v_angular = 0.0
            active_direction_btn = "BRAKE_ENGAGED"

        # Broadcast the command to control actuators
        twist.linear.x = v_linear
        twist.angular.z = v_angular
        self.publisher.publish(twist)

        # =========================================================
        # 4. ANTI-SPAM SMART TELEMETRY LOGGER
        # =========================================================
        is_moving: bool = (v_linear != 0.0 or v_angular != 0.0)
        
        # Round throttle to nearest 10% interval when driving to eliminate 
        # micro-fluctuations logs caused by analog jitter.
        jitter_filtered_ga: int = round(rounded_ga_int, -1) if is_moving else 0
        
        # Compute current state unique signature
        current_log_key = (
            active_direction_btn, 
            is_l2_pressed, 
            jitter_filtered_ga, 
            is_moving
        )

        # Trigger logging block only if an active state mutation is caught
        if current_log_key != self.prev_log_key:
            if is_l2_pressed:
                self.get_logger().warn(
                    "◆ [SYSTEM] ACTIVE BRAKE ENGAGED! (L2 Pressed) -> Hard Halt."
                )
            elif is_moving:
                self.get_logger().info(
                    f"✔ [DRIVE] Keys: {active_direction_btn:<16} | "
                    f"Throttle: {rounded_ga_int:03d}% (x{multiplier:.1f}) | "
                    f"Target V: {v_linear:+5.2f}m/s, W: {v_angular:+5.2f}rad/s"
                )
            else:
                # Caught a zero-velocity state drop (Keys released)
                self.get_logger().info(
                    "■ [STOP] All driving keys released. Velocity reset to zero."
                )
            
            # Save historical state frame
            self.prev_log_key = current_log_key


def main(args: Optional[List[str]] = None) -> None:
    """Main entry point for node registration and event loop execution."""
    rclpy.init(args=args)
    node = PS3TeleopNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Teleop node interrupted by user.")
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
