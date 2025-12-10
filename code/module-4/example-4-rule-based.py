#!/usr/bin/env python3
"""
Rule-Based Decisions Example

This module demonstrates rule-based decision making for humanoid robots,
showing how to implement and evaluate rules for various behaviors.
"""

from typing import Dict, List, Tuple, Optional, Any, Callable
import math
import random
import time
from enum import Enum
from dataclasses import dataclass


class RulePriority(Enum):
    """Priority levels for rules."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class RuleCategory(Enum):
    """Categories of rules."""
    SAFETY = "safety"
    BALANCE = "balance"
    NAVIGATION = "navigation"
    INTERACTION = "interaction"
    MANIPULATION = "manipulation"


@dataclass
class SensorCondition:
    """
    Represents a condition based on sensor data.
    """
    sensor_type: str
    comparison_operator: str  # ">", "<", ">=", "<=", "==", "!="
    threshold: float
    weight: float = 1.0  # Weight for combining multiple conditions

    def evaluate(self, sensor_data: Dict[str, Any]) -> bool:
        """Evaluate the condition against sensor data."""
        if self.sensor_type not in sensor_data:
            return False

        value = sensor_data[self.sensor_type]

        # Handle special cases for complex sensor data
        if isinstance(value, dict):
            # Extract value from dictionary if needed (e.g., "imu.roll")
            if "." in self.sensor_type:
                parts = self.sensor_type.split(".")
                for part in parts[1:]:
                    if isinstance(value, dict) and part in value:
                        value = value[part]
                    else:
                        return False

        if not isinstance(value, (int, float)):
            return False

        if self.comparison_operator == ">":
            return value > self.threshold
        elif self.comparison_operator == "<":
            return value < self.threshold
        elif self.comparison_operator == ">=":
            return value >= self.threshold
        elif self.comparison_operator == "<=":
            return value <= self.threshold
        elif self.comparison_operator == "==":
            return abs(value - self.threshold) < 0.001  # Account for floating point precision
        elif self.comparison_operator == "!=":
            return abs(value - self.threshold) >= 0.001
        else:
            return False


@dataclass
class RuleAction:
    """
    Represents an action to take when a rule fires.
    """
    name: str
    parameters: Dict[str, Any]
    execution_function: Optional[Callable] = None


class Rule:
    """
    Represents a rule with conditions and actions.
    """
    def __init__(self, name: str, conditions: List[SensorCondition], action: RuleAction,
                 priority: RulePriority = RulePriority.MEDIUM,
                 category: RuleCategory = RuleCategory.NAVIGATION,
                 confidence: float = 1.0) -> None:
        self.name = name
        self.conditions = conditions
        self.action = action
        self.priority = priority
        self.category = category
        self.confidence = confidence
        self.last_triggered = None
        self.trigger_count = 0
        self.enabled = True

    def evaluate(self, sensor_data: Dict[str, Any]) -> bool:
        """
        Evaluate if the rule should fire based on sensor data.

        Args:
            sensor_data: Dictionary of sensor data

        Returns:
            True if all conditions are met
        """
        if not self.enabled:
            return False

        for condition in self.conditions:
            if not condition.evaluate(sensor_data):
                return False

        return True

    def execute(self, sensor_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the rule's action.

        Args:
            sensor_data: Dictionary of sensor data

        Returns:
            Dictionary with execution results
        """
        if self.action.execution_function:
            try:
                result = self.action.execution_function(sensor_data, **self.action.parameters)
                self.last_triggered = time.time()
                self.trigger_count += 1
                return {
                    "success": True,
                    "action": self.action.name,
                    "parameters": self.action.parameters,
                    "result": result,
                    "timestamp": self.last_triggered
                }
            except Exception as e:
                return {
                    "success": False,
                    "action": self.action.name,
                    "parameters": self.action.parameters,
                    "error": str(e),
                    "timestamp": time.time()
                }
        else:
            # Default execution - just return the action parameters
            self.last_triggered = time.time()
            self.trigger_count += 1
            return {
                "success": True,
                "action": self.action.name,
                "parameters": self.action.parameters,
                "result": "Action executed",
                "timestamp": self.last_triggered
            }


