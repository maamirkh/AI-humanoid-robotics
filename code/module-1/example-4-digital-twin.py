#!/usr/bin/env python3
"""
Conceptual Digital Twin Example

This module demonstrates a conceptual digital twin for humanoid robots,
showing how to create and maintain a virtual representation of the physical robot.
"""

from typing import Dict, List, Optional, Tuple, Any
import time
import math
import random
from dataclasses import dataclass


@dataclass
class PhysicalState:
    """
    Represents the physical state of the robot in the real world.
    """
    timestamp: float
    position: Tuple[float, float, float]  # x, y, z in meters
    orientation: Tuple[float, float, float, float]  # quaternion (w, x, y, z)
    joint_angles: Dict[str, float]  # Joint names and angles in radians
    velocities: Dict[str, float]  # Joint velocities in rad/s
    accelerations: Dict[str, float]  # Joint accelerations in rad/s^2
    sensor_data: Dict[str, Any]  # Various sensor readings


@dataclass
class VirtualState:
    """
    Represents the virtual state of the robot in the digital twin.
    """
    timestamp: float
    position: Tuple[float, float, float]  # x, y, z in meters
    orientation: Tuple[float, float, float, float]  # quaternion (w, x, y, z)
    joint_angles: Dict[str, float]  # Joint names and angles in radians
    predicted_forces: Dict[str, float]  # Predicted forces at joints
    environment_model: Dict[str, Any]  # Model of the environment
    uncertainty: Dict[str, float]  # Uncertainty estimates for each parameter


