#!/usr/bin/env python3
"""
Friction Modeling Example

This module demonstrates conceptual friction modeling for humanoid robots,
showing how to model different types of friction and their effects on robot motion.
"""

from typing import Dict, List, Tuple, Optional
import math
import random
import time


class SurfaceProperties:
    """
    Represents the properties of a surface that affect friction.
    """

    def __init__(self, name: str, static_friction: float, kinetic_friction: float,
                 surface_roughness: float = 0.5, viscosity: float = 0.1) -> None:
        self.name = name
        self.static_friction = static_friction  # Coefficient of static friction (μs)
        self.kinetic_friction = kinetic_friction  # Coefficient of kinetic friction (μk)
        self.surface_roughness = surface_roughness  # Surface roughness (0.0 to 1.0)
        self.viscosity = viscosity  # Viscosity factor for fluid-like surfaces
        self.adhesion_factor = 0.1  # Additional adhesion effect

    def get_friction_coefficient(self, relative_velocity: float,
                                is_slipping: bool) -> float:
        """
        Get the appropriate friction coefficient based on conditions.

        Args:
            relative_velocity: Relative velocity between surfaces
            is_slipping: Whether surfaces are currently slipping

        Returns:
            Friction coefficient to use
        """
        # Use kinetic friction when slipping, static friction when not
        if is_slipping or abs(relative_velocity) > 0.001:  # Threshold for "not moving"
            # Adjust kinetic friction based on velocity (Stribeck effect)
            velocity_factor = max(0.8, 1.0 - (abs(relative_velocity) * 0.1))
            return self.kinetic_friction * velocity_factor
        else:
            # Static friction can vary up to its maximum value
            return self.static_friction


class ContactInterface:
    """
    Represents the interface between two surfaces in contact.
    """

    def __init__(self, surface_a: SurfaceProperties, surface_b: SurfaceProperties,
                 contact_area: float = 0.01, normal_force: float = 100.0) -> None:
        self.surface_a = surface_a
        self.surface_b = surface_b
        self.contact_area = contact_area  # Area of contact in m^2
        self.normal_force = normal_force  # Normal force pressing surfaces together
        self.relative_position = (0.0, 0.0, 0.0)  # Relative position of contact
        self.relative_velocity = (0.0, 0.0, 0.0)  # Relative velocity at contact
        self.temperature = 20.0  # Temperature in Celsius

        # Calculate combined surface properties
        self.combined_static_friction = math.sqrt(surface_a.static_friction * surface_b.static_friction)
        self.combined_kinetic_friction = math.sqrt(surface_a.kinetic_friction * surface_b.kinetic_friction)
        self.combined_roughness = (surface_a.surface_roughness + surface_b.surface_roughness) / 2.0

    def update_contact_state(self, new_normal_force: float,
                           new_relative_velocity: Tuple[float, float, float]) -> None:
        """Update the contact state with new forces and velocities."""
        self.normal_force = new_normal_force
        self.relative_velocity = new_relative_velocity

    def calculate_friction_force(self) -> Tuple[float, float, float]:
        """
        Calculate the friction force based on current contact state.

        Returns:
            Friction force vector opposing motion
        """
        # Calculate relative speed
        rel_speed = math.sqrt(
            self.relative_velocity[0]**2 +
            self.relative_velocity[1]**2 +
            self.relative_velocity[2]**2
        )

        # Determine if we're in static or kinetic friction regime
        is_slipping = rel_speed > 0.001

        # Get appropriate friction coefficient
        friction_coeff = self.combined_kinetic_friction if is_slipping else self.combined_static_friction
        friction_coeff = self._adjust_for_conditions(friction_coeff, rel_speed, is_slipping)

        # Calculate maximum possible friction force (Coulomb friction limit)
        max_friction_force = friction_coeff * abs(self.normal_force)

        # Calculate friction force opposing the direction of motion
        if rel_speed > 0.001:  # Moving
            # Friction opposes motion direction
            friction_direction = (
                -self.relative_velocity[0] / rel_speed,
                -self.relative_velocity[1] / rel_speed,
                -self.relative_velocity[2] / rel_speed
            )
            friction_magnitude = min(max_friction_force, rel_speed * 10.0)  # Proportional to speed
        else:  # Not moving - static friction can vary up to its limit
            # For this example, assume a small external force is trying to move the object
            # In reality, static friction would oppose that external force
            friction_direction = (0.0, 0.0, 0.0)
            friction_magnitude = min(max_friction_force, 5.0)  # Small static friction force

        # Calculate friction force vector
        friction_force = (
            friction_magnitude * friction_direction[0],
            friction_magnitude * friction_direction[1],
            friction_magnitude * friction_direction[2]
        )

        return friction_force

    def _adjust_for_conditions(self, base_coeff: float, rel_speed: float,
                             is_slipping: bool) -> float:
        """Adjust friction coefficient based on environmental conditions."""
        # Temperature effect (simplified)
        temp_factor = 1.0 - ((self.temperature - 20.0) * 0.001)  # Friction typically decreases with temperature
        adjusted_coeff = base_coeff * max(0.1, temp_factor)

        # Velocity effect (Stribeck effect)
        if is_slipping:
            # At very low velocities, friction can be higher (stiction)
            if rel_speed < 0.01:
                adjusted_coeff *= 1.1  # Slightly higher friction at very low speeds
            elif rel_speed > 1.0:
                # At high velocities, friction typically decreases
                adjusted_coeff *= max(0.7, 1.0 - (rel_speed * 0.1))

        # Surface roughness effect
        roughness_factor = 1.0 + (self.combined_roughness * 0.5)
        adjusted_coeff *= roughness_factor

        # Adhesion effect (more important at low forces)
        adhesion_effect = self.adhesion_factor * (1.0 / max(1.0, self.normal_force / 10.0))
        adjusted_coeff += adhesion_effect

        return adjusted_coeff


