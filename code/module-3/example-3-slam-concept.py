#!/usr/bin/env python3
"""
Conceptual SLAM Example

This module demonstrates conceptual SLAM (Simultaneous Localization and Mapping) for humanoid robots,
showing how to build a map of the environment while tracking the robot's position.
"""

from typing import Dict, List, Tuple, Optional, Any
import math
import random
import time
from dataclasses import dataclass


@dataclass
class Pose:
    """
    Represents a 2D pose with position and orientation.
    """
    x: float
    y: float
    theta: float  # Orientation in radians

    def distance_to(self, other: 'Pose') -> float:
        """Calculate Euclidean distance to another pose."""
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)


@dataclass
class Landmark:
    """
    Represents a landmark in the map.
    """
    id: int
    x: float
    y: float
    observed_count: int = 1
    covariance: Tuple[float, float, float] = (1.0, 1.0, 0.0)  # x_var, y_var, xy_cov


class SimpleMotionModel:
    """
    Models robot motion with uncertainty.
    """

    def __init__(self) -> None:
        self.linear_noise = 0.05   # Standard deviation for linear movement
        self.angular_noise = 0.02  # Standard deviation for angular movement

    def predict_motion(self, current_pose: Pose, control_input: Tuple[float, float],
                      dt: float) -> Pose:
        """
        Predict next pose based on control input with added noise.

        Args:
            current_pose: Current robot pose
            control_input: (linear_velocity, angular_velocity)
            dt: Time step

        Returns:
            Predicted pose with motion uncertainty
        """
        linear_vel, angular_vel = control_input

        # Calculate expected motion
        if abs(angular_vel) < 1e-5:  # Straight line motion
            new_x = current_pose.x + linear_vel * dt * math.cos(current_pose.theta)
            new_y = current_pose.y + linear_vel * dt * math.sin(current_pose.theta)
            new_theta = current_pose.theta
        else:  # Circular motion
            radius = linear_vel / angular_vel
            new_x = current_pose.x + radius * (math.sin(current_pose.theta + angular_vel * dt) - math.sin(current_pose.theta))
            new_y = current_pose.y + radius * (math.cos(current_pose.theta) - math.cos(current_pose.theta + angular_vel * dt))
            new_theta = current_pose.theta + angular_vel * dt

        # Add noise to simulate uncertainty
        new_x += random.gauss(0, self.linear_noise)
        new_y += random.gauss(0, self.linear_noise)
        new_theta += random.gauss(0, self.angular_noise)

        # Normalize angle
        new_theta = ((new_theta + math.pi) % (2 * math.pi)) - math.pi

        return Pose(new_x, new_y, new_theta)


class SimpleObservationModel:
    """
    Models sensor observations of landmarks with uncertainty.
    """

    def __init__(self) -> None:
        self.range_noise = 0.1     # Standard deviation for range measurements
        self.bearing_noise = 0.05  # Standard deviation for bearing measurements

    def observe_landmark(self, robot_pose: Pose, landmark: Landmark) -> Optional[Tuple[float, float]]:
        """
        Simulate observation of a landmark from robot pose.

        Args:
            robot_pose: Current robot pose
            landmark: Landmark to observe

        Returns:
            Tuple of (range, bearing) or None if landmark not visible
        """
        # Calculate true range and bearing
        dx = landmark.x - robot_pose.x
        dy = landmark.y - robot_pose.y
        true_range = math.sqrt(dx**2 + dy**2)
        true_bearing = math.atan2(dy, dx) - robot_pose.theta

        # Add sensor noise
        observed_range = true_range + random.gauss(0, self.range_noise)
        observed_bearing = true_bearing + random.gauss(0, self.bearing_noise)

        # Normalize bearing
        observed_bearing = ((observed_bearing + math.pi) % (2 * math.pi)) - math.pi

        # Check if landmark is within sensor range (simplified)
        if observed_range < 5.0:  # Sensor range limit
            return (observed_range, observed_bearing)
        else:
            return None

    def range_bearing_to_cartesian(self, robot_pose: Pose, range_val: float,
                                  bearing_val: float) -> Tuple[float, float]:
        """
        Convert range and bearing to Cartesian coordinates.

        Args:
            robot_pose: Robot pose from which measurement was taken
            range_val: Measured range
            bearing_val: Measured bearing

        Returns:
            Tuple of (x, y) landmark position in global coordinates
        """
        global_bearing = robot_pose.theta + bearing_val
        landmark_x = robot_pose.x + range_val * math.cos(global_bearing)
        landmark_y = robot_pose.y + range_val * math.sin(global_bearing)

        return (landmark_x, landmark_y)


