#!/usr/bin/env python3
"""
Forward/Inverse Kinematics Example

This module demonstrates conceptual forward and inverse kinematics for humanoid robots,
showing how to calculate joint angles and end-effector positions.
"""

from typing import Dict, List, Tuple, Optional, Any
import math
import random
import time
from dataclasses import dataclass


@dataclass
class Joint:
    """
    Represents a robot joint with position and constraints.
    """
    name: str
    position: float  # Current joint angle in radians
    min_angle: float = -math.pi  # Minimum joint angle
    max_angle: float = math.pi   # Maximum joint angle
    velocity: float = 0.0        # Current angular velocity
    torque: float = 0.0          # Current torque


@dataclass
class Link:
    """
    Represents a robot link with geometric properties.
    """
    name: str
    length: float  # Length of the link in meters
    offset: Tuple[float, float, float] = (0.0, 0.0, 0.0)  # Offset from joint
    mass: float = 0.0  # Mass of the link in kg


@dataclass
class Pose:
    """
    Represents a 3D pose with position and orientation.
    """
    position: Tuple[float, float, float]  # (x, y, z) in meters
    orientation: Tuple[float, float, float, float]  # Quaternion (w, x, y, z)


class SimpleKinematicChain:
    """
    Represents a simple kinematic chain for demonstration purposes.
    """
    def __init__(self, name: str, base_position: Tuple[float, float, float] = (0, 0, 0)) -> None:
        self.name = name
        self.base_position = base_position
        self.joints: List[Joint] = []
        self.links: List[Link] = []
        self.dh_parameters: List[Tuple[float, float, float, float]] = []  # (a, alpha, d, theta)

    def add_joint(self, joint: Joint, link: Link, dh_params: Tuple[float, float, float, float]) -> None:
        """
        Add a joint-link pair to the kinematic chain with DH parameters.

        DH parameters: (a, alpha, d, theta)
        - a: link length
        - alpha: link twist
        - d: link offset
        - theta: joint angle
        """
        self.joints.append(joint)
        self.links.append(link)
        self.dh_parameters.append(dh_params)

    def forward_kinematics(self, joint_angles: List[float]) -> List[Pose]:
        """
        Calculate forward kinematics - determine end-effector positions from joint angles.

        Args:
            joint_angles: List of joint angles in radians

        Returns:
            List of poses for each joint in the chain
        """
        if len(joint_angles) != len(self.joints):
            raise ValueError("Number of joint angles must match number of joints")

        poses = []
        current_transform = self._identity_transform()

        for i, angle in enumerate(joint_angles):
            # Update the joint angle in DH parameters
            a, alpha, d, _ = self.dh_parameters[i]
            updated_dh = (a, alpha, d, angle)

            # Calculate transformation matrix for this joint
            transform = self._dh_transform(*updated_dh)
            current_transform = self._multiply_transforms(current_transform, transform)

            # Extract position and create a simple orientation
            pos = (current_transform[0][3], current_transform[1][3], current_transform[2][3])
            # Simple orientation - in a real system, this would be calculated properly
            orientation = (1.0, 0.0, 0.0, 0.0)  # Identity quaternion
            pose = Pose(pos, orientation)
            poses.append(pose)

        return poses

    def _identity_transform(self) -> List[List[float]]:
        """Return a 4x4 identity transformation matrix."""
        return [
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ]

    def _dh_transform(self, a: float, alpha: float, d: float, theta: float) -> List[List[float]]:
        """
        Calculate transformation matrix using Denavit-Hartenberg parameters.
        """
        return [
            [math.cos(theta), -math.sin(theta)*math.cos(alpha), math.sin(theta)*math.sin(alpha), a*math.cos(theta)],
            [math.sin(theta), math.cos(theta)*math.cos(alpha), -math.cos(theta)*math.sin(alpha), a*math.sin(theta)],
            [0, math.sin(alpha), math.cos(alpha), d],
            [0, 0, 0, 1]
        ]

    def _multiply_transforms(self, t1: List[List[float]], t2: List[List[float]]) -> List[List[float]]:
        """Multiply two 4x4 transformation matrices."""
        result = [[0 for _ in range(4)] for _ in range(4)]
        for i in range(4):
            for j in range(4):
                for k in range(4):
                    result[i][j] += t1[i][k] * t2[k][j]
        return result

    def calculate_jacobian(self, joint_angles: List[float]) -> List[List[float]]:
        """
        Calculate the geometric Jacobian matrix for the kinematic chain.

        Args:
            joint_angles: List of joint angles in radians

        Returns:
            Jacobian matrix (6xN where N is number of joints)
        """
        # Forward kinematics to get all poses
        poses = self.forward_kinematics(joint_angles)
        end_effector_pos = poses[-1].position if poses else (0, 0, 0)

        # Initialize Jacobian (6xN - 3 for position, 3 for orientation)
        jacobian = [[0.0 for _ in range(len(joint_angles))] for _ in range(6)]

        current_transform = self._identity_transform()
        current_axis = [0, 0, 1]  # Initially z-axis

        for i, angle in enumerate(joint_angles):
            # Calculate transformation up to this joint
            a, alpha, d, _ = self.dh_parameters[i]
            joint_transform = self._dh_transform(a, alpha, d, angle)
            current_transform = self._multiply_transforms(current_transform, joint_transform)

            # Calculate the position of this joint
            joint_pos = (current_transform[0][3], current_transform[1][3], current_transform[2][3])

            # Calculate the axis of rotation for this joint (z-axis of current transform)
            z_axis = (current_transform[0][2], current_transform[1][2], current_transform[2][2])

            # Calculate position difference from this joint to end effector
            diff = (
                end_effector_pos[0] - joint_pos[0],
                end_effector_pos[1] - joint_pos[1],
                end_effector_pos[2] - joint_pos[2]
            )

            # Cross product for linear velocity part
            cross_product = (
                z_axis[1]*diff[2] - z_axis[2]*diff[1],
                z_axis[2]*diff[0] - z_axis[0]*diff[2],
                z_axis[0]*diff[1] - z_axis[1]*diff[0]
            )

            # Fill Jacobian matrix
            # Linear velocity part
            jacobian[0][i] = cross_product[0]  # x
            jacobian[1][i] = cross_product[1]  # y
            jacobian[2][i] = cross_product[2]  # z

            # Angular velocity part
            jacobian[3][i] = z_axis[0]  # wx
            jacobian[4][i] = z_axis[1]  # wy
            jacobian[5][i] = z_axis[2]  # wz

        return jacobian


