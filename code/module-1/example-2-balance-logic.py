#!/usr/bin/env python3
"""
Conceptual Balance Logic Example

This module demonstrates conceptual balance logic for humanoid robots,
showing how to maintain stability using sensor feedback and control algorithms.
"""

from typing import Dict, List, Tuple
import math
import time
import random


class BalanceController:
    """
    Implements balance control algorithms for humanoid robots.
    """

    def __init__(self) -> None:
        # PID controller parameters
        self.kp = 2.0  # Proportional gain
        self.ki = 0.1  # Integral gain
        self.kd = 0.5  # Derivative gain

        # Balance thresholds
        self.max_tilt_threshold = 15.0  # degrees
        self.target_com_height = 0.8    # meters

        # Internal state for PID
        self.previous_error = 0.0
        self.integral_error = 0.0

    def calculate_desired_joint_positions(self, current_state: Dict[str, float],
                                        target_balance: Dict[str, float]) -> Dict[str, float]:
        """
        Calculate desired joint positions to maintain balance.

        Args:
            current_state: Current robot state including joint angles and IMU data
            target_balance: Target balance state

        Returns:
            Dictionary of desired joint positions
        """
        # Calculate errors
        roll_error = target_balance["roll"] - current_state["roll"]
        pitch_error = target_balance["pitch"] - current_state["pitch"]
        com_height_error = target_balance["com_height"] - current_state["com_height"]

        # Update integral and derivative terms
        self.integral_error += roll_error
        derivative_error = roll_error - self.previous_error
        self.previous_error = roll_error

        # Apply PID control to calculate corrective action
        roll_correction = (self.kp * roll_error +
                          self.ki * self.integral_error +
                          self.kd * derivative_error)

        # Calculate desired joint positions based on corrections
        desired_positions = {
            # Hip joints for lateral balance
            "hip_left_roll": current_state["hip_left_roll"] + roll_correction * 0.1,
            "hip_right_roll": current_state["hip_right_roll"] - roll_correction * 0.1,
            # Hip joints for forward/back balance
            "hip_left_pitch": current_state["hip_left_pitch"] + pitch_error * 0.05,
            "hip_right_pitch": current_state["hip_right_pitch"] + pitch_error * 0.05,
            # Knee joints for height control
            "knee_left": current_state["knee_left"] + com_height_error * 0.2,
            "knee_right": current_state["knee_right"] + com_height_error * 0.2,
            # Ankle joints for fine balance adjustments
            "ankle_left_pitch": current_state["ankle_left_pitch"] - pitch_error * 0.1,
            "ankle_right_pitch": current_state["ankle_right_pitch"] - pitch_error * 0.1,
            "ankle_left_roll": current_state["ankle_left_roll"] - roll_correction * 0.05,
            "ankle_right_roll": current_state["ankle_right_roll"] - roll_correction * 0.05
        }

        # Apply joint limits
        for joint, position in desired_positions.items():
            if "hip" in joint:
                # Hip joint limits (in radians)
                desired_positions[joint] = max(-0.5, min(0.5, position))
            elif "knee" in joint:
                # Knee joint limits (in radians)
                desired_positions[joint] = max(0.0, min(1.5, position))
            elif "ankle" in joint:
                # Ankle joint limits (in radians)
                desired_positions[joint] = max(-0.3, min(0.3, position))

        return desired_positions

    def calculate_zmp(self, com_pos: Tuple[float, float, float],
                     com_vel: Tuple[float, float, float],
                     com_acc: Tuple[float, float, float]) -> Tuple[float, float]:
        """
        Calculate Zero Moment Point (ZMP) for balance control.

        Args:
            com_pos: Center of mass position (x, y, z)
            com_vel: Center of mass velocity
            com_acc: Center of mass acceleration

        Returns:
            ZMP position (x, y)
        """
        gravity = 9.81  # m/s^2
        z_com = com_pos[2]

        if z_com <= 0:
            return (com_pos[0], com_pos[1])

        zmp_x = com_pos[0] - (com_acc[0] * z_com) / (gravity + com_acc[2])
        zmp_y = com_pos[1] - (com_acc[1] * z_com) / (gravity + com_acc[2])

        return (zmp_x, zmp_y)

    def is_balanced(self, zmp: Tuple[float, float],
                   support_polygon: List[Tuple[float, float]]) -> bool:
        """
        Check if the robot is balanced based on ZMP and support polygon.

        Args:
            zmp: Zero Moment Point position
            support_polygon: Convex hull of support points (foot positions)

        Returns:
            True if balanced, False otherwise
        """
        # Simple check: is ZMP within the support polygon?
        # This is a simplified implementation - real systems use more sophisticated checks
        zmp_x, zmp_y = zmp

        # Find bounding box of support polygon
        min_x = min(point[0] for point in support_polygon)
        max_x = max(point[0] for point in support_polygon)
        min_y = min(point[1] for point in support_polygon)
        max_y = max(point[1] for point in support_polygon)

        # Add small safety margin
        margin = 0.05  # 5cm safety margin
        return (min_x + margin <= zmp_x <= max_x - margin and
                min_y + margin <= zmp_y <= max_y - margin)