class SimpleSLAM:
    """
    Implements a simple SLAM algorithm for demonstration purposes.
    """

    def __init__(self) -> None:
        self.motion_model = SimpleMotionModel()
        self.observation_model = SimpleObservationModel()
        self.robot_pose = Pose(0.0, 0.0, 0.0)
        self.landmarks: Dict[int, Landmark] = {}
        self.poses: List[Pose] = [self.robot_pose]
        self.landmark_observations: List[Dict[str, Any]] = []
        self.next_landmark_id = 1
        self.time = 0.0
        self.dt = 0.1  # 100ms time step

    def move_robot(self, control_input: Tuple[float, float]) -> Pose:
        """
        Move the robot based on control input.

        Args:
            control_input: (linear_velocity, angular_velocity)

        Returns:
            New robot pose
        """
        self.robot_pose = self.motion_model.predict_motion(
            self.robot_pose, control_input, self.dt
        )
        self.poses.append(self.robot_pose)
        self.time += self.dt
        return self.robot_pose

    def observe_environment(self, known_landmarks: List[Tuple[float, float]]) -> List[Dict[str, Any]]:
        """
        Observe the environment and detect landmarks.

        Args:
            known_landmarks: List of (x, y) positions of known landmarks

        Returns:
            List of observations
        """
        observations = []

        for lm_x, lm_y in known_landmarks:
            landmark = Landmark(self.next_landmark_id, lm_x, lm_y)
            obs = self.observation_model.observe_landmark(self.robot_pose, landmark)

            if obs is not None:
                range_val, bearing_val = obs
                # Check if this landmark is already in our map
                matched_landmark = self._match_landmark(range_val, bearing_val)

                if matched_landmark is not None:
                    # Update existing landmark
                    self._update_landmark(matched_landmark, range_val, bearing_val)
                    observations.append({
                        "landmark_id": matched_landmark.id,
                        "type": "existing",
                        "range": range_val,
                        "bearing": bearing_val
                    })
                else:
                    # Add new landmark to map
                    lm_x, lm_y = self.observation_model.range_bearing_to_cartesian(
                        self.robot_pose, range_val, bearing_val
                    )
                    new_landmark = Landmark(self.next_landmark_id, lm_x, lm_y)
                    self.landmarks[self.next_landmark_id] = new_landmark
                    self.next_landmark_id += 1

                    observations.append({
                        "landmark_id": new_landmark.id,
                        "type": "new",
                        "range": range_val,
                        "bearing": bearing_val
                    })

        # Store observations
        self.landmark_observations.append({
            "timestamp": self.time,
            "robot_pose": self.robot_pose,
            "observations": observations
        })

        return observations

    def _match_landmark(self, observed_range: float, observed_bearing: float) -> Optional[Landmark]:
        """
        Match an observation to an existing landmark using nearest neighbor.

        Args:
            observed_range: Observed range to landmark
            observed_bearing: Observed bearing to landmark

        Returns:
            Matching landmark or None if no match found
        """
        # Convert observation to Cartesian coordinates
        obs_x, obs_y = self.observation_model.range_bearing_to_cartesian(
            self.robot_pose, observed_range, observed_bearing
        )

        # Find closest landmark within threshold
        min_distance = float('inf')
        closest_landmark = None

        for landmark in self.landmarks.values():
            distance = math.sqrt((obs_x - landmark.x)**2 + (obs_y - landmark.y)**2)
            if distance < min_distance and distance < 0.5:  # Matching threshold
                min_distance = distance
                closest_landmark = landmark

        return closest_landmark

    def _update_landmark(self, landmark: Landmark, observed_range: float,
                        observed_bearing: float) -> None:
        """
        Update landmark position based on new observation.

        Args:
            landmark: Landmark to update
            observed_range: New range observation
            observed_bearing: New bearing observation
        """
        # Convert to Cartesian coordinates
        obs_x, obs_y = self.observation_model.range_bearing_to_cartesian(
            self.robot_pose, observed_range, observed_bearing
        )

        # Simple averaging for demonstration (in practice, would use Kalman filter)
        landmark.x = (landmark.x * landmark.observed_count + obs_x) / (landmark.observed_count + 1)
        landmark.y = (landmark.y * landmark.observed_count + obs_y) / (landmark.observed_count + 1)
        landmark.observed_count += 1

    def get_map(self) -> Dict[str, Any]:
        """
        Get the current map and trajectory.

        Returns:
            Dictionary containing map and trajectory information
        """
        return {
            "robot_trajectory": [(p.x, p.y) for p in self.poses],
            "landmarks": [(lm.x, lm.y, lm.id) for lm in self.landmarks.values()],
            "current_pose": (self.robot_pose.x, self.robot_pose.y, self.robot_pose.theta),
            "landmark_count": len(self.landmarks),
            "trajectory_length": len(self.poses),
            "time_elapsed": self.time
        }

    def get_localization_accuracy(self) -> float:
        """
        Calculate a simple measure of localization accuracy.

        Returns:
            Estimated accuracy (lower is better)
        """
        if len(self.poses) < 2:
            return float('inf')

        # Calculate accumulated error based on control consistency
        total_error = 0.0
        for i in range(1, len(self.poses)):
            # Distance between consecutive poses should match expected motion
            expected_distance = 0.1 * 0.5  # Assuming constant slow motion for demo
            actual_distance = self.poses[i].distance_to(self.poses[i-1])
            total_error += abs(actual_distance - expected_distance)

        return total_error / len(self.poses) if self.poses else float('inf')


