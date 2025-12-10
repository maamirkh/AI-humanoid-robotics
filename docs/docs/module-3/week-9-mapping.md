---
title: Week 9 - Mapping and Spatial Representation
description: SLAM concepts, map types (grid, topo), and pseudo mapping examples for humanoid robots
sidebar_position: 12
---

# Week 9 - Mapping and Spatial Representation

## SLAM: Simultaneous Localization and Mapping

SLAM (Simultaneous Localization and Mapping) represents one of the most fundamental challenges in robotics: building a map of an unknown environment while simultaneously using that map to navigate and determine the robot's location within it. For humanoid robots operating in human environments, SLAM is essential for autonomous navigation and task execution.

### The SLAM Problem

The SLAM problem can be stated mathematically as estimating the robot's trajectory and the map of landmarks simultaneously:

```
P(x_t, m | z_1:t, u_1:t)
```

Where:
- `x_t` is the robot's trajectory (poses over time)
- `m` is the map of landmarks
- `z_1:t` are the sensor observations
- `u_1:t` are the control inputs

### Why SLAM is Challenging

#### Uncertainty Accumulation
- Sensor measurements contain noise and uncertainty
- Odometry drift causes position uncertainty to grow over time
- Small errors accumulate into large positional errors

#### Data Association
- Determining which sensor observations correspond to which map features
- Distinguishing between new and previously observed features
- Handling dynamic objects that appear and disappear

#### Computational Complexity
- Large environments require extensive memory and processing
- Real-time requirements limit computational options
- Data association problems grow combinatorially

### SLAM Approaches

#### Filter-Based SLAM
- **Extended Kalman Filter (EKF) SLAM**: Linearizes the problem around current estimates
- **Particle Filter SLAM**: Uses sample-based representation of probability distributions
- **Information Filter SLAM**: Works with information matrices instead of covariance matrices

#### Graph-Based SLAM
- Represents the problem as an optimization over a graph of poses and constraints
- More robust to linearization errors
- Better suited for large-scale environments

#### Keyframe-Based SLAM
- Maintains key poses and connects them with constraints
- Reduces computational complexity
- Common in visual SLAM systems

### SLAM for Humanoid Robots

Humanoid robots face unique SLAM challenges:

#### Dynamic Body Pose
- Changing body configuration affects sensor positions
- Limb movements can create false motion estimates
- Need to account for kinematic changes

#### Human Environment Characteristics
- Environments designed for humans, not robots
- Cluttered spaces with many small objects
- Frequent changes due to human activity

#### Safety Requirements
- Mapping must be accurate for safe navigation
- Real-time performance critical for safety
- Failure modes must be safe

## Map Types for Physical AI

Different map types serve different purposes in humanoid robotics, each with advantages and limitations.

### Grid Maps

#### Occupancy Grid Maps
- Divide space into discrete cells representing occupancy probability
- Simple and intuitive representation
- Good for obstacle detection and avoidance

```
Map Structure:
2D Array: [x][y] = probability of occupancy
Resolution: typically 5-20 cm per cell
Size: variable based on environment
```

#### Advantages
- Simple to implement and understand
- Efficient for path planning algorithms
- Handle uncertainty through probabilistic representation
- Easy to update with new sensor data

#### Disadvantages
- Memory requirements grow quadratically with environment size
- Resolution trade-off: fine resolution = large memory
- Difficult to represent complex geometric features

#### Use Cases
- Indoor navigation and obstacle avoidance
- Path planning in structured environments
- Real-time mapping applications

### Topological Maps

#### Node-Link Representation
- Represent space as nodes (locations) connected by edges (paths)
- Focus on connectivity rather than geometric accuracy
- More abstract than metric maps

```
Map Structure:
Nodes: {location_id: (x, y, theta), attributes}
Edges: {connection_id: (node_a, node_b), path_properties}
```

#### Advantages
- Memory efficient for large environments
- Natural representation for route planning
- Stable over time despite environmental changes
- Good for high-level navigation

#### Disadvantages
- Lose geometric information
- Difficult for local navigation and obstacle avoidance
- Require predefined locations and connections
- Less intuitive for humans to understand

#### Use Cases
- Long-term navigation in large environments
- Route planning between known locations
- Semantic navigation (e.g., "go to kitchen")

### Feature Maps

#### Landmark-Based Representation
- Store distinctive features and their locations
- Efficient for environments with distinctive landmarks
- Good for localization and re-identification

```
Map Structure:
Landmarks: {id: (x, y, z, orientation), type, descriptor}
Relationships: {landmark_pairs: geometric_constraints}
```

#### Advantages
- Compact representation for landmark-rich environments
- Good for re-localization
- Invariant to environmental changes
- Suitable for loop closure detection

#### Disadvantages
- Dependent on distinctive landmarks
- Difficult in textureless or repetitive environments
- Complex data association problems
- May miss important navigational information

#### Use Cases
- Visual SLAM systems
- Environments with distinctive features
- Re-localization applications

### Semantic Maps

#### Object-Based Representation
- Combine spatial information with semantic labels
- Include functional and categorical information
- Enable context-aware behavior

```
Map Structure:
Objects: {id: (pose), category, attributes, relationships}
Spaces: {room_id: (boundary), function, accessibility}
```

