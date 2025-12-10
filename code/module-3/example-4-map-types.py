#!/usr/bin/env python3
"""
Conceptual Map Types Example

This module demonstrates different types of maps used in humanoid robotics,
including occupancy grids, topological maps, and feature maps.
"""

from typing import Dict, List, Tuple, Optional, Any, Union
import math
import random
import time
from enum import Enum


class MapType(Enum):
    """Types of maps used in robotics."""
    OCCUPANCY_GRID = "occupancy_grid"
    TOPOLOGICAL = "topological"
    FEATURE_BASED = "feature_based"
    TOPOGRAPHIC = "topographic"


class OccupancyCell:
    """
    Represents a cell in an occupancy grid map.
    """
    def __init__(self, occupancy: float = -1.0) -> None:
        """
        Initialize occupancy cell.

        Args:
            occupancy: -1 (unknown), 0 (free), 1 (occupied), or probability between 0-1
        """
        self.occupancy = occupancy  # -1: unknown, 0-1: probability of occupancy
        self.last_updated = time.time()
        self.visited_count = 0

    def update_occupancy(self, new_occupancy: float) -> None:
        """Update the occupancy probability using a simple filter."""
        # Simple temporal filtering
        if self.occupancy == -1:  # First measurement
            self.occupancy = new_occupancy
        else:
            # Exponential moving average
            alpha = 0.3  # Learning rate
            self.occupancy = alpha * new_occupancy + (1 - alpha) * self.occupancy

        self.last_updated = time.time()
        self.visited_count += 1


