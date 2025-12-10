#!/usr/bin/env python3
"""
Vision Pipeline Example

This module demonstrates a conceptual vision pipeline for humanoid robots,
showing how to process visual information for perception and understanding.
"""

from typing import Dict, List, Tuple, Optional, Any
import math
import random
import time
from dataclasses import dataclass


@dataclass
class ImageFrame:
    """
    Represents a single image frame from a robot's camera.
    """
    timestamp: float
    width: int
    height: int
    channels: int  # 1 for grayscale, 3 for RGB
    data: List[List[List[int]]]  # [height][width][channels] pixel values
    camera_params: Dict[str, float]  # Camera intrinsic parameters


class FeatureDetector:
    """
    Detects visual features in images such as edges, corners, and keypoints.
    """

    def __init__(self) -> None:
        self.edge_threshold = 50  # Minimum gradient magnitude for edge detection
        self.corner_threshold = 100  # Minimum corner response for detection
        self.feature_window_size = 5  # Size of window for feature analysis

    def detect_edges(self, image: ImageFrame) -> List[Tuple[int, int]]:
        """
        Detect edges in the image using a simple gradient-based approach.

        Args:
            image: Input image frame

        Returns:
            List of (row, col) coordinates of detected edge pixels
        """
        edges = []
        height, width = image.height, image.width

        # Convert to grayscale if needed (average of RGB channels)
        if image.channels == 3:
            grayscale = []
            for i in range(height):
                row = []
                for j in range(width):
                    # Average of RGB channels for grayscale
                    gray_val = sum(image.data[i][j]) // 3
                    row.append(gray_val)
                grayscale.append(row)
        else:
            # Already grayscale
            grayscale = [[image.data[i][j][0] for j in range(width)] for i in range(height)]

        # Simple Sobel edge detection
        for i in range(1, height - 1):
            for j in range(1, width - 1):
                # Calculate gradients using Sobel operators
                gx = (grayscale[i-1][j-1] + 2*grayscale[i][j-1] + grayscale[i+1][j-1] -
                      grayscale[i-1][j+1] - 2*grayscale[i][j+1] - grayscale[i+1][j+1])
                gy = (grayscale[i-1][j-1] + 2*grayscale[i-1][j] + grayscale[i-1][j+1] -
                      grayscale[i+1][j-1] - 2*grayscale[i+1][j] - grayscale[i+1][j+1])

                gradient_magnitude = math.sqrt(gx**2 + gy**2)

                if gradient_magnitude > self.edge_threshold:
                    edges.append((i, j))

        return edges

    def detect_corners(self, image: ImageFrame) -> List[Tuple[int, int, float]]:
        """
        Detect corners in the image using a Harris corner-like approach.

        Args:
            image: Input image frame

        Returns:
            List of (row, col, response) tuples for detected corners
        """
        corners = []
        height, width = image.height, image.width

        # Convert to grayscale
        if image.channels == 3:
            grayscale = []
            for i in range(height):
                row = []
                for j in range(width):
                    gray_val = sum(image.data[i][j]) // 3
                    row.append(gray_val)
                grayscale.append(row)
        else:
            grayscale = [[image.data[i][j][0] for j in range(width)] for i in range(height)]

        # Calculate gradients
        gx_values = [[0 for _ in range(width)] for _ in range(height)]
        gy_values = [[0 for _ in range(width)] for _ in range(height)]

        for i in range(1, height - 1):
            for j in range(1, width - 1):
                gx_values[i][j] = grayscale[i][j+1] - grayscale[i][j-1]
                gy_values[i][j] = grayscale[i+1][j] - grayscale[i-1][j]

        # Calculate corner responses
        for i in range(2, height - 2):
            for j in range(2, width - 2):
                # Calculate elements of the structure tensor
                ixx = iyy = ixy = 0.0

                # Sum over a window
                for di in range(-2, 3):
                    for dj in range(-2, 3):
                        ixx += gx_values[i+di][j+dj] ** 2
                        iyy += gy_values[i+di][j+dj] ** 2
                        ixy += gx_values[i+di][j+dj] * gy_values[i+di][j+dj]

                # Calculate Harris corner response
                det = ixx * iyy - ixy**2
                trace = ixx + iyy
                k = 0.04  # Harris detector parameter
                response = det - k * trace**2

                if response > self.corner_threshold:
                    corners.append((i, j, response))

        return corners

    def extract_descriptors(self, image: ImageFrame, keypoints: List[Tuple[int, int]]) -> Dict[Tuple[int, int], List[float]]:
        """
        Extract feature descriptors for given keypoints.

        Args:
            image: Input image frame
            keypoints: List of (row, col) coordinates

        Returns:
            Dictionary mapping keypoints to descriptor vectors
        """
        descriptors = {}

        # Convert to grayscale
        height, width = image.height, image.width
        if image.channels == 3:
            grayscale = []
            for i in range(height):
                row = []
                for j in range(width):
                    gray_val = sum(image.data[i][j]) // 3
                    row.append(gray_val)
                grayscale.append(row)
        else:
            grayscale = [[image.data[i][j][0] for j in range(width)] for i in range(height)]

        # Extract simple descriptors (histogram of gradients in a patch)
        patch_size = 10  # Size of patch around each keypoint

        for row, col in keypoints:
            if (patch_size <= row < height - patch_size and
                patch_size <= col < width - patch_size):

                # Extract patch
                patch = []
                for di in range(-patch_size, patch_size + 1):
                    patch_row = []
                    for dj in range(-patch_size, patch_size + 1):
                        patch_row.append(grayscale[row + di][col + dj])
                    patch.append(patch_row)

                # Calculate gradients in the patch
                gradients = []
                for i in range(1, len(patch) - 1):
                    for j in range(1, len(patch[0]) - 1):
                        dx = patch[i][j+1] - patch[i][j-1]
                        dy = patch[i+1][j] - patch[i-1][j]
                        magnitude = math.sqrt(dx**2 + dy**2)
                        gradients.append(magnitude)

                # Create simple descriptor (histogram of gradient magnitudes)
                bins = 8
                histogram = [0.0] * bins
                if gradients:
                    max_grad = max(gradients)
                    if max_grad > 0:
                        for grad in gradients:
                            bin_idx = min(bins - 1, int((grad / max_grad) * bins))
                            histogram[bin_idx] += 1.0

                # Normalize histogram
                total = sum(histogram)
                if total > 0:
                    histogram = [h / total for h in histogram]

                descriptors[(row, col)] = histogram

        return descriptors


