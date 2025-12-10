#!/usr/bin/env python3
"""
Contact Modeling Example

This module demonstrates conceptual contact modeling for humanoid robots,
showing how to model physical contact between robot and environment.
"""

from typing import Dict, List, Tuple, Optional
import math
import random
import time


class ContactPoint:
    """
    Represents a single point of contact between the robot and environment.
    """

    def __init__(self, position: Tuple[float, float, float],
                 normal: Tuple[float, float, float],
                 friction_coefficient: float = 0.5) -> None:
        self.position = position  # Contact position in world coordinates
        self.normal = self._normalize_vector(normal)  # Surface normal at contact point
        self.friction_coefficient = friction_coefficient
        self.contact_force: Tuple[float, float, float] = (0.0, 0.0, 0.0)
        self.is_active = False  # Whether contact is currently happening
        self.contact_area = 0.01  # Area of contact (m^2), affects pressure

    def _normalize_vector(self, v: Tuple[float, float, float]) -> Tuple[float, float, float]:
        """Normalize a 3D vector."""
        magnitude = math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)
        if magnitude == 0:
            return (0.0, 0.0, 1.0)  # Default to upward normal
        return (v[0]/magnitude, v[1]/magnitude, v[2]/magnitude)

    def calculate_contact_force(self, penetration_depth: float,
                               relative_velocity: Tuple[float, float, float],
                               dt: float) -> Tuple[float, float, float]:
        """
        Calculate the contact force based on penetration and relative motion.

        Args:
            penetration_depth: How deep the penetration is (m)
            relative_velocity: Relative velocity at contact point (m/s)
            dt: Time step (s)

        Returns:
            Contact force vector (fx, fy, fz)
        """
        if penetration_depth <= 0:
            self.is_active = False
            return (0.0, 0.0, 0.0)

        # Spring-damper model for normal force
        stiffness = 10000.0  # N/m
        damping = 100.0      # Ns/m

        normal_force_magnitude = (stiffness * penetration_depth -
                                 damping * self._dot_product(relative_velocity, self.normal))

        # Limit the force to prevent numerical instability
        max_normal_force = 10000.0  # N
        normal_force_magnitude = min(max_normal_force, max(0.0, normal_force_magnitude))

        # Calculate normal force vector
        normal_force = (
            normal_force_magnitude * self.normal[0],
            normal_force_magnitude * self.normal[1],
            normal_force_magnitude * self.normal[2]
        )

        # Calculate tangential velocity (velocity in the plane perpendicular to normal)
        normal_velocity_magnitude = self._dot_product(relative_velocity, self.normal)
        normal_velocity = (
            normal_velocity_magnitude * self.normal[0],
            normal_velocity_magnitude * self.normal[1],
            normal_velocity_magnitude * self.normal[2]
        )

        tangential_velocity = (
            relative_velocity[0] - normal_velocity[0],
            relative_velocity[1] - normal_velocity[1],
            relative_velocity[2] - normal_velocity[2]
        )

        # Calculate friction force using Coulomb friction model
        tangential_speed = math.sqrt(tangential_velocity[0]**2 +
                                   tangential_velocity[1]**2 +
                                   tangential_velocity[2]**2)

        if tangential_speed > 0.001:  # Avoid division by zero
            # Normalize tangential velocity
            tx = tangential_velocity[0] / tangential_speed
            ty = tangential_velocity[1] / tangential_speed
            tz = tangential_velocity[2] / tangential_speed

            # Calculate friction force magnitude (Coulomb friction)
            friction_force_magnitude = min(
                self.friction_coefficient * normal_force_magnitude,
                damping * tangential_speed  # Limit to prevent instability
            )

            # Friction force opposes tangential motion
            friction_force = (
                -friction_force_magnitude * tx,
                -friction_force_magnitude * ty,
                -friction_force_magnitude * tz
            )
        else:
            friction_force = (0.0, 0.0, 0.0)

        # Combine normal and friction forces
        total_force = (
            normal_force[0] + friction_force[0],
            normal_force[1] + friction_force[1],
            normal_force[2] + friction_force[2]
        )

        self.contact_force = total_force
        self.is_active = True

        return total_force

    def _dot_product(self, v1: Tuple[float, float, float],
                    v2: Tuple[float, float, float]) -> float:
        """Calculate the dot product of two vectors."""
        return v1[0]*v2[0] + v1[1]*v2[1] + v1[2]*v2[2]