class HumanoidArmKinematics:
    """
    Demonstrates kinematics for a humanoid arm.
    """
    def __init__(self) -> None:
        # Create a simple 3-DOF arm for demonstration
        self.arm_chain = SimpleKinematicChain("right_arm", (0.2, 0.0, 1.4))  # Starting position: shoulder

        # Add joints and links (simplified human arm)
        # Joint 1: Shoulder (rotation in x-z plane)
        self.arm_chain.add_joint(
            Joint("shoulder_yaw", 0.0, -math.pi/2, math.pi/2),
            Link("upper_arm", 0.3),  # 30cm upper arm
            (0.0, 0.0, 0.0, 0.0)  # DH parameters: a, alpha, d, theta
        )

        # Joint 2: Elbow
        self.arm_chain.add_joint(
            Joint("elbow_pitch", 0.0, 0.0, math.pi),  # Elbow only bends one way
            Link("forearm", 0.25),  # 25cm forearm
            (0.0, 0.0, 0.0, 0.0)
        )

        # Joint 3: Wrist
        self.arm_chain.add_joint(
            Joint("wrist_yaw", 0.0, -math.pi/2, math.pi/2),
            Link("hand", 0.08),  # 8cm hand approximation
            (0.0, 0.0, 0.0, 0.0)
        )

    def forward_kinematics_demo(self) -> Dict[str, Any]:
        """Demonstrate forward kinematics with different joint configurations."""
        results = {}

        # Example 1: Arm at side
        joint_angles_1 = [0.0, 0.0, 0.0]
        poses_1 = self.arm_chain.forward_kinematics(joint_angles_1)
        results["arm_at_side"] = {
            "joint_angles": joint_angles_1,
            "end_effector_position": poses_1[-1].position if poses_1 else None,
            "all_poses": [pose.position for pose in poses_1]
        }

        # Example 2: Arm raised forward
        joint_angles_2 = [0.2, 0.5, 0.0]
        poses_2 = self.arm_chain.forward_kinematics(joint_angles_2)
        results["arm_raised_forward"] = {
            "joint_angles": joint_angles_2,
            "end_effector_position": poses_2[-1].position if poses_2 else None,
            "all_poses": [pose.position for pose in poses_2]
        }

        # Example 3: Arm reaching to the side
        joint_angles_3 = [math.pi/3, 0.3, -math.pi/4]
        poses_3 = self.arm_chain.forward_kinematics(joint_angles_3)
        results["arm_reaching_side"] = {
            "joint_angles": joint_angles_3,
            "end_effector_position": poses_3[-1].position if poses_3 else None,
            "all_poses": [pose.position for pose in poses_3]
        }

        return results

    def jacobian_demo(self) -> Dict[str, Any]:
        """Demonstrate Jacobian calculation."""
        joint_angles = [0.1, 0.5, 0.2]
        jacobian = self.arm_chain.calculate_jacobian(joint_angles)

        return {
            "joint_angles": joint_angles,
            "jacobian": jacobian,
            "jacobian_shape": (len(jacobian), len(jacobian[0]) if jacobian else 0)
        }


