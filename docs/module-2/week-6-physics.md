---
title: Physics for Humanoid Robots
sidebar_position: 1
description: Contact, friction, and force concepts, how humanoids interact with ground, and physics scenario examples
---

# Physics for Humanoid Robots

## Contact, Friction, and Force Concepts

Understanding physics is fundamental to humanoid robotics, as these robots must interact with the physical world in ways that respect the laws of physics. Unlike digital systems, humanoid robots must manage contact forces, friction, and dynamic interactions.

### Contact Mechanics

#### Types of Contact
Humanoid robots experience various types of contact with their environment:

**Point Contact**
- Single point of interaction (e.g., tip of a finger)
- High pressure concentration
- Good for precise manipulation
- Challenging for stability

**Line Contact**
- Linear contact surface (e.g., edge of an object)
- Distributed pressure along a line
- Intermediate between point and surface contact
- Useful for specific manipulation tasks

**Surface Contact**
- Area of contact with a surface
- Distributed pressure across the contact area
- Provides stability for standing and walking
- Common for feet and palm interactions

#### Contact Modeling
Accurate contact models are essential for robot control:

**Rigid Contact Model**
- Assumes no deformation at contact points
- Simple but can cause numerical issues
- Good for initial approximations
- Fast computation

**Soft Contact Model**
- Allows for small deformations
- More realistic force behavior
- Better stability in simulations
- Higher computational cost

**Hybrid Models**
- Combine rigid and soft contact approaches
- Balance accuracy and efficiency
- Adapt based on contact conditions
- Most practical for real robots

### Friction Concepts

#### Static vs. Dynamic Friction
**Static Friction (μₛ)**
- Resistance to initial motion
- Generally higher than dynamic friction
- Prevents objects from sliding
- Critical for stable grasping

**Dynamic Friction (μₖ)**
- Resistance during motion
- Generally lower than static friction
- Affects sliding behavior
- Important for controlled movement

#### Friction Modeling
**Coulomb Friction Model**
- Simple model with constant coefficients
- Maximum friction force = μ × normal force
- Adequate for many applications
- Ignores velocity effects

**Advanced Models**
- Include velocity-dependent effects
- Account for temperature changes
- Consider surface condition variations
- More accurate but complex

### Force Concepts

#### Force Control
**Impedance Control**
- Control the relationship between force and position
- Allows for compliant behavior
- Essential for safe human interaction
- Variable stiffness and damping

**Admittance Control**
- Control motion in response to applied forces
- Opposite of impedance control
- Useful for following surfaces
- Good for uncertain environments

**Hybrid Force-Position Control**
- Control forces in some directions
- Control positions in others
- Useful for constrained motions
- Common in manipulation tasks

## How Humanoids Interact with Ground

### Ground Reaction Forces
When a humanoid robot stands or moves, it experiences ground reaction forces that are equal and opposite to the forces it applies to the ground.

#### Normal Forces
- Vertical forces supporting the robot's weight
- Must balance gravitational forces
- Critical for maintaining balance
- Vary with robot's posture and motion

#### Shear Forces
- Horizontal forces due to friction
- Enable walking and pushing
- Limited by friction coefficients
- Important for stability

### Contact Dynamics

#### Single Support Phase
- Robot stands on one foot
- Ground contact at single point/area
- Challenging for balance control
- Requires active stabilization

#### Double Support Phase
- Robot stands on both feet
- Two contact points with ground
- More stable than single support
- Common during walking transitions

#### Multi-Contact Scenarios
- Additional contacts (hands, knees, etc.)
- Increased stability potential
- Complex force distribution
- Useful for challenging tasks

### Ground Interaction Models

#### Point Mass Model
- Simplified representation of robot
- Treats robot as single point mass
- Good for basic balance analysis
- Ignores internal dynamics

#### Inverted Pendulum Model
- Models robot as inverted pendulum
- Captures essential balance dynamics
- Basis for many walking controllers
- Limited to small perturbations

#### Multi-Body Model
- Detailed representation of robot structure
- Accounts for joint dynamics
- Most accurate for control design
- Computationally intensive

## Example: Pseudo Physics Scenario

Consider a humanoid robot preparing to step over an obstacle:

```
Initial State:
- Robot standing in double support
- Center of mass (CoM) positioned between feet
- Ground reaction forces balanced

Planning Phase:
1. Calculate required CoM trajectory to clear obstacle
2. Determine foot placement for stable landing
3. Plan swing leg trajectory to avoid collision
4. Design balance control to maintain stability

Execution Phase:
1. Shift weight to stance leg (increase normal force)
2. Lift swing leg with controlled motion
3. Move CoM toward stance leg to maintain balance
4. Place swing leg beyond obstacle
5. Transfer weight to new stance configuration
6. Return to double support position

Physics Considerations:
- Maintain ZMP (Zero Moment Point) within support polygon
- Control ground reaction forces to prevent slipping
- Manage angular momentum during transfer
- Ensure sufficient friction for new foot placement
```

### Key Physics Calculations:

**Balance Maintenance:**
- ZMP = CoM position - (CoM_height / gravity) × CoM_acceleration
- Support polygon = convex hull of ground contact points
- Stability condition: ZMP ∈ support_polygon

**Friction Constraints:**
- Maximum horizontal force = friction_coefficient × normal_force
- Prevent slipping: |horizontal_force| ≤ max_friction
- Prevent tipping: normal_force_moment ≤ overturning_moment

**Energy Management:**
- Kinetic energy: KE = ½mv² + ½Iω²
- Potential energy: PE = mgh
- Energy efficiency: minimize unnecessary energy expenditure
- Smooth transitions: avoid energy discontinuities

## Practical Implementation Challenges

### Real-time Physics Simulation
- Fast computation of contact forces
- Stable numerical integration
- Accurate collision detection
- Efficient constraint solving

### Model Fidelity vs. Computation
- High-fidelity models for planning
- Simplified models for real-time control
- Adaptive model complexity
- Model validation and calibration

### Uncertainty Handling
- Unknown environment properties
- Model parameter uncertainty
- Sensor noise and delays
- Robust control design

Understanding physics principles is essential for creating humanoid robots that can interact safely and effectively with their environment. These concepts form the foundation for advanced locomotion, manipulation, and interaction capabilities that will be explored in subsequent modules.
