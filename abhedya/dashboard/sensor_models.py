"""
Sensor Models Module

Defines static, advisory-only sensor definitions for visualization purposes.

ADVISORY ONLY — SENSOR VISUALIZATION. NO CONTROL OR DECISION LOGIC.

ADVISORY ONLY — VISUAL SIMULATION
- No fire / launch / engage commands
- No ROE logic
- No autonomy
- No while True loops
- No time.sleep
- No uncontrolled reruns
- No randomness per rerun

STRICT CONSTRAINTS:
- Sensors are STATIC objects (no movement, no physics, no timing logic)
- Sensors do NOT detect, decide, or react
- Sensors expose only geometry + metadata
- Visualization only — all sensor definitions are for display purposes
- NO detection logic
- NO decision logic
- NO engagement logic
- NO weapon control
- Visual indication only — geometric overlap within coverage volumes
"""

from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass


class SensorType(str, Enum):
    """Sensor type enumeration."""
    LONG_RANGE_SURVEILLANCE = "Long-Range Surveillance Radar"
    FIRE_CONTROL = "Precision Tracking Radar"
    PASSIVE_ESM = "Passive / ESM Sensor"


@dataclass
class SensorGeometry:
    """
    Static sensor geometry definition.
    
    VISUALIZATION ONLY — Geometry is for visual representation only.
    No physics, no movement, no timing logic.
    """
    # Position (static, relative to defender)
    position_x_km: float
    position_y_km: float
    position_z_m: float
    
    # Physical dimensions (for 3D visualization)
    mast_height_m: float
    dome_radius_m: float
    
    # Coverage geometry (for visualization only)
    coverage_range_km: float
    coverage_altitude_ceiling_m: float
    
    # Beam geometry (for visualization only, no actual beam logic)
    beam_width_deg: float  # For directional sensors
    beam_elevation_deg: float  # For directional sensors


@dataclass
class SensorMetadata:
    """
    Static sensor metadata definition.
    
    VISUALIZATION ONLY — Metadata is for informational display only.
    No detection, decision, or reaction logic.
    """
    sensor_type: SensorType
    name: str
    role: str
    description: str
    
    # Visual properties (for display only)
    color: str
    coverage_color: str
    icon: str
    
    # Operational parameters (informational only, no actual operation)
    update_rate_hz: Optional[float] = None  # Informational only
    frequency_band: Optional[str] = None  # Informational only
    power_class: Optional[str] = None  # Informational only
    
    # Advisory note (mandatory)
    advisory_note: str = "VISUALIZATION ONLY — Sensor definition is for display purposes. No detection, decision, or engagement logic."


