#!/usr/bin/env python3
"""
Pseudo Physics Scenario Example

This module demonstrates conceptual physics scenarios for humanoid robots,
showing how to model contact, friction, and force interactions in simulation.
"""

from typing import Dict, List, Tuple, Optional
import math
import random
import time


class PhysicsObject:
    """
    Represents a physical object in the simulation with properties that affect physics interactions.
    """

    def __init__(self, name: str, mass: float, position: Tuple[float, float, float],
                 velocity: Tuple[float, float, float] = (0, 0, 0),
                 friction_coefficient: float = 0.5, restitution: float = 0.3) -> None:
        self.name = name
        self.mass = mass  # in kg
        self.position = position  # (x, y, z) in meters
        self.velocity = velocity  # (vx, vy, vz) in m/s
        self.acceleration: Tuple[float, float, float] = (0, 0, 0)  # (ax, ay, az) in m/s^2
        self.friction_coefficient = friction_coefficient  # Coefficient of friction
        self.restitution = restitution  # Coefficient of restitution (bounciness)
        self.forces: List[Tuple[str, Tuple[float, float, float]]] = []  # Applied forces

    def add_force(self, force_type: str, force_vector: Tuple[float, float, float]) -> None:
        """Add a force to the object."""
        self.forces.append((force_type, force_vector))

    def calculate_net_force(self) -> Tuple[float, float, float]:
        """Calculate the net force acting on the object."""
        net_fx = net_fy = net_fz = 0.0

        # Add gravitational force
        gravity = 9.81  # m/s^2
        net_fz -= self.mass * gravity  # Gravity acts downward

        # Add all other forces
        for _, force in self.forces:
            net_fx += force[0]
            net_fy += force[1]
            net_fz += force[2]

        return (net_fx, net_fy, net_fz)

    def update_physics(self, dt: float) -> None:
        """Update the object's physics state based on forces."""
        net_force = self.calculate_net_force()

        # Calculate acceleration (F = ma => a = F/m)
        ax = net_force[0] / self.mass
        ay = net_force[1] / self.mass
        az = net_force[2] / self.mass
        self.acceleration = (ax, ay, az)

        # Update velocity (v = v0 + a*dt)
        new_vx = self.velocity[0] + ax * dt
        new_vy = self.velocity[1] + ay * dt
        new_vz = self.velocity[2] + az * dt
        self.velocity = (new_vx, new_vy, new_vz)

        # Update position (p = p0 + v*dt)
        new_x = self.position[0] + self.velocity[0] * dt
        new_y = self.position[1] + self.velocity[1] * dt
        new_z = self.position[2] + self.velocity[2] * dt
        self.position = (new_x, new_y, new_z)

        # Reset forces after applying them
        self.forces = []


