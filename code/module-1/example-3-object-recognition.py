#!/usr/bin/env python3
"""
Conceptual Object Recognition Example

This module demonstrates conceptual object recognition for humanoid robots,
showing how to identify and classify objects in the environment using sensor data.
"""

from typing import Dict, List, Tuple, Optional
import random
import math


class FeatureExtractor:
    """
    Extracts features from sensor data for object recognition.
    """

    def __init__(self) -> None:
        self.color_bins = 8  # Number of bins for color histogram
        self.shape_features = ["corners", "edges", "symmetry", "aspect_ratio"]

    def extract_color_features(self, image_data: List[List[int]]) -> List[float]:
        """
        Extract color features from image data.

        Args:
            image_data: 2D list representing grayscale image

        Returns:
            Normalized color histogram
        """
        histogram = [0] * self.color_bins
        total_pixels = 0

        for row in image_data:
            for pixel_value in row:
                bin_index = min(int(pixel_value / 256 * self.color_bins), self.color_bins - 1)
                histogram[bin_index] += 1
                total_pixels += 1

        # Normalize histogram
        if total_pixels > 0:
            histogram = [count / total_pixels for count in histogram]

        return histogram

    def extract_shape_features(self, contour: List[Tuple[int, int]]) -> Dict[str, float]:
        """
        Extract shape features from contour data.

        Args:
            contour: List of (x, y) coordinates representing object contour

        Returns:
            Dictionary of shape features
        """
        if len(contour) < 3:
            return {
                "corners": 0,
                "edges": 0,
                "symmetry": 0.0,
                "aspect_ratio": 1.0
            }

        # Calculate bounding box
        min_x = min(point[0] for point in contour)
        max_x = max(point[0] for point in contour)
        min_y = min(point[1] for point in contour)
        max_y = max(point[1] for point in contour)

        width = max_x - min_x
        height = max_y - min_y
        aspect_ratio = width / height if height != 0 else 1.0

        # Count corners (simplified)
        corners = self._count_corners(contour)

        # Estimate symmetry (simplified)
        symmetry = self._estimate_symmetry(contour)

        return {
            "corners": corners,
            "edges": len(contour),
            "symmetry": symmetry,
            "aspect_ratio": aspect_ratio
        }

    def _count_corners(self, contour: List[Tuple[int, int]]) -> int:
        """Estimate number of corners in contour."""
        # Simplified corner detection
        if len(contour) < 4:
            return len(contour)

        # Count significant direction changes
        corners = 0
        for i in range(len(contour)):
            p1 = contour[i]
            p2 = contour[(i + 1) % len(contour)]
            p3 = contour[(i + 2) % len(contour)]

            # Calculate angle between consecutive segments
            angle = self._calculate_angle(p1, p2, p3)
            if angle < 160:  # Consider significant turns as corners
                corners += 1

        return min(corners, 10)  # Cap at 10 corners

    def _estimate_symmetry(self, contour: List[Tuple[int, int]]) -> float:
        """Estimate symmetry of shape."""
        if len(contour) < 4:
            return 0.0

        # Calculate centroid
        cx = sum(point[0] for point in contour) / len(contour)
        cy = sum(point[1] for point in contour) / len(contour)

        # Compare distances from centroid
        distances = [math.sqrt((point[0] - cx)**2 + (point[1] - cy)**2) for point in contour]
        avg_distance = sum(distances) / len(distances)

        if avg_distance == 0:
            return 1.0

        # Calculate variance of distances (lower variance = more symmetric)
        variance = sum((d - avg_distance)**2 for d in distances) / len(distances)
        normalized_variance = variance / (avg_distance**2) if avg_distance != 0 else 0

        # Convert to symmetry score (0 to 1, where 1 is most symmetric)
        symmetry_score = max(0.0, 1.0 - normalized_variance)
        return symmetry_score

    def _calculate_angle(self, p1: Tuple[int, int], p2: Tuple[int, int],
                        p3: Tuple[int, int]) -> float:
        """Calculate angle between three points."""
        # Vector from p2 to p1
        v1 = (p1[0] - p2[0], p1[1] - p2[1])
        # Vector from p2 to p3
        v2 = (p3[0] - p2[0], p3[1] - p2[1])

        # Calculate dot product and magnitudes
        dot_product = v1[0] * v2[0] + v1[1] * v2[1]
        mag_v1 = math.sqrt(v1[0]**2 + v1[1]**2)
        mag_v2 = math.sqrt(v2[0]**2 + v2[1]**2)

        if mag_v1 == 0 or mag_v2 == 0:
            return 180.0

        # Calculate angle in radians, then convert to degrees
        cos_angle = max(-1.0, min(1.0, dot_product / (mag_v1 * mag_v2)))
        angle_rad = math.acos(cos_angle)
        angle_deg = math.degrees(angle_rad)

        return angle_deg


