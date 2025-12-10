#!/usr/bin/env python3
"""
Conceptual Arm Reach Logic Example

This module demonstrates conceptual arm reach logic for humanoid robots,
showing how to plan and execute reaching motions with obstacle avoidance.
"""

from typing import Dict, List, Tuple, Optional, Any
import math
import random
import time
from enum import Enum


class ReachState(Enum):
    """States for the reaching process."""
    IDLE = "idle"
    PLANNING = "planning"
    EXECUTING = "executing"
    AVOIDING = "avoiding"
    COMPLETED = "completed"
    FAILED = "failed"


class Obstacle:
    """
    Represents an obstacle in the environment.
    """
    def __init__(self, position: Tuple[float, float, float],
                 size: Tuple[float, float, float],
                 shape: str = "box") -> None:
        self.position = position  # Center position (x, y, z)
        self.size = size  # Dimensions (width, depth, height)
        self.shape = shape  # "box", "sphere", "cylinder"
        self.id = f"obs_{int(time.time() * 1000) % 10000}"

    def is_collision(self, point: Tuple[float, float, float],
                    safety_margin: float = 0.05) -> bool:
        """
        Check if a point is in collision with this obstacle.

        Args:
            point: Point to check (x, y, z)
            safety_margin: Additional safety margin around obstacle

        Returns:
            True if collision detected
        """
        px, py, pz = point
        ox, oy, oz = self.position
        sx, sy, sz = self.size

        if self.shape == "box":
            # Check if point is within box bounds (with safety margin)
            return (abs(px - ox) <= sx/2 + safety_margin and
                    abs(py - oy) <= sy/2 + safety_margin and
                    abs(pz - oz) <= sz/2 + safety_margin)
        elif self.shape == "sphere":
            # Check if point is within sphere radius (with safety margin)
            distance = math.sqrt((px - ox)**2 + (py - oy)**2 + (pz - oz)**2)
            radius = max(sx, sy, sz) / 2  # Use max dimension as radius
            return distance <= radius + safety_margin
        elif self.shape == "cylinder":
            # Check if point is within cylinder
            distance_2d = math.sqrt((px - ox)**2 + (py - oy)**2)
            radius = max(sx, sy) / 2
            return (distance_2d <= radius + safety_margin and
                    abs(pz - oz) <= sz/2 + safety_margin)

        return False

    def get_bounding_box(self) -> Tuple[Tuple[float, float, float], Tuple[float, float, float]]:
        """Get the bounding box of the obstacle."""
        center_x, center_y, center_z = self.position
        width, depth, height = self.size

        min_point = (center_x - width/2, center_y - depth/2, center_z - height/2)
        max_point = (center_x + width/2, center_y + depth/2, center_z + height/2)

        return min_point, max_point


class ArmJoint:
    """
    Represents a joint in the robot arm.
    """
    def __init__(self, name: str, angle: float = 0.0,
                 min_angle: float = -math.pi, max_angle: float = math.pi,
                 velocity_limit: float = 1.0) -> None:
        self.name = name
        self.angle = angle
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.velocity_limit = velocity_limit  # rad/s
        self.current_velocity = 0.0

    def set_angle(self, new_angle: float) -> bool:
        """Set joint angle, respecting limits."""
        if self.min_angle <= new_angle <= self.max_angle:
            self.angle = new_angle
            return True
        return False

    def is_within_limits(self) -> bool:
        """Check if joint is within its limits."""
        return self.min_angle <= self.angle <= self.max_angle


