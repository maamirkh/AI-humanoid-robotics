#!/usr/bin/env python3
"""
Force Analysis Example

This module demonstrates conceptual force analysis for humanoid robots,
showing how to analyze forces acting on the robot and their effects on motion.
"""

from typing import Dict, List, Tuple, Optional
import math
import random
import time


class Force:
    """
    Represents a force vector with magnitude and direction.
    """

    def __init__(self, name: str, vector: Tuple[float, float, float],
                 application_point: Tuple[float, float, float] = (0, 0, 0),
                 duration: Optional[float] = None) -> None:
        self.name = name
        self.vector = vector  # (fx, fy, fz) in Newtons
        self.application_point = application_point  # Point where force is applied (x, y, z)
        self.magnitude = math.sqrt(vector[0]**2 + vector[1]**2 + vector[2]**2)
        self.start_time = time.time()
        self.duration = duration  # Duration in seconds, None means permanent
        self.active = True

    def is_active(self, current_time: float) -> bool:
        """Check if the force is still active."""
        if self.duration is None:
            return True  # Permanent force
        elapsed = current_time - self.start_time
        return elapsed < self.duration

    def get_force_at_time(self, current_time: float) -> Optional[Tuple[float, float, float]]:
        """Get the force vector if it's active at the given time."""
        if self.is_active(current_time):
            return self.vector
        return None


class Moment:
    """
    Represents a moment (torque) caused by a force at a distance from a reference point.
    """

    def __init__(self, force: Force, reference_point: Tuple[float, float, float]) -> None:
        self.force = force
        self.reference_point = reference_point

        # Calculate moment arm (vector from reference point to force application point)
        self.moment_arm = (
            force.application_point[0] - reference_point[0],
            force.application_point[1] - reference_point[1],
            force.application_point[2] - reference_point[2]
        )

        # Calculate moment (torque) using cross product: M = r × F
        self.moment = (
            self.moment_arm[1] * force.vector[2] - self.moment_arm[2] * force.vector[1],  # Mx
            self.moment_arm[2] * force.vector[0] - self.moment_arm[0] * force.vector[2],  # My
            self.moment_arm[0] * force.vector[1] - self.moment_arm[1] * force.vector[0]   # Mz
        )

        self.magnitude = math.sqrt(self.moment[0]**2 + self.moment[1]**2 + self.moment[2]**2)