class OccupancyGridMap:
    """
    Represents an occupancy grid map - a 2D grid where each cell has an occupancy probability.
    """
    def __init__(self, width: int, height: int, resolution: float = 0.1) -> None:
        """
        Initialize occupancy grid map.

        Args:
            width: Map width in cells
            height: Map height in cells
            resolution: Size of each cell in meters
        """
        self.width = width
        self.height = height
        self.resolution = resolution  # meters per cell
        self.origin_x = 0.0
        self.origin_y = 0.0

        # Initialize grid with unknown occupancy
        self.grid: List[List[OccupancyCell]] = [
            [OccupancyCell() for _ in range(width)] for _ in range(height)
        ]

    def world_to_grid(self, x: float, y: float) -> Tuple[int, int]:
        """Convert world coordinates to grid coordinates."""
        grid_x = int((x - self.origin_x) / self.resolution)
        grid_y = int((y - self.origin_y) / self.resolution)
        return grid_x, grid_y

    def grid_to_world(self, grid_x: int, grid_y: int) -> Tuple[float, float]:
        """Convert grid coordinates to world coordinates."""
        world_x = grid_x * self.resolution + self.origin_x
        world_y = grid_y * self.resolution + self.origin_y
        return world_x, world_y

    def is_valid_cell(self, x: int, y: int) -> bool:
        """Check if grid coordinates are within bounds."""
        return 0 <= x < self.width and 0 <= y < self.height

    def set_cell_occupancy(self, x: int, y: int, occupancy: float) -> bool:
        """Set occupancy for a cell."""
        if self.is_valid_cell(x, y):
            self.grid[y][x].update_occupancy(occupancy)
            return True
        return False

    def get_cell_occupancy(self, x: int, y: int) -> float:
        """Get occupancy of a cell."""
        if self.is_valid_cell(x, y):
            return self.grid[y][x].occupancy
        return -1.0  # Invalid coordinates

    def is_free(self, x: int, y: int) -> bool:
        """Check if a cell is free (occupancy < 0.5)."""
        occupancy = self.get_cell_occupancy(x, y)
        return occupancy >= 0 and occupancy < 0.5

    def is_occupied(self, x: int, y: int) -> bool:
        """Check if a cell is occupied (occupancy >= 0.5)."""
        occupancy = self.get_cell_occupancy(x, y)
        return occupancy >= 0.5

    def ray_trace(self, start: Tuple[float, float], end: Tuple[float, float],
                  occupied_prob: float = 0.9, free_prob: float = 0.1) -> None:
        """
        Perform ray tracing to update map based on sensor measurement.

        Args:
            start: Start point (x, y) in world coordinates
            end: End point (x, y) in world coordinates
            occupied_prob: Probability to assign to endpoint
            free_prob: Probability to assign to free space along ray
        """
        start_grid = self.world_to_grid(start[0], start[1])
        end_grid = self.world_to_grid(end[0], end[1])

        # Bresenham's line algorithm for ray tracing
        dx = abs(end_grid[0] - start_grid[0])
        dy = abs(end_grid[1] - start_grid[1])
        x_step = 1 if end_grid[0] > start_grid[0] else -1
        y_step = 1 if end_grid[1] > start_grid[1] else -1

        x, y = start_grid
        error = dx - dy

        # Mark free space along the ray
        while x != end_grid[0] or y != end_grid[1]:
            if self.is_valid_cell(x, y):
                self.set_cell_occupancy(x, y, free_prob)

            error2 = 2 * error
            if error2 > -dy:
                error -= dy
                x += x_step
            if error2 < dx:
                error += dx
                y += y_step

        # Mark endpoint as occupied
        if self.is_valid_cell(end_grid[0], end_grid[1]):
            self.set_cell_occupancy(end_grid[0], end_grid[1], occupied_prob)

    def get_free_space_percentage(self) -> float:
        """Calculate percentage of free space in the map."""
        total_cells = self.width * self.height
        free_cells = 0

        for row in self.grid:
            for cell in row:
                if cell.occupancy >= 0 and cell.occupancy < 0.5:
                    free_cells += 1

        return (free_cells / total_cells) * 100 if total_cells > 0 else 0.0

    def get_map_statistics(self) -> Dict[str, Any]:
        """Get statistics about the map."""
        total_cells = self.width * self.height
        known_cells = 0
        free_cells = 0
        occupied_cells = 0

        for row in self.grid:
            for cell in row:
                if cell.occupancy != -1:
                    known_cells += 1
                    if cell.occupancy < 0.5:
                        free_cells += 1
                    else:
                        occupied_cells += 1

        return {
            "total_cells": total_cells,
            "known_cells": known_cells,
            "free_cells": free_cells,
            "occupied_cells": occupied_cells,
            "unknown_percentage": ((total_cells - known_cells) / total_cells) * 100 if total_cells > 0 else 0.0,
            "free_percentage": (free_cells / total_cells) * 100 if total_cells > 0 else 0.0,
            "occupied_percentage": (occupied_cells / total_cells) * 100 if total_cells > 0 else 0.0,
            "resolution": self.resolution,
            "dimensions": (self.width * self.resolution, self.height * self.resolution)
        }


class TopologicalNode:
    """
    Represents a node in a topological map.
    """
    def __init__(self, id: str, x: float, y: float, name: str = "") -> None:
        self.id = id
        self.x = x
        self.y = y
        self.name = name
        self.neighbors: List[str] = []  # List of connected node IDs
        self.visited_count = 0
        self.last_visited = time.time()

    def add_neighbor(self, neighbor_id: str) -> None:
        """Add a neighbor to this node."""
        if neighbor_id not in self.neighbors:
            self.neighbors.append(neighbor_id)

    def remove_neighbor(self, neighbor_id: str) -> bool:
        """Remove a neighbor from this node."""
        if neighbor_id in self.neighbors:
            self.neighbors.remove(neighbor_id)
            return True
        return False