class ObjectClassifier:
    """
    Classifies objects based on extracted features.
    """

    def __init__(self) -> None:
        # Predefined object models with typical feature ranges
        self.object_models = {
            "ball": {
                "color_range": [(0.1, 0.3), (0.1, 0.3), (0.1, 0.3), (0.1, 0.3)],  # Even distribution
                "shape_features": {
                    "corners": (0, 3),
                    "symmetry": (0.7, 1.0),
                    "aspect_ratio": (0.8, 1.2)
                }
            },
            "box": {
                "color_range": [(0.2, 0.8), (0.0, 0.3), (0.0, 0.3), (0.0, 0.3)],  # Dominant first bin
                "shape_features": {
                    "corners": (3, 5),
                    "symmetry": (0.5, 1.0),
                    "aspect_ratio": (0.5, 2.0)
                }
            },
            "cylinder": {
                "color_range": [(0.1, 0.4), (0.1, 0.4), (0.1, 0.4), (0.1, 0.4)],
                "shape_features": {
                    "corners": (0, 2),
                    "symmetry": (0.6, 1.0),
                    "aspect_ratio": (0.3, 0.7)  # Tall object
                }
            },
            "person": {
                "color_range": [(0.1, 0.5), (0.1, 0.5), (0.1, 0.5), (0.1, 0.5)],
                "shape_features": {
                    "corners": (2, 6),
                    "symmetry": (0.4, 0.8),
                    "aspect_ratio": (0.3, 0.6)  # Tall and narrow
                }
            }
        }

    def classify_object(self, color_features: List[float],
                       shape_features: Dict[str, float]) -> Tuple[str, float]:
        """
        Classify an object based on its features.

        Args:
            color_features: Normalized color histogram
            shape_features: Dictionary of shape features

        Returns:
            Tuple of (object_class, confidence_score)
        """
        best_match = ("unknown", 0.0)

        for obj_class, model in self.object_models.items():
            confidence = self._calculate_match_confidence(
                color_features, shape_features, model
            )

            if confidence > best_match[1]:
                best_match = (obj_class, confidence)

        return best_match

    def _calculate_match_confidence(self, color_features: List[float],
                                  shape_features: Dict[str, float],
                                  model: Dict) -> float:
        """Calculate how well features match a model."""
        # Color match score
        color_score = 0.0
        if "color_range" in model:
            for i, (min_val, max_val) in enumerate(model["color_range"]):
                if i < len(color_features):
                    if min_val <= color_features[i] <= max_val:
                        # Score based on how close to center of range
                        center = (min_val + max_val) / 2
                        diff = abs(color_features[i] - center)
                        range_size = max_val - min_val
                        if range_size > 0:
                            score = 1.0 - min(1.0, (2 * diff) / range_size)
                            color_score += score
                        else:
                            color_score += 1.0 if color_features[i] == center else 0.0

        # Shape match score
        shape_score = 0.0
        if "shape_features" in model:
            for feature, (min_val, max_val) in model["shape_features"].items():
                if feature in shape_features:
                    value = shape_features[feature]
                    if min_val <= value <= max_val:
                        # Score based on how close to center of range
                        center = (min_val + max_val) / 2
                        diff = abs(value - center)
                        range_size = max_val - min_val
                        if range_size > 0:
                            score = 1.0 - min(1.0, (2 * diff) / range_size)
                            shape_score += score
                        else:
                            shape_score += 1.0 if value == center else 0.0

        # Combine scores (equal weight for color and shape)
        total_score = (color_score + shape_score) / (len(model.get("color_range", [])) +
                                                   len(model.get("shape_features", {})))
        return total_score


