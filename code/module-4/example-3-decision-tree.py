#!/usr/bin/env python3
"""
Decision Tree Example

This module demonstrates conceptual decision trees for humanoid robots,
showing how to make decisions based on sensor inputs and environmental conditions.
"""

from typing import Dict, List, Tuple, Optional, Any, Union
import math
import random
import time
from enum import Enum


class DecisionOutcome(Enum):
    """Possible outcomes of a decision."""
    SUCCESS = "success"
    FAILURE = "failure"
    UNCERTAIN = "uncertain"
    PARTIAL = "partial"


class SensorType(Enum):
    """Types of sensors used in decision making."""
    CAMERA = "camera"
    LIDAR = "lidar"
    IMU = "imu"
    FORCE_TORQUE = "force_torque"
    JOINT_ENCODERS = "joint_encoders"
    MICROPHONE = "microphone"


class DecisionNode:
    """
    Represents a node in a decision tree.
    """
    def __init__(self, name: str, condition_func=None, value: Any = None) -> None:
        self.name = name
        self.condition_func = condition_func  # Function that determines branching
        self.value = value  # Value for leaf nodes
        self.children: Dict[Any, 'DecisionNode'] = {}  # Child nodes based on condition results
        self.sensor_requirements: List[SensorType] = []  # Sensors needed for this decision
        self.confidence = 1.0  # Confidence in this decision path

    def add_child(self, condition_result: Any, child_node: 'DecisionNode') -> None:
        """Add a child node for a specific condition result."""
        self.children[condition_result] = child_node

    def evaluate(self, sensor_data: Dict[SensorType, Any]) -> Union['DecisionNode', Any]:
        """
        Evaluate this node and return the appropriate child or value.

        Args:
            sensor_data: Dictionary mapping sensor types to their data

        Returns:
            Child node or value based on condition evaluation
        """
        if self.condition_func:
            result = self.condition_func(sensor_data)
            return self.children.get(result, self.children.get("default", self.value))
        else:
            return self.value


class DecisionTree:
    """
    Represents a complete decision tree for a specific behavioral context.
    """
    def __init__(self, name: str, root_node: DecisionNode) -> None:
        self.name = name
        self.root = root_node
        self.created_at = time.time()
        self.last_updated = time.time()

    def make_decision(self, sensor_data: Dict[SensorType, Any]) -> Dict[str, Any]:
        """
        Navigate the decision tree to make a decision based on sensor data.

        Args:
            sensor_data: Dictionary mapping sensor types to their data

        Returns:
            Dictionary with decision result and metadata
        """
        current_node = self.root
        path = [current_node.name]
        confidence = 1.0

        while isinstance(current_node, DecisionNode) and current_node.children:
            # Check if we have required sensor data
            missing_sensors = []
            for req_sensor in current_node.sensor_requirements:
                if req_sensor not in sensor_data:
                    missing_sensors.append(req_sensor)

            if missing_sensors:
                return {
                    "decision": "insufficient_data",
                    "path": path,
                    "missing_sensors": missing_sensors,
                    "confidence": 0.0,
                    "timestamp": time.time()
                }

            # Evaluate the current node
            result = current_node.evaluate(sensor_data)
            if isinstance(result, DecisionNode):
                current_node = result
                path.append(current_node.name)
                confidence *= current_node.confidence
            else:
                # Reached a leaf node with a value
                return {
                    "decision": result,
                    "path": path,
                    "confidence": confidence,
                    "timestamp": time.time()
                }

        return {
            "decision": current_node.value,
            "path": path,
            "confidence": confidence,
            "timestamp": time.time()
        }