class ArmConfiguration:
    """
    Represents the configuration of the robot arm.
    """
    def __init__(self) -> None:
        # Create a simple 6-DOF arm configuration
        self.joints = [
            ArmJoint("shoulder_yaw", 0.0, -math.pi/2, math.pi/2, 0.5),
            ArmJoint("shoulder_pitch", 0.0, -math.pi/3, 2*math.pi/3, 0.5),
            ArmJoint("shoulder_roll", 0.0, -math.pi/2, math.pi/2, 0.5),
            ArmJoint("elbow_pitch", 0.0, 0.0, math.pi, 0.5),
            ArmJoint("wrist_yaw", 0.0, -math.pi/2, math.pi/2, 0.5),
            ArmJoint("wrist_pitch", 0.0, -math.pi/3, math.pi/3, 0.5)
        ]
        self.link_lengths = [0.2, 0.3, 0.05, 0.25, 0.05, 0.08]  # Lengths of each link
        self.base_position = (0.2, 0.0, 1.2)  # Shoulder position in world coordinates

    def get_joint_angles(self) -> List[float]:
        """Get all joint angles."""
        return [joint.angle for joint in self.joints]

    def set_joint_angles(self, angles: List[float]) -> bool:
        """Set all joint angles."""
        if len(angles) != len(self.joints):
            return False

        success = True
        for joint, angle in zip(self.joints, angles):
            if not joint.set_angle(angle):
                success = False
        return success

    def forward_kinematics(self) -> List[Tuple[float, float, float]]:
        """
        Simple forward kinematics to calculate joint positions.
        This is a simplified implementation for demonstration.
        """
        positions = []
        current_pos = self.base_position
        current_angle = 0.0  # Simplified - only considering one axis for demo

        for i, joint in enumerate(self.joints):
            # Simplified kinematics - in reality this would involve complex trigonometry
            # and rotation matrices
            if i == 0:  # Shoulder
                # Base position
                positions.append(current_pos)
            elif i == 1:  # Upper arm
                # Move along y-axis for upper arm
                new_pos = (current_pos[0], current_pos[1] + self.link_lengths[i-1] * math.sin(joint.angle), current_pos[2])
                positions.append(new_pos)
                current_pos = new_pos
            elif i == 3:  # Elbow to forearm
                # Move along a direction based on previous joint angles
                direction = math.pi/2 - joint.angle  # Simplified
                new_pos = (current_pos[0] + self.link_lengths[i-1] * math.cos(direction),
                          current_pos[1] + self.link_lengths[i-1] * math.sin(direction),
                          current_pos[2])
                positions.append(new_pos)
                current_pos = new_pos
            else:
                # For other joints, just keep the same position for simplicity
                positions.append(current_pos)

        # Add end-effector position (simplified)
        if positions:
            final_pos = positions[-1]
            # Small offset for end-effector
            end_effector = (final_pos[0] + 0.05, final_pos[1], final_pos[2])
            positions.append(end_effector)

        return positions


