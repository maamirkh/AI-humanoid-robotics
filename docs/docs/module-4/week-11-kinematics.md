---
title: Week 11 - Kinematics for Humanoid Robots
description: Forward/inverse kinematics (simple), motion intuition, and arm reach logic examples
sidebar_position: 15
---

# Week 11 - Kinematics for Humanoid Robots

## Forward and Inverse Kinematics: Simple Approaches

Kinematics is the study of motion without considering the forces that cause it. In humanoid robotics, kinematics is crucial for understanding how joint movements result in end-effector (hand, foot) positions and how desired end-effector positions can be achieved through appropriate joint movements.

### Forward Kinematics

Forward kinematics calculates the position and orientation of the end-effector given the joint angles. This is the "forward" direction from joint space to Cartesian space.

#### Mathematical Foundation

For a simple 2D planar manipulator with two joints:

```
Given:
- Joint angles: θ₁, θ₂
- Link lengths: L₁, L₂

End-effector position:
x = L₁ * cos(θ₁) + L₂ * cos(θ₁ + θ₂)
y = L₁ * sin(θ₁) + L₂ * sin(θ₁ + θ₂)
```

#### In Humanoid Robots

For humanoid robots, forward kinematics involves:

```
function forwardKinematics(joint_angles, robot_model):
    # Calculate transformation matrices for each joint
    for i in range(num_joints):
        T_i = calculateTransform(joint_angles[i], robot_model.links[i])
        T_total = T_total * T_i

    # Return final end-effector pose
    return extractPose(T_total)
```

#### Applications of Forward Kinematics

- **Pose Verification**: Confirming that commanded joint angles result in desired end-effector pose
- **Collision Detection**: Checking if robot limbs collide with environment during motion
- **Visualization**: Displaying robot configuration in simulation or user interfaces
- **Sensing Integration**: Understanding sensor positions based on joint configuration

### Inverse Kinematics

Inverse kinematics calculates the joint angles needed to achieve a desired end-effector position and orientation. This is the "inverse" direction from Cartesian space to joint space.

#### Mathematical Challenge

Inverse kinematics is more complex than forward kinematics because:
- Multiple solutions may exist (redundant robots)
- No solution may exist (out of reach)
- Analytical solutions are only available for simple structures
- Numerical methods are often required

#### Simple Inverse Kinematics Solution

For a 2D planar manipulator:

```
Given:
- Desired end-effector position: (x, y)
- Link lengths: L₁, L₂

Solution:
r² = x² + y²
cos(θ₂) = (L₁² + L₂² - r²) / (2 * L₁ * L₂)
sin(θ₂) = ±√(1 - cos²(θ₂))

θ₂ = atan2(sin(θ₂), cos(θ₂))
θ₁ = atan2(y, x) - atan2(L₂ * sin(θ₂), L₁ + L₂ * cos(θ₂))
```

#### Iterative Methods

For complex humanoid robots, iterative methods are often used:

```
function inverseKinematics(desired_pose, initial_joints, robot_model):
    current_joints = initial_joints
    current_pose = forwardKinematics(current_joints, robot_model)

    while distance(current_pose, desired_pose) > tolerance:
        # Calculate Jacobian matrix
        J = calculateJacobian(current_joints, robot_model)

        # Calculate pose error
        error = poseDifference(desired_pose, current_pose)

        # Update joint angles
        delta_joints = J_pseudo_inverse * error
        current_joints = current_joints + delta_joints

        # Recalculate current pose
        current_pose = forwardKinematics(current_joints, robot_model)

    return current_joints
```

### Kinematics in Humanoid Context

#### Humanoid-Specific Challenges

Humanoid robots present unique kinematic challenges:

- **Redundancy**: More joints than degrees of freedom needed
- **Multiple End-Effectors**: Hands, feet, head with different constraints
- **Balance Requirements**: Kinematic solutions must maintain stability
- **Collision Avoidance**: Motion must avoid self-collisions and environmental obstacles

#### Multi-Chain Kinematics

Humanoid robots have multiple kinematic chains:

```
Right Arm Chain: Torso → Shoulder → Elbow → Wrist → Hand
Left Arm Chain: Torso → Shoulder → Elbow → Wrist → Hand
Right Leg Chain: Torso → Hip → Knee → Ankle → Foot
Left Leg Chain: Torso → Hip → Knee → Ankle → Foot
Head Chain: Torso → Neck → Head
```

Each chain has its own forward and inverse kinematics, but they must be solved simultaneously to maintain whole-body coordination.

## Motion Intuition for Humanoid Systems

Motion intuition refers to the understanding of how movements feel and appear natural for humanoid systems, bridging the gap between mathematical kinematics and human-like behavior.

### Natural Movement Principles

#### Smooth Transitions
- Avoid sudden changes in velocity or acceleration
- Use smooth interpolation between waypoints
- Consider jerk (rate of acceleration change) minimization

```
function smoothTrajectory(start_pos, end_pos, duration, steps):
    trajectory = []
    for t in range(steps):
        # Use quintic polynomial for smooth motion
        s = t / steps
        blend = 6*s⁵ - 15*s⁴ + 10*s³  # Smooth blending function
        pos = start_pos + blend * (end_pos - start_pos)
        trajectory.append(pos)
    return trajectory
```