class RuleBasedSystem:
    """
    Manages a collection of rules and executes them based on sensor data.
    """
    def __init__(self) -> None:
        self.rules: List[Rule] = []
        self.sensor_data: Dict[str, Any] = {}
        self.execution_history: List[Dict[str, Any]] = []
        self.conflict_resolution_strategy = "priority"  # "priority", "recency", "specificity"

    def add_rule(self, rule: Rule) -> None:
        """Add a rule to the system."""
        self.rules.append(rule)

    def remove_rule(self, rule_name: str) -> bool:
        """Remove a rule by name."""
        for i, rule in enumerate(self.rules):
            if rule.name == rule_name:
                del self.rules[i]
                return True
        return False

    def update_sensor_data(self, sensor_type: str, data: Any) -> None:
        """Update sensor data."""
        self.sensor_data[sensor_type] = data

    def evaluate_rules(self) -> List[Rule]:
        """
        Evaluate all rules and return those that should fire.

        Returns:
            List of rules that should fire, sorted by priority
        """
        active_rules = []

        for rule in self.rules:
            if rule.evaluate(self.sensor_data):
                active_rules.append(rule)

        # Sort by priority (and potentially other factors based on strategy)
        if self.conflict_resolution_strategy == "priority":
            active_rules.sort(key=lambda r: r.priority.value, reverse=True)
        elif self.conflict_resolution_strategy == "recency":
            # For demo purposes, we'll sort by name if no last_triggered
            active_rules.sort(key=lambda r: r.last_triggered or 0, reverse=True)
        elif self.conflict_resolution_strategy == "specificity":
            # Sort by number of conditions (more specific rules first)
            active_rules.sort(key=lambda r: len(r.conditions), reverse=True)

        return active_rules

    def execute_rules(self) -> List[Dict[str, Any]]:
        """
        Execute all rules that should fire based on current sensor data.

        Returns:
            List of execution results
        """
        active_rules = self.evaluate_rules()
        results = []

        for rule in active_rules:
            result = rule.execute(self.sensor_data)
            results.append({
                "rule_name": rule.name,
                "category": rule.category.value,
                "priority": rule.priority.value,
                "confidence": rule.confidence,
                **result
            })

        # Add to execution history
        self.execution_history.extend(results)

        return results

    def get_active_rules_count(self) -> Dict[str, int]:
        """Get count of active rules by category."""
        active_rules = self.evaluate_rules()
        counts = {}
        for rule in active_rules:
            cat = rule.category.value
            counts[cat] = counts.get(cat, 0) + 1
        return counts

    def get_rule_statistics(self) -> Dict[str, Any]:
        """Get statistics about the rule system."""
        total_rules = len(self.rules)
        enabled_rules = len([r for r in self.rules if r.enabled])
        category_counts = {}
        priority_counts = {}

        for rule in self.rules:
            cat = rule.category.value
            priority_counts[rule.priority.name] = priority_counts.get(rule.priority.name, 0) + 1
            category_counts[cat] = category_counts.get(cat, 0) + 1

        return {
            "total_rules": total_rules,
            "enabled_rules": enabled_rules,
            "disabled_rules": total_rules - enabled_rules,
            "category_distribution": category_counts,
            "priority_distribution": priority_counts,
            "execution_count": len(self.execution_history),
            "active_sensors": list(self.sensor_data.keys())
        }


def create_safety_rules() -> List[Rule]:
    """
    Create safety-related rules.
    """
    rules = []

    # Rule 1: Emergency stop if IMU indicates falling
    conditions = [
        SensorCondition("imu.roll", ">", 0.5),
        SensorCondition("imu.pitch", ">", 0.5)
    ]
    action = RuleAction("emergency_stop", {"speed": 0.0, "reason": "falling_detected"})
    rules.append(Rule(
        "falling_emergency_stop",
        conditions,
        action,
        RulePriority.CRITICAL,
        RuleCategory.SAFETY,
        0.95
    ))

    # Rule 2: Reduce speed if close to obstacle
    conditions = [
        SensorCondition("lidar.min_distance", "<", 0.5)
    ]
    action = RuleAction("reduce_speed", {"factor": 0.3, "reason": "close_obstacle"})
    rules.append(Rule(
        "obstacle_speed_reduction",
        conditions,
        action,
        RulePriority.HIGH,
        RuleCategory.SAFETY,
        0.8
    ))

    # Rule 3: Stop if force/torque sensor indicates collision
    conditions = [
        SensorCondition("force_torque.left_hand", ">", 50.0),
        SensorCondition("force_torque.right_hand", ">", 50.0)
    ]
    action = RuleAction("stop_motion", {"reason": "collision_detected"})
    rules.append(Rule(
        "collision_stop",
        conditions,
        action,
        RulePriority.HIGH,
        RuleCategory.SAFETY,
        0.9
    ))

    return rules