class ReachPlanner:
    """
    Plans reaching motions for the robot arm.
    """
    def __init__(self) -> None:
        self.arm_config = ArmConfiguration()
        self.obstacles: List[Obstacle] = []
        self.current_state = ReachState.IDLE
        self.reach_history: List[Dict[str, Any]] = []

    def add_obstacle(self, obstacle: Obstacle) -> None:
        """Add an obstacle to the environment."""
        self.obstacles.append(obstacle)

    def remove_obstacle(self, obstacle_id: str) -> bool:
        """Remove an obstacle by ID."""
        for i, obs in enumerate(self.obstacles):
            if obs.id == obstacle_id:
                del self.obstacles[i]
                return True
        return False

    def check_collision_path(self, start: Tuple[float, float, float],
                           end: Tuple[float, float, float],
                           num_samples: int = 20) -> bool:
        """
        Check if a straight line path between two points has collisions.

        Args:
            start: Start position
            end: End position
            num_samples: Number of samples along the path to check

        Returns:
            True if collision detected along path
        """
        for i in range(num_samples + 1):
            t = i / num_samples
            x = start[0] + t * (end[0] - start[0])
            y = start[1] + t * (end[1] - start[1])
            z = start[2] + t * (end[2] - start[2])

            point = (x, y, z)
            for obstacle in self.obstacles:
                if obstacle.is_collision(point):
                    return True
        return False

    def plan_reach_motion(self, target: Tuple[float, float, float]) -> Optional[List[Tuple[float, float, float]]]:
        """
        Plan a reaching motion to the target, considering obstacles.

        Args:
            target: Target position to reach

        Returns:
            List of waypoints for the reach motion, or None if no path found
        """
        # Get current end-effector position
        current_positions = self.arm_config.forward_kinematics()
        if not current_positions:
            return None

        current_pos = current_positions[-1]  # Last position is end-effector

        # Check direct path first
        if not self.check_collision_path(current_pos, target):
            # Direct path is clear, return simple path
            return [current_pos, target]

        # If direct path is blocked, try to find an alternative
        # This is a simplified approach - real systems would use more sophisticated path planning
        waypoints = [current_pos]

        # Try to go around the obstacle by moving up first
        obstacle_in_path = False
        for obstacle in self.obstacles:
            if obstacle.is_collision((
                (current_pos[0] + target[0]) / 2,
                (current_pos[1] + target[1]) / 2,
                (current_pos[2] + target[2]) / 2
            )):
                obstacle_in_path = True
                break

        if obstacle_in_path:
            # Go up and around
            mid_point = ((current_pos[0] + target[0]) / 2,
                        (current_pos[1] + target[1]) / 2,
                        max(current_pos[2], target[2]) + 0.3)  # Go 30cm higher

            # Check if this path is clear
            if not self.check_collision_path(current_pos, mid_point) and \
               not self.check_collision_path(mid_point, target):
                waypoints.extend([mid_point, target])
            else:
                # Try another approach - go to the side
                side_point = (current_pos[0], current_pos[1] + 0.3, current_pos[2])
                if not self.check_collision_path(current_pos, side_point) and \
                   not self.check_collision_path(side_point, target):
                    waypoints.extend([side_point, target])
                else:
                    # No clear path found
                    return None
        else:
            waypoints.append(target)

        return waypoints

    def execute_reach(self, target: Tuple[float, float, float],
                     max_attempts: int = 3) -> Dict[str, Any]:
        """
        Execute a reaching motion to the target.

        Args:
            target: Target position to reach
            max_attempts: Maximum number of planning attempts

        Returns:
            Dictionary with execution results
        """
        self.current_state = ReachState.PLANNING

        for attempt in range(max_attempts):
            # Plan the motion
            waypoints = self.plan_reach_motion(target)

            if waypoints is None:
                if attempt < max_attempts - 1:
                    # Add a temporary obstacle to force a different path next time
                    continue
                else:
                    self.current_state = ReachState.FAILED
                    return {
                        "status": "failed",
                        "reason": "no_path_found",
                        "attempts": attempt + 1,
                        "waypoints": [],
                        "final_position": self.arm_config.forward_kinematics()[-1] if self.arm_config.forward_kinematics() else None
                    }

            # Execute the planned motion
            self.current_state = ReachState.EXECUTING

            # For this demo, we'll just record the planned waypoints
            # In a real system, this would involve actual joint control
            execution_result = {
                "status": "success",
                "attempts": attempt + 1,
                "waypoints": waypoints,
                "target_reached": True,  # For demo purposes
                "final_position": target
            }

            # Add to history
            self.reach_history.append({
                "timestamp": time.time(),
                "target": target,
                "waypoints": waypoints,
                "status": execution_result["status"],
                "attempts": execution_result["attempts"]
            })

            self.current_state = ReachState.COMPLETED
            return execution_result

        # If we get here, all attempts failed
        self.current_state = ReachState.FAILED
        return {
            "status": "failed",
            "reason": "max_attempts_exceeded",
            "attempts": max_attempts,
            "waypoints": [],
            "final_position": self.arm_config.forward_kinematics()[-1] if self.arm_config.forward_kinematics() else None
        }

    def get_reachability_analysis(self, target: Tuple[float, float, float]) -> Dict[str, Any]:
        """
        Analyze if a target is reachable given current configuration and obstacles.

        Args:
            target: Target position to analyze

        Returns:
            Dictionary with reachability analysis
        """
        current_positions = self.arm_config.forward_kinematics()
        if not current_positions:
            return {"reachable": False, "reason": "no_current_position"}

        current_pos = current_positions[-1]

        # Calculate straight-line distance
        distance = math.sqrt(
            (target[0] - current_pos[0])**2 +
            (target[1] - current_pos[1])**2 +
            (target[2] - current_pos[2])**2
        )

        # Estimate maximum reach (simplified)
        max_reach = sum(self.arm_config.link_lengths)

        # Check if target is within theoretical reach
        within_reach = distance <= max_reach * 1.1  # Add 10% tolerance

        # Check for obstacles in path
        path_clear = not self.check_collision_path(current_pos, target)

        # Check joint limits (simplified)
        joint_limits_ok = all(joint.is_within_limits() for joint in self.arm_config.joints)

        return {
            "reachable": within_reach and path_clear and joint_limits_ok,
            "distance": distance,
            "max_reach": max_reach,
            "path_clear": path_clear,
            "joint_limits_ok": joint_limits_ok,
            "within_reach": within_reach,
            "analysis_timestamp": time.time()
        }


class ArmReachSimulator:
    """
    Simulates arm reaching in a controlled environment.
    """
    def __init__(self) -> None:
        self.reach_planner = ReachPlanner()
        self.simulation_time = 0.0
        self.reach_attempts = 0

    def setup_environment(self) -> None:
        """Set up a sample environment with obstacles."""
        # Add some sample obstacles
        self.reach_planner.add_obstacle(Obstacle((0.5, 0.2, 1.3), (0.1, 0.1, 0.3), "box"))
        self.reach_planner.add_obstacle(Obstacle((0.3, -0.2, 1.4), (0.2, 0.2, 0.1), "sphere"))
        self.reach_planner.add_obstacle(Obstacle((0.6, 0.1, 1.2), (0.15, 0.15, 0.4), "cylinder"))

    def run_reach_scenario(self, target: Tuple[float, float, float]) -> Dict[str, Any]:
        """
        Run a reach scenario with the given target.

        Args:
            target: Target position for reaching

        Returns:
            Results of the reach attempt
        """
        self.reach_attempts += 1
        print(f"  Reach attempt {self.reach_attempts}: Target = {target}")

        # Analyze reachability first
        analysis = self.reach_planner.get_reachability_analysis(target)
        print(f"    Reachability: {analysis['reachable']}")
        print(f"    Distance: {analysis['distance']:.3f}m")
        print(f"    Path clear: {analysis['path_clear']}")

        if not analysis['within_reach']:
            print(f"    Target is out of theoretical reach")
            return {
                "status": "unreachable",
                "reason": "out_of_reach",
                "target": target,
                "analysis": analysis
            }

        # Execute the reach
        result = self.reach_planner.execute_reach(target)
        print(f"    Execution status: {result['status']}")
        print(f"    Attempts needed: {result['attempts']}")
        print(f"    Waypoints: {len(result['waypoints'])}")

        return result

    def get_simulation_stats(self) -> Dict[str, Any]:
        """Get statistics about the simulation."""
        return {
            "total_reach_attempts": self.reach_attempts,
            "successful_reaches": len([r for r in self.reach_planner.reach_history if r["status"] == "success"]),
            "failed_reaches": len([r for r in self.reach_planner.reach_history if r["status"] != "success"]),
            "total_obstacles": len(self.reach_planner.obstacles),
            "current_state": self.reach_planner.current_state.value
        }