class SensorInterface:
    """
    Simulates interface to physical sensors on the robot.
    """

    def __init__(self) -> None:
        self.joint_names = [
            "hip_left_roll", "hip_left_pitch", "hip_left_yaw",
            "knee_left", "ankle_left_pitch", "ankle_left_roll",
            "hip_right_roll", "hip_right_pitch", "hip_right_yaw",
            "knee_right", "ankle_right_pitch", "ankle_right_roll",
            "shoulder_left_roll", "shoulder_left_pitch", "shoulder_left_yaw",
            "elbow_left", "shoulder_right_roll", "shoulder_right_pitch",
            "shoulder_right_yaw", "elbow_right", "neck_pitch", "neck_yaw"
        ]
        self.last_state: Optional[PhysicalState] = None

    def read_sensors(self) -> PhysicalState:
        """
        Read current sensor values from the physical robot.

        Returns:
            PhysicalState object with current readings
        """
        timestamp = time.time()

        # Generate realistic joint angles (with some randomness for simulation)
        joint_angles = {}
        for joint in self.joint_names:
            if "knee" in joint:
                # Knee joints typically have limited range
                joint_angles[joint] = random.uniform(0.0, 1.5)
            elif "ankle" in joint:
                # Ankle joints have small range
                joint_angles[joint] = random.uniform(-0.3, 0.3)
            elif "hip" in joint:
                # Hip joints have moderate range
                joint_angles[joint] = random.uniform(-0.5, 0.5)
            elif "shoulder" in joint:
                # Shoulder joints have wide range
                joint_angles[joint] = random.uniform(-1.0, 1.0)
            elif "elbow" in joint:
                # Elbow joints have limited range
                joint_angles[joint] = random.uniform(-0.5, 0.5)
            elif "neck" in joint:
                # Neck joints have limited range
                joint_angles[joint] = random.uniform(-0.5, 0.5)

        # Calculate velocities based on previous state (if available)
        velocities: Dict[str, float] = {}
        accelerations: Dict[str, float] = {}
        if self.last_state:
            dt = timestamp - self.last_state.timestamp
            if dt > 0:
                for joint in self.joint_names:
                    if joint in self.last_state.joint_angles:
                        vel = (joint_angles[joint] - self.last_state.joint_angles[joint]) / dt
                        velocities[joint] = vel
                        if joint in self.last_state.velocities:
                            accel = (vel - self.last_state.velocities[joint]) / dt
                            accelerations[joint] = accel
                    else:
                        velocities[joint] = 0.0
                        accelerations[joint] = 0.0
        else:
            # Initialize velocities and accelerations to 0
            for joint in self.joint_names:
                velocities[joint] = 0.0
                accelerations[joint] = 0.0

        # Simulate IMU data (simplified)
        roll = random.uniform(-0.1, 0.1)
        pitch = random.uniform(-0.1, 0.1)
        yaw = random.uniform(-0.1, 0.1)

        # Convert Euler angles to quaternion
        cy = math.cos(yaw * 0.5)
        sy = math.sin(yaw * 0.5)
        cp = math.cos(pitch * 0.5)
        sp = math.sin(pitch * 0.5)
        cr = math.cos(roll * 0.5)
        sr = math.sin(roll * 0.5)

        orientation = (
            cr * cp * cy + sr * sp * sy,  # w
            sr * cp * cy - cr * sp * sy,  # x
            cr * sp * cy + sr * cp * sy,  # y
            cr * cp * sy - sr * sp * cy   # z
        )

        # Simulate position (simplified - moving slowly)
        position = (0.0, 0.0, 0.8)  # Fixed height for now
        if self.last_state:
            dt = timestamp - self.last_state.timestamp
            position = (
                self.last_state.position[0] + random.uniform(-0.01, 0.01) * dt,
                self.last_state.position[1] + random.uniform(-0.01, 0.01) * dt,
                0.8 + random.uniform(-0.02, 0.02)  # Small height variations
            )

        # Simulate various sensor data
        sensor_data = {
            "imu": {
                "orientation": orientation,
                "angular_velocity": (random.uniform(-0.1, 0.1),
                                   random.uniform(-0.1, 0.1),
                                   random.uniform(-0.1, 0.1)),
                "linear_acceleration": (random.uniform(-1.0, 1.0),
                                      random.uniform(-1.0, 1.0),
                                      random.uniform(8.0, 11.0))
            },
            "force_torque": {
                "left_foot": (random.uniform(-10, 10),
                            random.uniform(-10, 10),
                            random.uniform(300, 700)),  # Z is upward force
                "right_foot": (random.uniform(-10, 10),
                             random.uniform(-10, 10),
                             random.uniform(300, 700))
            },
            "encoders": joint_angles.copy(),
            "battery_level": random.uniform(0.7, 1.0)
        }

        # Create and store the new state
        state = PhysicalState(
            timestamp=timestamp,
            position=position,
            orientation=orientation,
            joint_angles=joint_angles,
            velocities=velocities,
            accelerations=accelerations,
            sensor_data=sensor_data
        )
        self.last_state = state

        return state


