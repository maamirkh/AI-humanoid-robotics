#!/usr/bin/env python3
"""
Human-Robot Interaction Example

This module demonstrates conceptual human-robot interaction patterns for humanoid robots,
showing how robots can recognize human gestures, attention, and intentions.
"""

from typing import Dict, List, Tuple, Optional, Any
import random
import time
import math


class HumanState:
    """
    Represents the state of a human in the interaction space.
    """

    def __init__(self, id: str, position: Tuple[float, float, float],
                 orientation: float, attention_target: Optional[str] = None) -> None:
        self.id = id
        self.position = position  # (x, y, z) in meters
        self.orientation = orientation  # in radians (0 to 2π)
        self.attention_target = attention_target  # What the human is attending to
        self.gesture = "neutral"  # Current gesture (wave, point, etc.)
        self.emotional_state = "neutral"  # happy, sad, angry, neutral
        self.engagement_level = 0.5  # 0.0 to 1.0
        self.last_update = time.time()

    def update_position(self, new_position: Tuple[float, float, float]) -> None:
        """Update the human's position."""
        self.position = new_position
        self.last_update = time.time()

    def update_orientation(self, new_orientation: float) -> None:
        """Update the human's orientation."""
        self.orientation = new_orientation
        self.last_update = time.time()

    def update_gesture(self, gesture: str) -> None:
        """Update the human's gesture."""
        self.gesture = gesture
        self.last_update = time.time()

    def update_attention(self, target: str) -> None:
        """Update what the human is attending to."""
        self.attention_target = target
        self.last_update = time.time()

    def update_emotional_state(self, state: str) -> None:
        """Update the human's emotional state."""
        self.emotional_state = state
        self.last_update = time.time()


class RobotState:
    """
    Represents the state of the robot in the interaction space.
    """

    def __init__(self, position: Tuple[float, float, float], orientation: float) -> None:
        self.position = position  # (x, y, z) in meters
        self.orientation = orientation  # in radians (0 to 2π)
        self.attention_target: Optional[str] = None
        self.intention = "idle"  # idle, approaching, gesturing, speaking
        self.engagement_level = 0.5  # 0.0 to 1.0
        self.last_interaction_time = time.time()

    def update_position(self, new_position: Tuple[float, float, float]) -> None:
        """Update the robot's position."""
        self.position = new_position

    def update_orientation(self, new_orientation: float) -> None:
        """Update the robot's orientation."""
        self.orientation = new_orientation

    def update_intention(self, intention: str) -> None:
        """Update the robot's intention."""
        self.intention = intention
        self.last_interaction_time = time.time()

    def update_attention(self, target: str) -> None:
        """Update what the robot is attending to."""
        self.attention_target = target


class GestureRecognizer:
    """
    Recognizes human gestures and infers intentions.
    """

    def __init__(self) -> None:
        self.known_gestures = {
            "wave": ["arm_raised", "arm_waving"],
            "point": ["arm_extended", "finger_pointing"],
            "beckon": ["arm_bent", "hand_moving_towards_body"],
            "stop": ["palm_facing_forward", "arm_extended"],
            "come_here": ["arm_waving_towards_body", "palm_facing_downward"]
        }
        self.gesture_threshold = 0.7  # Confidence threshold

    def recognize_gesture(self, human_features: Dict[str, Any]) -> Tuple[str, float]:
        """
        Recognize a gesture from human features.

        Args:
            human_features: Dictionary containing detected human features

        Returns:
            Tuple of (gesture_name, confidence_score)
        """
        # Simulate gesture recognition
        # In a real system, this would process visual/depth data

        # Calculate similarity between features and known gestures
        gesture_scores = {}
        for gesture, required_features in self.known_gestures.items():
            matching_features = 0
            total_required = len(required_features)

            for feature in required_features:
                if feature in human_features and human_features[feature]:
                    matching_features += 1

            if total_required > 0:
                score = matching_features / total_required
                gesture_scores[gesture] = score
            else:
                gesture_scores[gesture] = 0.0

        # Find the best matching gesture
        if gesture_scores:
            best_gesture = max(gesture_scores, key=gesture_scores.get)
            best_score = gesture_scores[best_gesture]

            if best_score >= self.gesture_threshold:
                return (best_gesture, best_score)

        return ("neutral", 0.0)

    def infer_intention_from_gesture(self, gesture: str) -> str:
        """
        Infer human intention from recognized gesture.

        Args:
            gesture: Recognized gesture

        Returns:
            Inferred intention
        """
        intention_map = {
            "wave": "greeting",
            "point": "directing_attention",
            "beckon": "requesting_approach",
            "stop": "requesting_halt",
            "come_here": "requesting_approach"
        }

        return intention_map.get(gesture, "unknown")