class DecisionEngine:
    """
    Manages multiple decision trees and coordinates decision making.
    """
    def __init__(self) -> None:
        self.decision_trees: Dict[str, DecisionTree] = {}
        self.sensor_data: Dict[SensorType, Any] = {}
        self.decision_history: List[Dict[str, Any]] = []
        self.confidence_threshold = 0.7  # Minimum confidence for action

    def register_decision_tree(self, tree: DecisionTree) -> None:
        """Register a decision tree with the engine."""
        self.decision_trees[tree.name] = tree

    def update_sensor_data(self, sensor_type: SensorType, data: Any) -> None:
        """Update sensor data for a specific sensor type."""
        self.sensor_data[sensor_type] = data

    def make_behavior_decision(self, behavior_context: str) -> Dict[str, Any]:
        """
        Make a decision for a specific behavior context.

        Args:
            behavior_context: Name of the behavior context (e.g., "navigation", "manipulation")

        Returns:
            Decision result dictionary
        """
        if behavior_context not in self.decision_trees:
            return {
                "decision": "no_tree_found",
                "behavior_context": behavior_context,
                "confidence": 0.0,
                "timestamp": time.time()
            }

        tree = self.decision_trees[behavior_context]
        result = tree.make_decision(self.sensor_data)

        # Add to history
        result["behavior_context"] = behavior_context
        self.decision_history.append(result)

        return result

    def get_decision_statistics(self) -> Dict[str, Any]:
        """Get statistics about decision making."""
        total_decisions = len(self.decision_history)
        high_confidence = len([d for d in self.decision_history if d.get("confidence", 0) >= self.confidence_threshold])
        behavior_counts = {}

        for decision in self.decision_history:
            context = decision.get("behavior_context", "unknown")
            behavior_counts[context] = behavior_counts.get(context, 0) + 1

        return {
            "total_decisions": total_decisions,
            "high_confidence_decisions": high_confidence,
            "confidence_rate": high_confidence / total_decisions if total_decisions > 0 else 0,
            "behavior_distribution": behavior_counts,
            "active_sensors": list(self.sensor_data.keys())
        }


def create_navigation_decision_tree() -> DecisionTree:
    """
    Create a decision tree for navigation decisions.
    """
    def evaluate_obstacle_distance(sensor_data: Dict[SensorType, Any]) -> str:
        """Evaluate obstacle distance from LIDAR data."""
        lidar_data = sensor_data.get(SensorType.LIDAR, [])
        if not lidar_data:
            return "unknown"

        min_distance = min(lidar_data) if lidar_data else float('inf')

        if min_distance < 0.5:
            return "close"
        elif min_distance < 2.0:
            return "medium"
        else:
            return "far"

    def evaluate_human_proximity(sensor_data: Dict[SensorType, Any]) -> str:
        """Evaluate if humans are nearby using camera data."""
        camera_data = sensor_data.get(SensorType.CAMERA, {})
        humans_detected = camera_data.get("humans", 0)

        if humans_detected > 0:
            return "nearby"
        else:
            return "none"

    # Create nodes
    root = DecisionNode("navigate", evaluate_obstacle_distance)
    root.sensor_requirements = [SensorType.LIDAR]

    # Obstacle distance branches
    close_obstacle = DecisionNode("close_obstacle")
    medium_obstacle = DecisionNode("medium_obstacle")
    far_obstacle = DecisionNode("far_obstacle")
    unknown_obstacle = DecisionNode("unknown_obstacle")

    # For close obstacles, check for humans
    close_obstacle.condition_func = evaluate_human_proximity
    close_obstacle.sensor_requirements = [SensorType.CAMERA]

    # Close obstacle sub-branches
    close_with_human = DecisionNode("stop_and_wait", "STOP", 0.9)
    close_no_human = DecisionNode("careful_navigation", "SLOW_DOWN", 0.8)

    # Connect close obstacle branches
    close_obstacle.add_child("nearby", close_with_human)
    close_obstacle.add_child("none", close_no_human)
    close_obstacle.add_child("default", close_no_human)

    # Medium obstacle branches
    medium_obstacle.value = "ADJUST_PATH"
    medium_obstacle.confidence = 0.7

    # Far obstacle branches
    far_obstacle.value = "CONTINUE_NORMAL"
    far_obstacle.confidence = 0.9

    # Unknown obstacle branches
    unknown_obstacle.value = "PROCEED_CAUTIOUSLY"
    unknown_obstacle.confidence = 0.5

    # Connect root to branches
    root.add_child("close", close_obstacle)
    root.add_child("medium", medium_obstacle)
    root.add_child("far", far_obstacle)
    root.add_child("default", unknown_obstacle)

    return DecisionTree("navigation", root)