class RobotDynamics:
    """
    Models the dynamic behavior of a humanoid robot under various forces.
    """

    def __init__(self, mass: float = 60.0, height: float = 1.7) -> None:
        self.mass = mass  # Robot mass in kg
        self.height = height  # Robot height in meters
        self.position: Tuple[float, float, float] = (0, 0, height/2)  # COM position
        self.velocity: Tuple[float, float, float] = (0, 0, 0)  # Linear velocity
        self.acceleration: Tuple[float, float, float] = (0, 0, 0)  # Linear acceleration
        self.orientation: Tuple[float, float, float, float] = (1, 0, 0, 0)  # Quaternion
        self.angular_velocity: Tuple[float, float, float] = (0, 0, 0)  # Angular velocity
        self.angular_acceleration: Tuple[float, float, float] = (0, 0, 0)  # Angular acceleration

        # Moments of inertia (simplified as a rectangular prism)
        # Ixx, Iyy, Izz for rotation around x, y, z axes
        width = 0.3  # Simplified width
        depth = 0.2  # Simplified depth
        self.moments_of_inertia = (
            (1/12) * mass * (height**2 + depth**2),  # Ixx
            (1/12) * mass * (width**2 + height**2),  # Iyy
            (1/12) * mass * (width**2 + depth**2)   # Izz
        )

        self.applied_forces: List[Force] = []
        self.contact_forces: Dict[str, Force] = {}  # Forces from environment contact

    def add_force(self, force: Force) -> None:
        """Add an external force to the robot."""
        self.applied_forces.append(force)

    def remove_force(self, force_name: str) -> bool:
        """Remove a force by name."""
        for i, force in enumerate(self.applied_forces):
            if force.name == force_name:
                del self.applied_forces[i]
                return True
        return False

    def update_contact_forces(self, contact_points: Dict[str, Tuple[float, float, float]]) -> None:
        """Update contact forces based on contact points."""
        self.contact_forces = {}
        current_time = time.time()

        for name, contact_pos in contact_points.items():
            # Calculate ground reaction force based on robot's position and velocity
            # This is a simplified model - real robots would have more complex contact models
            ground_level = 0.0

            if contact_pos[2] <= ground_level + 0.01:  # If near ground
                # Calculate force to prevent penetration
                penetration = max(0, ground_level - contact_pos[2])
                stiffness = 10000.0  # Spring constant

                # Calculate normal force
                normal_force = min(stiffness * penetration, 2000.0)  # Limit force

                # Calculate damping based on velocity
                damping = 100.0
                velocity_component = self.velocity[2]  # Z component of velocity
                damping_force = damping * abs(velocity_component)

                total_force = normal_force + damping_force

                # Apply force in upward direction
                contact_force = Force(
                    f"contact_{name}",
                    (0, 0, total_force),
                    contact_pos
                )
                self.contact_forces[name] = contact_force

    def calculate_net_force_and_moment(self) -> Tuple[Tuple[float, float, float], Tuple[float, float, float]]:
        """Calculate net force and net moment acting on the robot."""
        current_time = time.time()

        # Calculate net force
        net_fx = net_fy = net_fz = 0.0

        # Add gravitational force
        gravity = 9.81  # m/s^2
        net_fz -= self.mass * gravity  # Weight acts downward

        # Add all active applied forces
        for force in self.applied_forces:
            if force.is_active(current_time):
                force_vector = force.vector
                net_fx += force_vector[0]
                net_fy += force_vector[1]
                net_fz += force_vector[2]

        # Add contact forces
        for contact_force in self.contact_forces.values():
            force_vector = contact_force.vector
            net_fx += force_vector[0]
            net_fy += force_vector[1]
            net_fz += force_vector[2]

        # Calculate net moment around center of mass
        net_mx = net_my = net_mz = 0.0

        # Add moments from all active applied forces
        for force in self.applied_forces:
            if force.is_active(current_time):
                moment = Moment(force, self.position)
                net_mx += moment.moment[0]
                net_my += moment.moment[1]
                net_mz += moment.moment[2]

        # Add moments from contact forces
        for contact_force in self.contact_forces.values():
            moment = Moment(contact_force, self.position)
            net_mx += moment.moment[0]
            net_my += moment.moment[1]
            net_mz += moment.moment[2]

        return (net_fx, net_fy, net_fz), (net_mx, net_my, net_mz)

    def update_dynamics(self, dt: float) -> None:
        """Update robot dynamics based on forces and moments."""
        net_force, net_moment = self.calculate_net_force_and_moment()

        # Calculate linear acceleration (F = ma => a = F/m)
        ax = net_force[0] / self.mass
        ay = net_force[1] / self.mass
        az = net_force[2] / self.mass
        self.acceleration = (ax, ay, az)

        # Update linear velocity (v = v0 + a*dt)
        new_vx = self.velocity[0] + ax * dt
        new_vy = self.velocity[1] + ay * dt
        new_vz = self.velocity[2] + az * dt
        self.velocity = (new_vx, new_vy, new_vz)

        # Update position (p = p0 + v*dt)
        new_x = self.position[0] + self.velocity[0] * dt
        new_y = self.position[1] + self.velocity[1] * dt
        new_z = self.position[2] + self.velocity[2] * dt
        self.position = (new_x, new_y, new_z)

        # Calculate angular acceleration (M = Iα => α = M/I)
        # For simplicity, assume moments of inertia are constant and diagonal
        ixx, iyy, izz = self.moments_of_inertia

        # Avoid division by zero
        alpha_x = net_moment[0] / ixx if ixx != 0 else 0
        alpha_y = net_moment[1] / iyy if iyy != 0 else 0
        alpha_z = net_moment[2] / izz if izz != 0 else 0
        self.angular_acceleration = (alpha_x, alpha_y, alpha_z)

        # Update angular velocity (ω = ω0 + α*dt)
        new_omega_x = self.angular_velocity[0] + alpha_x * dt
        new_omega_y = self.angular_velocity[1] + alpha_y * dt
        new_omega_z = self.angular_velocity[2] + alpha_z * dt
        self.angular_velocity = (new_omega_x, new_omega_y, new_omega_z)

        # Update orientation based on angular velocity
        # This is a simplified integration of quaternion kinematics
        # In a real system, proper quaternion integration would be used
        self._update_orientation(dt)

        # Remove expired forces
        current_time = time.time()
        self.applied_forces = [f for f in self.applied_forces if f.is_active(current_time)]

    def _update_orientation(self, dt: float) -> None:
        """Update orientation based on angular velocity."""
        # Convert angular velocity to quaternion derivative
        # Simplified approach - in reality, quaternion integration is more complex
        wx, wy, wz = self.angular_velocity

        # Scale down angular velocity to prevent large orientation changes per step
        scale_factor = 0.1
        wx *= scale_factor
        wy *= scale_factor
        wz *= scale_factor

        # Calculate quaternion derivative
        q = self.orientation
        dq = (
            -0.5 * (wx * q[1] + wy * q[2] + wz * q[3]),
            0.5 * (wx * q[0] + wz * q[2] - wy * q[3]),
            0.5 * (wy * q[0] - wz * q[1] + wx * q[3]),
            0.5 * (wz * q[0] + wy * q[1] - wx * q[2])
        )

        # Update quaternion
        new_q = (
            q[0] + dq[0] * dt,
            q[1] + dq[1] * dt,
            q[2] + dq[2] * dt,
            q[3] + dq[3] * dt
        )

        # Normalize quaternion
        norm = math.sqrt(new_q[0]**2 + new_q[1]**2 + new_q[2]**2 + new_q[3]**2)
        if norm > 0:
            self.orientation = (new_q[0]/norm, new_q[1]/norm, new_q[2]/norm, new_q[3]/norm)

    def get_force_analysis(self) -> Dict[str, any]:
        """Get a detailed analysis of forces acting on the robot."""
        current_time = time.time()
        active_forces = [f for f in self.applied_forces if f.is_active(current_time)]

        analysis = {
            "total_mass": self.mass,
            "weight": self.mass * 9.81,
            "applied_forces_count": len(active_forces),
            "contact_forces_count": len(self.contact_forces),
            "net_force": self.calculate_net_force_and_moment()[0],
            "net_moment": self.calculate_net_force_and_moment()[1],
            "linear_momentum": (self.mass * self.velocity[0],
                              self.mass * self.velocity[1],
                              self.mass * self.velocity[2]),
            "angular_momentum": (self.moments_of_inertia[0] * self.angular_velocity[0],
                               self.moments_of_inertia[1] * self.angular_velocity[1],
                               self.moments_of_inertia[2] * self.angular_velocity[2]),
            "kinetic_energy": 0.5 * self.mass * sum(v**2 for v in self.velocity) +
                             0.5 * (self.moments_of_inertia[0] * self.angular_velocity[0]**2 +
                                   self.moments_of_inertia[1] * self.angular_velocity[1]**2 +
                                   self.moments_of_inertia[2] * self.angular_velocity[2]**2),
            "stability_index": self._calculate_stability_index()
        }

        return analysis

    def _calculate_stability_index(self) -> float:
        """Calculate a simple stability index."""
        # Calculate Zero Moment Point (ZMP) for stability assessment
        net_force = self.calculate_net_force_and_moment()[0]
        net_moment = self.calculate_net_force_and_moment()[1]

        if abs(net_force[2]) < 0.1:  # If vertical force is very small
            return 0.0

        # Calculate ZMP (simplified)
        zmp_x = self.position[0] - net_moment[1] / net_force[2]
        zmp_y = self.position[1] + net_moment[0] / net_force[2]

        # Calculate distance from ZMP to support polygon (simplified as feet positions)
        # For this example, assume feet are at fixed positions relative to COM
        foot_positions = [
            (self.position[0] + 0.1, self.position[1] - 0.1),  # left foot
            (self.position[0] + 0.1, self.position[1] + 0.1)   # right foot
        ]

        # Calculate distance from ZMP to nearest foot
        min_distance = min(
            math.sqrt((zmp_x - fx)**2 + (zmp_y - fy)**2)
            for fx, fy in foot_positions
        )

        # Stability is inversely related to ZMP distance from support base
        # Normalize to 0-1 scale (1 = very stable, 0 = unstable)
        max_stable_distance = 0.3  # 30cm threshold
        stability = max(0.0, min(1.0, (max_stable_distance - min_distance) / max_stable_distance))

        return stability