class FrictionModel:
    """
    Models friction for different parts of a humanoid robot.
    """

    def __init__(self) -> None:
        # Define different surface materials
        self.surfaces = {
            "rubber_sole": SurfaceProperties("Rubber shoe sole", 0.8, 0.7, 0.7, 0.05),
            "metal_foot": SurfaceProperties("Metal foot", 0.4, 0.3, 0.2, 0.1),
            "fabric": SurfaceProperties("Fabric clothing", 0.3, 0.25, 0.4, 0.08),
            "skin": SurfaceProperties("Human skin", 0.8, 0.7, 0.3, 0.15),
            "wood_floor": SurfaceProperties("Wooden floor", 0.5, 0.4, 0.4, 0.02),
            "tile_floor": SurfaceProperties("Tile floor", 0.6, 0.5, 0.3, 0.01),
            "carpet": SurfaceProperties("Carpet", 0.7, 0.6, 0.8, 0.2),
            "ice": SurfaceProperties("Ice", 0.1, 0.05, 0.1, 0.005)
        }

        # Contact interfaces for different robot parts
        self.contact_interfaces: Dict[str, ContactInterface] = {}
        self._setup_robot_contacts()

    def _setup_robot_contacts(self) -> None:
        """Set up contact interfaces for different robot parts."""
        # Feet contacts
        self.contact_interfaces["left_foot"] = ContactInterface(
            self.surfaces["rubber_sole"], self.surfaces["tile_floor"],
            contact_area=0.02, normal_force=300.0  # Assuming 300N per foot for 60kg robot
        )
        self.contact_interfaces["right_foot"] = ContactInterface(
            self.surfaces["rubber_sole"], self.surfaces["tile_floor"],
            contact_area=0.02, normal_force=300.0
        )

        # Hand contacts (for manipulation)
        self.contact_interfaces["left_hand"] = ContactInterface(
            self.surfaces["fabric"], self.surfaces["wood_floor"],
            contact_area=0.005, normal_force=50.0
        )
        self.contact_interfaces["right_hand"] = ContactInterface(
            self.surfaces["fabric"], self.surfaces["wood_floor"],
            contact_area=0.005, normal_force=50.0
        )

        # Other potential contact points
        self.contact_interfaces["knee_left"] = ContactInterface(
            self.surfaces["fabric"], self.surfaces["carpet"],
            contact_area=0.002, normal_force=100.0
        )

    def update_contact_forces(self, robot_state: Dict[str, any]) -> Dict[str, Tuple[float, float, float]]:
        """
        Update contact forces based on robot state.

        Args:
            robot_state: Current state of the robot

        Returns:
            Dictionary mapping contact points to friction forces
        """
        friction_forces = {}

        for name, interface in self.contact_interfaces.items():
            # Get relative velocity at this contact point
            # For this example, we'll use simplified values based on robot motion
            if "foot" in name:
                # Feet typically have low relative velocity when walking normally
                rel_vel = robot_state.get("foot_relative_velocity", (0.0, 0.0, 0.0))
            elif "hand" in name:
                # Hands may have higher relative velocity during manipulation
                rel_vel = robot_state.get("hand_relative_velocity", (0.0, 0.0, 0.0))
            else:
                # Other contact points
                rel_vel = robot_state.get("other_relative_velocity", (0.0, 0.0, 0.0))

            # Update contact state
            if name in ["left_foot", "right_foot"]:
                # Update normal force based on robot's weight distribution
                weight_on_foot = robot_state.get("weight_on_" + name.split("_")[0], 300.0)
                interface.update_contact_state(weight_on_foot, rel_vel)
            else:
                interface.update_contact_state(interface.normal_force, rel_vel)

            # Calculate friction force
            friction_force = interface.calculate_friction_force()
            friction_forces[name] = friction_force

        return friction_forces

    def get_friction_analysis(self) -> Dict[str, any]:
        """Get a detailed analysis of friction at all contact points."""
        analysis = {}

        for name, interface in self.contact_interfaces.items():
            rel_speed = math.sqrt(
                interface.relative_velocity[0]**2 +
                interface.relative_velocity[1]**2 +
                interface.relative_velocity[2]**2
            )

            is_slipping = rel_speed > 0.001
            friction_coeff = interface.combined_kinetic_friction if is_slipping else interface.combined_static_friction
            max_friction = friction_coeff * abs(interface.normal_force)

            friction_force = interface.calculate_friction_force()
            actual_friction_magnitude = math.sqrt(
                friction_force[0]**2 + friction_force[1]**2 + friction_force[2]**2
            )

            analysis[name] = {
                "normal_force": interface.normal_force,
                "relative_speed": rel_speed,
                "is_slipping": is_slipping,
                "friction_coefficient": friction_coeff,
                "max_possible_friction": max_friction,
                "actual_friction_force": actual_friction_magnitude,
                "surface_a": interface.surface_a.name,
                "surface_b": interface.surface_b.name,
                "friction_percentage": min(1.0, actual_friction_magnitude / max_friction) if max_friction > 0 else 0.0
            }

        return analysis

    def change_surface(self, contact_name: str, new_surface_name: str) -> bool:
        """Change the surface for a specific contact point."""
        if contact_name not in self.contact_interfaces:
            return False

        if new_surface_name not in self.surfaces:
            return False

        interface = self.contact_interfaces[contact_name]

        # Keep the same surface for the robot part, change the environment surface
        if "foot" in contact_name:
            # Robot foot surface stays the same, environment changes
            self.contact_interfaces[contact_name] = ContactInterface(
                interface.surface_a, self.surfaces[new_surface_name],
                interface.contact_area, interface.normal_force
            )
        elif "hand" in contact_name:
            # Robot hand surface stays the same, object surface changes
            self.contact_interfaces[contact_name] = ContactInterface(
                interface.surface_a, self.surfaces[new_surface_name],
                interface.contact_area, interface.normal_force
            )
        else:
            # For other contacts, change the environment surface
            self.contact_interfaces[contact_name] = ContactInterface(
                interface.surface_a, self.surfaces[new_surface_name],
                interface.contact_area, interface.normal_force
            )

        return True