def create_balance_decision_tree() -> DecisionTree:
    """
    Create a decision tree for balance-related decisions.
    """
    def evaluate_imu_data(sensor_data: Dict[SensorType, Any]) -> str:
        """Evaluate IMU data for balance state."""
        imu_data = sensor_data.get(SensorType.IMU, {})
        roll = imu_data.get("roll", 0)
        pitch = imu_data.get("pitch", 0)
        angular_velocity = imu_data.get("angular_velocity", (0, 0, 0))

        # Calculate tilt magnitude
        tilt_magnitude = math.sqrt(roll**2 + pitch**2)
        rotation_magnitude = math.sqrt(sum(v**2 for v in angular_velocity))

        if tilt_magnitude > 0.5 or rotation_magnitude > 1.0:  # High tilt or rotation
            return "unstable"
        elif tilt_magnitude > 0.2 or rotation_magnitude > 0.5:  # Moderate tilt or rotation
            return "caution"
        else:
            return "stable"

    def evaluate_force_data(sensor_data: Dict[SensorType, Any]) -> str:
        """Evaluate force/torque sensor data."""
        force_data = sensor_data.get(SensorType.FORCE_TORQUE, {})
        left_foot_force = force_data.get("left_foot", (0, 0, 0))
        right_foot_force = force_data.get("right_foot", (0, 0, 0))

        # Calculate total vertical force
        total_force = abs(left_foot_force[2]) + abs(right_foot_force[2])
        force_imbalance = abs(abs(left_foot_force[2]) - abs(right_foot_force[2]))

        if total_force < 100:  # Very low contact force
            return "airborne"
        elif force_imbalance > 200:  # Significant imbalance
            return "unbalanced"
        else:
            return "balanced"

    # Create nodes
    root = DecisionNode("balance_check", evaluate_imu_data)
    root.sensor_requirements = [SensorType.IMU]

    unstable_node = DecisionNode("unstable_assessment", evaluate_force_data)
    unstable_node.sensor_requirements = [SensorType.FORCE_TORQUE]

    caution_node = DecisionNode("caution_assessment", evaluate_force_data)
    caution_node.sensor_requirements = [SensorType.FORCE_TORQUE]

    stable_node = DecisionNode("maintain_balance", "STABLE", 0.95)

    # Unstable sub-branches
    airborne = DecisionNode("abort_motion", "ABORT", 0.9)
    unbalanced_force = DecisionNode("correct_balance", "ADJUST_POSTURE", 0.85)
    balanced_force = DecisionNode("minor_adjustment", "FINE_TUNE", 0.7)

    unstable_node.add_child("airborne", airborne)
    unstable_node.add_child("unbalanced", unbalanced_force)
    unstable_node.add_child("balanced", balanced_force)
    unstable_node.add_child("default", balanced_force)

    # Caution sub-branches
    caution_node.add_child("airborne", airborne)
    caution_node.add_child("unbalanced", DecisionNode("prepare_correction", "PREPARE_BALANCE", 0.7))
    caution_node.add_child("balanced", DecisionNode("monitor_closely", "MONITOR", 0.8))
    caution_node.add_child("default", DecisionNode("continue_cautiously", "CAUTIOUS", 0.75))

    # Connect root to branches
    root.add_child("unstable", unstable_node)
    root.add_child("caution", caution_node)
    root.add_child("stable", stable_node)
    root.add_child("default", stable_node)

    return DecisionTree("balance", root)


def create_interaction_decision_tree() -> DecisionTree:
    """
    Create a decision tree for human interaction decisions.
    """
    def evaluate_audio_presence(sensor_data: Dict[SensorType, Any]) -> str:
        """Evaluate if audio input indicates human presence."""
        audio_data = sensor_data.get(SensorType.MICROPHONE, {})
        sound_level = audio_data.get("sound_level", 0)
        speech_detected = audio_data.get("speech_detected", False)

        if speech_detected:
            return "speech"
        elif sound_level > 0.5:  # Above ambient noise
            return "sound"
        else:
            return "quiet"

    def evaluate_visual_attention(sensor_data: Dict[SensorType, Any]) -> str:
        """Evaluate if humans are paying attention."""
        camera_data = sensor_data.get(SensorType.CAMERA, {})
        humans_detected = camera_data.get("humans", 0)
        looking_at_robot = camera_data.get("looking_at_robot", 0)

        if humans_detected == 0:
            return "no_humans"
        elif looking_at_robot / max(humans_detected, 1) > 0.5:  # Majority looking at robot
            return "attention"
        else:
            return "present"

    # Create nodes
    root = DecisionNode("interaction_check", evaluate_audio_presence)
    root.sensor_requirements = [SensorType.MICROPHONE]

    speech_node = DecisionNode("speech_assessment", evaluate_visual_attention)
    speech_node.sensor_requirements = [SensorType.CAMERA]

    sound_node = DecisionNode("sound_assessment", evaluate_visual_attention)
    sound_node.sensor_requirements = [SensorType.CAMERA]

    quiet_node = DecisionNode("no_interaction", "IGNORE", 0.9)

    # Speech sub-branches
    speech_attention = DecisionNode("respond_to_speech", "RESPOND", 0.9)
    speech_present = DecisionNode("acknowledge_sound", "ACKNOWLEDGE", 0.7)
    speech_no_humans = DecisionNode("ignore_sound", "IGNORE", 0.95)

    speech_node.add_child("attention", speech_attention)
    speech_node.add_child("present", speech_present)
    speech_node.add_child("no_humans", speech_no_humans)
    speech_node.add_child("default", speech_present)

    # Sound sub-branches
    sound_attention = DecisionNode("check_sound", "INVESTIGATE", 0.6)
    sound_present = DecisionNode("monitor_sound", "MONITOR", 0.5)
    sound_no_humans = DecisionNode("ignore_sound", "IGNORE", 0.9)

    sound_node.add_child("attention", sound_attention)
    sound_node.add_child("present", sound_present)
    sound_node.add_child("no_humans", sound_no_humans)
    sound_node.add_child("default", sound_present)

    # Connect root to branches
    root.add_child("speech", speech_node)
    root.add_child("sound", sound_node)
    root.add_child("quiet", quiet_node)
    root.add_child("default", quiet_node)

    return DecisionTree("interaction", root)


