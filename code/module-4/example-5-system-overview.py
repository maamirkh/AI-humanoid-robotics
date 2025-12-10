#!/usr/bin/env python3
"""
System Overview Example

This module demonstrates how all components work together in a humanoid robot system,
showing the integration of perception, planning, control, and decision making.
"""

from typing import Dict, List, Tuple, Optional, Any
import math
import random
import time
from enum import Enum
from dataclasses import dataclass


class SystemState(Enum):
    """Overall system states."""
    INITIALIZING = "initializing"
    IDLE = "idle"
    ACTIVE = "active"
    SAFETY_MODE = "safety_mode"
    EMERGENCY_STOP = "emergency_stop"
    SHUTTING_DOWN = "shutting_down"


class ComponentStatus(Enum):
    """Status of individual system components."""
    OK = "ok"
    WARNING = "warning"
    ERROR = "error"
    OFFLINE = "offline"
    INITIALIZING = "initializing"


@dataclass
class SensorData:
    """Container for sensor data."""
    timestamp: float
    lidar_data: Optional[List[float]] = None
    camera_data: Optional[Dict[str, Any]] = None
    imu_data: Optional[Dict[str, float]] = None
    force_torque_data: Optional[Dict[str, Tuple[float, float, float]]] = None
    joint_positions: Optional[Dict[str, float]] = None
    battery_level: float = 1.0


@dataclass
class RobotState:
    """Current state of the robot."""
    position: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    orientation: Tuple[float, float, float, float] = (1.0, 0.0, 0.0, 0.0)  # quaternion
    joint_angles: Dict[str, float] = None
    velocities: Dict[str, float] = None
    forces: Dict[str, float] = None
    in_motion: bool = False
    balance_state: float = 1.0  # 0.0 (unstable) to 1.0 (stable)

    def __post_init__(self):
        if self.joint_angles is None:
            self.joint_angles = {}
        if self.velocities is None:
            self.velocities = {}
        if self.forces is None:
            self.forces = {}


class PerceptionModule:
    """
    Handles sensor data processing and environment understanding.
    """
    def __init__(self) -> None:
        self.status = ComponentStatus.INITIALIZING
        self.last_update = 0.0
        self.objects_detected: List[Dict[str, Any]] = []
        self.free_space_map: List[Tuple[float, float, float]] = []  # (x, y, distance)
        self.humans_tracked: List[Dict[str, Any]] = []

    def process_sensors(self, sensor_data: SensorData) -> Dict[str, Any]:
        """Process raw sensor data into meaningful information."""
        self.last_update = sensor_data.timestamp

        # Process LIDAR data to detect obstacles and free space
        if sensor_data.lidar_data:
            self._process_lidar(sensor_data.lidar_data)

        # Process camera data to detect objects and humans
        if sensor_data.camera_data:
            self._process_camera(sensor_data.camera_data)

        # Update status based on data quality
        if sensor_data.lidar_data and sensor_data.camera_data:
            self.status = ComponentStatus.OK
        elif sensor_data.lidar_data or sensor_data.camera_data:
            self.status = ComponentStatus.WARNING
        else:
            self.status = ComponentStatus.ERROR

        return {
            "objects_detected": len(self.objects_detected),
            "free_space_points": len(self.free_space_map),
            "humans_tracked": len(self.humans_tracked),
            "status": self.status.value
        }

    def _process_lidar(self, lidar_data: List[float]) -> None:
        """Process LIDAR data to identify obstacles and free space."""
        # Clear previous data
        self.free_space_map = []

        # Simple processing: identify free directions and obstacles
        for i, distance in enumerate(lidar_data):
            angle = i * (2 * math.pi / len(lidar_data))
            if distance > 0.5:  # Consider as free space if > 0.5m
                x = distance * math.cos(angle)
                y = distance * math.sin(angle)
                self.free_space_map.append((x, y, distance))

    def _process_camera(self, camera_data: Dict[str, Any]) -> None:
        """Process camera data to detect objects and humans."""
        # Clear previous detections
        self.objects_detected = []
        self.humans_tracked = []

        # Simulate object detection from camera data
        num_objects = camera_data.get("objects_detected", 0)
        for i in range(num_objects):
            self.objects_detected.append({
                "id": f"obj_{i}",
                "type": "unknown",
                "position": (random.uniform(-2, 2), random.uniform(-2, 2), random.uniform(0, 3)),
                "confidence": random.uniform(0.6, 1.0)
            })

        # Simulate human detection
        num_humans = camera_data.get("humans_detected", 0)
        for i in range(num_humans):
            self.humans_tracked.append({
                "id": f"human_{i}",
                "position": (random.uniform(-1, 1), random.uniform(-1, 1), 0),
                "velocity": (random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5), 0),
                "looking_at_robot": random.choice([True, False])
            })


