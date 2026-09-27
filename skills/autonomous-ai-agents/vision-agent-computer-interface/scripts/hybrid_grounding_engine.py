#!/usr/bin/env python3
"""
Hybrid Grounding Engine for Vision-Language Agent-Computer Interfaces (ACI).
Fuses Accessibility DOM Tree (AXTree) with visual bounding box detections.
Author: Bagas Cihuy & Hermes Agent
"""

import sys
import math
import json
import argparse
from typing import List, Dict, Any, Tuple, Optional

def calculate_box_center(box: List[float]) -> Tuple[float, float]:
    """Calculate (x_center, y_center) from [x, y, width, height]."""
    return (box[0] + box[2] / 2.0, box[1] + box[3] / 2.0)

def calculate_iou(box_a: List[float], box_b: List[float]) -> float:
    """Calculate Intersection over Union (IoU) between two bounding boxes."""
    xA = max(box_a[0], box_b[0])
    yA = max(box_a[1], box_b[1])
    xB = min(box_a[0] + box_a[2], box_b[0] + box_b[2])
    yB = min(box_a[1] + box_a[3], box_b[1] + box_b[3])

    inter_width = max(0.0, xB - xA)
    inter_height = max(0.0, yB - yA)
    inter_area = inter_width * inter_height

    area_a = box_a[2] * box_a[3]
    area_b = box_b[2] * box_b[3]
    union_area = area_a + area_b - inter_area

    if union_area <= 0.0:
        return 0.0
    return inter_area / union_area

class HybridGroundingEngine:
    def __init__(self, viewport: Tuple[int, int] = (1920, 1080), spatial_threshold_px: float = 48.0):
        self.viewport = viewport
        self.spatial_threshold = spatial_threshold_px

    def resolve_target(
        self,
        intent: str,
        ax_nodes: List[Dict[str, Any]],
        visual_candidates: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """
        Fuses AX tree semantics with visual candidate spatial bounding boxes.
        Returns ranked candidate targets with calculated confidence scores.
        """
        visual_candidates = visual_candidates or []
        intent_lower = intent.lower()
        intent_tokens = set(intent_lower.split())

        candidates = []

        for node in ax_nodes:
            name = str(node.get("name", "")).strip().lower()
            role = str(node.get("role", "")).strip().lower()
            box = node.get("box")  # [x, y, w, h]

            if not box or len(box) != 4:
                continue

            # Semantic match scoring
            semantic_score = 0.0
            if intent_lower == name:
                semantic_score = 0.65
            elif intent_lower in name:
                semantic_score = 0.50
            else:
                name_tokens = set(name.split())
                overlap = intent_tokens.intersection(name_tokens)
                if overlap:
                    semantic_score = 0.35 * (len(overlap) / max(1, len(intent_tokens)))

            # Role bonus for interactive affordances
            role_bonus = 0.0
            if role in ["button", "link", "combobox", "searchbox", "textbox", "checkbox", "menuitem"]:
                role_bonus = 0.15

            base_confidence = semantic_score + role_bonus
            if base_confidence <= 0.10:
                continue

            # Correlate with visual bounding boxes
            node_center = calculate_box_center(box)
            best_vis_dist = float("inf")
            best_vis = None
            best_iou = 0.0

            for vis in visual_candidates:
                vis_box = vis.get("box", [0, 0, 0, 0])
                vis_center = calculate_box_center(vis_box)
                dist = math.hypot(node_center[0] - vis_center[0], node_center[1] - vis_center[1])
                iou = calculate_iou(box, vis_box)

                if dist < best_vis_dist:
                    best_vis_dist = dist
                    best_vis = vis
                    best_iou = iou

            visual_bonus = 0.0
            grounding_mode = "ax_structural"

            if best_vis and best_vis_dist <= self.spatial_threshold:
                # Proximity score decay
                proximity_factor = 1.0 - (best_vis_dist / self.spatial_threshold)
                iou_factor = best_iou
                visual_bonus = 0.25 * proximity_factor + 0.15 * iou_factor
                grounding_mode = "hybrid_ax_vision"

            final_confidence = min(1.0, base_confidence + visual_bonus)

            candidates.append({
                "target_name": node.get("name"),
                "role": role,
                "box": box,
                "click_coordinate": [round(node_center[0], 1), round(node_center[1], 1)],
                "confidence": round(final_confidence, 4),
                "grounding_mode": grounding_mode,
                "iou_overlap": round(best_iou, 4) if best_vis else 0.0
            })

        # Rank by confidence descending
        candidates.sort(key=lambda c: c["confidence"], reverse=True)
        return candidates

def run_self_test():
    engine = HybridGroundingEngine(viewport=(1920, 1080))
    
    mock_ax = [
        {"id": "btn-1", "role": "button", "name": "Proceed to Checkout", "box": [1450, 60, 160, 42]},
        {"id": "btn-2", "role": "link", "name": "View Basket", "box": [1320, 60, 100, 42]},
        {"id": "txt-1", "role": "heading", "name": "Checkout Cart Summary", "box": [240, 120, 450, 48]}
    ]

    mock_vis = [
        {"label": "button", "box": [1448, 58, 164, 46], "confidence": 0.94},
        {"label": "link", "box": [1318, 62, 104, 38], "confidence": 0.82}
    ]

    results = engine.resolve_target("Proceed to Checkout", mock_ax, mock_vis)
    assert len(results) > 0, "Self-test failed: No candidate resolved."
    top = results[0]
    assert top["target_name"] == "Proceed to Checkout"
    assert top["confidence"] >= 0.85, f"Self-test failed: Low confidence {top['confidence']}"
    assert top["grounding_mode"] == "hybrid_ax_vision", "Self-test failed: Mode mismatch."
    assert top["click_coordinate"] == [1530.0, 81.0], "Self-test failed: Incorrect coordinate calculation."

    print("HYBRID GROUNDING VERIFIED: 100% Tests Passed.")
    print(json.dumps(results[:2], indent=2))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hybrid Grounding Engine for ACI")
    parser.add_argument("--test", action="store_true", help="Run internal validation suite")
    parser.add_argument("--intent", type=str, default="Checkout", help="Target action intent")
    args = parser.parse_args()

    if args.test:
        run_self_test()
    else:
        print(f"Executing intent resolution for: '{args.intent}'")
        engine = HybridGroundingEngine()
        res = engine.resolve_target(args.intent, [], [])
        print(json.dumps(res, indent=2))