class KinematicSolver:
    """
    Provides utilities for solving kinematic problems.
    """
    def __init__(self) -> None:
        pass

    def inverse_kinematics_simple(self, target_pos: Tuple[float, float, float],
                                chain: SimpleKinematicChain,
                                initial_angles: List[float],
                                max_iterations: int = 100,
                                tolerance: float = 0.01) -> Optional[List[float]]:
        """
        Solve inverse kinematics using a simple Jacobian transpose method.

        Args:
            target_pos: Target end-effector position (x, y, z)
            chain: Kinematic chain to solve for
            initial_angles: Initial joint angle guesses
            max_iterations: Maximum number of iterations
            tolerance: Position tolerance for convergence

        Returns:
            List of joint angles that achieve the target position, or None if no solution found
        """
        current_angles = initial_angles[:]
        target_x, target_y, target_z = target_pos

        for iteration in range(max_iterations):
            # Calculate current end-effector position
            current_poses = chain.forward_kinematics(current_angles)
            if not current_poses:
                return None

            current_pos = current_poses[-1].position
            current_x, current_y, current_z = current_pos

            # Calculate error
            error_x = target_x - current_x
            error_y = target_y - current_y
            error_z = target_z - current_z
            error_magnitude = math.sqrt(error_x**2 + error_y**2 + error_z**2)

            # Check if we're close enough
            if error_magnitude < tolerance:
                return current_angles

            # Calculate Jacobian
            jacobian = chain.calculate_jacobian(current_angles)

            # Use only position part of Jacobian (first 3 rows)
            j_pos = [row[:len(current_angles)] for row in jacobian[:3]]

            # Calculate joint adjustments using Jacobian transpose
            # delta_theta = J^T * delta_x
            delta_angles = [0.0] * len(current_angles)
            learning_rate = 0.1  # Small step size for stability

            for i in range(len(current_angles)):
                delta_angles[i] = learning_rate * (
                    j_pos[0][i] * error_x +
                    j_pos[1][i] * error_y +
                    j_pos[2][i] * error_z
                )

            # Apply joint angle updates with limits
            for i in range(len(current_angles)):
                new_angle = current_angles[i] + delta_angles[i]

                # Apply joint limits
                joint_min = chain.joints[i].min_angle
                joint_max = chain.joints[i].max_angle
                new_angle = max(joint_min, min(joint_max, new_angle))

                current_angles[i] = new_angle

        # Return None if we didn't converge
        return None

    def calculate_reachability(self, chain: SimpleKinematicChain) -> Dict[str, float]:
        """
        Calculate the theoretical reachability of a kinematic chain.

        Args:
            chain: Kinematic chain to analyze

        Returns:
            Dictionary with reachability information
        """
        total_length = sum(link.length for link in chain.links)

        # For a simple analysis, assume the workspace is roughly spherical
        # with radius equal to the sum of link lengths
        return {
            "maximum_reach": total_length,
            "workspace_volume": (4/3) * math.pi * total_length**3,  # Approximate
            "num_joints": len(chain.joints)
        }