class PlanningModule:
    """
    Plans robot actions based on goals and environmental information.
    """
    def __init__(self) -> None:
        self.status = ComponentStatus.INITIALIZING
        self.last_plan = None
        self.current_goal: Optional[str] = None
        self.path_to_goal: List[Tuple[float, float, float]] = []  # List of waypoints

    def plan_action(self, robot_state: RobotState, environment_info: Dict[str, Any],
                   goal: str) -> Dict[str, Any]:
        """Plan an action based on robot state and environment."""
        self.current_goal = goal

        # Generate a simple plan based on the goal
        if goal == "navigate_to_waypoint":
            plan = self._plan_navigation(robot_state, environment_info)
        elif goal == "avoid_obstacle":
            plan = self._plan_obstacle_avoidance(robot_state, environment_info)
        elif goal == "interact_with_human":
            plan = self._plan_human_interaction(robot_state, environment_info)
        else:
            plan = {"action": "wait", "duration": 1.0, "status": "unknown_goal"}

        self.last_plan = plan
        self.status = ComponentStatus.OK

        return plan

    def _plan_navigation(self, robot_state: RobotState, env_info: Dict[str, Any]) -> Dict[str, Any]:
        """Plan navigation to a waypoint."""
        # Simple navigation plan - move toward a target
        target = (2.0, 1.0, 0.0)  # Example target

        # Calculate path based on free space map
        self.path_to_goal = [target]  # Simplified - in reality, this would be a full path

        # Determine if path is clear
        path_clear = True  # Simplified check

        return {
            "action": "navigate",
            "target": target,
            "path_clear": path_clear,
            "path_length": len(self.path_to_goal),
            "estimated_time": 10.0  # seconds
        }

    def _plan_obstacle_avoidance(self, robot_state: RobotState, env_info: Dict[str, Any]) -> Dict[str, Any]:
        """Plan obstacle avoidance."""
        # Find alternative path around obstacles
        obstacle_positions = []  # Would come from perception

        # Simple avoidance: move around detected obstacles
        avoidance_vector = (random.uniform(-1, 1), random.uniform(-1, 1), 0)

        return {
            "action": "avoid_obstacle",
            "avoidance_vector": avoidance_vector,
            "status": "path_found"
        }

    def _plan_human_interaction(self, robot_state: RobotState, env_info: Dict[str, Any]) -> Dict[str, Any]:
        """Plan human interaction."""
        humans_nearby = env_info.get("humans_tracked", [])

        if humans_nearby:
            closest_human = min(humans_nearby, key=lambda h: math.sqrt(h["position"][0]**2 + h["position"][1]**2))

            return {
                "action": "approach_human",
                "target_human": closest_human["id"],
                "approach_position": (closest_human["position"][0] - 0.5, closest_human["position"][1], 0),  # Stay at safe distance
                "greeting_behavior": "wave" if closest_human.get("looking_at_robot", False) else "wait_for_attention"
            }
        else:
            return {
                "action": "wait_for_human",
                "status": "no_humans_detected"
            }