class SLAMSimulator:
    """
    Simulates a SLAM scenario with ground truth for comparison.
    """

    def __init__(self) -> None:
        self.slam = SimpleSLAM()
        self.ground_truth_landmarks: List[Tuple[float, float]] = []
        self.ground_truth_trajectory: List[Pose] = [Pose(0.0, 0.0, 0.0)]
        self._setup_environment()

    def _setup_environment(self) -> None:
        """Set up the simulated environment with landmarks."""
        # Create a square room with landmarks at corners and center
        self.ground_truth_landmarks = [
            (0.0, 0.0),    # Bottom-left
            (5.0, 0.0),    # Bottom-right
            (5.0, 5.0),    # Top-right
            (0.0, 5.0),    # Top-left
            (2.5, 2.5),    # Center
            (1.0, 1.0),    # Interior landmark 1
            (4.0, 1.0),    # Interior landmark 2
            (1.0, 4.0),    # Interior landmark 3
        ]

    def run_simulation_step(self, control_input: Tuple[float, float]) -> Dict[str, Any]:
        """
        Run one step of the SLAM simulation.

        Args:
            control_input: (linear_velocity, angular_velocity)

        Returns:
            Dictionary with simulation results
        """
        # Move robot in simulation
        true_pose = self._move_true_robot(control_input)
        self.ground_truth_trajectory.append(true_pose)

        # Move robot in SLAM system (with noise)
        estimated_pose = self.slam.move_robot(control_input)

        # Observe environment
        observations = self.slam.observe_environment(self.ground_truth_landmarks)

        # Calculate errors
        position_error = math.sqrt(
            (true_pose.x - estimated_pose.x)**2 + (true_pose.y - estimated_pose.y)**2
        )
        orientation_error = abs(true_pose.theta - estimated_pose.theta)

        return {
            "true_pose": true_pose,
            "estimated_pose": estimated_pose,
            "position_error": position_error,
            "orientation_error": orientation_error,
            "observations": observations,
            "landmark_count": len(self.slam.landmarks),
            "trajectory_length": len(self.slam.poses)
        }

    def _move_true_robot(self, control_input: Tuple[float, float]) -> Pose:
        """
        Move the true robot without noise for ground truth.

        Args:
            control_input: (linear_velocity, angular_velocity)

        Returns:
            New true pose
        """
        linear_vel, angular_vel = control_input
        current_pose = self.ground_truth_trajectory[-1]

        if abs(angular_vel) < 1e-5:  # Straight line motion
            new_x = current_pose.x + linear_vel * self.slam.dt * math.cos(current_pose.theta)
            new_y = current_pose.y + linear_vel * self.slam.dt * math.sin(current_pose.theta)
            new_theta = current_pose.theta
        else:  # Circular motion
            radius = linear_vel / angular_vel
            new_x = current_pose.x + radius * (math.sin(current_pose.theta + angular_vel * self.slam.dt) - math.sin(current_pose.theta))
            new_y = current_pose.y + radius * (math.cos(current_pose.theta) - math.cos(current_pose.theta + angular_vel * self.slam.dt))
            new_theta = current_pose.theta + angular_vel * self.slam.dt

        # Normalize angle
        new_theta = ((new_theta + math.pi) % (2 * math.pi)) - math.pi

        return Pose(new_x, new_y, new_theta)

    def get_simulation_state(self) -> Dict[str, Any]:
        """Get the current state of the simulation."""
        slam_map = self.slam.get_map()
        localization_error = self.slam.get_localization_accuracy()

        return {
            "slam_map": slam_map,
            "ground_truth_landmarks": self.ground_truth_landmarks,
            "ground_truth_trajectory": [(p.x, p.y) for p in self.ground_truth_trajectory],
            "localization_accuracy": localization_error,
            "total_simulation_time": self.slam.time
        }


