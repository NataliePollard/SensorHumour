"""
Pattern Tool - Create and modify Canopy LED patterns

This tool helps you:
1. Decode CTP-encoded patterns to human-readable JSON
2. Modify palettes and colors
3. Encode modified patterns back to CTP format for use in code

Usage:
    from pattern_tool import PatternTool

    tool = PatternTool()

    # Decode a pattern
    decoded = tool.decode_pattern(ctp_string)
    print(decoded)

    # Modify a palette and create new pattern
    new_pattern = tool.create_pattern_with_palette(
        base_pattern_ctp,
        new_palette_name="primary",
        new_colors=[
            (0.01, (0.5, 0.5, 0.5)),  # (position, (r, g, b))
            (0.5, (1.0, 1.0, 0.0)),
            (0.99, (0.0, 0.0, 0.0)),
        ]
    )
    print(f"New pattern CTP: {new_pattern}")
"""

import base64
import json
from typing import Dict, List, Tuple, Any


class PatternTool:
    """Tool for encoding/decoding and modifying Canopy patterns"""

    @staticmethod
    def decode_pattern(ctp_string: str) -> Dict[str, Any]:
        """
        Decode a CTP-encoded pattern string to JSON

        Args:
            ctp_string: Pattern string starting with "CTP-"

        Returns:
            Decoded pattern as dictionary
        """
        if not ctp_string.startswith("CTP-"):
            raise ValueError("Pattern must start with 'CTP-'")

        # Remove "CTP-" prefix
        encoded_json = ctp_string[4:]

        # Add padding if needed for base64 decoding
        if len(encoded_json) % 4 != 0:
            encoded_json += '=' * (4 - len(encoded_json) % 4)

        # Decode from base64
        decoded_json = base64.b64decode(encoded_json).decode('utf-8')

        # Parse as JSON
        return json.loads(decoded_json)

    @staticmethod
    def encode_pattern(pattern_dict: Dict[str, Any]) -> str:
        """
        Encode a pattern dictionary back to CTP format

        Args:
            pattern_dict: Pattern as dictionary

        Returns:
            CTP-encoded pattern string
        """
        # Convert to JSON string (no spaces for compact encoding)
        json_str = json.dumps(pattern_dict, separators=(',', ':'))

        # Encode to base64
        encoded = base64.b64encode(json_str.encode('utf-8')).decode('ascii')

        # Add CTP prefix
        return f"CTP-{encoded}"

    @staticmethod
    def print_pattern(pattern_dict: Dict[str, Any]) -> None:
        """Pretty print a decoded pattern"""
        print(json.dumps(pattern_dict, indent=2))

    @staticmethod
    def create_pattern_with_palette(
        base_ctp: str,
        palette_name: str,
        new_colors: List[Tuple[float, Tuple[float, float, float]]]
    ) -> str:
        """
        Create a new pattern based on an existing one with a modified palette

        Args:
            base_ctp: Base pattern CTP string
            palette_name: Name of palette to modify (usually "primary")
            new_colors: List of (position, (r, g, b)) tuples
                       Position ranges 0.0-1.0
                       RGB values range 0.0-1.0

        Returns:
            New CTP-encoded pattern string

        Example:
            new_pattern = tool.create_pattern_with_palette(
                PATTERN_RED,
                "primary",
                [
                    (0.01, (0.0, 1.0, 0.0)),  # Green at start
                    (0.52, (0.5, 1.0, 0.0)),  # Yellow-green middle
                    (0.99, (0.0, 0.0, 0.0)),  # Black at end
                ]
            )
        """
        # Decode the base pattern
        pattern = PatternTool.decode_pattern(base_ctp)

        # Convert color list to the format expected by the palette
        color_stops = [[pos, list(rgb)] for pos, rgb in new_colors]

        # Update the palette
        if "palettes" not in pattern:
            pattern["palettes"] = {}

        pattern["palettes"][palette_name] = color_stops

        # Re-encode and return
        return PatternTool.encode_pattern(pattern)

    @staticmethod
    def modify_pattern_property(
        base_ctp: str,
        path: str,
        value: Any
    ) -> str:
        """
        Modify a specific property in a pattern

        Args:
            base_ctp: Base pattern CTP string
            path: Dot-separated path to property (e.g., "params.speed" or "palettes.primary")
            value: New value for the property

        Returns:
            Modified CTP-encoded pattern string

        Example:
            # Change speed parameter
            new_pattern = tool.modify_pattern_property(PATTERN_RED, "params.speed", 0.2)

            # Change opacity of first layer
            new_pattern = tool.modify_pattern_property(
                PATTERN_RED,
                "layers.0.opacity",
                0.5
            )
        """
        pattern = PatternTool.decode_pattern(base_ctp)

        # Navigate and modify using dot notation
        keys = path.split('.')
        obj = pattern

        # Navigate to parent of target property
        for key in keys[:-1]:
            # Handle array indices like "layers.0"
            if key.isdigit():
                obj = obj[int(key)]
            else:
                if key not in obj:
                    obj[key] = {}
                obj = obj[key]

        # Set the final property
        final_key = keys[-1]
        if final_key.isdigit():
            obj[int(final_key)] = value
        else:
            obj[final_key] = value

        return PatternTool.encode_pattern(pattern)

    @staticmethod
    def create_gradient_pattern(
        name: str,
        key: str,
        colors: List[Tuple[float, Tuple[float, float, float]]],
        speed: float = 0.1,
        density_value: float = 0.5,
        opacity: float = 0.24
    ) -> str:
        """
        Create a gradient pattern from scratch

        Args:
            name: Pattern name
            key: Pattern key
            colors: List of (position, (r, g, b)) tuples
            speed: Animation speed (default 0.1)
            density_value: Density value for variation (0.0-1.0, default 0.5)
            opacity: Layer opacity (default 0.24)

        Returns:
            CTP-encoded pattern string
        """
        # Convert colors to palette format
        color_stops = [[pos, list(rgb)] for pos, rgb in colors]

        pattern = {
            "key": key,
            "version": 0,
            "name": name,
            "palettes": {
                "primary": color_stops,
                "_black-white": [
                    [0, [0, 0, 0]],
                    [1, [1, 1, 1]]
                ]
            },
            "params": {
                "size": "speed",
                "speed": speed,
                "density": {
                    "type": "rsaw",
                    "inputs": {
                        "value": density_value,
                        "min": 0,
                        "max": 1
                    }
                }
            },
            "layers": [
                {
                    "effect": "gradient",
                    "opacity": opacity,
                    "blend": "normal",
                    "palette": "primary",
                    "inputs": {
                        "offset": "density",
                        "size": 0.5,
                        "rotation": 0
                    }
                }
            ]
        }

        return PatternTool.encode_pattern(pattern)