class TopologicalMap:
    """
    Represents a topological map as a graph of connected locations.
    """
    def __init__(self) -> None:
        self.nodes: Dict[str, TopologicalNode] = {}
        self.edges: List[Tuple[str, str, float]] = []  # (node1, node2, distance)

    def add_node(self, node_id: str, x: float, y: float, name: str = "") -> bool:
        """Add a node to the topological map."""
        if node_id not in self.nodes:
            self.nodes[node_id] = TopologicalNode(node_id, x, y, name)
            return True
        return False

    def add_edge(self, node1_id: str, node2_id: str, distance: Optional[float] = None) -> bool:
        """Add an edge between two nodes."""
        if node1_id not in self.nodes or node2_id not in self.nodes:
            return False

        # Calculate distance if not provided
        if distance is None:
            n1 = self.nodes[node1_id]
            n2 = self.nodes[node2_id]
            distance = math.sqrt((n1.x - n2.x)**2 + (n1.y - n2.y)**2)

        # Add neighbor relationships
        self.nodes[node1_id].add_neighbor(node2_id)
        self.nodes[node2_id].add_neighbor(node1_id)

        # Add edge to list
        edge = (node1_id, node2_id, distance)
        if edge not in self.edges and (node2_id, node1_id, distance) not in self.edges:
            self.edges.append(edge)

        return True

    def get_shortest_path(self, start_id: str, end_id: str) -> List[str]:
        """
        Find shortest path between two nodes using Dijkstra's algorithm.

        Args:
            start_id: Starting node ID
            end_id: Ending node ID

        Returns:
            List of node IDs representing the shortest path
        """
        if start_id not in self.nodes or end_id not in self.nodes:
            return []

        # Initialize distances and previous nodes
        distances = {node_id: float('inf') for node_id in self.nodes}
        previous = {node_id: None for node_id in self.nodes}
        distances[start_id] = 0
        unvisited = set(self.nodes.keys())

        while unvisited:
            # Find node with minimum distance
            current_id = min(unvisited, key=lambda x: distances[x])
            if distances[current_id] == float('inf'):
                break  # No path exists
            if current_id == end_id:
                break  # Found target

            unvisited.remove(current_id)

            # Update distances to neighbors
            current_node = self.nodes[current_id]
            for neighbor_id in current_node.neighbors:
                if neighbor_id in unvisited:
                    # Find edge distance
                    edge_distance = float('inf')
                    for edge in self.edges:
                        if (edge[0] == current_id and edge[1] == neighbor_id) or \
                           (edge[1] == current_id and edge[0] == neighbor_id):
                            edge_distance = edge[2]
                            break

                    new_distance = distances[current_id] + edge_distance
                    if new_distance < distances[neighbor_id]:
                        distances[neighbor_id] = new_distance
                        previous[neighbor_id] = current_id

        # Reconstruct path
        path = []
        current_id = end_id
        while current_id is not None:
            path.insert(0, current_id)
            current_id = previous[current_id]

        return path if path[0] == start_id else []

    def get_map_statistics(self) -> Dict[str, Any]:
        """Get statistics about the topological map."""
        node_count = len(self.nodes)
        edge_count = len(self.edges)
        avg_connectivity = sum(len(node.neighbors) for node in self.nodes.values()) / node_count if node_count > 0 else 0

        return {
            "node_count": node_count,
            "edge_count": edge_count,
            "avg_connectivity": avg_connectivity,
            "node_names": [node.name for node in self.nodes.values() if node.name]
        }