def main() -> None:
    """
    Main function demonstrating forward and inverse kinematics.
    """
    print("Starting kinematics demonstration for humanoid robot...")
    print("Showing forward and inverse kinematics calculations.\n")

    # Initialize the humanoid arm kinematics
    arm_kinematics = HumanoidArmKinematics()
    kinematic_solver = KinematicSolver()

    print("1. Forward Kinematics Demo:")
    print("   Calculating end-effector positions from joint angles...\n")

    fk_results = arm_kinematics.forward_kinematics_demo()
    for pose_name, data in fk_results.items():
        print(f"   {pose_name}:")
        print(f"     Joint angles: {[f'{angle:.3f}' for angle in data['joint_angles']]} rad")
        print(f"     End-effector position: {data['end_effector_position']}")
        print(f"     All joint positions: {data['all_poses']}")
        print()

    print("2. Jacobian Demo:")
    print("   Calculating Jacobian matrix for motion planning...\n")

    jacobian_results = arm_kinematics.jacobian_demo()
    print(f"   Joint angles: {[f'{angle:.3f}' for angle in jacobian_results['joint_angles']]} rad")
    print(f"   Jacobian shape: {jacobian_results['jacobian_shape']}")
    print(f"   Sample Jacobian values (first column): {[row[0] for row in jacobian_results['jacobian'][:6]]}")
    print()

    print("3. Reachability Analysis:")
    reachability = kinematic_solver.calculate_reachability(arm_kinematics.arm_chain)
    print(f"   Maximum reach: {reachability['maximum_reach']:.3f} m")
    print(f"   Approximate workspace volume: {reachability['workspace_volume']:.3f} m³")
    print(f"   Number of joints: {reachability['num_joints']}")
    print()

    print("4. Inverse Kinematics Demo:")
    print("   Solving for joint angles to reach target positions...\n")

    # Define target positions to reach
    targets = [
        (0.5, 0.2, 1.3),   # Reach forward and slightly up
        (0.3, -0.3, 1.2),  # Reach to the left and down
        (0.6, 0.0, 1.5),   # Reach straight forward and higher
    ]

    for i, target in enumerate(targets):
        print(f"   Target {i+1}: {target}")

        # Use initial angles close to zero
        initial_angles = [0.0, 0.3, 0.0]

        # Solve inverse kinematics
        solution = kinematic_solver.inverse_kinematics_simple(
            target,
            arm_kinematics.arm_chain,
            initial_angles
        )

        if solution:
            print(f"     Solution found: {[f'{angle:.3f}' for angle in solution]} rad")

            # Verify the solution by running forward kinematics
            final_poses = arm_kinematics.arm_chain.forward_kinematics(solution)
            final_pos = final_poses[-1].position if final_poses else None

            if final_pos:
                distance_error = math.sqrt(
                    (final_pos[0] - target[0])**2 +
                    (final_pos[1] - target[1])**2 +
                    (final_pos[2] - target[2])**2
                )
                print(f"     Reached position: {final_pos}")
                print(f"     Position error: {distance_error:.3f} m")
        else:
            print(f"     No solution found within constraints")
        print()

    print("5. Workspace Visualization (Conceptual):")
    print("   The robot arm workspace is limited by:")
    print("   - Joint angle constraints")
    print("   - Link lengths")
    print("   - Physical interference between links")
    print("   - Balance constraints for the full robot")
    print()

    print("6. Kinematic Chain Properties:")
    chain = arm_kinematics.arm_chain
    print(f"   Chain name: {chain.name}")
    print(f"   Base position: {chain.base_position}")
    print(f"   Number of joints: {len(chain.joints)}")
    print(f"   Joint names: {[joint.name for joint in chain.joints]}")
    print(f"   Link lengths: {[link.length for link in chain.links]} m")
    print()

    # Demonstrate joint constraints
    print("7. Joint Constraints:")
    for i, joint in enumerate(chain.joints):
        print(f"   Joint {i+1} ({joint.name}):")
        print(f"     Range: [{joint.min_angle:.3f}, {joint.max_angle:.3f}] rad")
        print(f"     Current position: {joint.position:.3f} rad")
    print()

    print("Kinematics demonstration completed.")
    print("This shows how humanoid robots calculate the relationship between")
    print("joint angles and end-effector positions for movement planning.")


if __name__ == "__main__":
    main()