class DigitalTwin:
    """
    Maintains a digital twin of the physical robot.
    """

    def __init__(self) -> None:
        self.physical_state: Optional[PhysicalState] = None
        self.virtual_state: Optional[VirtualState] = None
        self.environment_objects: List[Dict[str, Any]] = []
        self.uncertainty_model: Dict[str, float] = {}
        self.update_history: List[Tuple[float, str]] = []  # timestamp, update_type

    def update_from_physical(self, physical_state: PhysicalState) -> VirtualState:
        """
        Update the digital twin based on physical state readings.

        Args:
            physical_state: Current state from physical robot

        Returns:
            Updated virtual state
        """
        timestamp = physical_state.timestamp

        # Calculate uncertainty based on sensor noise and time since last update
        uncertainty = self._calculate_uncertainty(physical_state)

        # Predict forces based on current state
        predicted_forces = self._predict_forces(physical_state)

        # Update environment model
        environment_model = self._update_environment_model(physical_state)

        # Create new virtual state
        virtual_state = VirtualState(
            timestamp=timestamp,
            position=physical_state.position,
            orientation=physical_state.orientation,
            joint_angles=physical_state.joint_angles.copy(),
            predicted_forces=predicted_forces,
            environment_model=environment_model,
            uncertainty=uncertainty
        )

        # Store the states
        self.physical_state = physical_state
        self.virtual_state = virtual_state

        # Record the update
        self.update_history.append((timestamp, "physical_update"))

        return virtual_state

    def predict_future_state(self, time_ahead: float) -> VirtualState:
        """
        Predict the robot's state at a future time based on current state.

        Args:
            time_ahead: Time in seconds to predict ahead

        Returns:
            Predicted virtual state
        """
        if not self.virtual_state:
            raise ValueError("Digital twin not initialized with physical state")

        # Get current state
        current = self.virtual_state

        # Predict position based on current velocity (simplified)
        predicted_position = current.position
        if self.physical_state and self.physical_state.velocities:
            # Simplified prediction based on average joint velocity
            avg_vel = sum(self.physical_state.velocities.values()) / len(self.physical_state.velocities)
            # Convert joint velocity to approximate linear velocity
            linear_vel = avg_vel * 0.1  # Simplified conversion
            predicted_position = (
                current.position[0] + linear_vel * time_ahead,
                current.position[1] + linear_vel * time_ahead,
                current.position[2]  # Assume height stays relatively constant
            )

        # Predict joint angles based on current velocity
        predicted_joints = {}
        if self.physical_state:
            for joint, angle in current.joint_angles.items():
                if joint in self.physical_state.velocities:
                    vel = self.physical_state.velocities[joint]
                    predicted_joints[joint] = angle + vel * time_ahead
                else:
                    predicted_joints[joint] = angle

        # Increase uncertainty over time
        predicted_uncertainty = {k: v * (1 + time_ahead * 0.1) for k, v in current.uncertainty.items()}

        # Create predicted state
        predicted_state = VirtualState(
            timestamp=current.timestamp + time_ahead,
            position=predicted_position,
            orientation=current.orientation,  # Simplified: orientation doesn't change much in short time
            joint_angles=predicted_joints,
            predicted_forces=current.predicted_forces,  # Forces prediction stays the same
            environment_model=current.environment_model,
            uncertainty=predicted_uncertainty
        )

        # Record the prediction
        self.update_history.append((predicted_state.timestamp, "prediction"))

        return predicted_state

    def _calculate_uncertainty(self, physical_state: PhysicalState) -> Dict[str, float]:
        """Calculate uncertainty values for the digital twin."""
        uncertainty = {}

        # Position uncertainty (increases with movement)
        uncertainty["position"] = 0.01  # Base uncertainty

        # Orientation uncertainty
        uncertainty["orientation"] = 0.02  # Base uncertainty

        # Joint angle uncertainty (based on sensor precision)
        for joint in physical_state.joint_angles:
            # Typical encoder precision is around 0.1 degrees = ~0.0017 radians
            uncertainty[joint] = 0.002

        # Add uncertainty based on time since last update if applicable
        if self.virtual_state:
            time_diff = physical_state.timestamp - self.virtual_state.timestamp
            for key in uncertainty:
                uncertainty[key] += time_diff * 0.01  # Increase uncertainty over time

        return uncertainty

    def _predict_forces(self, physical_state: PhysicalState) -> Dict[str, float]:
        """Predict forces at various joints based on current state."""
        predicted_forces = {}

        # Simplified force prediction based on joint positions and velocities
        for joint, angle in physical_state.joint_angles.items():
            # Base force is related to position (gravity, etc.)
            base_force = abs(angle) * 10  # Simplified model

            # Add force related to velocity (damping)
            if joint in physical_state.velocities:
                vel_force = abs(physical_state.velocities[joint]) * 5  # Simplified damping
            else:
                vel_force = 0

            # Add force related to acceleration
            if joint in physical_state.accelerations:
                acc_force = abs(physical_state.accelerations[joint]) * 2  # Simplified inertia
            else:
                acc_force = 0

            predicted_forces[joint] = base_force + vel_force + acc_force

        return predicted_forces

    def _update_environment_model(self, physical_state: PhysicalState) -> Dict[str, Any]:
        """Update the model of the environment based on sensor data."""
        # In a real system, this would process camera, LIDAR, etc. data
        # For this example, we'll create a simplified model

        env_model = {
            "last_update": physical_state.timestamp,
            "objects_nearby": [],  # Would be populated from perception system
            "surface_type": "flat_ground",  # Would be detected from force/torque sensors
            "obstacles": [],  # Would be detected from range sensors
            "free_space": {
                "front": random.uniform(0.5, 3.0),  # Distance to obstacle in front
                "left": random.uniform(0.5, 3.0),
                "right": random.uniform(0.5, 3.0),
                "back": random.uniform(0.5, 3.0)
            }
        }

        return env_model

    def synchronize_with_physical(self) -> None:
        """Synchronize the digital twin with the physical robot."""
        if not self.physical_state:
            print("Warning: No physical state available to synchronize with")
            return

        # In a real system, this would send commands to correct discrepancies
        # between virtual and physical states
        print("Synchronizing digital twin with physical robot...")
        print(f"  Position: {self.physical_state.position}")
        print(f"  Joint angles: {len(self.physical_state.joint_angles)} joints")