class FeatureMap:
    """
    Represents a feature-based map storing distinctive landmarks and features.
    """
    def __init__(self) -> None:
        self.features: Dict[str, Dict[str, Any]] = {}  # Feature ID -> feature properties

    def add_feature(self, feature_id: str, x: float, y: float, feature_type: str = "landmark",
                   description: str = "", confidence: float = 1.0) -> bool:
        """Add a feature to the map."""
        if feature_id not in self.features:
            self.features[feature_id] = {
                "id": feature_id,
                "x": x,
                "y": y,
                "type": feature_type,
                "description": description,
                "confidence": confidence,
                "observations": 1,
                "last_observed": time.time()
            }
            return True
        return False

    def update_feature(self, feature_id: str, new_x: Optional[float] = None,
                      new_y: Optional[float] = None, confidence: Optional[float] = None) -> bool:
        """Update an existing feature."""
        if feature_id in self.features:
            if new_x is not None:
                self.features[feature_id]["x"] = new_x
            if new_y is not None:
                self.features[feature_id]["y"] = new_y
            if confidence is not None:
                self.features[feature_id]["confidence"] = max(
                    self.features[feature_id]["confidence"], confidence
                )
            self.features[feature_id]["observations"] += 1
            self.features[feature_id]["last_observed"] = time.time()
            return True
        return False

    def find_features_in_radius(self, x: float, y: float, radius: float) -> List[Dict[str, Any]]:
        """Find all features within a certain radius of a point."""
        found_features = []
        for feature in self.features.values():
            distance = math.sqrt((feature["x"] - x)**2 + (feature["y"] - y)**2)
            if distance <= radius:
                found_features.append(feature)
        return found_features

    def get_feature_types(self) -> Dict[str, int]:
        """Get count of each feature type."""
        type_counts = {}
        for feature in self.features.values():
            ftype = feature["type"]
            type_counts[ftype] = type_counts.get(ftype, 0) + 1
        return type_counts

    def get_map_statistics(self) -> Dict[str, Any]:
        """Get statistics about the feature map."""
        feature_count = len(self.features)
        type_counts = self.get_feature_types()
        avg_confidence = sum(f["confidence"] for f in self.features.values()) / feature_count if feature_count > 0 else 0.0

        return {
            "feature_count": feature_count,
            "feature_types": type_counts,
            "avg_confidence": avg_confidence,
            "features_with_descriptions": sum(1 for f in self.features.values() if f["description"])
        }