class ControlModule:
    """
    Controls robot actuators based on planned actions.
    """
    def __init__(self) -> None:
        self.status = ComponentStatus.INITIALIZING
        self.current_trajectory: List[Dict[str, float]] = []
        self.motor_commands: Dict[str, float] = {}

    def execute_plan(self, plan: Dict[str, Any], robot_state: RobotState) -> Dict[str, Any]:
        """Execute a planned action by generating motor commands."""
        action = plan.get("action", "idle")

        if action == "navigate":
            commands = self._execute_navigation(plan, robot_state)
        elif action == "avoid_obstacle":
            commands = self._execute_avoidance(plan, robot_state)
        elif action == "approach_human":
            commands = self._execute_approach(plan, robot_state)
        elif action == "wait":
            commands = self._execute_wait(plan, robot_state)
        else:
            commands = self._execute_idle(robot_state)

        self.motor_commands = commands
        self.status = ComponentStatus.OK

        return {
            "commands_generated": len(commands),
            "action": action,
            "status": "executing"
        }

    def _execute_navigation(self, plan: Dict[str, Any], robot_state: RobotState) -> Dict[str, float]:
        """Execute navigation commands."""
        # Simplified navigation control
        # In reality, this would involve complex inverse kinematics and balance control
        target = plan.get("target", (0, 0, 0))

        # Calculate direction to target
        dx = target[0] - robot_state.position[0]
        dy = target[1] - robot_state.position[1]
        distance = math.sqrt(dx**2 + dy**2)

        # Generate simple motor commands based on direction
        commands = {
            "left_wheel_velocity": 0.5 if dx > 0 else -0.5,
            "right_wheel_velocity": 0.5 if dx > 0 else -0.5,
            "balance_adjust": robot_state.balance_state * 0.1
        }

        return commands

    def _execute_avoidance(self, plan: Dict[str, Any], robot_state: RobotState) -> Dict[str, float]:
        """Execute obstacle avoidance commands."""
        avoidance_vector = plan.get("avoidance_vector", (0, 0, 0))

        commands = {
            "left_wheel_velocity": avoidance_vector[0] * 0.3,
            "right_wheel_velocity": avoidance_vector[1] * 0.3,
            "steering_adjust": avoidance_vector[0] * 0.1
        }

        return commands

    def _execute_approach(self, plan: Dict[str, Any], robot_state: RobotState) -> Dict[str, float]:
        """Execute approach commands."""
        target_pos = plan.get("approach_position", (0, 0, 0))

        dx = target_pos[0] - robot_state.position[0]
        dy = target_pos[1] - robot_state.position[1]

        commands = {
            "left_wheel_velocity": 0.2 if dx > 0 else -0.2,
            "right_wheel_velocity": 0.2 if dx > 0 else -0.2,
            "head_pan": math.atan2(dy, dx),  # Look toward target
            "arm_position": "ready"  # Prepare arm for interaction
        }

        return commands

    def _execute_wait(self, plan: Dict[str, Any], robot_state: RobotState) -> Dict[str, float]:
        """Execute wait commands."""
        return {
            "left_wheel_velocity": 0.0,
            "right_wheel_velocity": 0.0,
            "balance_adjust": 0.0
        }

    def _execute_idle(self, robot_state: RobotState) -> Dict[str, float]:
        """Execute idle commands."""
        return {
            "left_wheel_velocity": 0.0,
            "right_wheel_velocity": 0.0,
            "balance_adjust": robot_state.balance_state * 0.05
        }


