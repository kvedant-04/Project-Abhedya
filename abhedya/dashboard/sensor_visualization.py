"""
Multi-Radar Sensor Visualization Module

Provides comprehensive multi-radar sensor visualization layer for SAM C2 dashboard.

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
- Visualization only, no autonomous actions
- Sensor visuals do NOT imply firing or authorization
- All outputs are advisory and informational
- NO weapon control
- NO interception logic
- Deterministic sensor positions and roles
- Visual indication only — geometric overlap within coverage volumes
"""

import math
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum


class RadarType(str, Enum):
    """Radar type enumeration."""
    LONG_RANGE_SURVEILLANCE = "Long-Range Surveillance"
    FIRE_CONTROL = "Precision Tracking"
    LOW_ALTITUDE_COUNTER_UAS = "Low-Altitude / Counter-UAS"
    EARLY_WARNING = "Early Warning"
    TRACKING = "Tracking"


class SensorStatus(str, Enum):
    """Sensor status enumeration."""
    ACTIVE = "Active"
    STANDBY = "Standby"
    MAINTENANCE = "Maintenance"
    DEGRADED = "Degraded"


class SensorVisualization:
    """
    Multi-radar sensor visualization component.
    
    ADVISORY ONLY — Provides visual representation of sensor systems.
    All sensor visuals are informational only and do NOT imply firing or authorization.
    """
    
    # Comprehensive radar sensor definitions
    RADAR_SENSORS = {
        RadarType.LONG_RANGE_SURVEILLANCE: {
            "name": "Long-Range Surveillance Radar",
            "role": "Wide-area airspace monitoring and early detection",
            "range_km": 150.0,
            "altitude_ceiling_m": 30000.0,
            "mast_height_m": 45.0,
            "dome_radius_m": 9.0,
            "color": "#52C41A",  # Green
            "coverage_color": "rgba(82, 196, 26, 0.10)",
            "icon": "📡",
            "description": "Primary surveillance radar for long-range detection and tracking of aircraft and missiles. Provides early warning and situational awareness."
        },
        RadarType.FIRE_CONTROL: {
            "name": "Precision Tracking Radar",
            "role": "Precision tracking for targeting support",
            "range_km": 80.0,
            "altitude_ceiling_m": 20000.0,
            "mast_height_m": 28.0,
            "dome_radius_m": 6.0,
            "color": "#1890FF",  # Blue
            "coverage_color": "rgba(24, 144, 255, 0.10)",
            "icon": "🎯",
            "description": "High-precision tracking radar for target acquisition and engagement guidance. Provides accurate position and velocity data for interception calculations."
        },
        RadarType.LOW_ALTITUDE_COUNTER_UAS: {
            "name": "Low-Altitude / Counter-UAS Radar",
            "role": "Detection and tracking of low-altitude threats and drones",
            "range_km": 25.0,
            "altitude_ceiling_m": 5000.0,
            "mast_height_m": 15.0,
            "dome_radius_m": 4.0,
            "color": "#FAAD14",  # Amber
            "coverage_color": "rgba(250, 173, 20, 0.10)",
            "icon": "🛸",
            "description": "Specialized radar for detecting and tracking low-altitude threats, including drones and small aircraft. Optimized for low radar cross-section targets."
        },
        RadarType.EARLY_WARNING: {
            "name": "Early Warning Radar",
            "role": "Extended range threat detection and classification",
            "range_km": 200.0,
            "altitude_ceiling_m": 35000.0,
            "mast_height_m": 50.0,
            "dome_radius_m": 10.0,
            "color": "#722ED1",  # Purple
            "coverage_color": "rgba(114, 46, 209, 0.08)",
            "icon": "⚠️",
            "description": "Extended-range early warning radar for maximum detection range. Provides initial threat detection and classification before handoff to tracking radars."
        },
        RadarType.TRACKING: {
            "name": "Tracking Radar",
            "role": "Continuous high-precision target tracking",
            "range_km": 60.0,
            "altitude_ceiling_m": 25000.0,
            "mast_height_m": 22.0,
            "dome_radius_m": 5.5,
            "color": "#13C2C2",  # Cyan
            "coverage_color": "rgba(19, 194, 194, 0.10)",
            "icon": "📊",
            "description": "Dedicated tracking radar for continuous high-precision target monitoring. Maintains accurate track data for threat assessment and interception planning."
        }
    }
    
    @staticmethod
    def get_sensor_configurations(
        defender_position: Dict[str, float],
        view_range: float,
        include_all_types: bool = True,
        selected_types: Optional[List[RadarType]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get sensor configurations for visualization.
        
        ADVISORY ONLY — Returns deterministic sensor positions and roles.
        
        Args:
            defender_position: Defender position dict with x, y, z
            view_range: View range in meters
            include_all_types: Whether to include all radar types
            selected_types: Optional list of specific radar types to include
            
        Returns:
            List of sensor configuration dictionaries
        """
        try:
            def_x_km = defender_position.get('x', 0.0) / 1000.0
            def_y_km = defender_position.get('y', 0.0) / 1000.0
            def_z = defender_position.get('z', 0.0)
            
            # Determine which radar types to include
            if selected_types:
                radar_types = selected_types
            elif include_all_types:
                radar_types = list(RadarType)
            else:
                radar_types = [
                    RadarType.LONG_RANGE_SURVEILLANCE,
                    RadarType.FIRE_CONTROL,
                    RadarType.LOW_ALTITUDE_COUNTER_UAS
                ]
            
            configurations = []
            
            # Deterministic positioning relative to defender
            # Positions form a tactical array around the defender
            position_offsets = {
                RadarType.LONG_RANGE_SURVEILLANCE: {'x': -8.0, 'y': -8.0, 'z': 0.0},
                RadarType.FIRE_CONTROL: {'x': 8.0, 'y': -8.0, 'z': 0.0},
                RadarType.LOW_ALTITUDE_COUNTER_UAS: {'x': 0.0, 'y': 12.0, 'z': 0.0},
                RadarType.EARLY_WARNING: {'x': -12.0, 'y': 0.0, 'z': 0.0},
                RadarType.TRACKING: {'x': 12.0, 'y': 0.0, 'z': 0.0}
            }
            
            for radar_type in radar_types:
                if radar_type not in SensorVisualization.RADAR_SENSORS:
                    continue
                
                sensor_def = SensorVisualization.RADAR_SENSORS[radar_type].copy()
                offset = position_offsets.get(radar_type, {'x': 0.0, 'y': 0.0, 'z': 0.0})
                
                config = {
                    'type': radar_type,
                    'name': sensor_def['name'],
                    'role': sensor_def['role'],
                    'description': sensor_def['description'],
                    'position_km': {
                        'x': def_x_km + offset['x'],
                        'y': def_y_km + offset['y'],
                        'z': def_z + offset['z']
                    },
                    'range_km': sensor_def['range_km'],
                    'altitude_ceiling_m': sensor_def['altitude_ceiling_m'],
                    'mast_height_m': sensor_def['mast_height_m'],
                    'dome_radius_m': sensor_def['dome_radius_m'],
                    'color': sensor_def['color'],
                    'coverage_color': sensor_def['coverage_color'],
                    'icon': sensor_def['icon'],
                    'status': SensorStatus.ACTIVE,  # Default status
                    'advisory_note': 'ADVISORY ONLY — Sensor visualization does not imply firing or authorization. Human judgment required.'
                }
                
                configurations.append(config)
            
            return configurations
        except Exception:
            return []
    
    @staticmethod
    def get_sensor_summary(sensor_config: Dict[str, Any]) -> str:
        """
        Get human-readable sensor summary.
        
        ADVISORY ONLY — Informational text only.
        
        Args:
            sensor_config: Sensor configuration dictionary
            
        Returns:
            Summary string
        """
        try:
            name = sensor_config.get('name', 'Unknown Sensor')
            role = sensor_config.get('role', 'Unknown Role')
            range_km = sensor_config.get('range_km', 0.0)
            status = sensor_config.get('status', SensorStatus.ACTIVE)
            
            return f"{name}: {role} | Range: {range_km:.0f} km | Status: {status.value}"
        except Exception:
            return "Sensor information unavailable"
    
    @staticmethod
    def get_sensor_hover_text(sensor_config: Dict[str, Any]) -> str:
        """
        Get hover tooltip text for sensor.
        
        ADVISORY ONLY — Informational tooltip only.
        
        Args:
            sensor_config: Sensor configuration dictionary
            
        Returns:
            HTML-formatted hover text
        """
        try:
            name = sensor_config.get('name', 'Unknown Sensor')
            role = sensor_config.get('role', 'Unknown Role')
            description = sensor_config.get('description', '')
            range_km = sensor_config.get('range_km', 0.0)
            altitude_ceiling_m = sensor_config.get('altitude_ceiling_m', 0.0)
            status = sensor_config.get('status', SensorStatus.ACTIVE)
            
            hover_text = (
                f"<b>{name}</b><br>"
                f"Role: {role}<br>"
                f"Range: {range_km:.0f} km<br>"
                f"Altitude Ceiling: {altitude_ceiling_m/1000:.1f} km<br>"
                f"Status: {status.value}<br>"
                f"<br>{description}<br>"
                f"<br><i>ADVISORY ONLY — Visual reference only</i>"
            )
            
            return hover_text
        except Exception:
            return "<b>Sensor</b><br>ADVISORY ONLY — Visual reference only"
    
    @staticmethod
    def get_sensor_legend() -> List[Dict[str, Any]]:
        """
        Get sensor legend for UI display.
        
        ADVISORY ONLY — Informational legend only.
        
        Returns:
            List of legend entries
        """
        try:
            legend = []
            for radar_type, sensor_def in SensorVisualization.RADAR_SENSORS.items():
                legend.append({
                    'type': radar_type.value,
                    'name': sensor_def['name'],
                    'role': sensor_def['role'],
                    'color': sensor_def['color'],
                    'icon': sensor_def['icon'],
                    'range_km': sensor_def['range_km']
                })
            return legend
        except Exception:
            return []