class Simulator:
    """
    Simulates robot state for balance control demonstration.
    """

    def __init__(self) -> None:
        self.state = self.initialize_state()

    def initialize_state(self) -> Dict[str, float]:
        """Initialize robot state with reasonable values."""
        return {
            "roll": 0.0,  # degrees
            "pitch": 0.0,  # degrees
            "com_height": 0.8,  # meters
            "hip_left_roll": 0.0,
            "hip_right_roll": 0.0,
            "hip_left_pitch": 0.1,
            "hip_right_pitch": 0.1,
            "knee_left": 1.0,
            "knee_right": 1.0,
            "ankle_left_pitch": 0.0,
            "ankle_right_pitch": 0.0,
            "ankle_left_roll": 0.0,
            "ankle_right_roll": 0.0
        }

    def apply_control(self, desired_positions: Dict[str, float]) -> None:
        """Apply control inputs to robot state."""
        # In a real robot, this would send commands to actuators
        # For simulation, we'll update the state with some delay and noise
        for joint, desired_pos in desired_positions.items():
            if joint in self.state:
                # Apply control with some delay and noise
                current_pos = self.state[joint]
                # Move 80% of the way to desired position
                self.state[joint] = current_pos * 0.2 + desired_pos * 0.8
                # Add small amount of noise
                self.state[joint] += random.uniform(-0.01, 0.01)

    def simulate_external_force(self) -> None:
        """Simulate external forces that affect balance."""
        # Random external force for demonstration
        if random.random() < 0.3:  # 30% chance of external force
            self.state["roll"] += random.uniform(-2.0, 2.0)
            self.state["pitch"] += random.uniform(-2.0, 2.0)


def main() -> None:
    """
    Main function demonstrating balance control logic.
    """
    print("Starting conceptual balance control for humanoid robot...")
    print("Demonstrating PID-based balance control with ZMP calculation.\n")

    controller = BalanceController()
    simulator = Simulator()

    # Define target balance state
    target_balance = {
        "roll": 0.0,      # No roll desired
        "pitch": 0.0,     # No pitch desired
        "com_height": 0.8 # Target CoM height
    }

    # Define support polygon (simplified as rectangle for feet)
    support_polygon = [
        (-0.1, -0.05),  # front left
        (-0.1, 0.05),   # front right
        (0.1, 0.05),    # back right
        (0.1, -0.05)    # back left
    ]

    try:
        for i in range(30):  # Run for 30 iterations
            print(f"Iteration {i+1}:")
            print(f"  Current state - Roll: {simulator.state['roll']:.2f}°, "
                  f"Pitch: {simulator.state['pitch']:.2f}°")

            # Calculate desired joint positions
            desired_positions = controller.calculate_desired_joint_positions(
                simulator.state, target_balance
            )

            # Calculate ZMP for balance verification
            com_pos = (0.0, 0.0, simulator.state["com_height"])
            com_vel = (0.0, 0.0, 0.0)  # Simplified
            com_acc = (0.0, 0.0, 0.0)  # Simplified
            zmp = controller.calculate_zmp(com_pos, com_vel, com_acc)

            # Check if balanced
            is_balanced = controller.is_balanced(zmp, support_polygon)

            print(f"  ZMP: ({zmp[0]:.3f}, {zmp[1]:.3f})")
            print(f"  Is balanced: {is_balanced}")
            print(f"  Applying {len(desired_positions)} control adjustments...")

            # Apply control to simulator
            simulator.apply_control(desired_positions)

            # Simulate external forces occasionally
            simulator.simulate_external_force()

            print(f"  New roll: {simulator.state['roll']:.2f}°, "
                  f"New pitch: {simulator.state['pitch']:.2f}°\n")

            time.sleep(0.3)  # Slow down simulation for readability

    except KeyboardInterrupt:
        print("\nBalance control demonstration stopped by user.")


if __name__ == "__main__":
    main()