class DecisionModule:
    """
    Makes high-level decisions based on system state and goals.
    """
    def __init__(self) -> None:
        self.status = ComponentStatus.INITIALIZING
        self.current_behavior = "idle"
        self.behavior_priority = 0

    def make_decision(self, robot_state: RobotState, environment_info: Dict[str, Any],
                    system_status: Dict[str, Any]) -> Dict[str, Any]:
        """Make high-level behavioral decisions."""
        # Check for safety-critical situations first
        if self._check_safety_critical(robot_state, environment_info):
            decision = {
                "behavior": "safety_response",
                "goal": "emergency_stop",
                "priority": 10
            }
        elif self._check_balance_critical(robot_state):
            decision = {
                "behavior": "balance_recovery",
                "goal": "stabilize",
                "priority": 9
            }
        elif self._check_humans_present(environment_info):
            decision = {
                "behavior": "social_interaction",
                "goal": "interact_with_human",
                "priority": 7
            }
        elif self._check_navigation_needed(robot_state, environment_info):
            decision = {
                "behavior": "navigation",
                "goal": "navigate_to_waypoint",
                "priority": 5
            }
        else:
            decision = {
                "behavior": "idle",
                "goal": "wait_for_command",
                "priority": 1
            }

        self.current_behavior = decision["behavior"]
        self.behavior_priority = decision["priority"]
        self.status = ComponentStatus.OK

        return decision

    def _check_safety_critical(self, robot_state: RobotState, env_info: Dict[str, Any]) -> bool:
        """Check if safety-critical situation exists."""
        # Check if forces are too high (possible collision)
        high_forces = any(abs(f) > 100 for f in robot_state.forces.values()) if robot_state.forces else False

        # Check if tilt is too high (falling)
        high_tilt = robot_state.balance_state < 0.3

        # Check if very close to obstacles
        lidar_data = env_info.get("raw_sensor_data", {}).get("lidar_data", [])
        if lidar_data:
            very_close_obstacles = any(dist < 0.2 for dist in lidar_data)
        else:
            very_close_obstacles = False

        return high_forces or high_tilt or very_close_obstacles

    def _check_balance_critical(self, robot_state: RobotState) -> bool:
        """Check if balance recovery is needed."""
        return robot_state.balance_state < 0.6

    def _check_humans_present(self, env_info: Dict[str, Any]) -> bool:
        """Check if humans are present for interaction."""
        return env_info.get("humans_tracked", []) != []

    def _check_navigation_needed(self, robot_state: RobotState, env_info: Dict[str, Any]) -> bool:
        """Check if navigation is needed."""
        # Simplified: always need navigation if we have a task
        return True


