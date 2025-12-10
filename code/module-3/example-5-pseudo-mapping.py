#!/usr/bin/env python3
"""
Conceptual Pseudo Mapping Example

This module demonstrates conceptual pseudo mapping for humanoid robots,
showing how to create simplified representations of the environment without full SLAM.
"""

from typing import Dict, List, Tuple, Optional, Any
import math
import random
import time
from enum import Enum


class RoomType(Enum):
    """Types of rooms that can be identified."""
    UNKNOWN = "unknown"
    CORRIDOR = "corridor"
    ROOM = "room"
    DOORWAY = "doorway"
    OPEN_SPACE = "open_space"


class PseudoMapCell:
    """
    Represents a cell in the pseudo map with semantic information.
    """
    def __init__(self, x: int, y: int, cell_type: str = "unknown") -> None:
        self.x = x
        self.y = y
        self.type = cell_type  # "free", "occupied", "door", "corridor", etc.
        self.confidence = 0.0  # Confidence in the classification
        self.visit_count = 0
        self.last_visited = time.time()
        self.semantic_label = "unexplored"  # Semantic meaning of the space

    def update_classification(self, new_type: str, confidence: float) -> None:
        """Update the cell classification with new confidence."""
        # Update with weighted average
        old_weight = self.confidence
        new_weight = confidence
        total_weight = old_weight + new_weight

        if total_weight > 0:
            # If confidence is high enough, update the type
            if confidence > 0.7 or (confidence > self.confidence and self.visit_count == 0):
                self.type = new_type
                self.confidence = confidence

        self.visit_count += 1
        self.last_visited = time.time()


class SemanticRegion:
    """
    Represents a region with semantic meaning (e.g., kitchen, bedroom, hallway).
    """
    def __init__(self, id: str, center: Tuple[float, float], region_type: RoomType) -> None:
        self.id = id
        self.center = center
        self.type = region_type
        self.cells: List[Tuple[int, int]] = []
        self.neighbors: List[str] = []
        self.size = 0
        self.confidence = 0.5  # Initial confidence in region classification
        self.last_updated = time.time()
        self.name = f"{region_type.value}_{id}"

    def add_cell(self, x: int, y: int) -> None:
        """Add a cell to this region."""
        if (x, y) not in self.cells:
            self.cells.append((x, y))
            self.size += 1

    def add_neighbor(self, neighbor_id: str) -> None:
        """Add a neighboring region."""
        if neighbor_id not in self.neighbors:
            self.neighbors.append(neighbor_id)

    def update_center(self) -> None:
        """Update the center based on contained cells."""
        if self.cells:
            avg_x = sum(cell[0] for cell in self.cells) / len(self.cells)
            avg_y = sum(cell[1] for cell in self.cells) / len(self.cells)
            self.center = (avg_x, avg_y)


