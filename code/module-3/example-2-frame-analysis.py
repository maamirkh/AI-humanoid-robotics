#!/usr/bin/env python3
"""
Conceptual Frame Analysis Example

This module demonstrates conceptual frame analysis for humanoid robots,
showing how to analyze visual frames to understand the environment and extract meaningful information.
"""

from typing import Dict, List, Tuple, Optional, Any
import math
import random
import time
from enum import Enum


class MotionType(Enum):
    """Types of motion that can be detected in frame sequences."""
    STATIC = "static"
    TRANSLATION = "translation"
    ROTATION = "rotation"
    PERIODIC = "periodic"
    COMPLEX = "complex"


class FrameSegment:
    """
    Represents a segment of a frame with associated properties.
    """

    def __init__(self, x: int, y: int, width: int, height: int,
                 avg_intensity: float, motion_vector: Tuple[float, float] = (0, 0)) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.avg_intensity = avg_intensity
        self.motion_vector = motion_vector  # (dx, dy) in pixels
        self.area = width * height
        self.centroid = (x + width // 2, y + height // 2)

    def intersects(self, other: 'FrameSegment') -> bool:
        """Check if this segment intersects with another."""
        return not (self.x + self.width < other.x or
                   other.x + other.width < self.x or
                   self.y + self.height < other.y or
                   other.y + other.height < self.y)

    def get_motion_speed(self) -> float:
        """Get the speed of motion for this segment."""
        return math.sqrt(self.motion_vector[0]**2 + self.motion_vector[1]**2)


class FrameAnalyzer:
    """
    Analyzes individual frames and sequences of frames to extract meaningful information.
    """

    def __init__(self) -> None:
        self.segment_threshold = 30  # Intensity difference threshold for segmentation
        self.motion_threshold = 2.0  # Minimum motion for detection
        self.temporal_window = 5     # Number of frames to consider for temporal analysis
        self.frame_buffer: List[Any] = []  # Buffer for temporal analysis

    def segment_frame(self, frame: List[List[int]], min_segment_size: int = 10) -> List[FrameSegment]:
        """
        Segment the frame into regions based on intensity similarity.

        Args:
            frame: 2D list representing grayscale frame
            min_segment_size: Minimum size for a valid segment

        Returns:
            List of FrameSegment objects
        """
        height, width = len(frame), len(frame[0]) if frame else (0, 0)
        if height == 0 or width == 0:
            return []

        # Simple region growing segmentation
        visited = [[False for _ in range(width)] for _ in range(height)]
        segments = []

        for i in range(height):
            for j in range(width):
                if not visited[i][j]:
                    # Start a new region
                    region_pixels = []
                    region_stack = [(i, j)]
                    start_intensity = frame[i][j]

                    while region_stack:
                        x, y = region_stack.pop()
                        if (0 <= x < height and 0 <= y < width and
                            not visited[x][y] and
                            abs(frame[x][y] - start_intensity) < self.segment_threshold):

                            visited[x][y] = True
                            region_pixels.append((x, y))

                            # Add neighbors to stack
                            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                                nx, ny = x + dx, y + dy
                                if 0 <= nx < height and 0 <= ny < width and not visited[nx][ny]:
                                    region_stack.append((nx, ny))

                    # Create segment if large enough
                    if len(region_pixels) >= min_segment_size:
                        min_x = min(p[0] for p in region_pixels)
                        max_x = max(p[0] for p in region_pixels)
                        min_y = min(p[1] for p in region_pixels)
                        max_y = max(p[1] for p in region_pixels)

                        avg_intensity = sum(frame[p[0]][p[1]] for p in region_pixels) / len(region_pixels)

                        segment = FrameSegment(
                            min_y, min_x, max_y - min_y + 1, max_x - min_x + 1,
                            avg_intensity
                        )
                        segments.append(segment)

        return segments

    def compute_optical_flow(self, frame1: List[List[int]], frame2: List[List[int]],
                           block_size: int = 8) -> List[List[Tuple[float, float]]]:
        """
        Compute optical flow between two frames using block matching.

        Args:
            frame1: First frame (grayscale)
            frame2: Second frame (grayscale)
            block_size: Size of blocks for matching

        Returns:
            2D list of motion vectors for each block
        """
        height, width = len(frame1), len(frame1[0]) if frame1 else (0, 0)
        if height == 0 or width == 0 or height != len(frame2) or width != len(frame2[0]):
            return []

        flow_field = []
        search_window = 5  # How far to search for matching blocks

        for i in range(0, height - block_size, block_size):
            flow_row = []
            for j in range(0, width - block_size, block_size):
                # Get block from first frame
                block1 = [frame1[i + di][j + dj] for di in range(block_size) for dj in range(block_size)]

                # Search for best match in second frame
                best_ssd = float('inf')
                best_dx, best_dy = 0, 0

                search_i_start = max(0, i - search_window)
                search_i_end = min(height - block_size, i + search_window)
                search_j_start = max(0, j - search_window)
                search_j_end = min(width - block_size, j + search_window)

                for si in range(search_i_start, search_i_end + 1):
                    for sj in range(search_j_start, search_j_end + 1):
                        block2 = [frame2[si + di][sj + dj] for di in range(block_size) for dj in range(block_size)]

                        # Calculate Sum of Squared Differences
                        ssd = sum((b1 - b2)**2 for b1, b2 in zip(block1, block2))

                        if ssd < best_ssd:
                            best_ssd = ssd
                            best_dx = sj - j
                            best_dy = si - i

                flow_row.append((best_dx, best_dy))
            flow_field.append(flow_row)

        return flow_field

    def analyze_frame_sequence(self, frames: List[List[List[int]]]) -> Dict[str, Any]:
        """
        Analyze a sequence of frames to detect motion patterns and temporal changes.

        Args:
            frames: List of frames to analyze

        Returns:
            Dictionary containing analysis results
        """
        if len(frames) < 2:
            return {"status": "insufficient_frames", "motion_types": []}

        # Compute motion between consecutive frames
        motion_analysis = []
        for i in range(len(frames) - 1):
            flow = self.compute_optical_flow(frames[i], frames[i + 1])
            motion_analysis.append(flow)

        # Analyze overall motion patterns
        total_motion_x = 0
        total_motion_y = 0
        motion_vectors = []

        for flow in motion_analysis:
            for row in flow:
                for dx, dy in row:
                    total_motion_x += dx
                    total_motion_y += dy
                    motion_vectors.append((dx, dy))

        avg_motion_x = total_motion_x / len(motion_vectors) if motion_vectors else 0
        avg_motion_y = total_motion_y / len(motion_vectors) if motion_vectors else 0

        # Calculate motion statistics
        motion_magnitudes = [math.sqrt(dx**2 + dy**2) for dx, dy in motion_vectors]
        avg_motion_magnitude = sum(motion_magnitudes) / len(motion_magnitudes) if motion_magnitudes else 0
        max_motion_magnitude = max(motion_magnitudes) if motion_magnitudes else 0

        # Determine motion type
        motion_type = self._classify_motion_type(motion_vectors, len(frames))

        # Analyze intensity changes over time
        intensity_changes = []
        for i in range(len(frames) - 1):
            frame1, frame2 = frames[i], frames[i + 1]
            height, width = len(frame1), len(frame1[0]) if frame1 else (0, 0)
            if height > 0 and width > 0:
                change = sum(abs(frame1[r][c] - frame2[r][c])
                           for r in range(height) for c in range(width))
                change_avg = change / (height * width)
                intensity_changes.append(change_avg)

        avg_intensity_change = sum(intensity_changes) / len(intensity_changes) if intensity_changes else 0

        return {
            "status": "analyzed",
            "motion_type": motion_type,
            "average_motion": (avg_motion_x, avg_motion_y),
            "average_motion_magnitude": avg_motion_magnitude,
            "max_motion_magnitude": max_motion_magnitude,
            "total_frames": len(frames),
            "intensity_change_rate": avg_intensity_change,
            "motion_vectors_count": len(motion_vectors)
        }

    def _classify_motion_type(self, motion_vectors: List[Tuple[float, float]],
                            num_frames: int) -> MotionType:
        """Classify the type of motion based on motion vectors."""
        if not motion_vectors:
            return MotionType.STATIC

        # Calculate statistics
        avg_x = sum(dx for dx, dy in motion_vectors) / len(motion_vectors)
        avg_y = sum(dy for dx, dy in motion_vectors) / len(motion_vectors)
        avg_magnitude = sum(math.sqrt(dx**2 + dy**2) for dx, dy in motion_vectors) / len(motion_vectors)

        # Check if motion is mostly zero (static scene)
        if avg_magnitude < self.motion_threshold:
            return MotionType.STATIC

        # Check for periodic motion (simple detection)
        if num_frames > 3:
            # Look for oscillating patterns
            x_values = [dx for dx, dy in motion_vectors]
            y_values = [dy for dx, dy in motion_vectors]

            # Check if values oscillate around zero
            x_oscillates = any(x * next_x < 0 for x, next_x in zip(x_values, x_values[1:]))
            y_oscillates = any(y * next_y < 0 for y, next_y in zip(y_values, y_values[1:]))

            if x_oscillates or y_oscillates:
                return MotionType.PERIODIC

        # Check for consistent direction (translation)
        if abs(avg_x) > self.motion_threshold or abs(avg_y) > self.motion_threshold:
            return MotionType.TRANSLATION

        # If motion is significant but not clearly translation or periodic
        return MotionType.COMPLEX

    def detect_objects_in_frame(self, frame: List[List[int]], min_size: int = 20) -> List[Dict[str, Any]]:
        """
        Detect objects in a frame based on segmentation and properties.

        Args:
            frame: Input frame (grayscale)
            min_size: Minimum size for object detection

        Returns:
            List of detected objects with properties
        """
        segments = self.segment_frame(frame, min_size)
        objects = []

        for seg in segments:
            # Classify segment based on properties
            shape_descriptor = self._describe_shape(seg)
            intensity_descriptor = "bright" if seg.avg_intensity > 128 else "dark"

            objects.append({
                "segment": seg,
                "position": seg.centroid,
                "size": seg.area,
                "intensity": seg.avg_intensity,
                "shape": shape_descriptor,
                "intensity_category": intensity_descriptor
            })

        return objects

    def _describe_shape(self, segment: FrameSegment) -> str:
        """Describe the shape of a segment."""
        aspect_ratio = segment.width / segment.height if segment.height > 0 else 1.0

        if 0.8 <= aspect_ratio <= 1.2:
            return "square" if segment.width < 50 else "circle"
        elif aspect_ratio > 2.0:
            return "horizontal_rectangle"
        elif aspect_ratio < 0.5:
            return "vertical_rectangle"
        else:
            return "rectangle"


class FrameSequenceAnalyzer:
    """
    Analyzes sequences of frames to understand dynamic scenes.
    """

    def __init__(self) -> None:
        self.analyzer = FrameAnalyzer()
        self.analysis_history: List[Dict[str, Any]] = []
        self.object_tracking: Dict[str, List[Tuple[float, float]]] = {}  # Track object positions

    def analyze_sequence(self, frames: List[List[List[int]]]) -> Dict[str, Any]:
        """
        Analyze a sequence of frames comprehensively.

        Args:
            frames: List of frames to analyze

        Returns:
            Comprehensive analysis results
        """
        if not frames:
            return {"status": "no_frames", "summary": {}}

        # Analyze motion in the sequence
        motion_analysis = self.analyzer.analyze_frame_sequence(frames)

        # Analyze the first frame in detail for static content
        if frames:
            objects = self.analyzer.detect_objects_in_frame(frames[0])
        else:
            objects = []

        # Calculate scene statistics
        scene_stats = self._calculate_scene_statistics(frames)

        # Combine all analysis
        analysis_result = {
            "motion_analysis": motion_analysis,
            "static_objects": objects,
            "scene_statistics": scene_stats,
            "timestamp": time.time()
        }

        # Add to history
        self.analysis_history.append(analysis_result)

        return analysis_result

    def _calculate_scene_statistics(self, frames: List[List[List[int]]]) -> Dict[str, float]:
        """Calculate various statistics about the scene."""
        if not frames:
            return {}

        # Calculate statistics for the first frame as representative
        frame = frames[0]
        height, width = len(frame), len(frame[0]) if frame else (0, 0)

        if height == 0 or width == 0:
            return {}

        # Intensity statistics
        all_pixels = [frame[i][j] for i in range(height) for j in range(width)]
        avg_intensity = sum(all_pixels) / len(all_pixels)
        intensity_std = math.sqrt(sum((p - avg_intensity)**2 for p in all_pixels) / len(all_pixels))
        min_intensity = min(all_pixels)
        max_intensity = max(all_pixels)

        # Calculate gradients for texture analysis
        gradients = []
        for i in range(1, height - 1):
            for j in range(1, width - 1):
                dx = abs(frame[i][j+1] - frame[i][j-1])
                dy = abs(frame[i+1][j] - frame[i-1][j])
                gradient_magnitude = math.sqrt(dx**2 + dy**2)
                gradients.append(gradient_magnitude)

        avg_gradient = sum(gradients) / len(gradients) if gradients else 0

        return {
            "average_intensity": avg_intensity,
            "intensity_std": intensity_std,
            "min_intensity": min_intensity,
            "max_intensity": max_intensity,
            "average_gradient": avg_gradient,
            "frame_height": height,
            "frame_width": width
        }

    def get_dynamic_scene_understanding(self) -> Dict[str, Any]:
        """
        Generate a high-level understanding of the dynamic scene.

        Returns:
            Dictionary with scene understanding
        """
        if not self.analysis_history:
            return {"status": "no_analysis_performed", "activity_level": 0.0}

        # Analyze recent history
        recent_analysis = self.analysis_history[-5:]  # Last 5 analyses

        # Calculate average motion across recent frames
        motion_magnitudes = []
        for analysis in recent_analysis:
            if analysis["motion_analysis"]["status"] == "analyzed":
                motion_magnitudes.append(analysis["motion_analysis"]["average_motion_magnitude"])

        avg_motion = sum(motion_magnitudes) / len(motion_magnitudes) if motion_magnitudes else 0.0

        # Determine activity level
        if avg_motion < 1.0:
            activity_level = "low"
        elif avg_motion < 5.0:
            activity_level = "medium"
        else:
            activity_level = "high"

        # Count objects across recent frames
        total_objects = sum(len(analysis["static_objects"]) for analysis in recent_analysis)
        avg_objects = total_objects / len(recent_analysis) if recent_analysis else 0

        # Determine dominant motion type
        motion_types = [analysis["motion_analysis"].get("motion_type", "static")
                       for analysis in recent_analysis]
        if motion_types:
            dominant_motion = max(set(motion_types), key=motion_types.count)
        else:
            dominant_motion = "static"

        return {
            "status": "active",
            "activity_level": activity_level,
            "average_motion_magnitude": avg_motion,
            "average_objects_count": avg_objects,
            "dominant_motion_type": dominant_motion,
            "total_analyzed_sequences": len(self.analysis_history),
            "recent_analysis_count": len(recent_analysis)
        }

    def compare_frames(self, frame1: List[List[int]], frame2: List[List[int]]) -> Dict[str, Any]:
        """
        Compare two frames to detect changes.

        Args:
            frame1: First frame
            frame2: Second frame

        Returns:
            Dictionary describing changes between frames
        """
        if len(frame1) != len(frame2) or (frame1 and frame2 and len(frame1[0]) != len(frame2[0])):
            return {"status": "frames_not_comparable", "reason": "different_dimensions"}

        height, width = len(frame1), len(frame1[0]) if frame1 else (0, 0)
        if height == 0 or width == 0:
            return {"status": "empty_frames"}

        # Calculate pixel-wise differences
        diff_count = 0
        total_diff = 0
        max_diff = 0

        for i in range(height):
            for j in range(width):
                pixel_diff = abs(frame1[i][j] - frame2[i][j])
                total_diff += pixel_diff
                if pixel_diff > 0:
                    diff_count += 1
                if pixel_diff > max_diff:
                    max_diff = pixel_diff

        avg_diff = total_diff / (height * width) if height * width > 0 else 0
        changed_percentage = (diff_count / (height * width)) * 100 if height * width > 0 else 0

        return {
            "status": "compared",
            "changed_pixels": diff_count,
            "changed_percentage": changed_percentage,
            "average_difference": avg_diff,
            "maximum_difference": max_diff
        }


def create_test_frames(num_frames: int, width: int, height: int) -> List[List[List[int]]]:
    """
    Create a sequence of test frames with controlled motion.

    Args:
        num_frames: Number of frames to create
        width: Frame width
        height: Frame height

    Returns:
        List of frames
    """
    frames = []

    for frame_idx in range(num_frames):
        frame = []
        for i in range(height):
            row = []
            for j in range(width):
                # Create a moving pattern
                pattern_value = int(128 + 100 * math.sin((i + frame_idx * 5) * 0.1) * math.cos((j + frame_idx * 3) * 0.1))
                # Add some noise
                pattern_value += random.randint(-10, 10)
                # Clamp to valid range
                pattern_value = max(0, min(255, pattern_value))
                row.append([pattern_value])  # Grayscale
            frame.append(row)
        frames.append(frame)

    return frames


def create_static_test_frames(num_frames: int, width: int, height: int) -> List[List[List[int]]]:
    """
    Create a sequence of static test frames.

    Args:
        num_frames: Number of frames to create
        width: Frame width
        height: Frame height

    Returns:
        List of frames
    """
    frames = []

    # Create a base pattern
    base_frame = []
    for i in range(height):
        row = []
        for j in range(width):
            # Create a static pattern with different regions
            if 50 < i < 100 and 50 < j < 100:
                value = 200  # Bright square
            elif math.sqrt((i - height//2)**2 + (j - width//2)**2) < 30:
                value = 150  # Circle
            else:
                value = 50   # Dark background
            row.append([value])
        base_frame.append(row)

    # Create multiple frames with the same pattern (static)
    for _ in range(num_frames):
        frames.append(base_frame)

    return frames


def main() -> None:
    """
    Main function demonstrating frame analysis.
    """
    print("Starting frame analysis demonstration for humanoid robot...")
    print("Showing how to analyze visual frames to understand the environment.\n")

    # Initialize the frame sequence analyzer
    sequence_analyzer = FrameSequenceAnalyzer()

    print("Analyzing different frame sequences:")

    # Test 1: Static scene
    print(f"\n1. Analyzing static scene (5 frames)...")
    static_frames = create_static_test_frames(5, 160, 120)
    static_analysis = sequence_analyzer.analyze_sequence(static_frames)

    print(f"   Motion type: {static_analysis['motion_analysis']['motion_type']}")
    print(f"   Average motion magnitude: {static_analysis['motion_analysis']['average_motion_magnitude']:.2f}")
    print(f"   Objects detected: {len(static_analysis['static_objects'])}")

    # Test 2: Moving pattern
    print(f"\n2. Analyzing moving pattern (8 frames)...")
    moving_frames = create_test_frames(8, 160, 120)
    moving_analysis = sequence_analyzer.analyze_sequence(moving_frames)

    print(f"   Motion type: {moving_analysis['motion_analysis']['motion_type']}")
    print(f"   Average motion magnitude: {moving_analysis['motion_analysis']['average_motion_magnitude']:.2f}")
    print(f"   Max motion magnitude: {moving_analysis['motion_analysis']['max_motion_magnitude']:.2f}")
    print(f"   Intensity change rate: {moving_analysis['motion_analysis']['intensity_change_rate']:.2f}")

    # Test 3: Frame comparison
    print(f"\n3. Comparing frames...")
    frame1 = static_frames[0]
    frame2 = moving_frames[0]
    comparison = sequence_analyzer.compare_frames(
        [[p[0] for p in row] for row in frame1],  # Extract grayscale
        [[p[0] for p in row] for row in frame2]
    )
    print(f"   Changed pixels: {comparison['changed_pixels']}")
    print(f"   Changed percentage: {comparison['changed_percentage']:.1f}%")
    print(f"   Average difference: {comparison['average_difference']:.2f}")

    # Detailed analysis of moving frames
    print(f"\n4. Detailed analysis of moving frames:")
    print(f"   Scene statistics:")
    stats = moving_analysis['scene_statistics']
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"     {key}: {value:.2f}")
        else:
            print(f"     {key}: {value}")

    # Object detection in the first moving frame
    print(f"\n5. Object detection in first moving frame:")
    objects = sequence_analyzer.analyzer.detect_objects_in_frame(
        [[p[0] for p in row] for row in moving_frames[0]]
    )
    print(f"   Detected {len(objects)} objects/segments:")
    for i, obj in enumerate(objects[:5]):  # Show first 5
        print(f"     Object {i+1}: pos={obj['position']}, size={obj['size']}, "
              f"shape={obj['shape']}, intensity={obj['intensity']:.1f}")

    # Dynamic scene understanding
    print(f"\n6. Dynamic scene understanding:")
    scene_understanding = sequence_analyzer.get_dynamic_scene_understanding()
    for key, value in scene_understanding.items():
        print(f"   {key}: {value}")

    # Show motion vector analysis
    print(f"\n7. Motion analysis details:")
    motion_analysis = moving_analysis['motion_analysis']
    print(f"   Motion vectors analyzed: {motion_analysis['motion_vectors_count']}")
    print(f"   Average motion: {motion_analysis['average_motion']}")
    print(f"   Motion type: {motion_analysis['motion_type']}")

    # Simulate processing a longer sequence to show temporal patterns
    print(f"\n8. Processing extended sequence (10 frames)...")
    extended_frames = create_test_frames(10, 160, 120)
    extended_analysis = sequence_analyzer.analyze_sequence(extended_frames)

    print(f"   Motion type: {extended_analysis['motion_analysis']['motion_type']}")
    print(f"   Total frames processed: {extended_analysis['motion_analysis']['total_frames']}")
    print(f"   Activity level: {sequence_analyzer.get_dynamic_scene_understanding()['activity_level']}")

    print(f"\nFrame analysis demonstration completed.")
    print("This shows how humanoid robots analyze visual frames to understand")
    print("motion, detect objects, and build a dynamic understanding of their environment.")


if __name__ == "__main__":
    main()