class ObjectDetector:
    """
    Detects objects in the visual field using template matching and simple classification.
    """

    def __init__(self) -> None:
        self.known_objects: Dict[str, Any] = {}
        self.matching_threshold = 0.7  # Minimum correlation for object detection

    def register_object_template(self, name: str, template: List[List[int]]) -> None:
        """
        Register a template for object detection.

        Args:
            name: Name of the object
            template: Template image for matching
        """
        self.known_objects[name] = template

    def detect_objects(self, image: ImageFrame) -> List[Dict[str, Any]]:
        """
        Detect known objects in the image using template matching.

        Args:
            image: Input image frame

        Returns:
            List of detected objects with position and confidence
        """
        detections = []

        # Convert image to grayscale for matching
        height, width = image.height, image.width
        if image.channels == 3:
            grayscale = []
            for i in range(height):
                row = []
                for j in range(width):
                    gray_val = sum(image.data[i][j]) // 3
                    row.append(gray_val)
                grayscale.append(row)
        else:
            grayscale = [[image.data[i][j][0] for j in range(width)] for i in range(height)]

        # Match against each known object
        for obj_name, template in self.known_objects.items():
            template_h, template_w = len(template), len(template[0])
            if template_h > height or template_w > width:
                continue

            # Perform template matching
            best_match = 0.0
            best_pos = (0, 0)

            for i in range(height - template_h):
                for j in range(width - template_w):
                    # Calculate normalized cross-correlation
                    template_sum = sum(sum(row) for row in template)
                    template_sq_sum = sum(sum(val**2 for val in row) for row in template)
                    img_sum = 0
                    img_sq_sum = 0
                    prod_sum = 0

                    for ti in range(template_h):
                        for tj in range(template_w):
                            img_val = grayscale[i + ti][j + tj]
                            img_sum += img_val
                            img_sq_sum += img_val**2
                            prod_sum += img_val * template[ti][tj]

                    n = template_h * template_w
                    numerator = n * prod_sum - template_sum * img_sum
                    denominator = math.sqrt(n * template_sq_sum - template_sum**2) * math.sqrt(n * img_sq_sum - img_sum**2)

                    if denominator != 0:
                        correlation = numerator / denominator
                        if correlation > best_match:
                            best_match = correlation
                            best_pos = (i + template_h // 2, j + template_w // 2)

            # Add detection if confidence is high enough
            if best_match > self.matching_threshold:
                detections.append({
                    "name": obj_name,
                    "center": best_pos,
                    "confidence": best_match,
                    "bbox": (best_pos[0] - template_h // 2, best_pos[1] - template_w // 2,
                             template_h, template_w)
                })

        return detections


class DepthEstimator:
    """
    Estimates depth information from visual data (stereo or motion-based).
    """

    def __init__(self) -> None:
        self.baseline = 0.1  # Stereo baseline in meters
        self.focal_length = 500  # Focal length in pixels
        self.previous_frame: Optional[ImageFrame] = None

    def estimate_depth_stereo(self, left_image: ImageFrame, right_image: ImageFrame) -> List[List[float]]:
        """
        Estimate depth using stereo vision.

        Args:
            left_image: Left camera image
            right_image: Right camera image

        Returns:
            Depth map as 2D array of distances in meters
        """
        if left_image.height != right_image.height or left_image.width != right_image.width:
            raise ValueError("Left and right images must have the same dimensions")

        height, width = left_image.height, left_image.width
        depth_map = [[float('inf') for _ in range(width)] for _ in range(height)]

        # Convert to grayscale
        def to_grayscale(img: ImageFrame) -> List[List[int]]:
            if img.channels == 3:
                return [[sum(img.data[i][j]) // 3 for j in range(width)] for i in range(height)]
            else:
                return [[img.data[i][j][0] for j in range(width)] for i in range(height)]

        left_gray = to_grayscale(left_image)
        right_gray = to_grayscale(right_image)

        # Simple block matching for disparity estimation
        block_size = 10
        max_disparity = 50

        for i in range(block_size, height - block_size):
            for j in range(block_size, width - block_size):
                min_ssd = float('inf')
                best_disparity = 0

                # Search for matching block in right image
                for d in range(min(max_disparity, j)):
                    if j - d < block_size:
                        continue

                    ssd = 0
                    for bi in range(-block_size//2, block_size//2):
                        for bj in range(-block_size//2, block_size//2):
                            left_val = left_gray[i + bi][j + bj]
                            right_val = right_gray[i + bi][j - d + bj]
                            ssd += (left_val - right_val) ** 2

                    if ssd < min_ssd:
                        min_ssd = ssd
                        best_disparity = d

                # Calculate depth from disparity (D = f*B/d)
                if best_disparity > 0:
                    depth = (self.focal_length * self.baseline) / best_disparity
                    depth_map[i][j] = depth
                else:
                    depth_map[i][j] = float('inf')

        return depth_map

    def estimate_depth_motion(self, current_image: ImageFrame, camera_motion: Tuple[float, float, float]) -> List[List[float]]:
        """
        Estimate depth based on camera motion and apparent motion of features.

        Args:
            current_image: Current image
            camera_motion: Camera motion (dx, dy, dz) in meters

        Returns:
            Depth map estimated from motion
        """
        # This is a simplified implementation
        # In a real system, this would use optical flow and motion parallax
        height, width = current_image.height, current_image.width
        depth_map = [[random.uniform(0.5, 10.0) for _ in range(width)] for _ in range(height)]  # Simulated

        return depth_map


class VisionPipeline:
    """
    Main vision pipeline that processes images and extracts meaningful information.
    """

    def __init__(self) -> None:
        self.feature_detector = FeatureDetector()
        self.object_detector = ObjectDetector()
        self.depth_estimator = DepthEstimator()
        self.pipeline_history: List[Dict[str, Any]] = []

        # Register some example object templates
        # In a real system, these would be learned or provided
        self.object_detector.register_object_template("ball", [[100, 150, 100], [150, 200, 150], [100, 150, 100]])
        self.object_detector.register_object_template("box", [[200, 200, 200], [200, 200, 200], [200, 200, 200]])

    def process_frame(self, image: ImageFrame) -> Dict[str, Any]:
        """
        Process a single image frame through the vision pipeline.

        Args:
            image: Input image frame

        Returns:
            Dictionary containing all processed visual information
        """
        start_time = time.time()

        # Detect features
        edges = self.feature_detector.detect_edges(image)
        corners = self.feature_detector.detect_corners(image)
        all_keypoints = [(r, c) for r, c, _ in corners]  # Use corners as keypoints for now
        descriptors = self.feature_detector.extract_descriptors(image, all_keypoints)

        # Detect objects
        objects = self.object_detector.detect_objects(image)

        # Estimate depth (simulated if no stereo pair provided)
        # For this example, we'll create a simulated depth map
        height, width = image.height, image.width
        depth_map = [[random.uniform(0.5, 5.0) for _ in range(width)] for _ in range(height)]

        # Calculate processing time
        processing_time = time.time() - start_time

        # Create result dictionary
        result = {
            "timestamp": image.timestamp,
            "features": {
                "edges": edges,
                "corners": [(r, c) for r, c, _ in corners],  # Just coordinates for now
                "descriptors": descriptors
            },
            "objects": objects,
            "depth_map": depth_map,
            "processing_time": processing_time,
            "frame_info": {
                "width": image.width,
                "height": image.height,
                "channels": image.channels
            }
        }

        # Add to history
        self.pipeline_history.append(result)

        return result

    def get_scene_understanding(self) -> Dict[str, Any]:
        """
        Generate a higher-level understanding of the scene based on processed frames.

        Returns:
            Dictionary containing scene understanding
        """
        if not self.pipeline_history:
            return {"status": "no_frames_processed", "objects": [], "layout": "unknown"}

        # Analyze the recent history to build scene understanding
        recent_frames = self.pipeline_history[-5:]  # Look at last 5 frames

        # Aggregate object detections
        all_objects = []
        for frame in recent_frames:
            all_objects.extend(frame["objects"])

        # Group similar objects together
        grouped_objects = {}
        for obj in all_objects:
            name = obj["name"]
            if name not in grouped_objects:
                grouped_objects[name] = []
            grouped_objects[name].append(obj)

        # Calculate average positions and confidence for each object type
        object_summary = {}
        for name, detections in grouped_objects.items():
            avg_confidence = sum(d["confidence"] for d in detections) / len(detections)
            avg_center = (
                sum(d["center"][0] for d in detections) / len(detections),
                sum(d["center"][1] for d in detections) / len(detections)
            )
            object_summary[name] = {
                "average_confidence": avg_confidence,
                "average_position": avg_center,
                "detection_count": len(detections)
            }

        # Estimate scene layout based on depth information
        if recent_frames:
            latest_depth = recent_frames[-1]["depth_map"]
            avg_depth = sum(sum(row) for row in latest_depth) / (len(latest_depth) * len(latest_depth[0]))
            scene_layout = "indoor" if avg_depth < 3.0 else "outdoor"
        else:
            scene_layout = "unknown"

        return {
            "status": "active",
            "object_summary": object_summary,
            "scene_layout": scene_layout,
            "total_objects_detected": len(all_objects),
            "frame_processing_history": len(self.pipeline_history)
        }


def create_sample_image(width: int, height: int, channels: int = 3) -> ImageFrame:
    """
    Create a sample image for testing the vision pipeline.

    Args:
        width: Image width
        height: Image height
        channels: Number of color channels (1 for grayscale, 3 for RGB)

    Returns:
        Sample image frame
    """
    # Create a simple test image with some geometric shapes
    data = []
    for i in range(height):
        row = []
        for j in range(width):
            if channels == 3:
                # Create a test pattern with different regions
                if 50 < i < 150 and 50 < j < 150:
                    # Central square
                    pixel = [200, 100, 100]  # Reddish
                elif 200 < i < 250 and 200 < j < 300:
                    # Another square
                    pixel = [100, 200, 100]  # Greenish
                elif math.sqrt((i - height//2)**2 + (j - width//2)**2) < 40:
                    # Circular region
                    pixel = [100, 100, 200]  # Blueish
                else:
                    # Background
                    pixel = [50, 50, 50]  # Dark gray
            else:
                # Grayscale
                if 50 < i < 150 and 50 < j < 150:
                    pixel = [180]  # Bright
                elif 200 < i < 250 and 200 < j < 300:
                    pixel = [120]  # Medium
                elif math.sqrt((i - height//2)**2 + (j - width//2)**2) < 40:
                    pixel = [160]  # Bright
                else:
                    pixel = [80]   # Dark

            row.append(pixel)
        data.append(row)

    return ImageFrame(
        timestamp=time.time(),
        width=width,
        height=height,
        channels=channels,
        data=data,
        camera_params={"focal_length": 500.0, "width": width, "height": height}
    )


def main() -> None:
    """
    Main function demonstrating the vision pipeline.
    """
    print("Starting vision pipeline demonstration for humanoid robot...")
    print("Showing how to process visual information for perception and understanding.\n")

    # Initialize the vision pipeline
    pipeline = VisionPipeline()

    # Create sample images of different sizes
    print("Processing sample images through the vision pipeline...")

    for i in range(3):
        print(f"\nProcessing image {i + 1}:")

        # Create a sample image
        if i == 0:
            sample_image = create_sample_image(320, 240, 3)  # Standard definition RGB
            print("  Image: 320x240 RGB")
        elif i == 1:
            sample_image = create_sample_image(640, 480, 1)  # HD Grayscale
            print("  Image: 640x480 Grayscale")
        else:
            sample_image = create_sample_image(160, 120, 3)  # Low-res RGB
            print("  Image: 160x120 RGB")

        # Process the image through the pipeline
        result = pipeline.process_frame(sample_image)

        # Display results
        print(f"  Features detected:")
        print(f"    Edges: {len(result['features']['edges'])}")
        print(f"    Corners: {len(result['features']['corners'])}")
        print(f"    Descriptors: {len(result['features']['descriptors'])}")
        print(f"  Objects detected: {len(result['objects'])}")
        for obj in result['objects']:
            print(f"    - {obj['name']} (confidence: {obj['confidence']:.2f})")
        print(f"  Processing time: {result['processing_time']:.4f} seconds")

    print(f"\nScene understanding after processing {len(pipeline.pipeline_history)} frames:")
    scene_understanding = pipeline.get_scene_understanding()

    if scene_understanding["status"] == "active":
        print(f"  Scene layout: {scene_understanding['scene_layout']}")
        print(f"  Total objects detected: {scene_understanding['total_objects_detected']}")
        print(f"  Object summary:")
        for obj_name, info in scene_understanding["object_summary"].items():
            print(f"    {obj_name}: {info['detection_count']} detections, "
                  f"avg confidence: {info['average_confidence']:.2f}")
    else:
        print(f"  No frames processed yet")

    # Demonstrate feature detection in detail
    print(f"\nDetailed feature analysis:")
    sample_image = create_sample_image(320, 240, 3)
    result = pipeline.process_frame(sample_image)

    # Show some edge and corner locations
    edges = result["features"]["edges"]
    corners = result["features"]["corners"]

    print(f"  Sample edge locations (first 5): {edges[:5]}")
    print(f"  Sample corner locations (first 5): {corners[:5]}")

    # Show depth map statistics (simulated)
    depth_map = result["depth_map"]
    avg_depth = sum(sum(row) for row in depth_map) / (len(depth_map) * len(depth_map[0]))
    min_depth = min(min(row) for row in depth_map)
    max_depth = max(max(row) for row in depth_map)

    print(f"  Depth map statistics:")
    print(f"    Average depth: {avg_depth:.2f} m")
    print(f"    Range: {min_depth:.2f} - {max_depth:.2f} m")

    print(f"\nVision pipeline demonstration completed.")
    print("This shows how humanoid robots process visual information to")
    print("understand their environment through feature detection, object recognition, and depth estimation.")


if __name__ == "__main__":
    main()