class ObjectRecognitionSystem:
    """
    Main system for object recognition in humanoid robots.
    """

    def __init__(self) -> None:
        self.feature_extractor = FeatureExtractor()
        self.classifier = ObjectClassifier()

    def recognize_objects(self, image_data: List[List[int]],
                        contour_data: List[List[Tuple[int, int]]]) -> List[Dict]:
        """
        Recognize objects in the environment.

        Args:
            image_data: 2D list representing image
            contour_data: List of contours representing objects

        Returns:
            List of recognized objects with classification and confidence
        """
        recognized_objects = []

        for i, contour in enumerate(contour_data):
            # Extract features
            color_features = self.feature_extractor.extract_color_features(image_data)
            shape_features = self.feature_extractor.extract_shape_features(contour)

            # Classify object
            obj_class, confidence = self.classifier.classify_object(
                color_features, shape_features
            )

            # Add to results if confidence is above threshold
            if confidence > 0.3:  # Confidence threshold
                object_info = {
                    "id": f"obj_{i}",
                    "class": obj_class,
                    "confidence": confidence,
                    "position": self._estimate_position(contour),
                    "size": self._estimate_size(contour)
                }
                recognized_objects.append(object_info)

        return recognized_objects

    def _estimate_position(self, contour: List[Tuple[int, int]]) -> Tuple[float, float]:
        """Estimate position of object from contour."""
        if not contour:
            return (0.0, 0.0)

        avg_x = sum(point[0] for point in contour) / len(contour)
        avg_y = sum(point[1] for point in contour) / len(contour)

        return (avg_x, avg_y)

    def _estimate_size(self, contour: List[Tuple[int, int]]) -> Tuple[float, float]:
        """Estimate size of object from contour."""
        if len(contour) < 2:
            return (0.0, 0.0)

        min_x = min(point[0] for point in contour)
        max_x = max(point[0] for point in contour)
        min_y = min(point[1] for point in contour)
        max_y = max(point[1] for point in contour)

        width = max_x - min_x
        height = max_y - min_y

        return (width, height)


def main() -> None:
    """
    Main function demonstrating object recognition.
    """
    print("Starting conceptual object recognition for humanoid robot...")
    print("Demonstrating feature extraction and classification.\n")

    # Initialize the object recognition system
    recognition_system = ObjectRecognitionSystem()

    # Simulate some sample data
    # Create a simple 20x20 "image" with some patterns
    sample_image = []
    for i in range(20):
        row = []
        for j in range(20):
            # Create some patterns: a central object with different colors
            if 8 <= i <= 12 and 8 <= j <= 12:
                # Central square object - brighter
                row.append(random.randint(150, 200))
            elif 5 <= i <= 6 and 5 <= j <= 15:
                # Vertical bar - medium brightness
                row.append(random.randint(100, 150))
            else:
                # Background - darker
                row.append(random.randint(0, 50))
        sample_image.append(row)

    # Create sample contours (simplified as rectangles for demonstration)
    sample_contours = [
        [(8, 8), (8, 12), (12, 12), (12, 8)],  # Square in center
        [(5, 5), (5, 6), (15, 6), (15, 5)],    # Horizontal bar
        [(2, 2), (2, 4), (4, 4), (4, 2)]       # Small square
    ]

    print("Processing image data and contours...")
    print(f"Image size: {len(sample_image)}x{len(sample_image[0])}")
    print(f"Number of contours detected: {len(sample_contours)}\n")

    # Perform object recognition
    recognized_objects = recognition_system.recognize_objects(
        sample_image, sample_contours
    )

    print("Recognition results:")
    if recognized_objects:
        for obj in recognized_objects:
            print(f"  Object {obj['id']}: {obj['class']} "
                  f"(confidence: {obj['confidence']:.2f}, "
                  f"position: {obj['position']}, "
                  f"size: {obj['size']})")
    else:
        print("  No objects recognized above confidence threshold.")

    print(f"\nTotal objects recognized: {len(recognized_objects)}")

    # Demonstrate feature extraction in detail for first contour
    if sample_contours:
        print(f"\nDetailed analysis of first contour:")
        contour = sample_contours[0]

        color_features = recognition_system.feature_extractor.extract_color_features(sample_image)
        shape_features = recognition_system.feature_extractor.extract_shape_features(contour)

        print(f"  Color histogram: {[f'{val:.2f}' for val in color_features[:4]]}...")
        print(f"  Shape features: corners={shape_features['corners']}, "
              f"aspect_ratio={shape_features['aspect_ratio']:.2f}, "
              f"symmetry={shape_features['symmetry']:.2f}")


if __name__ == "__main__":
    main()