class SystemMonitor:
    """
    Monitors overall system health and status.
    """
    def __init__(self) -> None:
        self.system_state = SystemState.INITIALIZING
        self.component_statuses: Dict[str, ComponentStatus] = {}
        self.performance_metrics: Dict[str, float] = {}
        self.error_log: List[Dict[str, Any]] = []
        self.last_update = time.time()

    def update_status(self, component_name: str, status: ComponentStatus) -> None:
        """Update status of a component."""
        self.component_statuses[component_name] = status
        self.last_update = time.time()

    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health assessment."""
        # Calculate system health based on component statuses
        ok_count = sum(1 for s in self.component_statuses.values() if s == ComponentStatus.OK)
        total_count = len(self.component_statuses)

        if total_count == 0:
            health_percentage = 0.0
        else:
            health_percentage = (ok_count / total_count) * 100

        # Determine system state based on component statuses
        if any(s == ComponentStatus.ERROR for s in self.component_statuses.values()):
            self.system_state = SystemState.SAFETY_MODE
        elif all(s == ComponentStatus.OK for s in self.component_statuses.values()):
            self.system_state = SystemState.ACTIVE
        else:
            self.system_state = SystemState.ACTIVE  # Mixed state

        return {
            "system_state": self.system_state.value,
            "health_percentage": health_percentage,
            "total_components": total_count,
            "ok_components": ok_count,
            "component_statuses": {k: v.value for k, v in self.component_statuses.items()},
            "last_update": self.last_update
        }

    def log_error(self, component: str, error_message: str, severity: str = "warning") -> None:
        """Log an error or warning."""
        self.error_log.append({
            "timestamp": time.time(),
            "component": component,
            "message": error_message,
            "severity": severity
        })


class HumanoidRobotSystem:
    """
    Main system that integrates all components.
    """
    def __init__(self) -> None:
        self.perception = PerceptionModule()
        self.planning = PlanningModule()
        self.control = ControlModule()
        self.decision = DecisionModule()
        self.monitor = SystemMonitor()

        self.current_state = RobotState()
        self.system_state = SystemState.INITIALIZING
        self.active = False
        self.start_time = time.time()

    def initialize(self) -> bool:
        """Initialize the entire system."""
        print("Initializing humanoid robot system...")

        # Initialize all modules
        self.monitor.update_status("perception", self.perception.status)
        self.monitor.update_status("planning", self.planning.status)
        self.monitor.update_status("control", self.control.status)
        self.monitor.update_status("decision", self.decision.status)

        # Wait for modules to initialize
        time.sleep(0.5)  # Simulate initialization time

        # Update statuses after initialization
        self.perception.status = ComponentStatus.OK
        self.planning.status = ComponentStatus.OK
        self.control.status = ComponentStatus.OK
        self.decision.status = ComponentStatus.OK

        self.monitor.update_status("perception", self.perception.status)
        self.monitor.update_status("planning", self.planning.status)
        self.monitor.update_status("control", self.control.status)
        self.monitor.update_status("decision", self.decision.status)

        self.system_state = SystemState.IDLE
        self.active = True

        print("System initialized successfully!")
        return True

    def process_cycle(self, sensor_data: SensorData) -> Dict[str, Any]:
        """Process one full cycle of the robot system."""
        if not self.active:
            return {"status": "system_not_active"}

        # Update robot state from sensor data
        self._update_robot_state(sensor_data)

        # Process perception
        env_info = self.perception.process_sensors(sensor_data)
        env_info["raw_sensor_data"] = {
            "lidar_data": sensor_data.lidar_data,
            "camera_data": sensor_data.camera_data
        }

        # Make high-level decisions
        decision = self.decision.make_decision(self.current_state, env_info,
                                            self.monitor.get_system_health())

        # Plan action based on decision
        plan = self.planning.plan_action(self.current_state, env_info, decision["goal"])

        # Execute plan
        execution_result = self.control.execute_plan(plan, self.current_state)

        # Update system monitor
        self.monitor.update_status("perception", self.perception.status)
        self.monitor.update_status("planning", self.planning.status)
        self.monitor.update_status("control", self.control.status)
        self.monitor.update_status("decision", self.decision.status)

        # Collect results
        cycle_result = {
            "timestamp": sensor_data.timestamp,
            "decision": decision,
            "plan": plan,
            "execution": execution_result,
            "environment": env_info,
            "system_health": self.monitor.get_system_health(),
            "robot_state": {
                "position": self.current_state.position,
                "balance": self.current_state.balance_state,
                "in_motion": self.current_state.in_motion
            }
        }

        return cycle_result

    def _update_robot_state(self, sensor_data: SensorData) -> None:
        """Update robot state from sensor data."""
        # Update position based on joint encoders (simplified)
        if sensor_data.joint_positions:
            self.current_state.joint_angles = sensor_data.joint_positions.copy()

        # Update IMU-based orientation and balance
        if sensor_data.imu_data:
            roll = sensor_data.imu_data.get("roll", 0)
            pitch = sensor_data.imu_data.get("pitch", 0)
            # Simplified balance calculation based on tilt
            tilt_magnitude = math.sqrt(roll**2 + pitch**2)
            self.current_state.balance_state = max(0.0, 1.0 - tilt_magnitude)

        # Update force data
        if sensor_data.force_torque_data:
            for joint, forces in sensor_data.force_torque_data.items():
                self.current_state.forces[joint] = math.sqrt(sum(f**2 for f in forces))

        # Update battery level
        self.current_state.forces["battery"] = sensor_data.battery_level

    def shutdown(self) -> None:
        """Shut down the system safely."""
        print("Shutting down humanoid robot system...")
        self.active = False
        self.system_state = SystemState.SHUTTING_DOWN

        # Log shutdown
        self.monitor.log_error("system", "System shutdown initiated", "info")


class SystemSimulator:
    """
    Simulates the complete humanoid robot system.
    """
    def __init__(self) -> None:
        self.robot_system = HumanoidRobotSystem()
        self.simulation_time = 0.0
        self.cycle_count = 0
        self.simulation_active = False

    def start_simulation(self) -> bool:
        """Start the system simulation."""
        success = self.robot_system.initialize()
        if success:
            self.simulation_active = True
            print("System simulation started!")
        return success

    def run_cycle(self) -> Dict[str, Any]:
        """Run one simulation cycle."""
        if not self.simulation_active:
            return {"status": "simulation_not_active"}

        # Generate simulated sensor data
        sensor_data = self._generate_sensor_data()

        # Process the cycle
        result = self.robot_system.process_cycle(sensor_data)

        self.cycle_count += 1
        self.simulation_time += 0.1  # 10Hz simulation

        return result

    def _generate_sensor_data(self) -> SensorData:
        """Generate simulated sensor data."""
        timestamp = time.time()

        # Simulate LIDAR data (360 degree scan)
        lidar_data = []
        for i in range(360):
            # Create a pattern with some obstacles
            angle = math.radians(i)
            if 45 <= i <= 135:  # Front right has an obstacle
                distance = 0.8 + random.uniform(-0.1, 0.1)
            elif 225 <= i <= 315:  # Back left has an obstacle
                distance = 1.2 + random.uniform(-0.1, 0.1)
            else:  # Other directions are mostly clear
                distance = 3.0 + random.uniform(-0.5, 0.5)
            lidar_data.append(max(0.1, distance))  # Minimum distance of 0.1m

        # Simulate camera data
        camera_data = {
            "objects_detected": random.randint(0, 3),
            "humans_detected": random.choice([0, 0, 0, 1, 1])  # 40% chance of human
        }

        # Simulate IMU data
        imu_data = {
            "roll": random.uniform(-0.1, 0.1),
            "pitch": random.uniform(-0.1, 0.1),
            "yaw": random.uniform(-0.2, 0.2),
            "angular_velocity": (random.uniform(-0.1, 0.1),
                               random.uniform(-0.1, 0.1),
                               random.uniform(-0.1, 0.1))
        }

        # Simulate force/torque data
        force_torque_data = {
            "left_foot": (random.uniform(-10, 10),
                         random.uniform(-10, 10),
                         random.uniform(300, 700)),
            "right_foot": (random.uniform(-10, 10),
                          random.uniform(-10, 10),
                          random.uniform(300, 700)),
            "left_hand": (random.uniform(-5, 5),
                         random.uniform(-5, 5),
                         random.uniform(-5, 5)),
            "right_hand": (random.uniform(-5, 5),
                          random.uniform(-5, 5),
                          random.uniform(-5, 5))
        }

        # Simulate joint positions
        joint_positions = {
            "hip_left": random.uniform(-0.2, 0.2),
            "knee_left": random.uniform(0.8, 1.2),
            "ankle_left": random.uniform(-0.1, 0.1),
            "hip_right": random.uniform(-0.2, 0.2),
            "knee_right": random.uniform(0.8, 1.2),
            "ankle_right": random.uniform(-0.1, 0.1),
            "shoulder_left": random.uniform(-0.5, 0.5),
            "elbow_left": random.uniform(0.0, 1.0),
            "shoulder_right": random.uniform(-0.5, 0.5),
            "elbow_right": random.uniform(0.0, 1.0)
        }

        return SensorData(
            timestamp=timestamp,
            lidar_data=lidar_data,
            camera_data=camera_data,
            imu_data=imu_data,
            force_torque_data=force_torque_data,
            joint_positions=joint_positions,
            battery_level=random.uniform(0.7, 1.0)
        )

    def run_simulation(self, cycles: int = 10) -> List[Dict[str, Any]]:
        """Run the simulation for a specified number of cycles."""
        results = []

        for i in range(cycles):
            result = self.run_cycle()
            results.append(result)

            if i % 5 == 0:  # Print every 5 cycles
                health = result.get("system_health", {})
                print(f"  Cycle {i+1}: System health = {health.get('health_percentage', 0):.1f}%")

        return results

    def stop_simulation(self) -> None:
        """Stop the simulation."""
        self.simulation_active = False
        self.robot_system.shutdown()


def main() -> None:
    """
    Main function demonstrating the complete system overview.
    """
    print("Starting humanoid robot system overview demonstration...")
    print("Showing how all components work together in an integrated system.\n")

    # Initialize the system simulator
    simulator = SystemSimulator()

    print("System initialization:")
    success = simulator.start_simulation()
    if not success:
        print("Failed to initialize system!")
        return

    print(f"  System initialized: {success}")
    print(f"  Initial system state: {simulator.robot_system.system_state.value}")
    print()

    print("Running system simulation for 15 cycles...")
    results = simulator.run_simulation(15)

    print(f"\nSimulation completed!")
    print(f"  Total cycles executed: {len(results)}")
    print(f"  Simulation time: {simulator.simulation_time:.1f} seconds")

    # Analyze results
    print(f"\nSystem analysis:")

    # Show system health progression
    health_percentages = []
    for result in results:
        health = result.get("system_health", {})
        if "health_percentage" in health:
            health_percentages.append(health["health_percentage"])

    if health_percentages:
        avg_health = sum(health_percentages) / len(health_percentages)
        min_health = min(health_percentages)
        max_health = max(health_percentages)
        print(f"  Average system health: {avg_health:.1f}%")
        print(f"  Health range: {min_health:.1f}% - {max_health:.1f}%")

    # Show behavior distribution
    behaviors = []
    for result in results:
        decision = result.get("decision", {})
        if "behavior" in decision:
            behaviors.append(decision["behavior"])

    if behaviors:
        from collections import Counter
        behavior_counts = Counter(behaviors)
        print(f"  Behavior distribution:")
        for behavior, count in behavior_counts.items():
            print(f"    {behavior}: {count} cycles")

    # Show sample cycle in detail
    print(f"\nSample cycle details (cycle 5):")
    if len(results) > 5:
        sample_result = results[4]
        decision = sample_result.get("decision", {})
        plan = sample_result.get("plan", {})
        execution = sample_result.get("execution", {})

        print(f"  Decision: {decision.get('behavior', 'unknown')} -> {decision.get('goal', 'unknown')}")
        print(f"  Plan: {plan.get('action', 'unknown')}")
        print(f"  Execution: {execution.get('action', 'unknown')}")
        print(f"  Robot balance: {sample_result.get('robot_state', {}).get('balance', 0):.2f}")

    # Show component status evolution
    print(f"\nComponent status evolution:")
    if results:
        final_health = results[-1].get("system_health", {})
        component_statuses = final_health.get("component_statuses", {})
        for component, status in component_statuses.items():
            print(f"  {component}: {status}")

    # Show system architecture
    print(f"\nSystem architecture:")
    print(f"  Perception Module: Processes sensor data into meaningful information")
    print(f"  Planning Module: Creates action plans based on goals and environment")
    print(f"  Control Module: Executes plans by generating motor commands")
    print(f"  Decision Module: Makes high-level behavioral decisions")
    print(f"  System Monitor: Tracks overall system health and status")
    print(f"  Integration: All modules work together in processing cycles")

    # Show performance metrics
    print(f"\nSystem performance:")
    print(f"  Processing cycles: {len(results)}")
    print(f"  Simulated time: {simulator.simulation_time:.1f} seconds")
    print(f"  Real-time factor: {(simulator.simulation_time / len(results)):.3f}s per cycle (simulated)")

    # Demonstrate error handling
    print(f"\nError handling demonstration:")
    # Add a simulated error to the monitor
    simulator.robot_system.monitor.log_error("lidar", "Sensor temporarily unavailable", "warning")
    simulator.robot_system.monitor.log_error("imu", "Calibration needed", "info")

    error_count = len(simulator.robot_system.monitor.error_log)
    print(f"  Total logged events: {error_count}")
    if error_count > 0:
        latest_error = simulator.robot_system.monitor.error_log[-1]
        print(f"  Latest event: {latest_error['message']} in {latest_error['component']}")

    simulator.stop_simulation()
    print(f"\nSystem overview demonstration completed.")
    print("This shows how all components of a humanoid robot system work together")
    print("in an integrated fashion, with each module contributing to the overall behavior.")


if __name__ == "__main__":
    main()