class AttentionEstimator:
    """
    Estimates where humans are directing their attention.
    """

    def __init__(self) -> None:
        self.head_orientation_weight = 0.7
        self.body_orientation_weight = 0.3

    def estimate_attention(self, human_state: HumanState,
                          objects_in_scene: List[Tuple[str, Tuple[float, float, float]]]) -> str:
        """
        Estimate where the human is directing attention.

        Args:
            human_state: Current state of the human
            objects_in_scene: List of (object_id, position) tuples

        Returns:
            ID of the attended object, or "none" if no clear attention target
        """
        if not objects_in_scene:
            return "none"

        # Calculate where the human is looking based on head and body orientation
        head_orientation = human_state.orientation
        body_orientation = human_state.orientation  # Simplified - in real systems these would be different

        # Combine head and body orientation
        estimated_facing = (head_orientation * self.head_orientation_weight +
                           body_orientation * self.body_orientation_weight)

        # Calculate direction vector from human position
        human_x, human_y, _ = human_state.position
        direction_x = math.cos(estimated_facing)
        direction_y = math.sin(estimated_facing)

        # Find the closest object in the direction of gaze
        closest_object = None
        smallest_angle = float('inf')

        for obj_id, obj_pos in objects_in_scene:
            obj_x, obj_y, _ = obj_pos

            # Calculate vector to object
            to_obj_x = obj_x - human_x
            to_obj_y = obj_y - human_y
            distance_to_obj = math.sqrt(to_obj_x**2 + to_obj_y**2)

            if distance_to_obj == 0:
                continue  # Skip if human is at the same position as object

            # Normalize vector to object
            to_obj_x /= distance_to_obj
            to_obj_y /= distance_to_obj

            # Calculate angle between facing direction and direction to object
            dot_product = direction_x * to_obj_x + direction_y * to_obj_y
            angle = math.acos(max(-1.0, min(1.0, dot_product)))  # Clamp to avoid numerical errors

            # Consider the object if it's within a reasonable angle (45 degrees)
            if angle < math.radians(45) and angle < smallest_angle:
                smallest_angle = angle
                closest_object = obj_id

        return closest_object or "none"