class FrictionSimulator:
    """
    Simulates friction effects on a humanoid robot.
    """

    def __init__(self) -> None:
        self.friction_model = FrictionModel()
        self.simulation_time = 0.0
        self.dt = 0.01  # 10ms time step

    def simulate_step(self, robot_velocity: Tuple[float, float, float],
                     robot_angular_velocity: Tuple[float, float, float]) -> Dict[str, Tuple[float, float, float]]:
        """
        Simulate one step of friction effects.

        Args:
            robot_velocity: Robot's linear velocity
            robot_angular_velocity: Robot's angular velocity

        Returns:
            Dictionary of friction forces at contact points
        """
        # Calculate relative velocities at contact points
        # This is a simplified model - in reality, this would involve forward kinematics
        robot_speed = math.sqrt(robot_velocity[0]**2 + robot_velocity[1]**2 + robot_velocity[2]**2)

        robot_state = {
            "foot_relative_velocity": (
                robot_velocity[0] * 0.8,  # Feet move slightly slower than COM
                robot_velocity[1] * 0.8,
                0.0  # Z velocity is typically 0 for feet in stance phase
            ),
            "hand_relative_velocity": (
                robot_velocity[0] * 1.1,  # Hands may move faster
                robot_velocity[1] * 1.1,
                robot_velocity[2] * 1.1
            ),
            "other_relative_velocity": robot_velocity,
            "weight_on_left": 300.0 + random.uniform(-50, 50),  # Weight distribution varies
            "weight_on_right": 300.0 + random.uniform(-50, 50)
        }

        # Calculate friction forces
        friction_forces = self.friction_model.update_contact_forces(robot_state)

        # Update simulation time
        self.simulation_time += self.dt

        return friction_forces

    def get_traction_analysis(self) -> Dict[str, any]:
        """Analyze the robot's traction capabilities."""
        analysis = self.friction_model.get_friction_analysis()

        total_traction = 0.0
        available_traction = 0.0
        number_of_contacts = 0

        for contact_info in analysis.values():
            total_traction += contact_info["actual_friction_force"]
            available_traction += contact_info["max_possible_friction"]
            number_of_contacts += 1

        avg_traction_utilization = (total_traction / available_traction) if available_traction > 0 else 0.0
        avg_normal_force = sum(info["normal_force"] for info in analysis.values()) / number_of_contacts if number_of_contacts > 0 else 0.0

        return {
            "total_traction": total_traction,
            "available_traction": available_traction,
            "traction_utilization": avg_traction_utilization,
            "avg_normal_force": avg_normal_force,
            "number_of_contacts": number_of_contacts,
            "slipping_contacts": sum(1 for info in analysis.values() if info["is_slipping"]),
            "contact_analysis": analysis
        }