class DecisionSimulator:
    """
    Simulates decision making in various scenarios.
    """
    def __init__(self) -> None:
        self.decision_engine = DecisionEngine()

        # Register decision trees
        self.decision_engine.register_decision_tree(create_navigation_decision_tree())
        self.decision_engine.register_decision_tree(create_balance_decision_tree())
        self.decision_engine.register_decision_tree(create_interaction_decision_tree())

        self.simulation_time = 0.0
        self.scenario_count = 0

    def run_scenario(self, scenario_name: str, sensor_inputs: Dict[SensorType, Any]) -> Dict[str, Any]:
        """
        Run a decision-making scenario with given sensor inputs.

        Args:
            scenario_name: Name of the scenario
            sensor_inputs: Dictionary of sensor data

        Returns:
            Results of the decision making process
        """
        self.scenario_count += 1
        print(f"\nScenario {self.scenario_count}: {scenario_name}")

        # Update sensor data
        for sensor_type, data in sensor_inputs.items():
            self.decision_engine.update_sensor_data(sensor_type, data)

        # Make decisions for different behavior contexts
        contexts = ["navigation", "balance", "interaction"]
        results = {}

        for context in contexts:
            result = self.decision_engine.make_behavior_decision(context)
            results[context] = result
            print(f"  {context}: {result.get('decision', 'unknown')} (confidence: {result.get('confidence', 0):.2f})")

        return {
            "scenario": scenario_name,
            "sensor_inputs": sensor_inputs,
            "decisions": results,
            "timestamp": time.time()
        }

    def get_simulation_summary(self) -> Dict[str, Any]:
        """Get a summary of the simulation."""
        return {
            "total_scenarios": self.scenario_count,
            "decision_statistics": self.decision_engine.get_decision_statistics(),
            "registered_trees": list(self.decision_engine.decision_trees.keys()),
            "simulation_time": self.simulation_time
        }