class IntentionInterpreter:
    """
    Interprets human intentions based on multiple cues.
    """

    def __init__(self) -> None:
        self.gesture_recognizer = GestureRecognizer()
        self.attention_estimator = AttentionEstimator()
        self.intention_confidence_threshold = 0.6

    def interpret_intention(self, human_state: HumanState,
                           robot_state: RobotState,
                           objects_in_scene: List[Tuple[str, Tuple[float, float, float]]]) -> Tuple[str, float]:
        """
        Interpret human intention based on multiple cues.

        Args:
            human_state: Current state of the human
            robot_state: Current state of the robot
            objects_in_scene: List of objects in the scene

        Returns:
            Tuple of (intention, confidence_score)
        """
        # Simulate feature extraction from sensors
        human_features = self._extract_features(human_state, robot_state, objects_in_scene)

        # Recognize gesture
        gesture, gesture_confidence = self.gesture_recognizer.recognize_gesture(human_features)

        # Estimate attention target
        attention_target = self.attention_estimator.estimate_attention(human_state, objects_in_scene)

        # Combine multiple cues to determine intention
        intention_scores = self._combine_cues(
            gesture, gesture_confidence, attention_target, human_state, robot_state
        )

        # Return the intention with highest confidence
        if intention_scores:
            best_intention = max(intention_scores, key=intention_scores.get)
            best_score = intention_scores[best_intention]

            if best_score >= self.intention_confidence_threshold:
                return (best_intention, best_score)

        return ("unknown", 0.0)

    def _extract_features(self, human_state: HumanState, robot_state: RobotState,
                         objects_in_scene: List[Tuple[str, Tuple[float, float, float]]]) -> Dict[str, bool]:
        """Extract relevant features from the scene."""
        features = {}

        # Simulate extracted features (in reality, these would come from perception systems)
        # For demonstration, we'll randomly generate some features based on the scenario
        distance_to_robot = math.sqrt(
            (human_state.position[0] - robot_state.position[0])**2 +
            (human_state.position[1] - robot_state.position[1])**2
        )

        # Generate features based on context
        features["arm_raised"] = random.random() < 0.3
        features["arm_waving"] = random.random() < 0.2
        features["arm_extended"] = random.random() < 0.25
        features["finger_pointing"] = random.random() < 0.15
        features["palm_facing_forward"] = random.random() < 0.1
        features["palm_facing_downward"] = random.random() < 0.1
        features["arm_waving_towards_body"] = random.random() < 0.1
        features["arm_bent"] = random.random() < 0.2

        # Add context-dependent features
        features["close_to_robot"] = distance_to_robot < 1.0
        features["facing_robot"] = abs(human_state.orientation - robot_state.orientation) < math.pi/3

        return features

    def _combine_cues(self, gesture: str, gesture_confidence: float, attention_target: str,
                     human_state: HumanState, robot_state: RobotState) -> Dict[str, float]:
        """Combine multiple cues to determine intention scores."""
        intention_scores = {
            "greeting": 0.1,
            "requesting_help": 0.1,
            "requesting_approach": 0.1,
            "directing_attention": 0.1,
            "ending_interaction": 0.1,
            "unknown": 0.1
        }

        # Boost score based on recognized gesture
        if gesture != "neutral":
            gesture_intention = self.gesture_recognizer.infer_intention_from_gesture(gesture)
            if gesture_intention in intention_scores:
                intention_scores[gesture_intention] += gesture_confidence * 0.8

        # Adjust based on attention target
        if attention_target == "robot":
            intention_scores["requesting_help"] += 0.2
            intention_scores["greeting"] += 0.15
        elif attention_target == "object":
            intention_scores["directing_attention"] += 0.3

        # Adjust based on emotional state
        if human_state.emotional_state == "happy":
            intention_scores["greeting"] += 0.2
        elif human_state.emotional_state == "frustrated":
            intention_scores["requesting_help"] += 0.3

        # Adjust based on engagement level
        for intention in intention_scores:
            intention_scores[intention] *= human_state.engagement_level

        # Normalize scores to 0-1 range
        max_score = max(intention_scores.values())
        if max_score > 0:
            for intention in intention_scores:
                intention_scores[intention] /= max_score

        return intention_scores


class InteractionManager:
    """
    Manages the human-robot interaction loop.
    """

    def __init__(self) -> None:
        self.intention_interpreter = IntentionInterpreter()
        self.interaction_history: List[Dict[str, Any]] = []
        self.current_interaction_state = "idle"

    def process_interaction(self, human_state: HumanState, robot_state: RobotState,
                           objects_in_scene: List[Tuple[str, Tuple[float, float, float]]]) -> str:
        """
        Process the interaction and determine robot response.

        Args:
            human_state: Current state of the human
            robot_state: Current state of the robot
            objects_in_scene: List of objects in the scene

        Returns:
            Robot action to perform
        """
        # Interpret human intention
        intention, confidence = self.intention_interpreter.interpret_intention(
            human_state, robot_state, objects_in_scene
        )

        # Determine appropriate response based on intention
        response = self._determine_response(intention, confidence, human_state, robot_state)

        # Record the interaction
        interaction_record = {
            "timestamp": time.time(),
            "human_state": human_state.__dict__.copy(),
            "robot_state": robot_state.__dict__.copy(),
            "interpreted_intention": intention,
            "confidence": confidence,
            "robot_response": response
        }
        self.interaction_history.append(interaction_record)

        return response

    def _determine_response(self, intention: str, confidence: float,
                           human_state: HumanState, robot_state: RobotState) -> str:
        """Determine appropriate robot response based on interpreted intention."""
        # Set minimum confidence threshold
        if confidence < self.intention_interpreter.intention_confidence_threshold:
            return "wait_and_observe"

        # Respond based on intention
        if intention == "greeting":
            return "greet_back"
        elif intention == "requesting_approach":
            return "approach_human"
        elif intention == "requesting_help":
            return "offer_assistance"
        elif intention == "directing_attention":
            return "look_at_target"
        elif intention == "ending_interaction":
            return "acknowledge_end"
        else:
            return "wait_and_observe"

    def get_interaction_feedback(self) -> Dict[str, Any]:
        """Get feedback about the interaction."""
        if not self.interaction_history:
            return {"status": "no_interactions", "history_length": 0}

        # Analyze interaction history
        recent_interactions = self.interaction_history[-5:]  # Last 5 interactions
        intentions = [record["interpreted_intention"] for record in recent_interactions]
        responses = [record["robot_response"] for record in recent_interactions]
        confidences = [record["confidence"] for record in recent_interactions]

        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        return {
            "status": "active",
            "history_length": len(self.interaction_history),
            "recent_intentions": intentions,
            "recent_responses": responses,
            "average_confidence": avg_confidence,
            "current_state": self.current_interaction_state
        }