class PseudoMapper:
    """
    Creates simplified pseudo maps based on sensor observations and movement patterns.
    """
    def __init__(self, width: int = 50, height: int = 50) -> None:
        self.width = width
        self.height = height
        self.resolution = 0.5  # meters per cell
        self.grid: List[List[PseudoMapCell]] = [
            [PseudoMapCell(x, y) for x in range(width)] for y in range(height)
        ]
        self.regions: Dict[str, SemanticRegion] = {}
        self.region_counter = 0
        self.robot_position = (width // 2, height // 2)  # Start in the middle
        self.previous_position = (width // 2, height // 2)
        self.motion_history: List[Tuple[int, int]] = [self.robot_position]
        self.sensor_history: List[Dict[str, Any]] = []
        self.current_region_id: Optional[str] = None
        self.last_region_change = time.time()

    def world_to_grid(self, x: float, y: float) -> Tuple[int, int]:
        """Convert world coordinates to grid coordinates."""
        grid_x = int(x / self.resolution + self.width // 2)
        grid_y = int(y / self.resolution + self.height // 2)
        return max(0, min(self.width - 1, grid_x)), max(0, min(self.height - 1, grid_y))

    def grid_to_world(self, grid_x: int, grid_y: int) -> Tuple[float, float]:
        """Convert grid coordinates to world coordinates."""
        world_x = (grid_x - self.width // 2) * self.resolution
        world_y = (grid_y - self.height // 2) * self.resolution
        return world_x, world_y

    def update_position(self, new_position: Tuple[float, float]) -> None:
        """Update robot position and trigger mapping updates."""
        old_grid_pos = self.robot_position
        self.previous_position = self.robot_position
        self.robot_position = self.world_to_grid(new_position[0], new_position[1])

        # Add to motion history
        self.motion_history.append(self.robot_position)

        # Check if we've moved to a new area that might be a different region
        self._check_region_boundary(old_grid_pos, self.robot_position)

    def _check_region_boundary(self, old_pos: Tuple[int, int], new_pos: Tuple[int, int]) -> None:
        """Check if movement crosses a region boundary."""
        # Calculate distance moved
        distance = math.sqrt((new_pos[0] - old_pos[0])**2 + (new_pos[1] - old_pos[1])**2)

        # If moved significantly and enough time has passed, consider it a new region
        if distance > 5 and (time.time() - self.last_region_change) > 10:  # 10 seconds
            # Check if we're in a corridor-like pattern (long, narrow movement)
            if self._is_corridor_pattern():
                self._create_region(RoomType.CORRIDOR)
            else:
                self._create_region(RoomType.ROOM)

            self.last_region_change = time.time()

    def _is_corridor_pattern(self) -> bool:
        """Check if recent motion suggests corridor-like movement."""
        if len(self.motion_history) < 10:
            return False

        # Look at the last 10 positions
        recent_positions = self.motion_history[-10:]
        if len(recent_positions) < 2:
            return False

        # Calculate the principal direction of movement
        dx_total = sum(pos[0] - recent_positions[i-1][0]
                      for i, pos in enumerate(recent_positions) if i > 0)
        dy_total = sum(pos[1] - recent_positions[i-1][1]
                      for i, pos in enumerate(recent_positions) if i > 0)

        # Calculate variance in perpendicular direction
        if dx_total**2 + dy_total**2 < 1:  # Not enough movement to determine direction
            return False

        # Calculate perpendicular distances to the main movement line
        distances = []
        for pos in recent_positions:
            # Project position onto movement line to find perpendicular distance
            if dx_total**2 + dy_total**2 > 0:
                t = ((pos[0] - recent_positions[0][0]) * dx_total +
                     (pos[1] - recent_positions[0][1]) * dy_total) / (dx_total**2 + dy_total**2)
                proj_x = recent_positions[0][0] + t * dx_total
                proj_y = recent_positions[0][1] + t * dy_total
                dist = math.sqrt((pos[0] - proj_x)**2 + (pos[1] - proj_y)**2)
                distances.append(dist)

        # If perpendicular distances are small, it's likely a corridor
        avg_perp_dist = sum(distances) / len(distances) if distances else 0
        return avg_perp_dist < 2  # If average perpendicular distance < 2 cells, likely corridor

    def _create_region(self, region_type: RoomType) -> str:
        """Create a new semantic region."""
        region_id = f"region_{self.region_counter}"
        self.region_counter += 1

        new_region = SemanticRegion(region_id, self.grid_to_world(*self.robot_position), region_type)
        self.regions[region_id] = new_region
        self.current_region_id = region_id

        # Add current cell to the region
        self._add_cell_to_region(region_id, self.robot_position[0], self.robot_position[1])

        return region_id

    def _add_cell_to_region(self, region_id: str, x: int, y: int) -> None:
        """Add a cell to a region."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y][x].semantic_label = self.regions[region_id].type.value
            self.regions[region_id].add_cell(x, y)
            self.regions[region_id].update_center()

    def update_sensor_data(self, sensor_readings: List[Dict[str, float]]) -> None:
        """
        Update map based on sensor readings (e.g., distances to obstacles).

        Args:
            sensor_readings: List of sensor readings with 'range' and 'angle' keys
        """
        self.sensor_history.append({
            "timestamp": time.time(),
            "position": self.robot_position,
            "readings": sensor_readings.copy()
        })

        # Update grid based on sensor readings
        robot_x, robot_y = self.robot_position
        for reading in sensor_readings:
            angle = reading["angle"]
            range_val = reading["range"]

            # Calculate the endpoint of the sensor reading
            end_x = robot_x + int(range_val / self.resolution * math.cos(angle))
            end_y = robot_y + int(range_val / self.resolution * math.sin(angle))

            # Check if endpoint is within grid bounds
            if 0 <= end_x < self.width and 0 <= end_y < self.height:
                # Mark the endpoint as occupied (likely an obstacle)
                self.grid[end_y][end_x].update_classification("occupied", 0.9)

                # Mark path as free (up to the obstacle)
                self._mark_path_free(robot_x, robot_y, end_x, end_y)

    def _mark_path_free(self, start_x: int, start_y: int, end_x: int, end_y: int) -> None:
        """Mark the path between start and end as free space."""
        # Bresenham's line algorithm to mark free space
        dx = abs(end_x - start_x)
        dy = abs(end_y - start_y)
        x_step = 1 if end_x > start_x else -1
        y_step = 1 if end_y > start_y else -1

        x, y = start_x, start_y
        error = dx - dy

        while x != end_x or y != end_y:
            if 0 <= x < self.width and 0 <= y < self.height:
                # Only mark as free if not already occupied with high confidence
                if self.grid[y][x].confidence < 0.7 or self.grid[y][x].type != "occupied":
                    self.grid[y][x].update_classification("free", 0.6)

            error2 = 2 * error
            if error2 > -dy:
                error -= dy
                x += x_step
            if error2 < dx:
                error += dx
                y += y_step

    def detect_doorways(self) -> List[Tuple[int, int]]:
        """Detect potential doorways based on map structure."""
        doorways = []

        # Look for narrow passages between larger open areas
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                cell = self.grid[y][x]
                if cell.type == "free":  # Only check free cells
                    # Count occupied neighbors
                    occupied_neighbors = 0
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            if dx == 0 and dy == 0:
                                continue
                            nx, ny = x + dx, y + dy
                            if (0 <= nx < self.width and 0 <= ny < self.height and
                                self.grid[ny][nx].type == "occupied"):
                                occupied_neighbors += 1

                    # If cell has many occupied neighbors, it might be a doorway
                    if occupied_neighbors >= 6:  # Most surrounding cells are occupied
                        doorways.append((x, y))

        return doorways

    def classify_room_types(self) -> Dict[str, RoomType]:
        """Classify regions based on their structure and connectivity."""
        classifications = {}

        for region_id, region in self.regions.items():
            # Calculate region properties
            size = region.size
            connectivity = len(region.neighbors)

            # Classify based on size and connectivity
            if size < 10:  # Small region
                if connectivity > 2:  # Highly connected
                    classifications[region_id] = RoomType.DOORWAY
                else:
                    classifications[region_id] = RoomType.UNKNOWN
            elif size > 50:  # Large region
                if connectivity <= 2:  # Less connected
                    classifications[region_id] = RoomType.ROOM
                else:
                    classifications[region_id] = RoomType.OPEN_SPACE
            else:  # Medium region
                if connectivity > 3:  # Highly connected
                    classifications[region_id] = RoomType.CORRIDOR
                else:
                    classifications[region_id] = RoomType.ROOM

            # Update region with classification
            region.type = classifications[region_id]
            region.name = f"{classifications[region_id].value}_{region_id}"

        return classifications

    def get_pseudo_map(self) -> Dict[str, Any]:
        """Get the current pseudo map as a dictionary."""
        # Count different cell types
        cell_counts = {"free": 0, "occupied": 0, "unknown": 0}
        for row in self.grid:
            for cell in row:
                if cell.type in cell_counts:
                    cell_counts[cell.type] += 1
                else:
                    cell_counts["unknown"] += 1

        return {
            "grid_size": (self.width, self.height),
            "resolution": self.resolution,
            "cell_counts": cell_counts,
            "regions": {
                rid: {
                    "type": region.type.value,
                    "center": region.center,
                    "size": region.size,
                    "name": region.name,
                    "neighbors": region.neighbors
                } for rid, region in self.regions.items()
            },
            "doorways": self.detect_doorways(),
            "robot_position": self.grid_to_world(*self.robot_position),
            "motion_path_length": len(self.motion_history),
            "total_regions": len(self.regions)
        }

    def get_navigation_recommendation(self, target: Tuple[float, float]) -> Dict[str, Any]:
        """
        Provide navigation recommendations based on the pseudo map.

        Args:
            target: Target position (x, y) in world coordinates

        Returns:
            Navigation recommendations
        """
        target_grid = self.world_to_grid(target[0], target[1])

        # Calculate straight-line distance
        current_world = self.grid_to_world(*self.robot_position)
        straight_distance = math.sqrt((target[0] - current_world[0])**2 + (target[1] - current_world[1])**2)

        # Find nearby doorways
        doorways = self.detect_doorways()
        nearby_doorways = []
        for dx, dy in doorways:
            distance = math.sqrt((dx - self.robot_position[0])**2 + (dy - self.robot_position[1])**2)
            if distance < 10:  # Within 10 cells
                nearby_doorways.append((dx, dy, distance))

        # Find regions that might contain the target
        potential_path_regions = []
        target_region = None
        for region_id, region in self.regions.items():
            region_distance = math.sqrt((region.center[0] - target[0])**2 + (region.center[1] - target[1])**2)
            if region_distance < 3:  # Within 3 meters of target
                target_region = region_id
            if region_distance < 10:  # Within 10 meters
                potential_path_regions.append((region_id, region_distance))

        return {
            "straight_distance": straight_distance,
            "nearby_doorways": len(nearby_doorways),
            "target_region": target_region,
            "accessible_regions": len(potential_path_regions),
            "navigation_hint": "use_doorways" if nearby_doorways else "open_space_navigation"
        }


class PseudoMappingSimulator:
    """
    Simulates pseudo mapping in a controlled environment.
    """
    def __init__(self) -> None:
        self.pseudo_mapper = PseudoMapper()
        self.simulation_time = 0.0
        self.simulation_steps = 0
        self.ground_truth_rooms = [
            {"name": "living_room", "center": (0, 0), "size": (8, 6), "type": RoomType.ROOM},
            {"name": "kitchen", "center": (5, 2), "size": (4, 4), "type": RoomType.ROOM},
            {"name": "bedroom", "center": (-4, 3), "size": (5, 5), "type": RoomType.ROOM},
            {"name": "hallway", "center": (0, 4), "size": (10, 2), "type": RoomType.CORRIDOR}
        ]

    def simulate_robot_movement(self) -> Tuple[float, float]:
        """
        Simulate robot movement based on the environment.

        Returns:
            New robot position (x, y)
        """
        # Simple exploration pattern: move in a spiral
        step = self.simulation_steps
        angle = step * 0.3
        radius = min(8.0, step * 0.1)  # Expand outward up to 8m radius

        new_x = radius * math.cos(angle)
        new_y = radius * math.sin(angle)

        # Add some randomness to simulate real-world imperfections
        new_x += random.uniform(-0.2, 0.2)
        new_y += random.uniform(-0.2, 0.2)

        return (new_x, new_y)

    def simulate_sensor_readings(self, position: Tuple[float, float]) -> List[Dict[str, float]]:
        """
        Simulate sensor readings based on the environment.

        Args:
            position: Robot position (x, y)

        Returns:
            List of sensor readings
        """
        readings = []

        # Simulate 16 sensor readings around the robot
        for i in range(16):
            angle = i * (2 * math.pi / 16)

            # Calculate distance to the nearest "wall" in this direction
            # For simulation, we'll create artificial obstacles
            min_distance = 5.0  # Default max range

            # Simulate some walls based on the ground truth rooms
            for room in self.ground_truth_rooms:
                center_x, center_y = room["center"]
                half_width = room["size"][0] / 2
                half_height = room["size"][1] / 2

                # Check for intersection with room boundaries
                # This is a simplified check
                dx = abs(position[0] - center_x)
                dy = abs(position[1] - center_y)

                if dx < half_width + 1 and dy < half_height + 1:
                    # Calculate distance to closest wall in this direction
                    dist_to_right = (center_x + half_width) - position[0]
                    dist_to_left = position[0] - (center_x - half_width)
                    dist_to_top = (center_y + half_height) - position[1]
                    dist_to_bottom = position[1] - (center_y - half_height)

                    # Find distance in the sensor direction
                    if math.cos(angle) > 0:
                        wall_dist = dist_to_right / math.cos(angle) if math.cos(angle) > 0.1 else float('inf')
                    else:
                        wall_dist = dist_to_left / abs(math.cos(angle)) if math.cos(angle) < -0.1 else float('inf')

                    if math.sin(angle) > 0:
                        wall_dist = min(wall_dist, dist_to_top / math.sin(angle)) if math.sin(angle) > 0.1 else wall_dist
                    else:
                        wall_dist = min(wall_dist, dist_to_bottom / abs(math.sin(angle))) if math.sin(angle) < -0.1 else wall_dist

                    if wall_dist > 0 and wall_dist < min_distance:
                        min_distance = wall_dist

            # Add some noise to the sensor reading
            distance = max(0.3, min_distance + random.uniform(-0.1, 0.1))

            readings.append({
                "angle": angle,
                "range": min(distance, 5.0)  # Cap at 5m range
            })

        return readings

    def run_simulation_step(self) -> Dict[str, Any]:
        """Run one step of the simulation."""
        # Move robot
        new_position = self.simulate_robot_movement()
        self.pseudo_mapper.update_position(new_position)

        # Get sensor readings
        sensor_readings = self.simulate_sensor_readings(new_position)

        # Update map with sensor data
        self.pseudo_mapper.update_sensor_data(sensor_readings)

        # Update simulation state
        self.simulation_time += 0.1  # 100ms per step
        self.simulation_steps += 1

        return {
            "step": self.simulation_steps,
            "position": new_position,
            "sensor_readings_count": len(sensor_readings),
            "regions_count": len(self.pseudo_mapper.regions)
        }

    def get_simulation_summary(self) -> Dict[str, Any]:
        """Get a summary of the simulation."""
        pseudo_map = self.pseudo_mapper.get_pseudo_map()

        return {
            "simulation_time": self.simulation_time,
            "simulation_steps": self.simulation_steps,
            "pseudo_map": pseudo_map,
            "ground_truth_rooms": len(self.ground_truth_rooms),
            "mapping_accuracy_estimate": len(pseudo_map["regions"]) / len(self.ground_truth_rooms) if self.ground_truth_rooms else 0
        }


def main() -> None:
    """
    Main function demonstrating pseudo mapping.
    """
    print("Starting pseudo mapping demonstration for humanoid robot...")
    print("Showing how to create simplified environment representations.\n")

    # Initialize the pseudo mapping simulator
    simulator = PseudoMappingSimulator()

    print("Ground truth environment:")
    for room in simulator.ground_truth_rooms:
        print(f"  {room['name']} ({room['type'].value}): center={room['center']}, size={room['size']}")
    print()

    print("Running pseudo mapping simulation...")

    # Run simulation for 50 steps
    for step in range(50):
        result = simulator.run_simulation_step()

        if step % 10 == 0:  # Print every 10 steps
            print(f"  Step {result['step']:2d}: Pos={result['position']}, "
                  f"Sensors={result['sensor_readings_count']}, "
                  f"Regions={result['regions_count']}")

    print(f"\nSimulation completed after {simulator.simulation_time:.1f} seconds!")

    # Get final summary
    summary = simulator.get_simulation_summary()
    pseudo_map = summary["pseudo_map"]

    print(f"\nFinal pseudo map statistics:")
    print(f"  Grid size: {pseudo_map['grid_size'][0]} x {pseudo_map['grid_size'][1]} cells")
    print(f"  Resolution: {pseudo_map['resolution']}m per cell")
    print(f"  Total regions identified: {pseudo_map['total_regions']}")
    print(f"  Doorways detected: {len(pseudo_map['doorways'])}")
    print(f"  Motion path length: {pseudo_map['motion_path_length']} steps")

    # Show cell type distribution
    print(f"  Cell type distribution:")
    for cell_type, count in pseudo_map['cell_counts'].items():
        percentage = (count / (pseudo_map['grid_size'][0] * pseudo_map['grid_size'][1])) * 100
        print(f"    {cell_type}: {count} cells ({percentage:.1f}%)")

    # Show regions
    print(f"\nIdentified regions:")
    for region_id, region_info in list(pseudo_map['regions'].items())[:5]:  # Show first 5
        print(f"  {region_info['name']}: type={region_info['type']}, "
              f"size={region_info['size']} cells, "
              f"center=({region_info['center'][0]:.1f}, {region_info['center'][1]:.1f})")

    # Demonstrate navigation recommendation
    print(f"\nNavigation demonstration:")
    target_pos = (3.0, 1.0)  # Target near the kitchen
    nav_recommendation = simulator.pseudo_mapper.get_navigation_recommendation(target_pos)
    print(f"  From {pseudo_map['robot_position']} to {target_pos}:")
    print(f"    Straight-line distance: {nav_recommendation['straight_distance']:.2f}m")
    print(f"    Nearby doorways: {nav_recommendation['nearby_doorways']}")
    print(f"    Target region: {nav_recommendation['target_region']}")
    print(f"    Accessible regions: {nav_recommendation['accessible_regions']}")
    print(f"    Navigation hint: {nav_recommendation['navigation_hint']}")

    # Show doorways
    doorways = pseudo_map['doorways']
    print(f"\nDetected doorways ({len(doorways)} total):")
    for i, (dx, dy) in enumerate(doorways[:5]):  # Show first 5
        world_pos = simulator.pseudo_mapper.grid_to_world(dx, dy)
        print(f"  Doorway {i+1}: grid=({dx},{dy}), world=({world_pos[0]:.1f}, {world_pos[1]:.1f})")

    # Evaluate mapping quality
    print(f"\nMapping evaluation:")
    print(f"  Ground truth rooms: {summary['ground_truth_rooms']}")
    print(f"  Pseudo map regions: {pseudo_map['total_regions']}")
    print(f"  Region identification accuracy: {summary['mapping_accuracy_estimate']:.2f} (approx)")

    # Show motion history pattern
    motion_length = pseudo_map['motion_path_length']
    if motion_length > 1:
        start_pos = simulator.pseudo_mapper.grid_to_world(*simulator.pseudo_mapper.motion_history[0])
        end_pos = simulator.pseudo_mapper.grid_to_world(*simulator.pseudo_mapper.motion_history[-1])
        direct_distance = math.sqrt((end_pos[0] - start_pos[0])**2 + (end_pos[1] - start_pos[1])**2)
        print(f"  Exploration path: {motion_length} positions recorded")
        print(f"  Start position: ({start_pos[0]:.1f}, {start_pos[1]:.1f})")
        print(f"  End position: ({end_pos[0]:.1f}, {end_pos[1]:.1f})")
        print(f"  Direct distance: {direct_distance:.2f}m")

    print(f"\nPseudo mapping demonstration completed.")
    print("This shows how humanoid robots can create simplified environment representations")
    print("using sensor data and movement patterns, without requiring full SLAM.")


if __name__ == "__main__":
    main()