def main() -> None:
    """
    Main function demonstrating SLAM concepts.
    """
    print("Starting conceptual SLAM demonstration for humanoid robot...")
    print("Showing how to build a map while tracking position.\n")

    # Initialize the SLAM simulator
    slam_simulator = SLAMSimulator()

    print("Environment setup:")
    print(f"  Ground truth landmarks: {len(slam_simulator.ground_truth_landmarks)}")
    print(f"  Landmark positions: {slam_simulator.ground_truth_landmarks[:3]}... (showing first 3)")
    print()

    # Define a simple exploration path
    print("Executing exploration path...")
    exploration_commands = [
        # Move in a square pattern to observe landmarks
        (0.3, 0.0),   # Move forward
        (0.3, 0.0),
        (0.3, 0.0),
        (0.0, 0.5),   # Turn right
        (0.3, 0.0),   # Move forward
        (0.3, 0.0),
        (0.3, 0.0),
        (0.0, 0.5),   # Turn right
        (0.3, 0.0),   # Move forward
        (0.3, 0.0),
        (0.3, 0.0),
        (0.0, 0.5),   # Turn right
        (0.3, 0.0),   # Move forward
        (0.3, 0.0),
        (0.3, 0.0),
        (0.0, 0.5),   # Turn right
        # Spiral inward
        (0.2, 0.0),
        (0.0, 0.3),
        (0.2, 0.0),
        (0.0, 0.3),
        (0.15, 0.0),
        (0.0, 0.3),
        (0.15, 0.0),
        (0.0, 0.3),
    ]

    # Track errors over time
    position_errors = []
    orientation_errors = []

    for step, command in enumerate(exploration_commands):
        result = slam_simulator.run_simulation_step(command)

        position_errors.append(result["position_error"])
        orientation_errors.append(result["orientation_error"])

        if step % 5 == 0:  # Print every 5 steps
            print(f"  Step {step + 1:2d}: Pos err={result['position_error']:.2f}m, "
                  f"Orientation err={math.degrees(result['orientation_error']):.1f}°, "
                  f"Landmarks mapped: {result['landmark_count']}")

    print(f"\nExploration completed!")
    print(f"  Total steps: {len(exploration_commands)}")
    print(f"  Final position error: {position_errors[-1]:.2f}m")
    print(f"  Final orientation error: {math.degrees(orientation_errors[-1]):.1f}°")

    # Get final simulation state
    final_state = slam_simulator.get_simulation_state()
    slam_map = final_state["slam_map"]

    print(f"\nFinal SLAM results:")
    print(f"  Estimated landmarks: {slam_map['landmark_count']}")
    print(f"  Trajectory length: {slam_map['trajectory_length']} poses")
    print(f"  Estimated accuracy: {final_state['localization_accuracy']:.3f}")

    # Calculate statistics
    avg_position_error = sum(position_errors) / len(position_errors) if position_errors else 0
    max_position_error = max(position_errors) if position_errors else 0
    avg_orientation_error = sum(orientation_errors) / len(orientation_errors) if orientation_errors else 0

    print(f"\nError statistics:")
    print(f"  Average position error: {avg_position_error:.2f}m")
    print(f"  Maximum position error: {max_position_error:.2f}m")
    print(f"  Average orientation error: {math.degrees(avg_orientation_error):.1f}°")

    # Show map comparison
    print(f"\nMap building results:")
    print(f"  Ground truth landmarks: {len(final_state['ground_truth_landmarks'])}")
    print(f"  SLAM-estimated landmarks: {len(slam_map['landmarks'])}")
    print(f"  Landmark mapping accuracy: {min(1.0, len(slam_map['landmarks']) / len(final_state['ground_truth_landmarks'])):.2f}")

    # Show some landmark positions
    if slam_map['landmarks']:
        print(f"  Sample estimated landmark positions: {slam_map['landmarks'][:3]}")

    # Show trajectory
    print(f"\nTrajectory information:")
    print(f"  Ground truth path length: {len(final_state['ground_truth_trajectory'])}")
    print(f"  Estimated path length: {len(slam_map['robot_trajectory'])}")
    if slam_map['robot_trajectory']:
        start_pos = slam_map['robot_trajectory'][0]
        end_pos = slam_map['robot_trajectory'][-1]
        total_distance = math.sqrt((end_pos[0] - start_pos[0])**2 + (end_pos[1] - start_pos[1])**2)
        print(f"  Estimated start position: ({start_pos[0]:.1f}, {start_pos[1]:.1f})")
        print(f"  Estimated end position: ({end_pos[0]:.1f}, {end_pos[1]:.1f})")
        print(f"  Total estimated travel distance: {total_distance:.1f}m")

    print(f"\nSLAM demonstration completed.")
    print("This shows how humanoid robots can simultaneously map their environment")
    print("and determine their location within it, even with sensor and motion uncertainty.")


if __name__ == "__main__":
    main()