def main() -> None:
    """
    Main function demonstrating human-robot interaction.
    """
    print("Starting human-robot interaction demonstration...")
    print("Showing how robots recognize gestures, attention, and intentions.\n")

    # Initialize the interaction manager
    interaction_manager = InteractionManager()

    # Create initial human and robot states
    human = HumanState(
        id="person_1",
        position=(1.5, 0.0, 0.0),
        orientation=math.pi,  # Facing robot (180 degrees)
        attention_target="robot"
    )

    robot = RobotState(
        position=(0.0, 0.0, 0.0),
        orientation=0.0  # Facing human
    )

    # Define objects in the scene
    objects_in_scene = [
        ("table", (2.0, 1.0, 0.0)),
        ("chair", (2.5, -1.0, 0.0)),
        ("robot", robot.position)  # Robot itself is an object
    ]

    print("Initial state:")
    print(f"  Human: pos={human.position}, orientation={human.orientation:.2f}, gesture={human.gesture}")
    print(f"  Robot: pos={robot.position}, orientation={robot.orientation:.2f}, intention={robot.intention}")
    print(f"  Objects: {[obj[0] for obj in objects_in_scene]}")
    print()

    # Simulate several interaction cycles
    print("Simulating interaction scenarios:")

    for cycle in range(8):
        print(f"\nInteraction Cycle {cycle + 1}:")

        # Update human state based on the scenario
        if cycle == 0:
            print("  Scenario: Human waves to get robot's attention")
            human.update_gesture("wave")
            human.update_emotional_state("happy")
        elif cycle == 1:
            print("  Scenario: Human points to an object")
            human.update_gesture("point")
            human.update_attention("table")
        elif cycle == 2:
            print("  Scenario: Human beckons robot to approach")
            human.update_gesture("beckon")
            human.update_emotional_state("neutral")
        elif cycle == 3:
            print("  Scenario: Human shows frustrated expression")
            human.update_gesture("stop")
            human.update_emotional_state("frustrated")
            human.update_attention("robot")
        elif cycle == 4:
            print("  Scenario: Human makes come-here gesture")
            human.update_gesture("come_here")
            human.update_emotional_state("neutral")
        elif cycle == 5:
            print("  Scenario: Human turns away (ending interaction)")
            human.update_orientation(math.pi/2)  # Turn sideways
            human.update_attention("none")
        elif cycle == 6:
            print("  Scenario: Human waves goodbye")
            human.update_gesture("wave")
            human.update_orientation(math.pi)  # Turn back
            human.update_emotional_state("happy")
        elif cycle == 7:
            print("  Scenario: Human stands neutral")
            human.update_gesture("neutral")
            human.update_emotional_state("neutral")

        # Process the interaction
        robot_response = interaction_manager.process_interaction(
            human, robot, objects_in_scene
        )

        print(f"  Interpreted intention: {interaction_manager.interaction_history[-1]['interpreted_intention']}")
        print(f"  Intention confidence: {interaction_manager.interaction_history[-1]['confidence']:.2f}")
        print(f"  Robot response: {robot_response}")

        # Update robot state based on response
        if robot_response == "greet_back":
            robot.update_intention("greeting")
        elif robot_response == "approach_human":
            robot.update_intention("approaching")
            # Simulate approaching by updating position
            robot.update_position((
                human.position[0] * 0.7,  # Move closer but not too close
                human.position[1] * 0.7,
                robot.position[2]
            ))
        elif robot_response == "look_at_target":
            robot.update_attention("table")
        elif robot_response == "offer_assistance":
            robot.update_intention("assisting")
        elif robot_response == "acknowledge_end":
            robot.update_intention("acknowledging_end")

    print(f"\nInteraction summary:")
    feedback = interaction_manager.get_interaction_feedback()
    print(f"  Total interactions processed: {feedback['history_length']}")
    print(f"  Average intention confidence: {feedback['average_confidence']:.2f}")
    print(f"  Most common responses: {set(feedback['recent_responses'])}")

    print(f"\nHRI demonstration completed.")
    print("This shows how humanoid robots can recognize human gestures,")
    print("interpret intentions, and respond appropriately in social contexts.")


if __name__ == "__main__":
    main()