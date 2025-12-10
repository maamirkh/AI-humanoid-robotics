#!/usr/bin/env python3
"""
Conceptual Sensor Loop Example

This module demonstrates a conceptual sensor loop for humanoid robots,
showing how sensors collect data, process it, and trigger appropriate responses.
"""

from typing import Dict, List, Optional, Union
import time
import random


class SensorData:
    """
    Represents data from various sensors in a humanoid robot.
    """

    def __init__(self) -> None:
        self.accelerometer: Dict[str, float] = {"x": 0.0, "y": 0.0, "z": 0.0}
        self.gyroscope: Dict[str, float] = {"x": 0.0, "y": 0.0, "z": 0.0}
        self.camera: Optional[List[List[int]]] = None  # Simplified representation
        self.lidar: Optional[List[float]] = None  # Distance measurements
        self.joint_positions: Dict[str, float] = {}
        self.timestamp: float = time.time()

    def update_random_data(self) -> None:
        """Generate random sensor data for demonstration purposes."""
        self.accelerometer = {
            "x": random.uniform(-2.0, 2.0),
            "y": random.uniform(-2.0, 2.0),
            "z": random.uniform(8.0, 12.0)  # Gravity component
        }
        self.gyroscope = {
            "x": random.uniform(-1.0, 1.0),
            "y": random.uniform(-1.0, 1.0),
            "z": random.uniform(-1.0, 1.0)
        }
        self.camera = [[random.randint(0, 255) for _ in range(10)] for _ in range(10)]
        self.lidar = [random.uniform(0.1, 10.0) for _ in range(360)]
        self.joint_positions = {
            "hip_left": random.uniform(-0.5, 0.5),
            "knee_left": random.uniform(0.0, 1.5),
            "ankle_left": random.uniform(-0.3, 0.3),
            "hip_right": random.uniform(-0.5, 0.5),
            "knee_right": random.uniform(0.0, 1.5),
            "ankle_right": random.uniform(-0.3, 0.3)
        }
        self.timestamp = time.time()


class SensorProcessor:
    """
    Processes sensor data to extract meaningful information.
    """

    def __init__(self) -> None:
        self.stability_threshold = 0.5
        self.obstacle_distance_threshold = 1.0

    def calculate_balance_state(self, sensor_data: SensorData) -> Dict[str, Union[bool, float]]:
        """
        Calculate the balance state of the humanoid based on accelerometer and gyroscope data.

        Args:
            sensor_data: Current sensor readings

        Returns:
            Dictionary containing balance information
        """
        # Simplified balance calculation
        accel_magnitude = (
            sensor_data.accelerometer["x"] ** 2 +
            sensor_data.accelerometer["y"] ** 2 +
            sensor_data.accelerometer["z"] ** 2
        ) ** 0.5

        gyro_magnitude = (
            sensor_data.gyroscope["x"] ** 2 +
            sensor_data.gyroscope["y"] ** 2 +
            sensor_data.gyroscope["z"] ** 2
        ) ** 0.5

        is_stable = gyro_magnitude < self.stability_threshold
        stability_score = max(0.0, self.stability_threshold - gyro_magnitude)

        return {
            "is_stable": is_stable,
            "stability_score": stability_score,
            "acceleration_magnitude": accel_magnitude,
            "rotation_rate": gyro_magnitude
        }

    def detect_obstacles(self, sensor_data: SensorData) -> List[Dict[str, float]]:
        """
        Detect obstacles using LIDAR data.

        Args:
            sensor_data: Current sensor readings

        Returns:
            List of obstacles with position and distance information
        """
        if not sensor_data.lidar:
            return []

        obstacles = []
        for angle, distance in enumerate(sensor_data.lidar):
            if distance < self.obstacle_distance_threshold:
                obstacles.append({
                    "angle": angle,
                    "distance": distance,
                    "direction": "front" if 315 <= angle or angle <= 45 else
                               "right" if 45 < angle < 135 else
                               "back" if 135 <= angle <= 225 else "left"
                })

        return obstacles


class ActionPlanner:
    """
    Plans actions based on processed sensor data.
    """

    def __init__(self) -> None:
        self.max_step_size = 0.3
        self.step_height = 0.1

    def plan_response(self, balance_state: Dict[str, Union[bool, float]],
                     obstacles: List[Dict[str, float]]) -> Dict[str, Union[str, float, bool]]:
        """
        Plan appropriate response based on balance state and obstacle detection.

        Args:
            balance_state: Output from calculate_balance_state
            obstacles: List of obstacles from detect_obstacles

        Returns:
            Dictionary containing planned action
        """
        if not balance_state["is_stable"]:
            return {
                "action": "adjust_posture",
                "priority": "high",
                "stability_required": True
            }

        if obstacles:
            closest_obstacle = min(obstacles, key=lambda x: x["distance"])
            if closest_obstacle["distance"] < 0.5:
                return {
                    "action": "stop_and_avoid",
                    "avoid_direction": closest_obstacle["direction"],
                    "priority": "high"
                }
            else:
                return {
                    "action": "proceed_with_caution",
                    "obstacle_direction": closest_obstacle["direction"],
                    "priority": "medium"
                }

        return {
            "action": "continue_moving",
            "priority": "low"
        }


def main() -> None:
    """
    Main function demonstrating the sensor loop.
    """
    print("Starting conceptual sensor loop for humanoid robot...")
    print("Press Ctrl+C to stop the simulation.\n")

    sensor_processor = SensorProcessor()
    action_planner = ActionPlanner()
    sensor_data = SensorData()

    try:
        for i in range(20):  # Run for 20 iterations for demonstration
            # Update sensor data (in real system, this would come from actual sensors)
            sensor_data.update_random_data()

            # Process sensor data
            balance_state = sensor_processor.calculate_balance_state(sensor_data)
            obstacles = sensor_processor.detect_obstacles(sensor_data)

            # Plan response based on processed data
            planned_action = action_planner.plan_response(balance_state, obstacles)

            # Display information
            print(f"Iteration {i+1}:")
            print(f"  Balance: Stable={balance_state['is_stable']}, "
                  f"Score={balance_state['stability_score']:.2f}")
            print(f"  Obstacles detected: {len(obstacles)}")
            print(f"  Planned action: {planned_action['action']}")
            print(f"  Priority: {planned_action['priority']}")
            print()

            # In a real system, this would control the robot's actuators
            time.sleep(0.5)  # Simulate time between sensor readings

    except KeyboardInterrupt:
        print("\nSensor loop stopped by user.")


if __name__ == "__main__":
    main()