#### Advantages
- Enable high-level task planning
- Support human-like spatial reasoning
- Provide functional information about spaces
- Facilitate human-robot interaction

#### Disadvantages
- Require complex perception systems
- More computationally demanding
- Dependent on accurate object recognition
- Difficult to maintain consistency

#### Use Cases
- Task-oriented navigation
- Human-aware robotics
- Collaborative robotics applications

## Pseudo Mapping Example

Let's examine a conceptual mapping process that demonstrates the principles of map building for humanoid robots:

### Scenario: Room Mapping

Consider a humanoid robot mapping an unknown rectangular room with furniture:

```
Initial State:
- Robot position: Unknown
- Map: Empty
- Environment: Unknown rectangular room with table, chairs, door

Goal:
- Build complete map of room
- Determine robot position within map
- Identify navigable areas
```

### Mapping Process

#### Step 1: Initial Exploration
```
function initialExploration():
    map = initializeEmptyMap()
    robotPose = initializePoseUncertainty()
    visitedAreas = set()

    while not coverageGoalReached(visitedAreas):
        frontier = identifyFrontiers(map, robotPose)
        nextPose = selectFrontier(frontier, robotPose)
        path = planPath(robotPose, nextPose, map)

        for waypoint in path:
            sensorData = acquireSensorData(waypoint)
            map = updateMapWithSensorData(map, sensorData, waypoint)
            robotPose = updatePoseEstimate(robotPose, sensorData, waypoint)
            visitedAreas.add(waypoint)

    return map, robotPose
```

#### Step 2: Map Refinement
```
function refineMap(initialMap, initialPose):
    refinedMap = copy(initialMap)
    refinedPose = copy(initialPose)

    # Loop closure detection
    loopClosures = detectLoopClosures(refinedMap, refinedPose)

    # Graph optimization
    optimizedMap, optimizedPose = optimizeGraph(
        refinedMap, refinedPose, loopClosures
    )

    # Cleanup and validation
    finalMap = validateAndCleanMap(optimizedMap)

    return finalMap
```

#### Step 3: Semantic Annotation
```
function annotateSemantically(map, robotPose):
    annotatedMap = copy(map)

    # Object recognition
    objects = recognizeObjectsInMap(map, robotPose)

    # Space classification
    spaces = classifySpaces(map, objects)

    # Accessibility analysis
    navigableAreas = analyzeAccessibility(map, robotPose)

    # Annotate map
    annotatedMap.objects = objects
    annotatedMap.spaces = spaces
    annotatedMap.accessibility = navigableAreas

    return annotatedMap
```

### Key Mapping Concepts Demonstrated

#### Incremental Map Building
- Map is built gradually as robot explores
- Each sensor observation updates the map
- Uncertainty is managed throughout the process

#### Multi-Modal Sensor Fusion
- Different sensors contribute to map building
- Visual, depth, and proprioceptive data integrated
- Consistency maintained across sensor modalities

#### Loop Closure
- Robot recognizes previously visited locations
- Map consistency improved through loop closure
- Drift corrected by connecting map segments

#### Map Optimization
- Graph-based optimization improves map accuracy
- Constraints from multiple observations combined
- Final map is globally consistent

### Mapping Challenges

#### Dynamic Objects
- Moving objects create mapping challenges
- Need to distinguish static from dynamic elements
- Temporary obstacles vs. permanent features

#### Sensor Limitations
- Limited field of view requires multiple observations
- Occlusions create mapping gaps
- Sensor noise affects map quality

#### Computational Constraints
- Real-time mapping requires efficient algorithms
- Memory limitations affect map resolution
- Processing power limits update frequency

#### Environmental Changes
- Environments change over time
- Need to detect and handle changes
- Maintain map relevance over time

## Mapping for Humanoid-Specific Applications

### Human-Aware Mapping
- Track human locations and movement patterns
- Identify human-used areas vs. robot areas
- Predict human movement for safe navigation

### Manipulation-Focused Mapping
- Detailed mapping of manipulation areas
- Object affordance mapping
- Tool and workspace mapping

### Social Space Mapping
- Map social interaction zones
- Identify appropriate robot positioning
- Respect human spatial preferences

## Integration with Digital Twins

Mapping results integrate with digital twin concepts from Module 1:

#### Real-Time Synchronization
- Physical observations update digital model
- Consistent representation across physical and digital
- Continuous refinement of world model

#### Simulation Integration
- Maps used for virtual environment creation
- Navigation planning in simulation
- Behavior testing in mapped environments

#### Multi-Robot Coordination
- Shared maps enable team coordination
- Consistent spatial understanding
- Distributed mapping tasks

## Looking Forward

Mapping provides the spatial foundation for all navigation and interaction tasks. The maps created through SLAM enable robots to operate autonomously in unknown environments, building persistent representations that support long-term operation.

In the next week, we'll explore navigation systems that use these maps to enable robots to move purposefully through their environment. The mapping concepts developed here provide the essential spatial understanding that navigation systems require.

The integration of mapping with perception, planning, and control creates the foundation for truly autonomous humanoid robots capable of operating in complex, human environments. Understanding these mapping principles is essential for developing robots that can build and maintain accurate models of their world.