def main() -> None:
    """
    Main function demonstrating decision trees.
    """
    print("Starting decision tree demonstration for humanoid robot...")
    print("Showing how to make decisions based on sensor inputs and environmental conditions.\n")

    # Initialize the decision simulator
    simulator = DecisionSimulator()

    print("Registered decision trees:")
    for tree_name in simulator.decision_engine.decision_trees.keys():
        print(f"  - {tree_name}")
    print()

    # Define test scenarios
    scenarios = [
        {
            "name": "Clear path navigation",
            "inputs": {
                SensorType.LIDAR: [3.0, 3.1, 2.9, 3.2, 3.0],  # Clear path
                SensorType.CAMERA: {"humans": 0},
                SensorType.IMU: {"roll": 0.01, "pitch": 0.02, "angular_velocity": (0.01, 0.02, 0.01)},
                SensorType.FORCE_TORQUE: {"left_foot": (10, 5, 400), "right_foot": (-5, 8, 380)},
                SensorType.MICROPHONE: {"sound_level": 0.2, "speech_detected": False}
            }
        },
        {
            "name": "Obstacle avoidance with human present",
            "inputs": {
                SensorType.LIDAR: [0.3, 0.4, 1.5, 2.0, 1.8],  # Close obstacle ahead
                SensorType.CAMERA: {"humans": 1, "looking_at_robot": 1},
                SensorType.IMU: {"roll": 0.05, "pitch": 0.08, "angular_velocity": (0.05, 0.08, 0.02)},
                SensorType.FORCE_TORQUE: {"left_foot": (2, -3, 390), "right_foot": (1, 4, 395)},
                SensorType.MICROPHONE: {"sound_level": 0.4, "speech_detected": True}
            }
        },
        {
            "name": "Balance recovery needed",
            "inputs": {
                SensorType.LIDAR: [2.5, 2.4, 2.6, 2.5, 2.4],
                SensorType.CAMERA: {"humans": 0},
                SensorType.IMU: {"roll": 0.3, "pitch": 0.4, "angular_velocity": (0.8, 0.9, 0.1)},  # Unstable
                SensorType.FORCE_TORQUE: {"left_foot": (50, 30, 200), "right_foot": (-40, -25, 180)},  # Unbalanced
                SensorType.MICROPHONE: {"sound_level": 0.1, "speech_detected": False}
            }
        },
        {
            "name": "Human interaction initiated",
            "inputs": {
                SensorType.LIDAR: [1.5, 1.6, 1.4, 1.7, 1.5],
                SensorType.CAMERA: {"humans": 1, "looking_at_robot": 1},
                SensorType.IMU: {"roll": 0.02, "pitch": 0.03, "angular_velocity": (0.01, 0.01, 0.005)},
                SensorType.FORCE_TORQUE: {"left_foot": (5, 2, 410), "right_foot": (-3, -1, 405)},
                SensorType.MICROPHONE: {"sound_level": 0.8, "speech_detected": True}  # Speech detected
            }
        }
    ]

    # Run scenarios
    scenario_results = []
    for scenario in scenarios:
        result = simulator.run_scenario(scenario["name"], scenario["inputs"])
        scenario_results.append(result)

    print(f"\nAll scenarios completed!")
    print(f"  Total scenarios run: {simulator.scenario_count}")

    # Show decision statistics
    stats = simulator.decision_engine.get_decision_statistics()
    print(f"\nDecision making statistics:")
    print(f"  Total decisions made: {stats['total_decisions']}")
    print(f"  High confidence decisions: {stats['high_confidence_decisions']}")
    print(f"  Confidence rate: {stats['confidence_rate']:.2%}")
    print(f"  Active sensors: {stats['active_sensors']}")
    print(f"  Behavior distribution: {stats['behavior_distribution']}")

    # Show sample decision path from one scenario
    print(f"\nSample decision path from first scenario:")
    first_result = scenario_results[0] if scenario_results else None
    if first_result:
        nav_decision = first_result["decisions"]["navigation"]
        print(f"  Behavior: navigation")
        print(f"  Decision: {nav_decision['decision']}")
        print(f"  Path: {' -> '.join(nav_decision['path'])}")
        print(f"  Confidence: {nav_decision['confidence']:.2f}")

    # Show tree structures
    print(f"\nDecision tree structures:")
    for tree_name, tree in simulator.decision_engine.decision_trees.items():
        print(f"  {tree_name} tree:")
        # For this demo, we'll just show that the trees exist
        # In a real implementation, we might want to show the tree structure
        print(f"    Root node: {tree.root.name}")
        print(f"    Created at: {time.ctime(tree.created_at)}")

    # Show sensor data example
    print(f"\nSample sensor data processed:")
    sample_sensor_data = scenarios[0]["inputs"]
    for sensor_type, data in sample_sensor_data.items():
        print(f"  {sensor_type.value}: {str(data)[:50]}{'...' if len(str(data)) > 50 else ''}")

    # Demonstrate confidence thresholding
    print(f"\nConfidence thresholding example:")
    print(f"  Threshold: {simulator.decision_engine.confidence_threshold}")
    high_conf_results = [
        r for result in scenario_results
        for r in result["decisions"].values()
        if r.get("confidence", 0) >= simulator.decision_engine.confidence_threshold
    ]
    low_conf_results = [
        r for result in scenario_results
        for r in result["decisions"].values()
        if r.get("confidence", 0) < simulator.decision_engine.confidence_threshold
    ]
    print(f"  High confidence decisions: {len(high_conf_results)}")
    print(f"  Low confidence decisions: {len(low_conf_results)}")

    print(f"\nDecision tree demonstration completed.")
    print("This shows how humanoid robots make complex decisions by evaluating")
    print("sensor data through structured decision trees tailored to specific behaviors.")


if __name__ == "__main__":
    main()