def main() -> None:
    """
    Main function demonstrating digital twin functionality.
    """
    print("Starting conceptual digital twin for humanoid robot...")
    print("Demonstrating synchronization between physical and virtual states.\n")

    # Initialize components
    sensor_interface = SensorInterface()
    digital_twin = DigitalTwin()

    print("Reading initial sensor data from physical robot...")
    initial_state = sensor_interface.read_sensors()
    print(f"  Initial position: {initial_state.position}")
    print(f"  Number of joints: {len(initial_state.joint_angles)}")
    print()

    # Update digital twin with initial state
    print("Updating digital twin with initial physical state...")
    virtual_state = digital_twin.update_from_physical(initial_state)
    print(f"  Virtual position: {virtual_state.position}")
    print(f"  Uncertainty in position: ±{virtual_state.uncertainty['position']:.3f}m")
    print()

    # Simulate several updates
    print("Simulating continuous updates...")
    for i in range(5):
        print(f"Update cycle {i+1}:")

        # Read new physical state
        new_physical_state = sensor_interface.read_sensors()

        # Update digital twin
        new_virtual_state = digital_twin.update_from_physical(new_physical_state)

        # Show changes
        pos_change = math.sqrt(
            (new_virtual_state.position[0] - virtual_state.position[0])**2 +
            (new_virtual_state.position[1] - virtual_state.position[1])**2 +
            (new_virtual_state.position[2] - virtual_state.position[2])**2
        )
        print(f"  Position changed by: {pos_change:.3f}m")
        print(f"  Uncertainty: ±{new_virtual_state.uncertainty['position']:.3f}m")

        # Update reference for next iteration
        virtual_state = new_virtual_state
        time.sleep(0.1)  # Brief pause to simulate real-time operation

    print()

    # Demonstrate prediction capability
    print("Demonstrating prediction capability...")
    try:
        predicted_state = digital_twin.predict_future_state(time_ahead=1.0)
        print(f"  Predicted position in 1 second: {predicted_state.position}")
        print(f"  Predicted uncertainty: ±{predicted_state.uncertainty['position']:.3f}m")
        print(f"  Predicted joint angles: {len(predicted_state.joint_angles)} joints")
    except ValueError as e:
        print(f"  Could not predict: {e}")

    print()

    # Show environment model
    if digital_twin.virtual_state:
        env = digital_twin.virtual_state.environment_model
        print("Environment model:")
        print(f"  Free space - Front: {env['free_space']['front']:.1f}m, "
              f"Left: {env['free_space']['left']:.1f}m")
        print(f"  Surface type: {env['surface_type']}")
        print(f"  Last updated: {env['last_update']:.2f}")

    print()
    print(f"Total updates performed: {len([u for u in digital_twin.update_history if u[1] == 'physical_update'])}")
    print(f"Total predictions made: {len([u for u in digital_twin.update_history if u[1] == 'prediction'])}")


if __name__ == "__main__":
    main()