def create_balance_rules() -> List[Rule]:
    """
    Create balance-related rules.
    """
    rules = []

    # Rule 1: Adjust posture if tilt exceeds threshold
    conditions = [
        SensorCondition("imu.roll", ">", 0.2),
        SensorCondition("imu.roll", "<", 0.5)
    ]
    action = RuleAction("adjust_posture", {"axis": "roll", "amount": 0.1})
    rules.append(Rule(
        "roll_adjustment",
        conditions,
        action,
        RulePriority.HIGH,
        RuleCategory.BALANCE,
        0.85
    ))

    # Rule 2: Major balance correction for high tilt
    conditions = [
        SensorCondition("imu.pitch", ">", 0.3)
    ]
    action = RuleAction("major_balance_correction", {"direction": "pitch", "amount": 0.2})
    rules.append(Rule(
        "major_pitch_correction",
        conditions,
        action,
        RulePriority.CRITICAL,
        RuleCategory.BALANCE,
        0.9
    ))

    # Rule 3: Minor balance adjustments for small tilts
    conditions = [
        SensorCondition("imu.roll", ">", 0.05),
        SensorCondition("imu.roll", "<", 0.2)
    ]
    action = RuleAction("minor_balance_adjust", {"axis": "roll", "amount": 0.02})
    rules.append(Rule(
        "minor_roll_adjust",
        conditions,
        action,
        RulePriority.MEDIUM,
        RuleCategory.BALANCE,
        0.7
    ))

    return rules


def create_navigation_rules() -> List[Rule]:
    """
    Create navigation-related rules.
    """
    rules = []

    # Rule 1: Path clear, proceed normally
    conditions = [
        SensorCondition("lidar.min_distance", ">", 2.0)
    ]
    action = RuleAction("proceed_normally", {"speed": 0.5})
    rules.append(Rule(
        "clear_path_normal_speed",
        conditions,
        action,
        RulePriority.MEDIUM,
        RuleCategory.NAVIGATION,
        0.8
    ))

    # Rule 2: Medium obstacle distance, slow down
    conditions = [
        SensorCondition("lidar.min_distance", ">", 0.8),
        SensorCondition("lidar.min_distance", "<=", 2.0)
    ]
    action = RuleAction("reduce_speed", {"speed": 0.2})
    rules.append(Rule(
        "medium_obstacle_slow_down",
        conditions,
        action,
        RulePriority.MEDIUM,
        RuleCategory.NAVIGATION,
        0.75
    ))

    # Rule 3: Humans detected, be cautious
    conditions = [
        SensorCondition("camera.humans_detected", ">", 0)
    ]
    action = RuleAction("cautious_navigation", {"speed": 0.1, "behavior": "yield_to_humans"})
    rules.append(Rule(
        "human_aware_navigation",
        conditions,
        action,
        RulePriority.HIGH,
        RuleCategory.NAVIGATION,
        0.85
    ))

    return rules


def create_interaction_rules() -> List[Rule]:
    """
    Create interaction-related rules.
    """
    rules = []

    # Rule 1: Human speaking, pay attention
    conditions = [
        SensorCondition("microphone.speech_detected", "==", True)
    ]
    action = RuleAction("focus_attention", {"target": "speaker", "behavior": "listening"})
    rules.append(Rule(
        "human_speech_attention",
        conditions,
        action,
        RulePriority.MEDIUM,
        RuleCategory.INTERACTION,
        0.8
    ))

    # Rule 2: Human waving, acknowledge
    conditions = [
        SensorCondition("camera.wave_detected", "==", True)
    ]
    action = RuleAction("acknowledge_gesture", {"gesture": "wave", "response": "greeting"})
    rules.append(Rule(
        "wave_acknowledgment",
        conditions,
        action,
        RulePriority.MEDIUM,
        RuleCategory.INTERACTION,
        0.75
    ))

    # Rule 3: No interaction for a while, enter idle mode
    conditions = [
        SensorCondition("interaction.time_since_last", ">", 30.0)  # 30 seconds
    ]
    action = RuleAction("enter_idle_mode", {"timeout": 30.0})
    rules.append(Rule(
        "idle_mode_activation",
        conditions,
        action,
        RulePriority.LOW,
        RuleCategory.INTERACTION,
        0.6
    ))

    return rules