class MapManager:
    """
    Manages different types of maps for a humanoid robot.
    """
    def __init__(self) -> None:
        self.occupancy_map = OccupancyGridMap(100, 100, 0.2)  # 20m x 20m at 0.2m resolution
        self.topological_map = TopologicalMap()
        self.feature_map = FeatureMap()
        self.current_position = (0.0, 0.0)
        self.map_history: List[Dict[str, Any]] = []

    def update_occupancy_map(self, sensor_data: List[Tuple[float, float]]) -> None:
        """
        Update occupancy grid based on sensor data (e.g., LIDAR or depth sensor).

        Args:
            sensor_data: List of (range, bearing) measurements
        """
        robot_x, robot_y = self.current_position

        for range_val, bearing in sensor_data:
            # Calculate world coordinates of detected point
            world_x = robot_x + range_val * math.cos(bearing)
            world_y = robot_y + range_val * math.sin(bearing)

            # Perform ray tracing to update map
            self.occupancy_map.ray_trace(
                (robot_x, robot_y), (world_x, world_y),
                occupied_prob=0.9, free_prob=0.1
            )

    def update_topological_map(self, location_name: str) -> str:
        """
        Add current location to topological map if it's a new significant location.

        Args:
            location_name: Name for the new location

        Returns:
            ID of the created or existing node
        """
        robot_x, robot_y = self.current_position

        # Check if we're near an existing node
        existing_node = None
        for node_id, node in self.topological_map.nodes.items():
            distance = math.sqrt((node.x - robot_x)**2 + (node.y - robot_y)**2)
            if distance < 1.0:  # If closer than 1 meter to existing node
                existing_node = node_id
                break

        if existing_node:
            # Update existing node
            self.topological_map.nodes[existing_node].visited_count += 1
            self.topological_map.nodes[existing_node].last_visited = time.time()
            return existing_node
        else:
            # Create new node
            node_id = f"loc_{int(time.time()) % 10000}"
            self.topological_map.add_node(node_id, robot_x, robot_y, location_name)
            return node_id

    def update_feature_map(self, detected_features: List[Dict[str, Any]]) -> None:
        """
        Update feature map with newly detected features.

        Args:
            detected_features: List of detected features with properties
        """
        robot_x, robot_y = self.current_position

        for feature in detected_features:
            # Convert bearing and range to world coordinates if needed
            if "range" in feature and "bearing" in feature:
                world_x = robot_x + feature["range"] * math.cos(feature["bearing"] + math.atan2(robot_y, robot_x))
                world_y = robot_y + feature["range"] * math.sin(feature["bearing"] + math.atan2(robot_y, robot_x))
            else:
                world_x, world_y = feature.get("x", robot_x), feature.get("y", robot_y)

            feature_id = feature.get("id", f"feat_{int(time.time()) % 10000}")
            feature_type = feature.get("type", "landmark")
            description = feature.get("description", "")
            confidence = feature.get("confidence", 0.8)

            # Add or update feature
            if feature_id not in self.feature_map.features:
                self.feature_map.add_feature(feature_id, world_x, world_y, feature_type, description, confidence)
            else:
                self.feature_map.update_feature(feature_id, world_x, world_y, confidence)

    def move_robot(self, new_position: Tuple[float, float]) -> None:
        """Update robot position."""
        self.current_position = new_position

    def get_map_summary(self) -> Dict[str, Any]:
        """Get a summary of all maps."""
        return {
            "occupancy_map_stats": self.occupancy_map.get_map_statistics(),
            "topological_map_stats": self.topological_map.get_map_statistics(),
            "feature_map_stats": self.feature_map.get_map_statistics(),
            "current_position": self.current_position
        }

    def get_navigation_info(self, target_position: Tuple[float, float]) -> Dict[str, Any]:
        """
        Get navigation information using different map types.

        Args:
            target_position: Target position (x, y)

        Returns:
            Navigation information using different map types
        """
        robot_x, robot_y = self.current_position
        target_x, target_y = target_position

        # Euclidean distance (simple navigation)
        straight_line_distance = math.sqrt((target_x - robot_x)**2 + (target_y - robot_y)**2)

        # Find closest topological nodes to start and end
        closest_start_node = None
        closest_end_node = None
        min_start_dist = float('inf')
        min_end_dist = float('inf')

        for node_id, node in self.topological_map.nodes.items():
            start_dist = math.sqrt((node.x - robot_x)**2 + (node.y - robot_y)**2)
            end_dist = math.sqrt((node.x - target_x)**2 + (node.y - target_y)**2)

            if start_dist < min_start_dist:
                min_start_dist = start_dist
                closest_start_node = node_id

            if end_dist < min_end_dist:
                min_end_dist = end_dist
                closest_end_node = node_id

        # Find topological path if both nodes exist
        topological_path = []
        path_distance = straight_line_distance  # Default to straight line
        if closest_start_node and closest_end_node:
            topological_path = self.topological_map.get_shortest_path(closest_start_node, closest_end_node)
            if topological_path and len(topological_path) > 1:
                # Calculate path distance
                path_distance = 0.0
                prev_node = self.topological_map.nodes[topological_path[0]]
                for node_id in topological_path[1:]:
                    node = self.topological_map.nodes[node_id]
                    path_distance += math.sqrt((node.x - prev_node.x)**2 + (node.y - prev_node.y)**2)
                    prev_node = node

        return {
            "straight_line_distance": straight_line_distance,
            "topological_path_exists": len(topological_path) > 0,
            "topological_path_length": len(topological_path),
            "path_distance": path_distance,
            "topological_path": topological_path,
            "closest_start_node": closest_start_node,
            "closest_end_node": closest_end_node
        }


