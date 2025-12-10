---
title: Week 3 - Motor Control and Locomotion
description: Basic locomotion theory, joint control concepts, stability basics, and balance logic examples
sidebar_position: 4
---

# Week 3 - Motor Control and Locomotion

## Basic Locomotion Theory

Locomotion represents one of the most fundamental challenges in humanoid robotics - how to move effectively through physical space while maintaining stability and achieving goals. Unlike wheeled or tracked vehicles, legged locomotion must deal with intermittent ground contact, dynamic balance, and complex multi-body dynamics.

### The Challenge of Legged Locomotion

Legged locomotion presents unique challenges compared to other forms of mobility:

- **Intermittent Support**: Unlike wheeled systems that maintain continuous contact with the ground, legged systems have phases where they are only partially or not at all supported
- **Dynamic Balance**: The system must maintain balance during motion, not just at rest
- **Multi-body Dynamics**: Multiple interconnected segments create complex dynamic interactions
- **Energy Efficiency**: Minimizing energy consumption while achieving locomotion goals
- **Terrain Adaptation**: Adapting to varying ground conditions and obstacles

### Locomotion Paradigms

Different approaches to locomotion have emerged based on the desired characteristics:

#### Static Stability
In static stability, the robot maintains balance at all times by keeping its center of mass within the support polygon formed by ground contact points. This approach is inherently stable but typically results in slow, energy-inefficient movement.

#### Dynamic Stability
Dynamic stability allows the system to be dynamically unstable in the short term but stable over time. This enables more natural, energy-efficient movement patterns that can be faster and more human-like, but requires sophisticated control algorithms.

#### Passive Dynamics
Passive dynamic locomotion exploits the natural dynamics of the mechanical system to achieve efficient movement. This approach mimics biological systems that use mechanical design to simplify control requirements.

### Walking Patterns and Gait Types

Different walking patterns serve different purposes:

#### Single Support vs. Double Support
- **Single Support**: Only one foot is in contact with the ground
- **Double Support**: Both feet are in contact with the ground
- Walking typically alternates between these phases

#### Common Gait Types
- **Walk**: Alternating single and double support, stable at all times
- **Run**: Both feet leave the ground simultaneously
- **Trot**: Diagonal pairs of legs move together
- **Bound**: Legs move in pairs (front and back together)

## Joint Control Concepts

Joint control forms the foundation of all physical movement in humanoid robots. Each joint must be precisely controlled to achieve desired movements while maintaining stability and safety.

### Joint Types and Degrees of Freedom

Humanoid robots typically have several types of joints:

#### Revolute Joints
- Allow rotation around a single axis
- Most common in humanoid robots
- Examples: elbow, knee, shoulder rotation

#### Prismatic Joints
- Allow linear motion along a single axis
- Less common but useful for specific applications
- Examples: telescoping limbs, linear actuators

#### Spherical Joints
- Allow rotation around multiple axes
- Provide greater flexibility but are mechanically complex
- Examples: hip, shoulder ball joints

### Control Approaches

Different control approaches are used depending on the requirements:

#### Position Control
- Commands specific joint angles
- Simple but may not account for external forces
- Good for pre-planned movements

#### Velocity Control
- Commands specific joint velocities
- Useful for smooth transitions between positions
- Good for dynamic movements

#### Force Control
- Commands specific forces or torques
- Essential for safe interaction with environment
- Critical for manipulation tasks

#### Impedance Control
- Controls the mechanical impedance (stiffness, damping) of joints
- Allows compliant interaction with environment
- Important for safe human-robot interaction

### Control Architecture

Joint control typically follows a hierarchical structure:

#### High-Level Planning
- Determines desired movements and trajectories
- Considers overall goals and constraints
- Generates reference signals for lower levels

#### Mid-Level Control
- Translates high-level goals to joint-level commands
- Handles coordination between multiple joints
- Implements feedback control loops

#### Low-Level Actuator Control
- Directly controls motor currents and positions
- Handles real-time safety and protection
- Provides precise position and force control

## Stability Basics

Stability is fundamental to all physical AI systems, particularly those that must maintain balance while moving or interacting with the environment.

### Static Stability

Static stability refers to stability when the system is not moving or moving very slowly:

#### Center of Mass (CoM)
- The point where the total mass of the system can be considered concentrated
- For static stability, the CoM must remain within the support polygon
- Critical for standing and slow movement

#### Support Polygon
- The area defined by ground contact points
- For bipedal systems, this changes as feet move
- Determines the stable region for the CoM

#### Stability Margin
- The distance between the CoM projection and the edge of the support polygon
- Larger margins provide greater stability but may limit mobility
- Trade-off between stability and agility

### Dynamic Stability

Dynamic stability considers stability during motion:

#### Zero Moment Point (ZMP)
- A point where the net moment of ground reaction forces is zero
- Critical for dynamic walking control
- Used in many humanoid walking algorithms

#### Capture Point
- The point where the robot must step to stop its motion
- Useful for balance recovery strategies
- Helps determine appropriate stepping locations

#### Linear Inverted Pendulum Model (LIPM)
- Simplified model of bipedal dynamics
- Assumes constant height and linearized dynamics
- Foundation for many walking controllers

### Balance Recovery Strategies

When stability is compromised, robots must employ recovery strategies:

#### Ankle Strategy
- Use ankle joints to adjust balance
- Effective for small perturbations
- Maintains foot position

#### Hip Strategy
- Use hip joints to adjust balance
- Effective for moderate perturbations
- Allows greater balance adjustment

#### Stepping Strategy
- Take a step to expand the support polygon
- Most effective for large perturbations
- Fundamental to walking and running

## Conceptual Example: Balance Logic

Let's examine a conceptual balance control system that demonstrates the principles of maintaining stability in a humanoid robot:

### Balance Control Architecture

```
Sensors → State Estimation → Balance Planning → Joint Control → Robot → Sensors
```

This feedback loop continuously monitors and adjusts the robot's balance:

1. **Sensors**: Measure current state (IMU, joint encoders, force sensors)
2. **State Estimation**: Estimate current balance state and stability
3. **Balance Planning**: Determine appropriate corrective actions
4. **Joint Control**: Execute balance commands on joints
5. **Robot**: Physical system responds to commands
6. **Sensors**: New measurements begin next iteration

### Balance Control Algorithm Example

```
function balanceControl(currentState, desiredState):
    # Calculate stability metrics
    comPosition = calculateCoM(currentState)
    supportPolygon = calculateSupportPolygon(currentState)
    stabilityMargin = calculateStabilityMargin(comPosition, supportPolygon)

    # Determine control strategy based on stability
    if stabilityMargin > SAFE_THRESHOLD:
        # System is stable, make small adjustments
        desiredCoM = desiredState.comPosition
        controlMode = "PREVENTIVE"
    elif stabilityMargin > CRITICAL_THRESHOLD:
        # System needs active stabilization
        desiredCoM = adjustForStability(comPosition, supportPolygon)
        controlMode = "ACTIVE"
    else:
        # System is unstable, emergency response needed
        desiredCoM = emergencyStabilization(comPosition, supportPolygon)
        controlMode = "RECOVERY"

    # Generate joint commands to achieve desired CoM
    jointCommands = inverseKinematics(desiredCoM, currentState)

    # Apply impedance control for safe interaction
    compliantCommands = applyImpedanceControl(jointCommands, currentState)

    return compliantCommands
```

### Key Balance Control Concepts

This conceptual system demonstrates several important principles:

#### Multi-level Control
The system operates at multiple levels simultaneously - high-level stability planning, mid-level trajectory generation, and low-level actuator control.

#### Predictive Control
The system anticipates stability issues before they occur, enabling preventive rather than reactive control.

#### Adaptive Stiffness
Impedance control allows the system to adjust its mechanical compliance based on the situation, providing both stability and safety.

#### Hierarchical Priorities
Different control objectives (stability, efficiency, safety) are prioritized hierarchically to resolve conflicts.

### Stability Control Strategies

The system might employ different strategies depending on the situation:

#### Standing Balance
- Minimal movement to maintain stability
- Focus on CoM positioning within support polygon
- Low energy consumption

#### Walking Balance
- Dynamic balance using ZMP or capture point control
- Predictive foot placement
- Energy-efficient gait patterns

#### Perturbation Recovery
- Rapid response to unexpected disturbances
- Multiple recovery strategies (ankle, hip, stepping)
- Safety-focused control

## Control Challenges and Considerations

Motor control in humanoid robots faces several significant challenges:

### Real-time Requirements
Balance and locomotion control must operate in real-time with strict timing constraints. Delays in control can lead to instability and falls.

### Model Uncertainty
Perfect models of robot dynamics are impossible to achieve. Control systems must operate robustly despite model inaccuracies.

### Sensor Noise
Sensors provide noisy measurements that must be filtered and interpreted correctly for stable control.

### Actuator Limitations
Physical actuators have limited torque, speed, and precision that constrain control capabilities.

### Environmental Interaction
The robot must safely interact with an unpredictable environment while maintaining stability.

## Looking Forward

Motor control and locomotion form the foundation of physical mobility. The principles covered in this week - stability, balance, and joint control - enable robots to move through the physical world. In the coming weeks, we'll explore how robots use perception to understand their environment and make intelligent decisions about movement and interaction.

The integration of sensing, control, and locomotion creates the basis for more complex behaviors like manipulation, navigation, and human interaction. Understanding these fundamental control principles is essential for developing more sophisticated physical AI systems.