"""
Scenario Presets Module

Provides deterministic scenario definitions for Training & Simulation Mode.
All scenarios are completely deterministic - no randomness, same geometry on every reload.

ADVISORY ONLY — VISUAL SIMULATION
- No fire / launch / engage commands
- No ROE logic
- No autonomy
- No while True loops
- No time.sleep
- No uncontrolled reruns
- No randomness per rerun

KINEMATIC OBJECTS ONLY:
- Targets are NOT agents - they do NOT react, decide, or change behavior autonomously
- Pure kinematic motion: position(t) = initial_position + velocity × Δt
- Motion updates only on Streamlit rerun OR Plotly animation frames
- Δt derived from session timestamp
- Motion is slow, smooth, professional
- No acceleration unless explicitly defined in scenario
"""

from typing import List, Dict, Any
import math


class ScenarioPresets:
    """
    Deterministic scenario presets for training and simulation.
    
    Each scenario defines:
    - Initial positions (x, y, z in meters)
    - Velocities (vx, vy, vz in m/s)
    - Altitudes (meters)
    - Classifications (Friendly / Hostile / Unknown)
    - Object types (AIRCRAFT / AERIAL_DRONE / UNKNOWN_OBJECT)
    """
    
    SCENARIOS = {
        "civil_air_traffic": {
            "name": "Civil Air Traffic (All Friendly)",
            "description": "4 aircraft with stable parallel trajectories",
            "tracks": [
                {
                    "track_id": "CIV_001",
                    "object_type": "AIRCRAFT",
                    "position": {"x": -20000.0, "y": 15000.0, "z": 10000.0},
                    "velocity": {"vx": 200.0, "vy": 0.0, "vz": 0.0},
                    "altitude_meters": 10000.0,
                    "classification": "FRIENDLY",
                    "threat_level": "NONE",
                    "confidence": 0.95
                },
                {
                    "track_id": "CIV_002",
                    "object_type": "AIRCRAFT",
                    "position": {"x": -20000.0, "y": 5000.0, "z": 10000.0},
                    "velocity": {"vx": 200.0, "vy": 0.0, "vz": 0.0},
                    "altitude_meters": 10000.0,
                    "classification": "FRIENDLY",
                    "threat_level": "NONE",
                    "confidence": 0.95
                },
                {
                    "track_id": "CIV_003",
                    "object_type": "AIRCRAFT",
                    "position": {"x": -20000.0, "y": -5000.0, "z": 10000.0},
                    "velocity": {"vx": 200.0, "vy": 0.0, "vz": 0.0},
                    "altitude_meters": 10000.0,
                    "classification": "FRIENDLY",
                    "threat_level": "NONE",
                    "confidence": 0.95
                },
                {
                    "track_id": "CIV_004",
                    "object_type": "AIRCRAFT",
                    "position": {"x": -20000.0, "y": -15000.0, "z": 10000.0},
                    "velocity": {"vx": 200.0, "vy": 0.0, "vz": 0.0},
                    "altitude_meters": 10000.0,
                    "classification": "FRIENDLY",
                    "threat_level": "NONE",
                    "confidence": 0.95
                }
            ]
        },
        "mixed_airspace": {
            "name": "Mixed Airspace (1 Hostile)",
            "description": "3 friendly aircraft, 1 hostile aircraft deviating course",
            "tracks": [
                {
                    "track_id": "FRD_001",
                    "object_type": "AIRCRAFT",
                    "position": {"x": -25000.0, "y": 20000.0, "z": 12000.0},
                    "velocity": {"vx": 180.0, "vy": 0.0, "vz": 0.0},
                    "altitude_meters": 12000.0,
                    "classification": "FRIENDLY",
                    "threat_level": "NONE",
                    "confidence": 0.92
                },
                {
                    "track_id": "FRD_002",
                    "object_type": "AIRCRAFT",
                    "position": {"x": -25000.0, "y": 0.0, "z": 12000.0},
                    "velocity": {"vx": 180.0, "vy": 0.0, "vz": 0.0},
                    "altitude_meters": 12000.0,
                    "classification": "FRIENDLY",
                    "threat_level": "NONE",
                    "confidence": 0.92
                },
                {
                    "track_id": "FRD_003",
                    "object_type": "AIRCRAFT",
                    "position": {"x": -25000.0, "y": -20000.0, "z": 12000.0},
                    "velocity": {"vx": 180.0, "vy": 0.0, "vz": 0.0},
                    "altitude_meters": 12000.0,
                    "classification": "FRIENDLY",
                    "threat_level": "NONE",
                    "confidence": 0.92
                },
                {
                    "track_id": "HST_001",
                    "object_type": "AIRCRAFT",
                    "position": {"x": -30000.0, "y": 10000.0, "z": 8000.0},
                    "velocity": {"vx": 250.0, "vy": -50.0, "vz": -5.0},  # Deviating course
                    "altitude_meters": 8000.0,
                    "classification": "HOSTILE",
                    "threat_level": "HIGH",
                    "confidence": 0.75
                }
            ]
        },
        "drone_swarm": {
            "name": "Drone Swarm",
            "description": "8-12 low-altitude drones with grouped vectors and slight spread",
            "tracks": [
                {
                    "track_id": "DRN_001",
                    "object_type": "AERIAL_DRONE",
                    "position": {"x": -15000.0, "y": 5000.0, "z": 500.0},
                    "velocity": {"vx": 30.0, "vy": 10.0, "vz": 0.0},
                    "altitude_meters": 500.0,
                    "classification": "UNKNOWN",
                    "threat_level": "MEDIUM",
                    "confidence": 0.70
                },
                {
                    "track_id": "DRN_002",
                    "object_type": "AERIAL_DRONE",
                    "position": {"x": -15000.0, "y": 6000.0, "z": 500.0},
                    "velocity": {"vx": 30.0, "vy": 10.0, "vz": 0.0},
                    "altitude_meters": 500.0,
                    "classification": "UNKNOWN",
                    "threat_level": "MEDIUM",
                    "confidence": 0.70
                },
                {
                    "track_id": "DRN_003",
                    "object_type": "AERIAL_DRONE",
                    "position": {"x": -15000.0, "y": 4000.0, "z": 500.0},
                    "velocity": {"vx": 30.0, "vy": 10.0, "vz": 0.0},
                    "altitude_meters": 500.0,
                    "classification": "UNKNOWN",
                    "threat_level": "MEDIUM",
                    "confidence": 0.70
                },
                {
                    "track_id": "DRN_004",
                    "object_type": "AERIAL_DRONE",
                    "position": {"x": -16000.0, "y": 5500.0, "z": 500.0},
                    "velocity": {"vx": 30.0, "vy": 10.0, "vz": 0.0},
                    "altitude_meters": 500.0,
                    "classification": "UNKNOWN",
                    "threat_level": "MEDIUM",
                    "confidence": 0.70
                },
                {
                    "track_id": "DRN_005",
                    "object_type": "AERIAL_DRONE",
                    "position": {"x": -16000.0, "y": 4500.0, "z": 500.0},
                    "velocity": {"vx": 30.0, "vy": 10.0, "vz": 0.0},
                    "altitude_meters": 500.0,
                    "classification": "UNKNOWN",
                    "threat_level": "MEDIUM",
                    "confidence": 0.70
                },
                {
                    "track_id": "DRN_006",
                    "object_type": "AERIAL_DRONE",
                    "position": {"x": -14000.0, "y": 5500.0, "z": 500.0},
                    "velocity": {"vx": 30.0, "vy": 10.0, "vz": 0.0},
                    "altitude_meters": 500.0,
                    "classification": "UNKNOWN",
                    "threat_level": "MEDIUM",
                    "confidence": 0.70
                },
                {
                    "track_id": "DRN_007",
                    "object_type": "AERIAL_DRONE",
                    "position": {"x": -14000.0, "y": 4500.0, "z": 500.0},
                    "velocity": {"vx": 30.0, "vy": 10.0, "vz": 0.0},
                    "altitude_meters": 500.0,
                    "classification": "UNKNOWN",
                    "threat_level": "MEDIUM",
                    "confidence": 0.70
                },
                {
                    "track_id": "DRN_008",
                    "object_type": "AERIAL_DRONE",
                    "position": {"x": -15000.0, "y": 3500.0, "z": 500.0},
                    "velocity": {"vx": 30.0, "vy": 10.0, "vz": 0.0},
                    "altitude_meters": 500.0,
                    "classification": "UNKNOWN",
                    "threat_level": "MEDIUM",
                    "confidence": 0.70
                },
                {
                    "track_id": "DRN_009",
                    "object_type": "AERIAL_DRONE",
                    "position": {"x": -15000.0, "y": 7000.0, "z": 500.0},
                    "velocity": {"vx": 30.0, "vy": 10.0, "vz": 0.0},
                    "altitude_meters": 500.0,
                    "classification": "UNKNOWN",
                    "threat_level": "MEDIUM",
                    "confidence": 0.70
                },
                {
                    "track_id": "DRN_010",
                    "object_type": "AERIAL_DRONE",
                    "position": {"x": -15500.0, "y": 5000.0, "z": 500.0},
                    "velocity": {"vx": 30.0, "vy": 10.0, "vz": 0.0},
                    "altitude_meters": 500.0,
                    "classification": "UNKNOWN",
                    "threat_level": "MEDIUM",
                    "confidence": 0.70
                }
            ]
        },
        "saturation_test": {
            "name": "Saturation Test (Advanced)",
            "description": "2 aircraft and 6 drones at different altitudes",
            "tracks": [
                {
                    "track_id": "ACR_001",
                    "object_type": "AIRCRAFT",
                    "position": {"x": -22000.0, "y": 12000.0, "z": 11000.0},
                    "velocity": {"vx": 220.0, "vy": 0.0, "vz": 0.0},
                    "altitude_meters": 11000.0,
                    "classification": "FRIENDLY",
                    "threat_level": "LOW",
                    "confidence": 0.88
                },
                {
                    "track_id": "ACR_002",
                    "object_type": "AIRCRAFT",
                    "position": {"x": -22000.0, "y": -12000.0, "z": 13000.0},
                    "velocity": {"vx": 220.0, "vy": 0.0, "vz": 0.0},
                    "altitude_meters": 13000.0,
                    "classification": "FRIENDLY",
                    "threat_level": "LOW",
                    "confidence": 0.88
                },
                {
                    "track_id": "DRN_A1",
                    "object_type": "AERIAL_DRONE",
                    "position": {"x": -18000.0, "y": 8000.0, "z": 800.0},
                    "velocity": {"vx": 25.0, "vy": 5.0, "vz": 0.0},
                    "altitude_meters": 800.0,
                    "classification": "UNKNOWN",
                    "threat_level": "MEDIUM",
                    "confidence": 0.65
                },
                {
                    "track_id": "DRN_A2",
                    "object_type": "AERIAL_DRONE",
                    "position": {"x": -18000.0, "y": 9000.0, "z": 800.0},
                    "velocity": {"vx": 25.0, "vy": 5.0, "vz": 0.0},
                    "altitude_meters": 800.0,
                    "classification": "UNKNOWN",
                    "threat_level": "MEDIUM",
                    "confidence": 0.65
                },
                {
                    "track_id": "DRN_A3",
                    "object_type": "AERIAL_DRONE",
                    "position": {"x": -18000.0, "y": 7000.0, "z": 800.0},
                    "velocity": {"vx": 25.0, "vy": 5.0, "vz": 0.0},
                    "altitude_meters": 800.0,
                    "classification": "UNKNOWN",
                    "threat_level": "MEDIUM",
                    "confidence": 0.65
                },
                {
                    "track_id": "DRN_B1",
                    "object_type": "AERIAL_DRONE",
                    "position": {"x": -19000.0, "y": -8000.0, "z": 1200.0},
                    "velocity": {"vx": 28.0, "vy": -8.0, "vz": 0.0},
                    "altitude_meters": 1200.0,
                    "classification": "UNKNOWN",
                    "threat_level": "MEDIUM",
                    "confidence": 0.65
                },
                {
                    "track_id": "DRN_B2",
                    "object_type": "AERIAL_DRONE",
                    "position": {"x": -19000.0, "y": -9000.0, "z": 1200.0},
                    "velocity": {"vx": 28.0, "vy": -8.0, "vz": 0.0},
                    "altitude_meters": 1200.0,
                    "classification": "UNKNOWN",
                    "threat_level": "MEDIUM",
                    "confidence": 0.65
                },
                {
                    "track_id": "DRN_B3",
                    "object_type": "AERIAL_DRONE",
                    "position": {"x": -19000.0, "y": -7000.0, "z": 1200.0},
                    "velocity": {"vx": 28.0, "vy": -8.0, "vz": 0.0},
                    "altitude_meters": 1200.0,
                    "classification": "UNKNOWN",
                    "threat_level": "MEDIUM",
                    "confidence": 0.65
                }
            ]
        }
    }
    
    @staticmethod
    def get_scenario(scenario_key: str) -> Dict[str, Any]:
        """
        Get a scenario by key.
        
        Args:
            scenario_key: Key identifying the scenario
            
        Returns:
            Scenario dictionary with name, description, and tracks
        """
        return ScenarioPresets.SCENARIOS.get(scenario_key, ScenarioPresets.SCENARIOS["civil_air_traffic"])
    
    @staticmethod
    def get_scenario_list() -> List[Dict[str, str]]:
        """
        Get list of available scenarios for dropdown.
        
        Returns:
            List of dictionaries with 'key' and 'name' fields
        """
        return [
            {"key": key, "name": data["name"]}
            for key, data in ScenarioPresets.SCENARIOS.items()
        ]
    
    @staticmethod
    def _compute_sensor_contributions(track: Dict[str, Any], scenario_key: str) -> Dict[str, float]:
        """
        Compute deterministic sensor contributions for a track.
        
        ADVISORY ONLY — EXPLAINABLE, NOT DECISIONAL
        - Values sum to 1.0
        - Deterministic per scenario and track characteristics
        - Synthetic but stable in training mode
        - Placeholder in live mode (clearly labeled)
        
        Args:
            track: Track dictionary
            scenario_key: Scenario identifier
            
        Returns:
            Dictionary mapping sensor names to contribution values (0.0-1.0)
        """
        try:
            # Deterministic contribution based on track characteristics
            # Higher confidence tracks get more balanced contributions
            confidence = float(track.get("confidence", 0.5))
            track_id = str(track.get("track_id", ""))
            
            # Base contributions vary by scenario and track characteristics
            if scenario_key == "civil_air_traffic":
                # Civil traffic: Surveillance dominant, balanced contributions
                base_surveillance = 0.50
                base_precision = 0.30
                base_passive = 0.20
            elif scenario_key == "mixed_airspace":
                # Mixed: Balanced contributions, precision higher for hostile
                if track.get("classification") == "HOSTILE":
                    base_surveillance = 0.35
                    base_precision = 0.45
                    base_passive = 0.20
                else:
                    base_surveillance = 0.50
                    base_precision = 0.30
                    base_passive = 0.20
            elif scenario_key == "drone_swarm":
                # Drone swarm: Passive + surveillance emphasized
                base_surveillance = 0.40
                base_precision = 0.20
                base_passive = 0.40
            else:
                # Default: Balanced
                base_surveillance = 0.45
                base_precision = 0.35
                base_passive = 0.20
            
            # Adjust based on confidence (higher confidence = more balanced)
            confidence_factor = confidence * 0.2  # Small adjustment
            base_surveillance += confidence_factor * 0.1
            base_precision += confidence_factor * 0.05
            base_passive -= confidence_factor * 0.15
            
            # Normalize to ensure sum = 1.0
            total = base_surveillance + base_precision + base_passive
            if total > 0:
                base_surveillance /= total
                base_precision /= total
                base_passive /= total
            else:
                # Fallback
                base_surveillance = 0.45
                base_precision = 0.35
                base_passive = 0.20
            
            return {
                "Surveillance Radar": max(0.0, min(1.0, base_surveillance)),
                "Precision Tracking Radar": max(0.0, min(1.0, base_precision)),
                "Passive RF / ESM": max(0.0, min(1.0, base_passive))
            }
        except Exception:
            # Fail-safe: balanced contributions
            return {
                "Surveillance Radar": 0.45,
                "Precision Tracking Radar": 0.35,
                "Passive RF / ESM": 0.20
            }
    
    @staticmethod
    def get_scenario_tracks(scenario_key: str, time_offset_seconds: float = 0.0) -> List[Dict[str, Any]]:
        """
        Get tracks for a scenario using deterministic kinematics.
        
        KINEMATIC OBJECTS ONLY - These are NOT agents:
        - No reactions
        - No decisions
        - No autonomous behavior changes
        - Pure kinematic motion: position(t) = initial_position + velocity × Δt
        
        Motion Rules:
        - Δt derived from session timestamp (time_offset_seconds)
        - Motion updates only on Streamlit rerun OR Plotly animation frames
        - Motion is slow, smooth, professional
        - No acceleration unless explicitly defined in scenario
        
        Args:
            scenario_key: Key identifying the scenario
            time_offset_seconds: Time offset in seconds from scenario start (Δt)
            
        Returns:
            List of track dictionaries with updated positions based on kinematics
        """
        scenario = ScenarioPresets.get_scenario(scenario_key)
        tracks = []
        
        for track_template in scenario["tracks"]:
            # Create a copy of the track to avoid modifying the template
            track = track_template.copy()
            
            # Extract initial position (from template - never modified)
            initial_x = track_template["position"]["x"]
            initial_y = track_template["position"]["y"]
            initial_z = track_template["position"]["z"]
            
            # Extract velocity (constant - never changes, no acceleration)
            vx = track_template["velocity"]["vx"]
            vy = track_template["velocity"]["vy"]
            vz = track_template["velocity"].get("vz", 0.0)
            
            # Apply deterministic kinematics: position(t) = initial_position + velocity × Δt
            # This is pure kinematic motion - no acceleration, no reactions, no decisions
            track["position"] = {
                "x": initial_x + vx * time_offset_seconds,
                "y": initial_y + vy * time_offset_seconds,
                "z": initial_z + vz * time_offset_seconds
            }
            
            # Update altitude (derived from z position)
            track["altitude_meters"] = track["position"]["z"]
            
            # Velocity remains constant (no acceleration)
            # Calculate speed magnitude from velocity components
            speed = math.sqrt(vx**2 + vy**2 + vz**2)
            track["velocity"]["speed"] = speed
            track["speed_meters_per_second"] = speed
            
            # Calculate heading from velocity vector (derived, not autonomous)
            if vx != 0 or vy != 0:
                heading_rad = math.atan2(vx, vy)
                track["heading_degrees"] = math.degrees(heading_rad)
            else:
                track["heading_degrees"] = 0.0
            
            # Add simulation metadata
            track["is_simulation"] = True
            track["simulation_label"] = "SIMULATION / TRAINING DATA"
            
            # Ensure all required fields are present
            if "entity_type" not in track:
                track["entity_type"] = track["object_type"]
            
            # Store initial position for reference (not used in calculations, but available)
            track["_initial_position"] = {
                "x": initial_x,
                "y": initial_y,
                "z": initial_z
            }
            
            # Add sensor contributions (deterministic, synthetic in training mode)
            # ADVISORY ONLY — READ-ONLY EXTENSION
            # Values sum to 1.0, deterministic per scenario
            track["sensor_contributions"] = ScenarioPresets._compute_sensor_contributions(
                track, scenario_key
            )
            
            tracks.append(track)
        
        return tracks