#### Biomechanical Constraints
- Respect joint limits and natural ranges of motion
- Consider muscle-like activation patterns
- Maintain balance during motion
- Follow natural movement synergies

#### Rhythmic Patterns
- Use natural frequencies for repetitive motions
- Coordinate bilateral movements (left/right arms/legs)
- Maintain phase relationships between joints

### Intuitive Motion Generation

#### Human-Inspired Motion
- Study human movement patterns
- Extract key features of natural motion
- Apply to robot control

#### Motion Primitives
- Predefined basic movements that can be combined
- Building blocks for complex behaviors
- Examples: reaching, grasping, stepping, gesturing

```
function executeReachPrimitive(target_position, hand_id):
    # Define via points for natural reaching motion
    shoulder_pos = getShoulderPosition(hand_id)
    via_point = calculateViaPoint(shoulder_pos, target_position)

    # Plan smooth path through via point
    path = [shoulder_pos, via_point, target_position]

    # Execute with appropriate velocity profile
    trajectory = planSmoothTrajectory(path, VELOCITY_PROFILE)

    return executeTrajectory(trajectory)
```

## Arm Reach Logic Examples

Arm reaching is a fundamental humanoid capability that demonstrates the integration of kinematics, motion planning, and control.

### Reach Planning Process

```
function planReach(target_object, robot_state):
    # 1. Object localization
    target_pose = locateObject(target_object, robot_state)

    # 2. Approach planning
    approach_pose = calculateApproachPose(target_pose, robot_state)

    # 3. Grasp planning
    grasp_pose = calculateGraspPose(target_pose, approach_pose)

    # 4. Kinematic solution
    joint_trajectory = solveInverseKinematics(grasp_pose, robot_state)

    # 5. Safety validation
    if validateTrajectory(joint_trajectory, robot_state):
        return joint_trajectory
    else:
        return alternativeReachStrategy(target_object, robot_state)
```

### Reach Execution with Obstacle Avoidance

```
function executeReachWithObstacleAvoidance(target, obstacles, robot_state):
    # Initial reach planning
    nominal_trajectory = planReach(target, robot_state)

    # Check for collisions
    if trajectoryHasCollisions(nominal_trajectory, obstacles):
        # Plan around obstacles
        collision_free_trajectory = planAroundObstacles(
            nominal_trajectory, obstacles, robot_state
        )

        if collision_free_trajectory is not None:
            return executeTrajectory(collision_free_trajectory)
        else:
            # Try alternative approach
            return executeAlternativeReach(target, obstacles, robot_state)
    else:
        return executeTrajectory(nominal_trajectory)
```

### Adaptive Reach Logic

```
function adaptiveReach(target, robot_state, context):
    # Determine reach type based on context
    if context == "delicate_object":
        reach_params = {
            "speed": SLOW_SPEED,
            "precision": HIGH_PRECISION,
            "approach_angle": OPTIMAL_ANGLE
        }
    elif context == "heavy_object":
        reach_params = {
            "speed": MODERATE_SPEED,
            "precision": MEDIUM_PRECISION,
            "approach_angle": STABLE_ANGLE
        }
    elif context == "social_interaction":
        reach_params = {
            "speed": SOCIAL_SPEED,
            "precision": SOCIAL_PRECISION,
            "approach_angle": NON_THREATENING_ANGLE
        }

    # Plan reach with parameters
    trajectory = planReachWithParameters(target, reach_params, robot_state)

    # Execute with real-time adjustments
    return executeWithAdjustments(trajectory, robot_state)
```

### Reach Failure Recovery

```
function robustReach(target, robot_state):
    try:
        trajectory = planReach(target, robot_state)
        result = executeTrajectory(trajectory)

        if result.success:
            return result
        else:
            return handleReachFailure(target, robot_state, result.error)
    except KinematicException as e:
        return alternativeReachStrategy(target, robot_state, e)
    except CollisionException as e:
        return avoidAndRetry(target, robot_state, e)
```

## Kinematic Constraints and Limitations

### Joint Limit Constraints
- Physical limits on joint angles
- Need to maintain solutions within safe ranges
- Can create unreachable workspace regions

### Singularity Handling
- Points where kinematic equations become unsolvable
- Loss of degrees of freedom at singular configurations
- Need to avoid or carefully handle singularities

### Workspace Analysis
- Understanding reachable and dexterous workspace
- Identifying optimal configurations for tasks
- Planning transitions between workspaces

## Integration with Other Systems

### Perception Integration
- Object pose estimation for reach planning
- Real-time tracking during reach execution
- Visual servoing for precision adjustments

### Control Integration
- Low-level joint control for trajectory following
- Compliance control for safe interaction
- Feedback integration for error correction

### Planning Integration
- High-level task planning with kinematic feasibility
- Multi-step manipulation planning
- Coordination with navigation and locomotion

## Looking Forward

Kinematics provides the mathematical foundation for all manipulation and movement in humanoid robots. The forward and inverse kinematics concepts enable robots to plan and execute precise movements, while motion intuition ensures these movements appear natural and appropriate.

In the next week, we'll explore decision-making systems that determine what movements and actions the robot should perform based on its goals, environment, and context. The kinematic capabilities developed here provide the means for executing the decisions made by higher-level systems.

The integration of kinematics with perception, planning, and control creates the foundation for sophisticated manipulation and interaction capabilities. Understanding these kinematic principles is essential for developing robots that can move with precision and purpose.