if __name__ == "__main__":
    # Example usage
    tool = PatternTool()

    # Example 1: Decode a pattern
    print("=" * 60)
    print("Example 1: Decoding PATTERN_RED")
    print("=" * 60)
    PATTERN_RED_CTP = "CTP-eyJrZXkiOiJyZWQtZmxvdyIsInZlcnNpb24iOjAsIm5hbWUiOiJyZWQtZmxvdyIsInBhbGV0dGVzIjp7InByaW1hcnkiOltbMC4wMSxbMSwwLDBdXSxbMC41MixbMC45MjE1Njg2Mjc0NTA5ODAzLDAuMTI5NDExNzY0NzA1ODgyMzcsMC41MzcyNTQ5MDE5NjA3ODQzXV0sWzAuOTksWzAsMCwwXV1dLCJfYmxhY2std2hpdGUiOltbMCxbMCwwLDBdXSxbMSxbMSwxLDFdXV19LCJwYXJhbXMiOnsic2l6ZSI6InNwZWVkIiwic3BlZWQiOjAuMSwiZGVuc2l0eSI6eyJ0eXBlIjoicnNhdyIsImlucHV0cyI6eyJ2YWx1ZSI6MC41LCJtaW4iOjAsIm1heCI6MX19fSwibGF5ZXJzIjpbeyJlZmZlY3QiOiJncmFkaWVudCIsIm9wYWNpdHkiOjAuMjQsImJsZW5kIjoibm9ybWFsIiwicGFsZXR0ZSI6InByaW1hcnkiLCJpbnB1dHMiOnsib2Zmc2V0IjoiZGVuc2l0eSIsInNpemUiOjAuNSwicm90YXRpb24iOjB9fV19"
    decoded = tool.decode_pattern(PATTERN_RED_CTP)
    tool.print_pattern(decoded)

    # Example 2: Create a green pattern from red template
    print("\n" + "=" * 60)
    print("Example 2: Creating GREEN pattern from RED template")
    print("=" * 60)
    green_colors = [
        (0.01, (0.0, 1.0, 0.0)),      # Pure green start
        (0.52, (0.5, 1.0, 0.3)),      # Yellow-green middle
        (0.99, (0.0, 0.0, 0.0)),      # Black end
    ]
    green_pattern = tool.create_pattern_with_palette(
        PATTERN_RED_CTP,
        "primary",
        green_colors
    )
    print(f"Green pattern CTP:\n{green_pattern}\n")

    # Verify it decodes correctly
    print("Decoded green pattern:")
    tool.print_pattern(tool.decode_pattern(green_pattern))

    # Example 3: Create a custom pattern from scratch
    print("\n" + "=" * 60)
    print("Example 3: Creating custom CYAN pattern from scratch")
    print("=" * 60)
    cyan_pattern = tool.create_gradient_pattern(
        name="cyan-flow",
        key="cyan-flow",
        colors=[
            (0.01, (0.0, 1.0, 1.0)),   # Cyan start
            (0.52, (0.0, 0.7, 0.8)),   # Darker cyan middle
            (0.99, (0.0, 0.0, 0.0)),   # Black end
        ],
        speed=0.1,
        density_value=0.5,
        opacity=0.24
    )
    print(f"Cyan pattern CTP:\n{cyan_pattern}\n")
    print("Decoded cyan pattern:")
    tool.print_pattern(tool.decode_pattern(cyan_pattern))
