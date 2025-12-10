#!/usr/bin/env python3
"""
Conceptual Embodiment Example

This module demonstrates the concept of embodiment in humanoid robots,
showing how physical form influences perception, cognition, and behavior.
"""

from typing import Dict, List, Tuple, Optional, Any
import time
import math
import random


class BodySchema:
    """
    Represents the robot's internal model of its own body.
    """

    def __init__(self) -> None:
        self.links = {
            "torso": {"length": 0.6, "mass": 5.0, "center_of_mass": (0, 0, 0.3)},
            "head": {"length": 0.2, "mass": 1.0, "center_of_mass": (0, 0, 0.1)},
            "upper_arm_left": {"length": 0.3, "mass": 1.5, "center_of_mass": (0, 0, 0.15)},
            "forearm_left": {"length": 0.25, "mass": 1.0, "center_of_mass": (0, 0, 0.125)},
            "hand_left": {"length": 0.1, "mass": 0.5, "center_of_mass": (0, 0, 0.05)},
            "upper_arm_right": {"length": 0.3, "mass": 1.5, "center_of_mass": (0, 0, 0.15)},
            "forearm_right": {"length": 0.25, "mass": 1.0, "center_of_mass": (0, 0, 0.125)},
            "hand_right": {"length": 0.1, "mass": 0.5, "center_of_mass": (0, 0, 0.05)},
            "thigh_left": {"length": 0.4, "mass": 3.0, "center_of_mass": (0, 0, 0.2)},
            "shin_left": {"length": 0.4, "mass": 2.5, "center_of_mass": (0, 0, 0.2)},
            "foot_left": {"length": 0.25, "mass": 1.0, "center_of_mass": (0.05, 0, 0.02)},
            "thigh_right": {"length": 0.4, "mass": 3.0, "center_of_mass": (0, 0, 0.2)},
            "shin_right": {"length": 0.4, "mass": 2.5, "center_of_mass": (0, 0, 0.2)},
            "foot_right": {"length": 0.25, "mass": 1.0, "center_of_mass": (0.05, 0, 0.02)}
        }

        self.joints = {
            "neck_pitch": {"range": (-0.5, 0.5), "connected_links": ["torso", "head"]},
            "neck_yaw": {"range": (-0.5, 0.5), "connected_links": ["torso", "head"]},
            "shoulder_left_roll": {"range": (-1.5, 1.0), "connected_links": ["torso", "upper_arm_left"]},
            "shoulder_left_pitch": {"range": (-1.5, 1.5), "connected_links": ["torso", "upper_arm_left"]},
            "shoulder_left_yaw": {"range": (-0.5, 1.5), "connected_links": ["torso", "upper_arm_left"]},
            "elbow_left": {"range": (0.0, 1.5), "connected_links": ["upper_arm_left", "forearm_left"]},
            "wrist_left": {"range": (-0.5, 0.5), "connected_links": ["forearm_left", "hand_left"]},
            "shoulder_right_roll": {"range": (-1.0, 1.5), "connected_links": ["torso", "upper_arm_right"]},
            "shoulder_right_pitch": {"range": (-1.5, 1.5), "connected_links": ["torso", "upper_arm_right"]},
            "shoulder_right_yaw": {"range": (-1.5, 0.5), "connected_links": ["torso", "upper_arm_right"]},
            "elbow_right": {"range": (0.0, 1.5), "connected_links": ["upper_arm_right", "forearm_right"]},
            "wrist_right": {"range": (-0.5, 0.5), "connected_links": ["forearm_right", "hand_right"]},
            "hip_left_roll": {"range": (-0.3, 0.3), "connected_links": ["torso", "thigh_left"]},
            "hip_left_pitch": {"range": (-0.5, 1.5), "connected_links": ["torso", "thigh_left"]},
            "hip_left_yaw": {"range": (-0.2, 0.2), "connected_links": ["torso", "thigh_left"]},
            "knee_left": {"range": (0.0, 1.5), "connected_links": ["thigh_left", "shin_left"]},
            "ankle_left_pitch": {"range": (-0.3, 0.3), "connected_links": ["shin_left", "foot_left"]},
            "ankle_left_roll": {"range": (-0.2, 0.2), "connected_links": ["shin_left", "foot_left"]},
            "hip_right_roll": {"range": (-0.3, 0.3), "connected_links": ["torso", "thigh_right"]},
            "hip_right_pitch": {"range": (-0.5, 1.5), "connected_links": ["torso", "thigh_right"]},
            "hip_right_yaw": {"range": (-0.2, 0.2), "connected_links": ["torso", "thigh_right"]},
            "knee_right": {"range": (0.0, 1.5), "connected_links": ["thigh_right", "shin_right"]},
            "ankle_right_pitch": {"range": (-0.3, 0.3), "connected_links": ["shin_right", "foot_right"]},
            "ankle_right_roll": {"range": (-0.2, 0.2), "connected_links": ["shin_right", "foot_right"]}
        }

        self.mass_center = (0, 0, 0)  # Will be calculated based on configuration

    def update_mass_center(self, joint_angles: Dict[str, float]) -> Tuple[float, float, float]:
        """
        Update the center of mass based on joint configuration.

        Args:
            joint_angles: Current joint angles

        Returns:
            Global center of mass position
        """
        total_mass = sum(link["mass"] for link in self.links.values())
        if total_mass == 0:
            return (0, 0, 0)

        weighted_sum = [0.0, 0.0, 0.0]

        # For simplicity, we'll use a basic calculation
        # In reality, this would require forward kinematics
        for link_name, link_props in self.links.items():
            # Approximate position based on typical humanoid stance
            if "foot" in link_name:
                z_pos = 0.02  # Feet on ground
            elif "shin" in link_name:
                z_pos = 0.2  # Lower legs
            elif "thigh" in link_name:
                z_pos = 0.4  # Upper legs
            elif "torso" in link_name:
                z_pos = 0.6  # Torso
            elif "head" in link_name:
                z_pos = 1.6  # Head
            else:
                z_pos = 0.8  # Arms and other parts

            weighted_sum[0] += 0 * link_props["mass"]  # Simplified x position
            weighted_sum[1] += 0 * link_props["mass"]  # Simplified y position
            weighted_sum[2] += z_pos * link_props["mass"]  # Z position

        com = (
            weighted_sum[0] / total_mass,
            weighted_sum[1] / total_mass,
            weighted_sum[2] / total_mass
        )

        self.mass_center = com
        return com