class RuleBasedSimulator:
    """
    Simulates rule-based decision making in various scenarios.
    """
    def __init__(self) -> None:
        self.rule_system = RuleBasedSystem()

        # Add all rules to the system
        all_rules = []
        all_rules.extend(create_safety_rules())
        all_rules.extend(create_balance_rules())
        all_rules.extend(create_navigation_rules())
        all_rules.extend(create_interaction_rules())

        for rule in all_rules:
            self.rule_system.add_rule(rule)

        self.simulation_time = 0.0
        self.scenario_count = 0

    def run_scenario(self, scenario_name: str, sensor_inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run a rule-based scenario with given sensor inputs.

        Args:
            scenario_name: Name of the scenario
            sensor_inputs: Dictionary of sensor data

        Returns:
            Results of the rule evaluation and execution
        """
        self.scenario_count += 1
        print(f"\nScenario {self.scenario_count}: {scenario_name}")

        # Update sensor data
        for sensor_type, data in sensor_inputs.items():
            self.rule_system.update_sensor_data(sensor_type, data)

        # Evaluate and execute rules
        active_rules = self.rule_system.evaluate_rules()
        print(f"  Active rules: {len(active_rules)}")
        for rule in active_rules[:3]:  # Show first 3
            print(f"    - {rule.name} ({rule.category.value}, priority {rule.priority.name})")

        results = self.rule_system.execute_rules()
        print(f"  Executed actions: {len(results)}")
        for result in results[:3]:  # Show first 3
            print(f"    - {result['action']} (rule: {result['rule_name']})")

        return {
            "scenario": scenario_name,
            "sensor_inputs": sensor_inputs,
            "active_rules": [rule.name for rule in active_rules],
            "executed_actions": [result["action"] for result in results],
            "execution_results": results,
            "timestamp": time.time()
        }

    def get_simulation_summary(self) -> Dict[str, Any]:
        """Get a summary of the simulation."""
        return {
            "total_scenarios": self.scenario_count,
            "rule_system_stats": self.rule_system.get_rule_statistics(),
            "total_rules": len(self.rule_system.rules),
            "execution_history_count": len(self.rule_system.execution_history),
            "simulation_time": self.simulation_time
        }


def simple_motor_control_action(sensor_data: Dict[str, Any], **params) -> str:
    """
    Example action function for motor control.
    """
    # In a real system, this would interface with the robot's motor control system
    speed = params.get("speed", 0.0)
    behavior = params.get("behavior", "default")
    return f"Motor command: speed={speed}, behavior={behavior}"


def posture_adjustment_action(sensor_data: Dict[str, Any], **params) -> str:
    """
    Example action function for posture adjustment.
    """
    # In a real system, this would adjust joint angles
    axis = params.get("axis", "none")
    amount = params.get("amount", 0.0)
    return f"Posture adjustment: {axis} by {amount} radians"


def main() -> None:
    """
    Main function demonstrating rule-based decision making.
    """
    print("Starting rule-based decision making demonstration for humanoid robot...")
    print("Showing how to implement and evaluate rules for various behaviors.\n")

    # Initialize the rule-based simulator
    simulator = RuleBasedSimulator()

    # Add execution functions to some rules
    for rule in simulator.rule_system.rules:
        if "adjust_posture" in rule.action.name:
            rule.action.execution_function = posture_adjustment_action
        elif "reduce_speed" in rule.action.name or "proceed" in rule.action.name:
            rule.action.execution_function = simple_motor_control_action

    print("Rule system initialized:")
    stats = simulator.rule_system.get_rule_statistics()
    print(f"  Total rules: {stats['total_rules']}")
    print(f"  Enabled rules: {stats['enabled_rules']}")
    print(f"  Rule categories: {list(stats['category_distribution'].keys())}")
    print(f"  Rule priorities: {list(stats['priority_distribution'].keys())}")
    print()

    # Define test scenarios
    scenarios = [
        {
            "name": "Normal navigation with clear path",
            "inputs": {
                "lidar.min_distance": 3.0,
                "camera.humans_detected": 0,
                "imu.roll": 0.01,
                "imu.pitch": 0.02,
                "force_torque.left_hand": 5.0,
                "force_torque.right_hand": 3.0,
                "microphone.speech_detected": False,
                "interaction.time_since_last": 10.0
            }
        },
        {
            "name": "Close obstacle avoidance",
            "inputs": {
                "lidar.min_distance": 0.3,
                "camera.humans_detected": 0,
                "imu.roll": 0.02,
                "imu.pitch": 0.03,
                "force_torque.left_hand": 8.0,
                "force_torque.right_hand": 6.0,
                "microphone.speech_detected": False,
                "interaction.time_since_last": 5.0
            }
        },
        {
            "name": "Balance recovery needed",
            "inputs": {
                "lidar.min_distance": 2.5,
                "camera.humans_detected": 0,
                "imu.roll": 0.35,  # High roll - needs correction
                "imu.pitch": 0.25,  # High pitch - needs correction
                "force_torque.left_hand": 12.0,
                "force_torque.right_hand": 15.0,
                "microphone.speech_detected": False,
                "interaction.time_since_last": 2.0
            }
        },
        {
            "name": "Human interaction scenario",
            "inputs": {
                "lidar.min_distance": 1.5,
                "camera.humans_detected": 1,
                "camera.wave_detected": True,
                "imu.roll": 0.05,
                "imu.pitch": 0.03,
                "force_torque.left_hand": 4.0,
                "force_torque.right_hand": 3.0,
                "microphone.speech_detected": True,
                "interaction.time_since_last": 0.5
            }
        },
        {
            "name": "Emergency safety situation",
            "inputs": {
                "lidar.min_distance": 0.1,  # Very close obstacle
                "camera.humans_detected": 1,
                "imu.roll": 0.6,  # Falling
                "imu.pitch": 0.7,  # Falling
                "force_torque.left_hand": 60.0,  # Collision detected
                "force_torque.right_hand": 55.0,  # Collision detected
                "microphone.speech_detected": False,
                "interaction.time_since_last": 1.0
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

    # Show rule statistics
    stats = simulator.rule_system.get_rule_statistics()
    print(f"\nRule system statistics:")
    print(f"  Total rules: {stats['total_rules']}")
    print(f"  Enabled rules: {stats['enabled_rules']}")
    print(f"  Disabled rules: {stats['disabled_rules']}")
    print(f"  Total executions: {stats['execution_count']}")
    print(f"  Active sensors: {stats['active_sensors']}")
    print(f"  Category distribution: {stats['category_distribution']}")
    print(f"  Priority distribution: {stats['priority_distribution']}")

    # Show active rules by category for the last scenario
    print(f"\nActive rules in last scenario:")
    active_counts = simulator.rule_system.get_active_rules_count()
    for category, count in active_counts.items():
        print(f"  {category}: {count} rules active")

    # Show sample execution from one scenario
    print(f"\nSample rule execution from emergency scenario:")
    emergency_result = scenario_results[4] if len(scenario_results) > 4 else scenario_results[-1] if scenario_results else None
    if emergency_result:
        print(f"  Scenario: {emergency_result['scenario']}")
        print(f"  Active rules: {len(emergency_result['active_rules'])}")
        print(f"  Executed actions: {len(emergency_result['executed_actions'])}")
        for action in emergency_result['executed_actions'][:3]:
            print(f"    - {action}")

    # Show rule evaluation details
    print(f"\nRule evaluation details:")
    for category in RuleCategory:
        rules_in_category = [r for r in simulator.rule_system.rules if r.category == category]
        active_in_category = [r for r in rules_in_category if r.evaluate(scenarios[0]["inputs"])]
        print(f"  {category.value}: {len(active_in_category)}/{len(rules_in_category)} rules active in normal scenario")

    # Show conflict resolution example
    print(f"\nConflict resolution example:")
    print(f"  Strategy: {simulator.rule_system.conflict_resolution_strategy}")
    normal_scenario_active = [r for r in simulator.rule_system.rules if r.evaluate(scenarios[0]["inputs"])]
    normal_scenario_active.sort(key=lambda r: r.priority.value, reverse=True)
    print(f"  Top 3 rules by priority in normal scenario:")
    for i, rule in enumerate(normal_scenario_active[:3]):
        print(f"    {i+1}. {rule.name} (Priority: {rule.priority.name}, Category: {rule.category.value})")

    # Show sensor condition evaluation
    print(f"\nSensor condition evaluation example:")
    sample_rule = simulator.rule_system.rules[0]  # First rule
    print(f"  Rule: {sample_rule.name}")
    print(f"  Conditions:")
    for i, condition in enumerate(sample_rule.conditions):
        result = condition.evaluate(scenarios[0]["inputs"])
        print(f"    {i+1}. {condition.sensor_type} {condition.comparison_operator} {condition.threshold} = {result}")

    print(f"\nRule-based decision making demonstration completed.")
    print("This shows how humanoid robots can make decisions using predefined rules")
    print("that evaluate sensor conditions and trigger appropriate actions.")


if __name__ == "__main__":
    main()