class SensorModels:
    """
    Static sensor model definitions.
    
    ADVISORY ONLY — All sensor definitions are for visualization purposes only.
    Sensors are static objects with no movement, physics, or timing logic.
    Sensors do NOT detect, decide, or react.
    """
    
    # Long-Range Surveillance Radar
    LONG_RANGE_SURVEILLANCE = {
        "type": SensorType.LONG_RANGE_SURVEILLANCE,
        "name": "Long-Range Surveillance Radar",
        "role": "Wide-area airspace monitoring and early detection",
        "description": (
            "Primary surveillance radar for long-range detection and tracking of aircraft and missiles. "
            "Provides early warning and situational awareness. Wide coverage area with low update rate. "
            "VISUALIZATION ONLY — No actual detection or tracking logic."
        ),
        "geometry": SensorGeometry(
            position_x_km=-8.0,
            position_y_km=-8.0,
            position_z_m=0.0,
            mast_height_m=45.0,
            dome_radius_m=9.0,
            coverage_range_km=150.0,
            coverage_altitude_ceiling_m=30000.0,
            beam_width_deg=360.0,  # Omnidirectional
            beam_elevation_deg=90.0  # Vertical coverage
        ),
        "metadata": SensorMetadata(
            sensor_type=SensorType.LONG_RANGE_SURVEILLANCE,
            name="Long-Range Surveillance Radar",
            role="Wide-area airspace monitoring and early detection",
            description=(
                "Primary surveillance radar for long-range detection and tracking of aircraft and missiles. "
                "Provides early warning and situational awareness. Wide coverage area with low update rate."
            ),
            color="#52C41A",  # Green
            coverage_color="rgba(82, 196, 26, 0.10)",
            icon="📡",
            update_rate_hz=1.0,  # Informational only
            frequency_band="L-Band",  # Informational only
            power_class="High",  # Informational only
            advisory_note="VISUALIZATION ONLY — Sensor definition is for display purposes. No detection, decision, or engagement logic."
        )
    }
    
    # Precision Tracking Radar (formerly Fire Control)
    FIRE_CONTROL = {
        "type": SensorType.FIRE_CONTROL,
        "name": "Precision Tracking Radar",
            "role": "Precision tracking for targeting support",
            "description": (
                "High-precision tracking radar for target acquisition and targeting support. "
                "Provides accurate position and velocity data for interception calculations. "
                "Narrower beam with higher precision. VISUALIZATION ONLY — Visual indication only."
        ),
        "geometry": SensorGeometry(
            position_x_km=8.0,
            position_y_km=-8.0,
            position_z_m=0.0,
            mast_height_m=28.0,
            dome_radius_m=6.0,
            coverage_range_km=80.0,
            coverage_altitude_ceiling_m=20000.0,
            beam_width_deg=2.0,  # Narrow beam
            beam_elevation_deg=60.0  # Focused elevation
        ),
        "metadata": SensorMetadata(
            sensor_type=SensorType.FIRE_CONTROL,
            name="Precision Tracking Radar",
            role="Precision tracking for targeting support",
            description=(
                "High-precision tracking radar for target acquisition and targeting support. "
                "Provides accurate position and velocity data for interception calculations. "
                "Narrower beam with higher precision."
            ),
            color="#1890FF",  # Blue
            coverage_color="rgba(24, 144, 255, 0.10)",
            icon="🎯",
            update_rate_hz=10.0,  # Informational only
            frequency_band="X-Band",  # Informational only
            power_class="Medium",  # Informational only
            advisory_note="VISUALIZATION ONLY — Sensor definition is for display purposes. No detection, decision, or engagement logic."
        )
    }
    
    # Passive / ESM Sensor
    PASSIVE_ESM = {
        "type": SensorType.PASSIVE_ESM,
        "name": "Passive / ESM Sensor",
        "role": "Electronic Support Measures - no emission",
        "description": (
            "Passive electronic support measures sensor for detecting and analyzing electromagnetic emissions. "
            "No active emission - receives only. Directional detection cones for EW awareness. "
            "VISUALIZATION ONLY — No actual detection or analysis logic."
        ),
        "geometry": SensorGeometry(
            position_x_km=0.0,
            position_y_km=12.0,
            position_z_m=0.0,
            mast_height_m=20.0,
            dome_radius_m=5.0,
            coverage_range_km=100.0,
            coverage_altitude_ceiling_m=25000.0,
            beam_width_deg=45.0,  # Directional cone
            beam_elevation_deg=30.0  # Elevated cone
        ),
        "metadata": SensorMetadata(
            sensor_type=SensorType.PASSIVE_ESM,
            name="Passive / ESM Sensor",
            role="Electronic Support Measures - no emission",
            description=(
                "Passive electronic support measures sensor for detecting and analyzing electromagnetic emissions. "
                "No active emission - receives only. Directional detection cones for EW awareness."
            ),
            color="#722ED1",  # Purple
            coverage_color="rgba(114, 46, 209, 0.08)",
            icon="📻",
            update_rate_hz=None,  # Passive - no update rate
            frequency_band="Multi-Band",  # Informational only
            power_class="N/A (Passive)",  # Informational only
            advisory_note="VISUALIZATION ONLY — Sensor definition is for display purposes. No detection, decision, or engagement logic."
        )
    }
    
    @staticmethod
    def get_sensor_definition(sensor_type: SensorType) -> Optional[Dict[str, Any]]:
        """
        Get sensor definition by type.
        
        VISUALIZATION ONLY — Returns static sensor definition for display purposes.
        No detection, decision, or engagement logic.
        
        Args:
            sensor_type: Sensor type enumeration
            
        Returns:
            Sensor definition dictionary or None if not found
        """
        sensor_map = {
            SensorType.LONG_RANGE_SURVEILLANCE: SensorModels.LONG_RANGE_SURVEILLANCE,
            SensorType.FIRE_CONTROL: SensorModels.FIRE_CONTROL,
            SensorType.PASSIVE_ESM: SensorModels.PASSIVE_ESM
        }
        return sensor_map.get(sensor_type)
    
    @staticmethod
    def get_all_sensor_definitions() -> List[Dict[str, Any]]:
        """
        Get all sensor definitions.
        
        VISUALIZATION ONLY — Returns all static sensor definitions for display purposes.
        No detection, decision, or engagement logic.
        
        Returns:
            List of sensor definition dictionaries
        """
        return [
            SensorModels.LONG_RANGE_SURVEILLANCE,
            SensorModels.FIRE_CONTROL,
            SensorModels.PASSIVE_ESM
        ]
    
    @staticmethod
    def get_sensor_geometry(sensor_type: SensorType) -> Optional[SensorGeometry]:
        """
        Get sensor geometry by type.
        
        VISUALIZATION ONLY — Returns static geometry for visual representation only.
        No physics, no movement, no timing logic.
        
        Args:
            sensor_type: Sensor type enumeration
            
        Returns:
            SensorGeometry object or None if not found
        """
        sensor_def = SensorModels.get_sensor_definition(sensor_type)
        if sensor_def:
            return sensor_def.get("geometry")
        return None
    
    @staticmethod
    def get_sensor_metadata(sensor_type: SensorType) -> Optional[SensorMetadata]:
        """
        Get sensor metadata by type.
        
        VISUALIZATION ONLY — Returns static metadata for informational display only.
        No detection, decision, or reaction logic.
        
        Args:
            sensor_type: Sensor type enumeration
            
        Returns:
            SensorMetadata object or None if not found
        """
        sensor_def = SensorModels.get_sensor_definition(sensor_type)
        if sensor_def:
            return sensor_def.get("metadata")
        return None
    
    @staticmethod
    def get_sensor_list() -> List[Dict[str, Any]]:
        """
        Get simplified sensor list for UI display.
        
        VISUALIZATION ONLY — Returns simplified sensor information for display purposes.
        No detection, decision, or engagement logic.
        
        Returns:
            List of simplified sensor dictionaries with name, type, role, icon, color
        """
        sensors = []
        for sensor_def in SensorModels.get_all_sensor_definitions():
            metadata = sensor_def.get("metadata")
            if metadata:
                sensors.append({
                    "type": sensor_def.get("type"),
                    "name": metadata.name,
                    "role": metadata.role,
                    "icon": metadata.icon,
                    "color": metadata.color,
                    "advisory_note": metadata.advisory_note
                })
        return sensors
    
    @staticmethod
    def get_scenario_sensor_layout(scenario_key: str) -> List[SensorType]:
        """
        Get scenario-specific sensor layout (which sensors to show).
        
        VISUALIZATION ONLY — Returns list of sensor types to display for a given scenario.
        No detection, decision, or engagement logic.
        
        Scenario-specific layouts:
        - Mixed Air Traffic → all sensors active
        - Drone Swarm → passive + surveillance emphasized
        - High-Altitude Threat → long-range radar dominant
        
        Args:
            scenario_key: Scenario key from ScenarioPresets
            
        Returns:
            List of SensorType enums to display
        """
        try:
            # Scenario-specific sensor layouts
            scenario_layouts = {
                "civil_air_traffic": [
                    SensorType.LONG_RANGE_SURVEILLANCE,
                    SensorType.FIRE_CONTROL,
                    SensorType.PASSIVE_ESM
                ],
                "mixed_airspace": [
                    # Mixed Air Traffic → all sensors active
                    SensorType.LONG_RANGE_SURVEILLANCE,
                    SensorType.FIRE_CONTROL,
                    SensorType.PASSIVE_ESM
                ],
                "drone_swarm": [
                    # Drone Swarm → passive + surveillance emphasized
                    SensorType.LONG_RANGE_SURVEILLANCE,
                    SensorType.PASSIVE_ESM
                    # Precision Tracking Radar omitted to emphasize passive + surveillance
                ],
                "saturation_test": [
                    # Saturation Test → all sensors for comprehensive coverage
                    SensorType.LONG_RANGE_SURVEILLANCE,
                    SensorType.FIRE_CONTROL,
                    SensorType.PASSIVE_ESM
                ],
                # High-Altitude Threat scenario (if exists) → long-range radar dominant
                "high_altitude_threat": [
                    SensorType.LONG_RANGE_SURVEILLANCE
                    # Long-range radar dominant, others optional
                ]
            }
            
            # Return scenario-specific layout or default (all sensors)
            return scenario_layouts.get(scenario_key, [
                SensorType.LONG_RANGE_SURVEILLANCE,
                SensorType.FIRE_CONTROL,
                SensorType.PASSIVE_ESM
            ])
        except Exception:
            # Fail-safe: return all sensors
            return [
                SensorType.LONG_RANGE_SURVEILLANCE,
                SensorType.FIRE_CONTROL,
                SensorType.PASSIVE_ESM
            ]