class SensorimotorController:
    """
    Manages the sensorimotor loop that connects perception to action.
    """

    def __init__(self) -> None:
        self.sensory_buffer: Dict[str, Any] = {}
        self.motor_commands: List[Dict[str, float]] = []
        self.action_history: List[Tuple[str, float]] = []  # action, timestamp

    def process_sensory_input(self, sensor_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process raw sensory data into meaningful percepts.

        Args:
            sensor_data: Raw sensor readings

        Returns:
            Processed perceptual information
        """
        processed = {}

        # Process visual input
        if "camera" in sensor_data:
            processed["visual"] = self._process_visual_input(sensor_data["camera"])

        # Process proprioceptive input (joint angles, etc.)
        if "encoders" in sensor_data:
            processed["proprioceptive"] = sensor_data["encoders"].copy()

        # Process vestibular input (balance, orientation)
        if "imu" in sensor_data:
            imu_data = sensor_data["imu"]
            processed["vestibular"] = {
                "orientation": imu_data["orientation"],
                "angular_velocity": imu_data["angular_velocity"],
                "linear_acceleration": imu_data["linear_acceleration"]
            }

        # Process tactile input
        if "force_torque" in sensor_data:
            processed["tactile"] = sensor_data["force_torque"]

        self.sensory_buffer = processed
        return processed

    def _process_visual_input(self, camera_data: List[List[int]]) -> Dict[str, Any]:
        """Process visual input to extract meaningful information."""
        # Simplified visual processing
        height, width = len(camera_data), len(camera_data[0]) if camera_data else (0, 0)

        # Calculate simple features
        avg_brightness = 0
        if height > 0 and width > 0:
            total_pixels = 0
            for row in camera_data:
                avg_brightness += sum(row)
                total_pixels += len(row)
            avg_brightness = avg_brightness / total_pixels if total_pixels > 0 else 0

        # Detect simple edges (simplified)
        edges = 0
        for i in range(1, height):
            for j in range(1, width):
                if abs(camera_data[i][j] - camera_data[i-1][j]) > 50:
                    edges += 1
                if abs(camera_data[i][j] - camera_data[i][j-1]) > 50:
                    edges += 1

        return {
            "avg_brightness": avg_brightness,
            "edge_count": edges,
            "image_shape": (height, width),
            "detected_objects": []  # Would be populated by object recognition
        }

    def generate_motor_commands(self, goal: str, current_state: Dict[str, Any]) -> List[Dict[str, float]]:
        """
        Generate motor commands to achieve a given goal based on current state.

        Args:
            goal: Desired goal or behavior
            current_state: Current state of the robot

        Returns:
            List of motor commands
        """
        commands = []

        if goal == "reach_forward":
            # Generate commands to reach forward with right arm
            commands.append({
                "shoulder_right_pitch": 0.8,  # Lift arm
                "elbow_right": 1.0,           # Extend elbow partially
                "shoulder_right_yaw": 0.0     # Keep arm centered
            })
        elif goal == "balance":
            # Generate balance commands based on orientation
            if "vestibular" in self.sensory_buffer:
                orientation = self.sensory_buffer["vestibular"]["orientation"]
                # Simplified balance response
                commands.append({
                    "ankle_left_pitch": -orientation[2] * 0.5,
                    "ankle_right_pitch": -orientation[2] * 0.5,
                    "ankle_left_roll": -orientation[1] * 0.5,
                    "ankle_right_roll": -orientation[1] * 0.5
                })
        elif goal == "look_at_target":
            # Generate neck movement commands
            commands.append({
                "neck_pitch": 0.1,
                "neck_yaw": 0.2
            })
        elif goal == "walk_forward":
            # Generate simplified walking pattern
            commands.append({
                "hip_left_pitch": 0.2,
                "knee_left": 0.8,
                "ankle_left_pitch": -0.1,
                "hip_right_pitch": 0.1,
                "knee_right": 0.9,
                "ankle_right_pitch": -0.1
            })

        self.motor_commands = commands
        return commands

    def execute_motor_commands(self, commands: List[Dict[str, float]]) -> Dict[str, float]:
        """
        Simulate execution of motor commands.

        Args:
            commands: List of motor commands to execute

        Returns:
            Simulated resulting joint positions
        """
        # In a real robot, this would send commands to actuators
        # For simulation, we'll just return the command values as new positions
        result = {}
        for cmd in commands:
            result.update(cmd)

        # Add some noise to simulate real actuator behavior
        noisy_result = {}
        for joint, angle in result.items():
            noisy_angle = angle + random.uniform(-0.02, 0.02)
            # Apply joint limits
            if joint in ["hip_left_pitch", "hip_right_pitch"]:
                noisy_angle = max(-0.5, min(1.5, noisy_angle))
            elif joint in ["knee_left", "knee_right"]:
                noisy_angle = max(0.0, min(1.5, noisy_angle))
            elif "ankle" in joint:
                noisy_angle = max(-0.3, min(0.3, noisy_angle))
            elif "shoulder" in joint:
                noisy_angle = max(-1.5, min(1.5, noisy_angle))
            elif "elbow" in joint:
                noisy_angle = max(0.0, min(1.5, noisy_angle))

            noisy_result[joint] = noisy_angle

        return noisy_result


class EmbodiedCognition:
    """
    Demonstrates how embodiment influences cognition and behavior.
    """

    def __init__(self) -> None:
        self.body_schema = BodySchema()
        self.sensorimotor_controller = SensorimotorController()
        self.internal_state = {
            "energy_level": 1.0,  # 0.0 to 1.0
            "balance_confidence": 0.9,  # 0.0 to 1.0
            "curiosity": 0.7,  # 0.0 to 1.0
            "goal_directedness": 0.8  # 0.0 to 1.0
        }

    def perceive_environment(self, sensor_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process sensory information in the context of the body's capabilities.

        Args:
            sensor_data: Raw sensor data from the robot

        Returns:
            Interpretation of the environment relative to the robot's body
        """
        processed_sensory = self.sensorimotor_controller.process_sensory_input(sensor_data)

        # Interpret environment relative to robot's physical capabilities
        interpretation = {
            "navigable_space": self._interpret_navigable_space(processed_sensory),
            "graspable_objects": self._interpret_graspable_objects(processed_sensory),
            "balance_challenges": self._interpret_balance_challenges(processed_sensory),
            "affordances": self._interpret_affordances(processed_sensory)
        }

        return interpretation

    def _interpret_navigable_space(self, sensory: Dict[str, Any]) -> Dict[str, float]:
        """Interpret space in terms of the robot's mobility."""
        # Based on leg length and joint ranges, determine navigable space
        leg_length = self.body_schema.links["thigh_left"]["length"] + self.body_schema.links["shin_left"]["length"]
        max_step_height = leg_length * 0.3  # Simplified: can step over obstacles up to 30% of leg length

        # Simulated navigable space based on LIDAR-like data (simplified)
        free_space = {
            "forward": random.uniform(0.5, 2.0),  # Distance to obstacle in front
            "max_step_height": max_step_height,
            "traversable_slope": 15.0  # Max slope in degrees the robot can handle
        }

        return free_space

    def _interpret_graspable_objects(self, sensory: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Interpret objects in terms of the robot's manipulation capabilities."""
        graspable = []

        # For demonstration, create some simulated objects
        # In reality, this would come from perception system
        if "visual" in sensory:
            # Simulate detecting objects within reach
            arm_length = (self.body_schema.links["upper_arm_left"]["length"] +
                         self.body_schema.links["forearm_left"]["length"])

            for i in range(2):  # Simulate 2 objects
                obj_distance = random.uniform(0.2, arm_length + 0.1)
                if obj_distance <= arm_length + 0.1:  # Within reach
                    obj = {
                        "id": f"obj_{i}",
                        "distance": obj_distance,
                        "size": random.uniform(0.05, 0.2),  # Object size in meters
                        "graspability": self._calculate_graspability(obj_distance),
                        "required_posture": "reach_forward"
                    }
                    graspable.append(obj)

        return graspable

    def _calculate_graspability(self, distance: float) -> float:
        """Calculate how graspable an object is based on distance."""
        arm_length = (self.body_schema.links["upper_arm_left"]["length"] +
                     self.body_schema.links["forearm_left"]["length"])
        max_reach = arm_length + 0.1  # Small extension beyond arm length

        if distance > max_reach:
            return 0.0  # Not graspable
        else:
            # Graspability decreases with distance (closest is most graspable)
            return 1.0 - (distance / max_reach)

    def _interpret_balance_challenges(self, sensory: Dict[str, Any]) -> Dict[str, float]:
        """Interpret the environment in terms of balance challenges."""
        challenges = {"stability": 0.9}  # Default high stability

        if "vestibular" in sensory:
            # Analyze orientation data for balance challenges
            orientation = sensory["vestibular"]["orientation"]
            # Simplified: if orientation deviates significantly, it's a challenge
            deviation = abs(orientation[1]) + abs(orientation[2])  # Roll + pitch
            challenges["stability"] = max(0.1, 1.0 - deviation)

        if "tactile" in sensory:
            # Analyze force/torque data for balance challenges
            forces = sensory["tactile"]
            for foot, force_data in forces.items():
                z_force = force_data[2]  # Z is upward force
                # If force is too low or too high, it's a balance challenge
                if z_force < 200 or z_force > 800:  # Outside normal range
                    challenges["stability"] = min(challenges["stability"], 0.5)

        return challenges

    def _interpret_affordances(self, sensory: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Interpret what actions the environment affords based on the robot's body."""
        affordances = []

        # Affordances are action possibilities provided by the environment
        # given the robot's physical capabilities

        # Walking affordance
        if "navigable_space" in self.internal_state:
            free_space = self.internal_state["navigable_space"]
            if free_space["forward"] > 0.3:  # Enough space to take a step
                affordances.append({
                    "action": "walk_forward",
                    "confidence": 0.9,
                    "energy_cost": 0.1
                })

        # Reaching affordance
        graspable_objects = self._interpret_graspable_objects(sensory)
        if graspable_objects:
            affordances.append({
                "action": "reach_and_grasp",
                "confidence": 0.8,
                "energy_cost": 0.2,
                "target_objects": [obj["id"] for obj in graspable_objects]
            })

        # Looking affordance (always available)
        affordances.append({
            "action": "look_around",
            "confidence": 1.0,
            "energy_cost": 0.01
        })

        return affordances

    def decide_action(self, environmental_interpretation: Dict[str, Any]) -> str:
        """
        Decide on an action based on environmental interpretation and internal state.

        Args:
            environmental_interpretation: Interpretation of environment relative to body

        Returns:
            Selected action to perform
        """
        # Get available affordances
        affordances = environmental_interpretation.get("affordances", [])

        if not affordances:
            return "idle"  # No actions available

        # Consider internal state when selecting action
        # Higher curiosity might lead to exploration
        # Lower energy might lead to rest
        # Lower balance confidence might lead to stabilization

        # For demonstration, select action probabilistically based on confidence
        # and considering internal state
        valid_affordances = [a for a in affordances if a["confidence"] > 0.3]

        if not valid_affordances:
            return "idle"

        # Adjust preferences based on internal state
        adjusted_affordances = []
        for affordance in valid_affordances:
            score = affordance["confidence"]

            # Adjust based on energy level
            if "energy" in affordance.get("energy_cost", 0):
                score *= self.internal_state["energy_level"]

            # Adjust based on balance confidence if it's a movement action
            if affordance["action"] in ["walk_forward", "reach_and_grasp"]:
                score *= self.internal_state["balance_confidence"]

            # Adjust based on curiosity if it's an exploratory action
            if affordance["action"] in ["look_around", "reach_and_grasp"]:
                score *= self.internal_state["curiosity"]

            adjusted_affordances.append((affordance, score))

        # Select the highest-scoring affordance
        best_affordance = max(adjusted_affordances, key=lambda x: x[1])
        return best_affordance[0]["action"]


def main() -> None:
    """
    Main function demonstrating embodiment concepts.
    """
    print("Starting conceptual embodiment demonstration for humanoid robot...")
    print("Showing how physical form influences perception and action.\n")

    # Initialize the embodied cognition system
    embodied_system = EmbodiedCognition()

    # Simulate initial sensor data
    initial_sensor_data = {
        "camera": [[random.randint(0, 255) for _ in range(10)] for _ in range(10)],
        "encoders": {
            "hip_left_pitch": 0.1, "knee_left": 1.0, "ankle_left_pitch": 0.0,
            "hip_right_pitch": 0.1, "knee_right": 1.0, "ankle_right_pitch": 0.0,
            "shoulder_left_pitch": 0.0, "elbow_left": 0.0,
            "shoulder_right_pitch": 0.0, "elbow_right": 0.0,
            "neck_pitch": 0.0, "neck_yaw": 0.0
        },
        "imu": {
            "orientation": (1.0, 0.0, 0.0, 0.0),  # No rotation (quaternion)
            "angular_velocity": (0.0, 0.0, 0.0),
            "linear_acceleration": (0.0, 0.0, 9.81)  # Gravity
        },
        "force_torque": {
            "left_foot": (0, 0, 500),  # Weight on left foot
            "right_foot": (0, 0, 500)  # Weight on right foot
        }
    }

    print("Initial robot state:")
    print(f"  Center of mass: {embodied_system.body_schema.update_mass_center(initial_sensor_data['encoders'])}")
    print(f"  Internal state: energy={embodied_system.internal_state['energy_level']:.1f}, "
          f"balance={embodied_system.internal_state['balance_confidence']:.1f}, "
          f"curiosity={embodied_system.internal_state['curiosity']:.1f}")
    print()

    # Process initial environmental perception
    print("Processing environmental perception based on body schema...")
    environment_interpretation = embodied_system.perceive_environment(initial_sensor_data)

    print("Environmental interpretation:")
    print(f"  Navigable space: forward={environment_interpretation['navigable_space']['forward']:.2f}m, "
          f"max step height={environment_interpretation['navigable_space']['max_step_height']:.2f}m")
    print(f"  Graspable objects: {len(environment_interpretation['graspable_objects'])}")
    print(f"  Balance stability: {environment_interpretation['balance_challenges']['stability']:.2f}")
    print(f"  Available affordances: {[a['action'] for a in environment_interpretation['affordances']]}")
    print()

    # Decide on action based on interpretation
    selected_action = embodied_system.decide_action(environment_interpretation)
    print(f"Selected action: {selected_action}")

    # Execute the action
    print(f"\nExecuting '{selected_action}'...")
    motor_commands = embodied_system.sensorimotor_controller.generate_motor_commands(
        selected_action, initial_sensor_data
    )
    print(f"  Generated {len(motor_commands)} motor command sets")

    # Simulate command execution
    if motor_commands:
        resulting_positions = embodied_system.sensorimotor_controller.execute_motor_commands(motor_commands)
        print(f"  Resulting joint positions: {len(resulting_positions)} joints affected")

    print()

    # Simulate a few more cycles to show the embodied loop
    print("Simulating embodied cognition loop for 3 more cycles...")
    current_sensors = initial_sensor_data
    for cycle in range(3):
        print(f"\nCycle {cycle + 1}:")

        # Update some sensor values to simulate movement
        current_sensors["encoders"]["hip_left_pitch"] += random.uniform(-0.1, 0.1)
        current_sensors["encoders"]["knee_left"] += random.uniform(-0.1, 0.1)
        current_sensors["imu"]["orientation"] = (
            1.0,
            random.uniform(-0.05, 0.05),  # Small roll
            random.uniform(-0.05, 0.05),  # Small pitch
            random.uniform(-0.01, 0.01)   # Small yaw
        )

        # Process new environmental perception
        new_interpretation = embodied_system.perceive_environment(current_sensors)

        # Decide new action
        new_action = embodied_system.decide_action(new_interpretation)
        print(f"  New action: {new_action}")

        # Execute action
        new_motor_commands = embodied_system.sensorimotor_controller.generate_motor_commands(
            new_action, current_sensors
        )
        if new_motor_commands:
            new_positions = embodied_system.sensorimotor_controller.execute_motor_commands(new_motor_commands)
            print(f"  Updated {len(new_positions)} joint positions")

        # Update internal state slightly
        embodied_system.internal_state["energy_level"] = max(0.5,
            embodied_system.internal_state["energy_level"] - random.uniform(0.01, 0.05))

    print(f"\nEmbodiment demonstration completed.")
    print(f"The robot's physical form shaped its perception of the world")
    print(f"and influenced which actions seemed possible or appropriate.")


if __name__ == "__main__":
    main()