def main() -> None:
    """
    Main function demonstrating friction modeling.
    """
    print("Starting friction modeling demonstration for humanoid robot...")
    print("Showing how to model different types of friction and their effects.\n")

    # Initialize the friction simulator
    simulator = FrictionSimulator()

    # Initial robot state
    robot_velocity = (0.0, 0.0, 0.0)  # Initially at rest
    robot_angular_velocity = (0.0, 0.0, 0.0)

    print("Initial friction state:")
    initial_analysis = simulator.get_traction_analysis()
    print(f"  Total available traction: {initial_analysis['available_traction']:.1f} N")
    print(f"  Current traction usage: {initial_analysis['total_traction']:.1f} N")
    print(f"  Traction utilization: {initial_analysis['traction_utilization']:.2f}")
    print(f"  Number of contacts: {initial_analysis['number_of_contacts']}")
    print()

    # Simulate different friction scenarios
    print("Simulating friction scenarios:")

    for scenario in range(5):
        print(f"\nScenario {scenario + 1}:")

        if scenario == 0:
            print("  Robot standing still on tile floor")
            for step in range(10):
                friction_forces = simulator.simulate_step(robot_velocity, robot_angular_velocity)
                if step == 0:
                    analysis = simulator.get_traction_analysis()
                    print(f"    Initial traction: {analysis['total_traction']:.1f} N")

        elif scenario == 1:
            print("  Robot starting to walk forward")
            robot_velocity = (0.3, 0.0, 0.0)  # 0.3 m/s forward
            for step in range(20):
                friction_forces = simulator.simulate_step(robot_velocity, robot_angular_velocity)
                if step == 19:
                    analysis = simulator.get_traction_analysis()
                    print(f"    Traction during walking: {analysis['total_traction']:.1f} N")

        elif scenario == 2:
            print("  Robot stepping on ice surface")
            simulator.friction_model.change_surface("left_foot", "ice")
            simulator.friction_model.change_surface("right_foot", "ice")
            for step in range(15):
                friction_forces = simulator.simulate_step(robot_velocity, robot_angular_velocity)
                if step == 14:
                    analysis = simulator.get_traction_analysis()
                    print(f"    Traction on ice: {analysis['total_traction']:.1f} N")
                    print(f"    Slipping contacts: {analysis['slipping_contacts']}")

        elif scenario == 3:
            print("  Robot walking on carpet")
            simulator.friction_model.change_surface("left_foot", "carpet")
            simulator.friction_model.change_surface("right_foot", "carpet")
            robot_velocity = (0.2, 0.0, 0.0)  # Slower on carpet
            for step in range(15):
                friction_forces = simulator.simulate_step(robot_velocity, robot_angular_velocity)
                if step == 14:
                    analysis = simulator.get_traction_analysis()
                    print(f"    Traction on carpet: {analysis['total_traction']:.1f} N")

        elif scenario == 4:
            print("  Robot experiencing lateral force (side push)")
            robot_velocity = (0.1, 0.4, 0.0)  # Moving sideways
            robot_angular_velocity = (0.1, 0.0, 0.0)  # Rotational motion
            for step in range(15):
                friction_forces = simulator.simulate_step(robot_velocity, robot_angular_velocity)
                if step == 14:
                    analysis = simulator.get_traction_analysis()
                    print(f"    Traction under lateral motion: {analysis['total_traction']:.1f} N")

    print(f"\nFinal friction analysis:")
    final_analysis = simulator.get_traction_analysis()
    print(f"  Total available traction: {final_analysis['available_traction']:.1f} N")
    print(f"  Current traction usage: {final_analysis['total_traction']:.1f} N")
    print(f"  Traction utilization: {final_analysis['traction_utilization']:.2f}")
    print(f"  Slipping contacts: {final_analysis['slipping_contacts']}")

    # Detailed contact analysis
    print(f"\nDetailed contact analysis:")
    contact_analysis = final_analysis['contact_analysis']
    for contact_name, details in contact_analysis.items():
        print(f"  {contact_name}:")
        print(f"    Surfaces: {details['surface_a']} vs {details['surface_b']}")
        print(f"    Normal force: {details['normal_force']:.1f} N")
        print(f"    Friction coeff: {details['friction_coefficient']:.2f}")
        print(f"    Actual friction: {details['actual_friction_force']:.1f} N")
        print(f"    Is slipping: {details['is_slipping']}")

    # Surface comparison
    print(f"\nSurface friction comparison:")
    surfaces_to_compare = ["tile_floor", "carpet", "ice", "wood_floor"]
    robot_state = {"foot_relative_velocity": (0.1, 0.0, 0.0), "weight_on_left": 300.0, "weight_on_right": 300.0}

    for surface_name in surfaces_to_compare:
        # Create a temporary contact interface
        rubber_on_surface = ContactInterface(
            simulator.friction_model.surfaces["rubber_sole"],
            simulator.friction_model.surfaces[surface_name],
            contact_area=0.02, normal_force=300.0
        )
        rubber_on_surface.update_contact_state(300.0, (0.1, 0.0, 0.0))
        friction_force = rubber_on_surface.calculate_friction_force()
        friction_magnitude = math.sqrt(sum(f**2 for f in friction_force))

        print(f"  Rubber on {surface_name}: {friction_magnitude:.1f} N traction")

    print(f"\nFriction modeling demonstration completed.")
    print("This shows how humanoid robots model friction to understand")
    print("traction capabilities and adapt to different surfaces.")


if __name__ == "__main__":
    main()