class ForceAnalyzer:
    """
    Analyzes forces acting on a humanoid robot and their effects.
    """

    def __init__(self) -> None:
        self.dynamics_model = RobotDynamics()
        self.analysis_history: List[Dict] = []

    def apply_impulse(self, force_vector: Tuple[float, float, float],
                     application_point: Tuple[float, float, float],
                     duration: float = 0.1) -> str:
        """Apply an impulse force to the robot."""
        force_name = f"impulse_{int(time.time() * 1000)}"
        impulse_force = Force(force_name, force_vector, application_point, duration)
        self.dynamics_model.add_force(impulse_force)
        return force_name

    def apply_continuous_force(self, name: str, force_vector: Tuple[float, float, float],
                             application_point: Tuple[float, float, float]) -> None:
        """Apply a continuous force to the robot."""
        force = Force(name, force_vector, application_point)
        self.dynamics_model.add_force(force)

    def simulate_step(self, dt: float = 0.01) -> Dict[str, any]:
        """Simulate one step of force analysis."""
        # Update contact forces based on current position
        contact_points = {
            "left_foot": (self.dynamics_model.position[0] + 0.1,
                         self.dynamics_model.position[1] - 0.1, 0.0),
            "right_foot": (self.dynamics_model.position[0] + 0.1,
                          self.dynamics_model.position[1] + 0.1, 0.0)
        }
        self.dynamics_model.update_contact_forces(contact_points)

        # Update dynamics
        self.dynamics_model.update_dynamics(dt)

        # Perform analysis
        analysis = self.dynamics_model.get_force_analysis()
        analysis["timestamp"] = time.time()
        analysis["position"] = self.dynamics_model.position
        analysis["velocity"] = self.dynamics_model.velocity
        analysis["acceleration"] = self.dynamics_model.acceleration

        self.analysis_history.append(analysis)
        return analysis

    def get_force_breakdown(self) -> Dict[str, float]:
        """Get a breakdown of different types of forces."""
        current_time = time.time()
        active_forces = [f for f in self.dynamics_model.applied_forces if f.is_active(current_time)]

        breakdown = {
            "gravity": self.dynamics_model.mass * 9.81,
            "applied_horizontal": 0.0,
            "applied_vertical": 0.0,
            "applied_lateral": 0.0,
            "contact_vertical": 0.0,
            "contact_horizontal": 0.0
        }

        # Sum up applied forces by component
        for force in active_forces:
            breakdown["applied_horizontal"] += abs(force.vector[0])
            breakdown["applied_vertical"] += abs(force.vector[2])  # Z is vertical
            breakdown["applied_lateral"] += abs(force.vector[1])

        # Sum up contact forces by component
        for contact_force in self.dynamics_model.contact_forces.values():
            breakdown["contact_vertical"] += abs(contact_force.vector[2])
            breakdown["contact_horizontal"] += math.sqrt(contact_force.vector[0]**2 + contact_force.vector[1]**2)

        return breakdown