class ContactPatch:
    """
    Represents a patch of contact with multiple contact points.
    """

    def __init__(self, center_position: Tuple[float, float, float],
                 surface_normal: Tuple[float, float, float],
                 size: float = 0.1, num_points: int = 4) -> None:
        self.center = center_position
        self.normal = surface_normal
        self.size = size  # Size of the contact patch in meters
        self.contact_points: List[ContactPoint] = []

        # Create multiple contact points in the patch
        for i in range(num_points):
            # Distribute points in a grid pattern
            dx = (i % 2) * size - size/2
            dy = (i // 2) * size - size/2
            dz = 0  # Assume flat surface for this example

            point_pos = (
                center_position[0] + dx,
                center_position[1] + dy,
                center_position[2] + dz
            )

            self.contact_points.append(ContactPoint(
                point_pos, surface_normal,
                friction_coefficient=random.uniform(0.4, 0.8)
            ))

    def calculate_total_contact_force(self, penetration_depth: float,
                                    relative_velocity: Tuple[float, float, float],
                                    dt: float) -> Tuple[float, float, float]:
        """Calculate total contact force from all points in the patch."""
        total_fx = total_fy = total_fz = 0.0

        for point in self.contact_points:
            force = point.calculate_contact_force(penetration_depth, relative_velocity, dt)
            total_fx += force[0]
            total_fy += force[1]
            total_fz += force[2]

        return (total_fx, total_fy, total_fz)

    def get_active_contacts(self) -> List[ContactPoint]:
        """Get list of currently active contact points."""
        return [point for point in self.contact_points if point.is_active]


class RobotContactModel:
    """
    Models contact for an entire humanoid robot with multiple contact points.
    """

    def __init__(self) -> None:
        self.contact_patches: Dict[str, ContactPatch] = {}
        self.global_contact_forces: Dict[str, Tuple[float, float, float]] = {}
        self.contact_history: List[Dict] = []

    def add_contact_patch(self, name: str, position: Tuple[float, float, float],
                         normal: Tuple[float, float, float], body_part: str) -> None:
        """Add a contact patch for a specific body part."""
        # Different body parts might have different properties
        if body_part == "foot":
            patch_size = 0.15  # Larger for feet
            num_points = 6
        elif body_part == "hand":
            patch_size = 0.05  # Smaller for hands
            num_points = 4
        else:
            patch_size = 0.1  # Default size
            num_points = 4

        self.contact_patches[name] = ContactPatch(position, normal, patch_size, num_points)

    def detect_environment_contacts(self, robot_position: Tuple[float, float, float],
                                  robot_orientation: Tuple[float, float, float, float],
                                  environment_heightmap: Optional[Dict[str, float]] = None) -> Dict[str, float]:
        """
        Detect potential contact points with the environment.

        Args:
            robot_position: Robot's position in world coordinates
            robot_orientation: Robot's orientation as quaternion (w, x, y, z)
            environment_heightmap: Optional heightmap of environment

        Returns:
            Dictionary mapping contact patch names to penetration depth
        """
        penetrations = {}

        # For this example, we'll simulate contact with a flat ground
        # In a real system, this would use environment data
        ground_level = 0.0

        for name, patch in self.contact_patches.items():
            # Transform patch position based on robot pose
            # For simplicity, we'll just use the z-coordinate for ground contact
            transformed_z = patch.center[2]

            # Calculate penetration depth with ground
            if transformed_z <= ground_level:
                penetration_depth = ground_level - transformed_z
                penetrations[name] = max(0.0, penetration_depth)
            else:
                penetrations[name] = 0.0

        # Add some simulated obstacles
        for name, patch in self.contact_patches.items():
            if "foot" in name.lower():
                # Simulate stepping on a small obstacle
                if 1.0 < robot_position[0] < 1.2 and 0.8 < robot_position[1] < 1.0:
                    # There's a 2cm high obstacle at this location
                    obstacle_height = 0.02
                    if patch.center[2] <= obstacle_height:
                        penetration = obstacle_height - patch.center[2]
                        penetrations[name] = max(penetration, penetrations[name])

        return penetrations

    def calculate_contact_forces(self, penetrations: Dict[str, float],
                               robot_velocity: Tuple[float, float, float],
                               dt: float) -> Dict[str, Tuple[float, float, float]]:
        """
        Calculate contact forces for all contact patches.

        Args:
            penetrations: Dictionary of penetration depths for each patch
            robot_velocity: Robot's velocity
            dt: Time step

        Returns:
            Dictionary mapping patch names to contact forces
        """
        forces = {}

        for name, patch in self.contact_patches.items():
            penetration = penetrations.get(name, 0.0)

            # For simplicity, assume relative velocity is the same as robot velocity
            # In reality, this would account for local velocities at contact points
            force = patch.calculate_total_contact_force(penetration, robot_velocity, dt)
            forces[name] = force

            # Store in global forces
            self.global_contact_forces[name] = force

        return forces

    def get_contact_status(self) -> Dict[str, Dict[str, any]]:
        """Get status of all contact patches."""
        status = {}

        for name, patch in self.contact_patches.items():
            active_contacts = patch.get_active_contacts()
            total_force = self.global_contact_forces.get(name, (0, 0, 0))

            status[name] = {
                "active_points": len(active_contacts),
                "total_force": total_force,
                "max_force_component": max(abs(c) for c in total_force),
                "contact_positions": [cp.position for cp in active_contacts]
            }

        return status


class ContactSimulator:
    """
    Simulates contact interactions for humanoid robots.
    """

    def __init__(self) -> None:
        self.robot_model = RobotContactModel()
        self.time = 0.0
        self.dt = 0.01  # 10ms time step

    def setup_robot_contacts(self) -> None:
        """Set up contact patches for a humanoid robot."""
        # Add contact patches for feet
        self.robot_model.add_contact_patch(
            "left_foot_center", (0.1, -0.1, 0.05), (0, 0, 1), "foot"
        )
        self.robot_model.add_contact_patch(
            "right_foot_center", (0.1, 0.1, 0.05), (0, 0, 1), "foot"
        )

        # Add contact patches for hands
        self.robot_model.add_contact_patch(
            "left_hand", (-0.3, -0.2, 0.8), (1, 0, 0), "hand"
        )
        self.robot_model.add_contact_patch(
            "right_hand", (-0.3, 0.2, 0.8), (1, 0, 0), "hand"
        )

        # Add contact patch for pelvis (for when robot falls)
        self.robot_model.add_contact_patch(
            "pelvis", (0.0, 0.0, 0.5), (0, 0, 1), "body"
        )

    def simulate_step(self, robot_position: Tuple[float, float, float],
                     robot_orientation: Tuple[float, float, float, float],
                     robot_velocity: Tuple[float, float, float]) -> Dict[str, Tuple[float, float, float]]:
        """
        Simulate one step of contact physics.

        Args:
            robot_position: Robot's current position
            robot_orientation: Robot's current orientation (quaternion)
            robot_velocity: Robot's current velocity

        Returns:
            Dictionary of contact forces
        """
        # Detect potential contacts
        penetrations = self.robot_model.detect_environment_contacts(
            robot_position, robot_orientation
        )

        # Calculate contact forces
        forces = self.robot_model.calculate_contact_forces(penetrations, robot_velocity, self.dt)

        # Update time
        self.time += self.dt

        return forces

    def get_stability_measure(self) -> float:
        """
        Calculate a simple stability measure based on contact forces.

        Returns:
            Stability measure (0.0 to 1.0, where 1.0 is perfectly stable)
        """
        status = self.robot_model.get_contact_status()

        if not status:
            return 0.0

        # Calculate stability based on number of contact points and force distribution
        total_active_points = sum(data["active_points"] for data in status.values())
        total_force_magnitude = sum(
            math.sqrt(sum(c**2 for c in data["total_force"]))
            for data in status.values()
        )

        # Simple stability metric
        # More contact points generally mean more stability
        # Balanced forces also contribute to stability
        stability = min(1.0, total_active_points / 4.0)  # Assume 4 main contact points

        # Reduce stability if forces are too high (indicating impact)
        if total_force_magnitude > 1000:  # 1000N threshold
            stability *= 0.5

        return stability


def main() -> None:
    """
    Main function demonstrating contact modeling.
    """
    print("Starting contact modeling demonstration for humanoid robot...")
    print("Showing how to model physical contact between robot and environment.\n")

    # Initialize the contact simulator
    simulator = ContactSimulator()
    simulator.setup_robot_contacts()

    # Initial robot state
    robot_position = (0.0, 0.0, 0.8)  # Standing at 0.8m height
    robot_orientation = (1.0, 0.0, 0.0, 0.0)  # No rotation (quaternion)
    robot_velocity = (0.0, 0.0, 0.0)  # Initially at rest

    print("Initial robot state:")
    print(f"  Position: {robot_position}")
    print(f"  Velocity: {robot_velocity}")
    print(f"  Initial stability: {simulator.get_stability_measure():.2f}")
    print()

    # Simulate several steps to demonstrate contact modeling
    print("Simulating contact scenarios:")

    for step in range(10):
        print(f"\nStep {step + 1}: Time = {simulator.time:.2f}s")

        # Apply different scenarios based on step
        if step == 0:
            print("  Scenario: Robot standing still")
        elif step == 1:
            print("  Scenario: Robot starts to lean forward")
            robot_velocity = (0.1, 0.0, 0.0)  # Slow forward motion
        elif step == 2:
            print("  Scenario: Robot continues forward motion")
        elif step == 3:
            print("  Scenario: Robot steps forward (simulated)")
            robot_position = (robot_position[0] + 0.1, robot_position[1], robot_position[2])
        elif step == 4:
            print("  Scenario: Robot encounters small obstacle")
            # Move robot position to trigger obstacle contact
            robot_position = (1.1, 0.9, robot_position[2])
        elif step == 5:
            print("  Scenario: Robot applies corrective motion")
            robot_velocity = (-0.05, 0.0, 0.0)  # Move back slightly
        elif step == 6:
            print("  Scenario: Robot maintains position")
            robot_velocity = (0.0, 0.0, 0.0)
        elif step == 7:
            print("  Scenario: Simulated external force (push)")
            robot_velocity = (-0.2, 0.0, 0.0)  # Simulated push backward
        elif step == 8:
            print("  Scenario: Robot recovers from push")
            robot_velocity = (0.1, 0.0, 0.0)  # Move forward to recover
        elif step == 9:
            print("  Scenario: Robot stabilizes")

        # Simulate contact physics
        contact_forces = simulator.simulate_step(
            robot_position, robot_orientation, robot_velocity
        )

        # Update robot position based on velocity
        robot_position = (
            robot_position[0] + robot_velocity[0] * simulator.dt,
            robot_position[1] + robot_velocity[1] * simulator.dt,
            robot_position[2] + robot_velocity[2] * simulator.dt
        )

        # Print contact information
        contact_status = simulator.robot_model.get_contact_status()
        active_contacts = sum(1 for data in contact_status.values() if data["active_points"] > 0)
        total_force = sum(
            math.sqrt(sum(c**2 for c in data["total_force"]))
            for data in contact_status.values()
        )

        print(f"  Active contact patches: {active_contacts}/5")
        print(f"  Total contact force magnitude: {total_force:.2f} N")
        print(f"  Current stability measure: {simulator.get_stability_measure():.2f}")

        # Print forces for each contact patch
        for name, force in contact_forces.items():
            if any(abs(f) > 0.01 for f in force):  # Only print if force is significant
                print(f"    {name}: F=({force[0]:.1f}, {force[1]:.1f}, {force[2]:.1f}) N")

    print(f"\nFinal state:")
    print(f"  Position: {robot_position}")
    print(f"  Final stability: {simulator.get_stability_measure():.2f}")

    # Analyze the contact patterns
    print(f"\nContact analysis:")
    final_status = simulator.robot_model.get_contact_status()
    for name, data in final_status.items():
        if data["active_points"] > 0:
            print(f"  {name}: {data['active_points']} active points, "
                  f"force magnitude: {math.sqrt(sum(c**2 for c in data['total_force'])):.1f} N")

    print(f"\nContact modeling demonstration completed.")
    print("This shows how humanoid robots model physical contact to maintain")
    print("stability and respond appropriately to environmental interactions.")


if __name__ == "__main__":
    main()