def main() -> None:
    """
    Main function demonstrating arm reach logic.
    """
    print("Starting arm reach logic demonstration for humanoid robot...")
    print("Showing how to plan and execute reaching motions with obstacle avoidance.\n")

    # Initialize the arm reach simulator
    simulator = ArmReachSimulator()
    simulator.setup_environment()

    print("Environment setup:")
    print(f"  Number of obstacles: {len(simulator.reach_planner.obstacles)}")
    for i, obs in enumerate(simulator.reach_planner.obstacles):
        print(f"    Obstacle {i+1}: {obs.shape} at {obs.position}, size {obs.size}")
    print()

    # Define targets to reach
    test_targets = [
        (0.7, 0.0, 1.3),    # Reach forward (should be clear)
        (0.5, 0.2, 1.3),    # Reach toward first obstacle (will need to avoid)
        (0.8, -0.3, 1.5),   # Reach to the side and up
        (0.4, 0.0, 1.0),    # Reach down and closer
    ]

    print("Executing reach scenarios:")
    results = []

    for i, target in enumerate(test_targets):
        print(f"\nScenario {i+1}:")
        result = simulator.run_reach_scenario(target)
        results.append(result)

    print(f"\nReach scenarios completed!")
    print(f"  Total attempts: {simulator.reach_attempts}")

    # Show results summary
    successful = sum(1 for r in results if r.get('status') == 'success' or r.get('status') == 'reachable')
    print(f"  Successful reaches: {successful}/{len(results)}")

    # Show simulation statistics
    stats = simulator.get_simulation_stats()
    print(f"\nSimulation statistics:")
    print(f"  Total reach attempts: {stats['total_reach_attempts']}")
    print(f"  Successful reaches: {stats['successful_reaches']}")
    print(f"  Failed reaches: {stats['failed_reaches']}")
    print(f"  Current state: {stats['current_state']}")

    # Show reach history
    print(f"\nReach history:")
    for i, record in enumerate(simulator.reach_planner.reach_history):
        print(f"  Attempt {i+1}: Target {record['target']} -> {record['status']} (attempts: {record['attempts']})")

    # Demonstrate collision checking
    print(f"\nCollision checking demonstration:")
    test_points = [
        (0.5, 0.2, 1.3),  # Inside first obstacle
        (0.7, 0.0, 1.3),  # Clear space
        (0.3, -0.2, 1.4), # Near sphere obstacle
    ]

    for point in test_points:
        collisions = []
        for obs in simulator.reach_planner.obstacles:
            if obs.is_collision(point):
                collisions.append(obs.id)
        print(f"  Point {point}: {'Collision with ' + ', '.join(collisions) if collisions else 'No collision'}")

    # Show arm configuration
    print(f"\nArm configuration:")
    config = simulator.reach_planner.arm_config
    print(f"  Base position: {config.base_position}")
    print(f"  Number of joints: {len(config.joints)}")
    print(f"  Link lengths: {[f'{l:.2f}m' for l in config.link_lengths]}")
    print(f"  Joint names: {[j.name for j in config.joints]}")

    # Show forward kinematics
    print(f"\nForward kinematics:")
    joint_positions = config.forward_kinematics()
    for i, pos in enumerate(joint_positions):
        print(f"  Joint {i} position: ({pos[0]:.3f}, {pos[1]:.3f}, {pos[2]:.3f})")

    print(f"\nArm reach logic demonstration completed.")
    print("This shows how humanoid robots plan reaching motions while")
    print("considering obstacles, joint limits, and kinematic constraints.")


if __name__ == "__main__":
    main()