def main() -> None:
    """
    Main function demonstrating force analysis.
    """
    print("Starting force analysis demonstration for humanoid robot...")
    print("Showing how to analyze forces and their effects on robot motion.\n")

    # Initialize the force analyzer
    analyzer = ForceAnalyzer()

    print("Initial robot state:")
    initial_analysis = analyzer.dynamics_model.get_force_analysis()
    print(f"  Position: {analyzer.dynamics_model.position}")
    print(f"  Velocity: {analyzer.dynamics_model.velocity}")
    print(f"  Weight: {initial_analysis['weight']:.1f} N")
    print(f"  Initial stability: {initial_analysis['stability_index']:.2f}")
    print()

    # Simulate various force scenarios
    print("Simulating force analysis scenarios:")

    dt = 0.01  # 10ms time step
    steps_per_scenario = 50  # 0.5 seconds per scenario

    for scenario in range(5):
        print(f"\nScenario {scenario + 1}:")

        if scenario == 0:
            print("  Initial state - robot standing still")
            for step in range(steps_per_scenario):
                analysis = analyzer.simulate_step(dt)
                if step == 0:
                    print(f"    Starting stability: {analysis['stability_index']:.2f}")

        elif scenario == 1:
            print("  Applying forward push force")
            push_force = analyzer.apply_impulse((100, 0, 0), (0, 0, 0.8), 0.5)  # 100N forward push
            for step in range(steps_per_scenario):
                analysis = analyzer.simulate_step(dt)
                if step == steps_per_scenario - 1:
                    print(f"    Final velocity after push: {math.sqrt(sum(v**2 for v in analysis['velocity'])):.2f} m/s")

        elif scenario == 2:
            print("  Applying upward lift force")
            lift_force = analyzer.apply_impulse((0, 0, 300), (0, 0, 0.5), 0.3)  # 300N upward
            for step in range(steps_per_scenario):
                analysis = analyzer.simulate_step(dt)
                if step == steps_per_scenario - 1:
                    print(f"    Position change due to lift: {analysis['position'][2] - analyzer.dynamics_model.position[2]:.2f} m")

        elif scenario == 3:
            print("  Applying lateral force (side push)")
            lateral_force = analyzer.apply_impulse((0, 150, 0), (0, 0, 0.7), 0.4)  # 150N side push
            for step in range(steps_per_scenario):
                analysis = analyzer.simulate_step(dt)
                if step == steps_per_scenario - 1:
                    print(f"    Lateral displacement: {abs(analysis['position'][1] - analyzer.dynamics_model.position[1]):.2f} m")

        elif scenario == 4:
            print("  Recovery phase - observing natural dynamics")
            for step in range(steps_per_scenario):
                analysis = analyzer.simulate_step(dt)
                if step == 0:
                    print(f"    Initial state: pos={analysis['position']}, vel={analysis['velocity']}")
                elif step == steps_per_scenario - 1:
                    print(f"    Final state: pos={analysis['position']}, vel={analysis['velocity']}")

    print(f"\nFinal analysis:")
    final_analysis = analyzer.dynamics_model.get_force_analysis()
    print(f"  Final position: {analyzer.dynamics_model.position}")
    print(f"  Final velocity: {math.sqrt(sum(v**2 for v in analyzer.dynamics_model.velocity)):.2f} m/s")
    print(f"  Final stability: {final_analysis['stability_index']:.2f}")
    print(f"  Kinetic energy: {final_analysis['kinetic_energy']:.2f} J")

    # Show force breakdown
    force_breakdown = analyzer.get_force_breakdown()
    print(f"\nForce breakdown:")
    for force_type, magnitude in force_breakdown.items():
        print(f"  {force_type}: {magnitude:.1f} N")

    # Analyze the history
    print(f"\nDynamics analysis:")
    if len(analyzer.analysis_history) > 1:
        initial = analyzer.analysis_history[0]
        final = analyzer.analysis_history[-1]

        print(f"  Position change: ({final['position'][0] - initial['position'][0]:.2f}, "
              f"{final['position'][1] - initial['position'][1]:.2f}, "
              f"{final['position'][2] - initial['position'][2]:.2f}) m")
        print(f"  Velocity change magnitude: {math.sqrt(sum(v**2 for v in final['velocity'])):.2f} m/s")
        print(f"  Peak kinetic energy during simulation: {max(a['kinetic_energy'] for a in analyzer.analysis_history):.2f} J")

    print(f"\nForce analysis demonstration completed.")
    print("This shows how humanoid robots analyze forces to understand")
    print("their motion and maintain stability under various conditions.")


if __name__ == "__main__":
    main()