def main() -> None:
    """
    Main function demonstrating different map types.
    """
    print("Starting map types demonstration for humanoid robot...")
    print("Showing occupancy grids, topological maps, and feature maps.\n")

    # Initialize the map manager
    map_manager = MapManager()

    print("Initial map states:")
    initial_summary = map_manager.get_map_summary()
    print(f"  Occupancy map: {initial_summary['occupancy_map_stats']['known_cells']} known cells")
    print(f"  Topological map: {initial_summary['topological_map_stats']['node_count']} nodes")
    print(f"  Feature map: {initial_summary['feature_map_stats']['feature_count']} features")
    print()

    # Simulate robot movement and mapping
    print("Simulating robot exploration and mapping...")

    # Define a simple exploration path
    exploration_path = [
        (0, 0), (2, 0), (4, 0), (6, 0), (6, 2), (6, 4), (4, 4), (2, 4), (0, 4), (0, 2)
    ]

    for i, pos in enumerate(exploration_path):
        print(f"  Step {i+1}: Moving to position {pos}")

        # Move robot
        map_manager.move_robot(pos)

        # Simulate sensor data (range and bearing to obstacles)
        # In a real system, this would come from LIDAR or other sensors
        sensor_data = []
        for angle in range(0, 360, 30):  # Sample every 30 degrees
            bearing = math.radians(angle)
            # Simulate obstacles at various distances
            if i % 3 == 0:
                range_val = 1.5  # Close obstacle
            elif i % 3 == 1:
                range_val = 3.0  # Medium obstacle
            else:
                range_val = 5.0  # Far obstacle
            sensor_data.append((range_val, bearing))

        # Update occupancy map
        map_manager.update_occupancy_map(sensor_data)

        # Add location to topological map
        location_name = f"Area_{i+1}"
        node_id = map_manager.update_topological_map(location_name)

        # Simulate detecting features
        features = [
            {"id": f"door_{i}", "type": "door", "range": 2.0, "bearing": math.radians(45)},
            {"id": f"table_{i}", "type": "furniture", "range": 1.5, "bearing": math.radians(135)},
            {"id": f"chair_{i}", "type": "furniture", "range": 2.5, "bearing": math.radians(225)}
        ]
        map_manager.update_feature_map(features)

    print(f"\nExploration completed!")
    print(f"  Visited {len(exploration_path)} locations")

    # Get final map summary
    final_summary = map_manager.get_map_summary()
    print(f"\nFinal map statistics:")
    print(f"  Occupancy map:")
    print(f"    Known cells: {final_summary['occupancy_map_stats']['known_cells']}")
    print(f"    Free space: {final_summary['occupancy_map_stats']['free_percentage']:.1f}%")
    print(f"    Occupied space: {final_summary['occupancy_map_stats']['occupied_percentage']:.1f}%")
    print(f"    Resolution: {final_summary['occupancy_map_stats']['resolution']}m")

    print(f"  Topological map:")
    print(f"    Nodes: {final_summary['topological_map_stats']['node_count']}")
    print(f"    Edges: {final_summary['topological_map_stats']['edge_count']}")
    print(f"    Average connectivity: {final_summary['topological_map_stats']['avg_connectivity']:.1f}")

    print(f"  Feature map:")
    print(f"    Features: {final_summary['feature_map_stats']['feature_count']}")
    print(f"    Feature types: {final_summary['feature_map_stats']['feature_types']}")
    print(f"    Average confidence: {final_summary['feature_map_stats']['avg_confidence']:.2f}")

    # Demonstrate navigation using different map types
    print(f"\nNavigation demonstration:")
    target_pos = (5, 3)
    nav_info = map_manager.get_navigation_info(target_pos)
    print(f"  From {map_manager.current_position} to {target_pos}:")
    print(f"    Straight-line distance: {nav_info['straight_line_distance']:.2f}m")
    print(f"    Topological path exists: {nav_info['topological_path_exists']}")
    print(f"    Topological path length: {nav_info['topological_path_length']} nodes")
    print(f"    Path distance: {nav_info['path_distance']:.2f}m")
    print(f"    Topological path: {nav_info['topological_path']}")

    # Show some features around the current position
    print(f"\nFeatures near current position:")
    nearby_features = map_manager.feature_map.find_features_in_radius(
        map_manager.current_position[0], map_manager.current_position[1], 3.0
    )
    print(f"  Found {len(nearby_features)} features within 3m radius:")
    for feature in nearby_features[:5]:  # Show first 5
        print(f"    {feature['id']} ({feature['type']}) at ({feature['x']:.1f}, {feature['y']:.1f})")

    # Show topological map structure
    print(f"\nTopological map structure:")
    for node_id, node in list(map_manager.topological_map.nodes.items())[:5]:  # Show first 5
        print(f"  Node {node_id} '{node.name}' at ({node.x:.1f}, {node.y:.1f}) connected to {len(node.neighbors)} neighbors")

    print(f"\nMap types demonstration completed.")
    print("This shows how humanoid robots use different map representations:")
    print("- Occupancy grids for detailed spatial mapping")
    print("- Topological maps for efficient path planning")
    print("- Feature maps for landmark-based navigation")


if __name__ == "__main__":
    main()