class ContactModel:
    """
    Models contact interactions between objects.
    """

    def __init__(self) -> None:
        self.contact_distance_threshold = 0.01  # 1cm threshold for contact

    def detect_contact(self, obj1: PhysicsObject, obj2: PhysicsObject) -> bool:
        """Detect if two objects are in contact."""
        pos1 = obj1.position
        pos2 = obj2.position

        distance = math.sqrt(
            (pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2 + (pos1[2] - pos2[2])**2
        )

        return distance < self.contact_distance_threshold

    def calculate_contact_force(self, obj1: PhysicsObject, obj2: PhysicsObject) -> Tuple[float, float, float]:
        """Calculate the contact force between two objects."""
        pos1 = obj1.position
        pos2 = obj2.position

        # Calculate normal vector from obj1 to obj2
        dx = pos2[0] - pos1[0]
        dy = pos2[1] - pos1[1]
        dz = pos2[2] - pos1[2]

        distance = math.sqrt(dx**2 + dy**2 + dz**2)

        if distance == 0:
            return (0, 0, 0)  # Objects are at same position, avoid division by zero

        # Normalize the vector
        nx = dx / distance
        ny = dy / distance
        nz = dz / distance

        # Calculate relative velocity
        rel_vx = obj2.velocity[0] - obj1.velocity[0]
        rel_vy = obj2.velocity[1] - obj1.velocity[1]
        rel_vz = obj2.velocity[2] - obj1.velocity[2]

        # Calculate relative velocity in normal direction
        rel_vel_normal = rel_vx * nx + rel_vy * ny + rel_vz * nz

        # Calculate contact force based on relative velocity and material properties
        # This is a simplified model - real physics engines use more complex calculations
        stiffness = 1000.0  # Spring constant for contact
        damping = 50.0      # Damping coefficient

        # Penetration depth (simplified)
        penetration = max(0, self.contact_distance_threshold - distance)

        # Normal force (spring-like response)
        normal_force_magnitude = stiffness * penetration - damping * rel_vel_normal

        # Apply coefficient of restitution for bounce
        normal_force_magnitude *= obj1.restitution * obj2.restitution

        # Calculate friction force (opposes tangential motion)
        # Simplified friction model
        tangential_speed = math.sqrt(
            (rel_vx - rel_vel_normal * nx)**2 +
            (rel_vy - rel_vel_normal * ny)**2 +
            (rel_vz - rel_vel_normal * nz)**2
        )

        # Effective friction coefficient
        effective_friction = min(obj1.friction_coefficient, obj2.friction_coefficient)
        friction_force_magnitude = min(
            effective_friction * abs(normal_force_magnitude),
            damping * tangential_speed
        )

        # Calculate friction force vector (opposes tangential motion)
        if tangential_speed > 0:
            tx = (rel_vx - rel_vel_normal * nx) / tangential_speed
            ty = (rel_vy - rel_vel_normal * ny) / tangential_speed
            tz = (rel_vz - rel_vel_normal * nz) / tangential_speed

            friction_fx = -friction_force_magnitude * tx
            friction_fy = -friction_force_magnitude * ty
            friction_fz = -friction_force_magnitude * tz
        else:
            friction_fx = friction_fy = friction_fz = 0

        # Combine normal and friction forces
        contact_fx = normal_force_magnitude * nx + friction_fx
        contact_fy = normal_force_magnitude * ny + friction_fy
        contact_fz = normal_force_magnitude * nz + friction_fz

        return (contact_fx, contact_fy, contact_fz)


class PhysicsSimulator:
    """
    Simulates physics interactions for humanoid robots.
    """

    def __init__(self) -> None:
        self.objects: List[PhysicsObject] = []
        self.contact_model = ContactModel()
        self.gravity_enabled = True
        self.ground_level = 0.0  # Z position of ground

    def add_object(self, obj: PhysicsObject) -> None:
        """Add an object to the simulation."""
        self.objects.append(obj)

    def handle_ground_collision(self, obj: PhysicsObject) -> None:
        """Handle collision with the ground."""
        if obj.position[2] <= self.ground_level:
            # Position object on ground
            obj.position = (obj.position[0], obj.position[1], self.ground_level)

            # Apply ground reaction force to stop downward motion
            if obj.velocity[2] < 0:  # Moving downward
                # Calculate ground reaction force
                # This is simplified - real physics engines handle this more precisely
                impact_force = -obj.mass * obj.velocity[2] / 0.01  # Impulse over 0.01s
                ground_force = min(impact_force, obj.mass * 9.81 * 5)  # Limit force

                # Apply damping to vertical velocity
                bounce_factor = obj.restitution
                new_vz = -obj.velocity[2] * bounce_factor
                obj.velocity = (obj.velocity[0], obj.velocity[1], max(0, new_vz))

            # Apply friction with ground
            if abs(obj.velocity[0]) > 0.01 or abs(obj.velocity[1]) > 0.01:
                # Apply friction to horizontal motion
                friction_coeff = obj.friction_coefficient
                normal_force = obj.mass * 9.81  # Weight
                max_friction_force = friction_coeff * normal_force

                # Calculate friction force opposing motion
                speed = math.sqrt(obj.velocity[0]**2 + obj.velocity[1]**2)
                if speed > 0:
                    friction_fx = -max_friction_force * (obj.velocity[0] / speed)
                    friction_fy = -max_friction_force * (obj.velocity[1] / speed)

                    # Apply friction force
                    obj.add_force("friction", (friction_fx, friction_fy, 0))

    def simulate_step(self, dt: float) -> None:
        """Simulate one time step of physics."""
        # Apply forces and update physics for all objects
        for obj in self.objects:
            # Handle ground collision
            self.handle_ground_collision(obj)

            # Update physics
            obj.update_physics(dt)

        # Handle object-to-object contacts
        for i in range(len(self.objects)):
            for j in range(i + 1, len(self.objects)):
                obj1 = self.objects[i]
                obj2 = self.objects[j]

                if self.contact_model.detect_contact(obj1, obj2):
                    # Calculate contact forces
                    contact_force = self.contact_model.calculate_contact_force(obj1, obj2)

                    # Apply equal and opposite forces
                    obj1.add_force("contact", (-contact_force[0], -contact_force[1], -contact_force[2]))
                    obj2.add_force("contact", contact_force)

    def apply_external_force(self, obj_name: str, force: Tuple[float, float, float]) -> bool:
        """Apply an external force to a named object."""
        for obj in self.objects:
            if obj.name == obj_name:
                obj.add_force("external", force)
                return True
        return False


def main() -> None:
    """
    Main function demonstrating pseudo physics scenarios.
    """
    print("Starting pseudo physics simulation for humanoid robot scenarios...")
    print("Demonstrating contact, friction, and force interactions.\n")

    # Create a physics simulator
    simulator = PhysicsSimulator()

    # Create a humanoid robot (simplified as a single object for this example)
    humanoid = PhysicsObject(
        name="humanoid_robot",
        mass=60.0,  # 60 kg
        position=(0.0, 0.0, 1.0),  # 1 meter above ground
        velocity=(0.0, 0.0, 0.0),  # Initially at rest
        friction_coefficient=0.7,  # Higher friction for better grip
        restitution=0.2  # Low bounce for stability
    )

    # Create a box to interact with
    box = PhysicsObject(
        name="box",
        mass=5.0,  # 5 kg
        position=(0.5, 0.0, 0.1),  # 0.1m above ground (on the ground)
        velocity=(0.0, 0.0, 0.0),
        friction_coefficient=0.5,
        restitution=0.3
    )

    # Add objects to simulator
    simulator.add_object(humanoid)
    simulator.add_object(box)

    print("Initial state:")
    print(f"  Humanoid: pos={humanoid.position}, vel={humanoid.velocity}")
    print(f"  Box: pos={box.position}, vel={box.velocity}")
    print()

    # Simulate for a number of steps
    dt = 0.01  # 10ms time step
    steps = 500  # 5 seconds of simulation

    print(f"Running simulation for {steps * dt:.1f} seconds...")
    print("Applying various forces to demonstrate physics interactions:\n")

    for step in range(steps):
        # Apply external forces at specific times to demonstrate different scenarios
        if step == 10:  # After 0.1 seconds, apply a push to the humanoid
            simulator.apply_external_force("humanoid_robot", (50.0, 0.0, 0.0))  # Push forward
            print(f"Step {step}: Applied 50N forward force to humanoid")

        if step == 50:  # After 0.5 seconds, apply a force to the box
            simulator.apply_external_force("box", (20.0, 0.0, 0.0))  # Push box
            print(f"Step {step}: Applied 20N forward force to box")

        if step == 100:  # After 1 second, apply upward force (like a jump)
            simulator.apply_external_force("humanoid_robot", (0.0, 0.0, 300.0))  # Jump
            print(f"Step {step}: Applied 300N upward force to humanoid (jump)")

        if step == 200:  # After 2 seconds, apply a lateral push
            simulator.apply_external_force("humanoid_robot", (0.0, -100.0, 0.0))  # Push sideways
            print(f"Step {step}: Applied 100N lateral force to humanoid")

        # Run the simulation step
        simulator.simulate_step(dt)

        # Print status at regular intervals
        if step % 100 == 0 and step > 0:
            print(f"Step {step}: Humanoid pos={humanoid.position}, vel={humanoid.velocity}")
            print(f"         Box pos={box.position}, vel={box.velocity}")

    print(f"\nFinal state after {steps * dt:.1f} seconds:")
    print(f"  Humanoid: pos={humanoid.position}, vel={humanoid.velocity}")
    print(f"  Box: pos={box.position}, vel={box.velocity}")

    # Analyze the results
    print(f"\nPhysics analysis:")
    print(f"  Humanoid moved from z={1.0:.2f} to z={humanoid.position[2]:.2f}")
    print(f"  Box moved from x={0.5:.2f} to x={box.position[0]:.2f}")
    print(f"  Final humanoid velocity: {math.sqrt(sum(v**2 for v in humanoid.velocity)):.2f} m/s")

    # Demonstrate contact detection
    final_distance = math.sqrt(
        (humanoid.position[0] - box.position[0])**2 +
        (humanoid.position[1] - box.position[1])**2 +
        (humanoid.position[2] - box.position[2])**2
    )
    print(f"  Final distance between humanoid and box: {final_distance:.3f} m")
    print(f"  Are they in contact? {final_distance < simulator.contact_model.contact_distance_threshold}")

    print(f"\nPhysics simulation completed.")
    print("This demonstrates how contact, friction, and force interactions")
    print("affect the behavior of humanoid robots in their environment.")


if __name__ == "__main__":
    main()