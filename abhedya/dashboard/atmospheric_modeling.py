"""
Atmospheric Modeling Module

Provides atmospheric effects modeling for visualization and advisory purposes.

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
- Environmental effects affect visual confidence only, NOT decisions
- All outputs are advisory and informational
- NO engagement logic changes
- NO weapon control
- Deterministic outputs only
"""

import math
from typing import Dict, Any, Optional, Tuple, List
from enum import Enum


class VisibilityLevel(str, Enum):
    """Visibility level enumeration."""
    CLEAR = "Clear"
    HAZE = "Haze"
    RAIN = "Rain"
    STORM = "Storm"


class AtmosphericStability(str, Enum):
    """Atmospheric stability enumeration."""
    STABLE = "Stable"
    NEUTRAL = "Neutral"
    UNSTABLE = "Unstable"


class AtmosphericPreset(str, Enum):
    """Atmospheric preset scenarios for training mode."""
    CLEAR_DAY = "Clear Day"
    HIGH_WIND = "High Wind"
    MONSOON_STORM = "Monsoon / Storm"
    DESERT_HAZE = "Desert Haze"


class AtmosphericModel:
    """
    Atmospheric effects modeling for visualization and advisory purposes.
    
    ADVISORY ONLY — Provides environmental context that affects visual confidence,
    NOT decisions. All effects are deterministic and visualization-only.
    """
    
    # Standard atmospheric constants
    SEA_LEVEL_PRESSURE_PA = 101325.0  # Pascals
    SEA_LEVEL_TEMPERATURE_K = 288.15  # Kelvin
    LAPSE_RATE_K_PER_M = 0.0065  # K/m
    GAS_CONSTANT = 287.05  # J/(kg·K)
    GRAVITY_MS2 = 9.80665  # m/s²
    
    # Preset definitions (deterministic)
    PRESETS = {
        AtmosphericPreset.CLEAR_DAY: {
            "wind_speed_ms": 5.0,
            "wind_direction_deg": 180.0,
            "temperature_c": 25.0,
            "visibility": VisibilityLevel.CLEAR,
            "stability": AtmosphericStability.NEUTRAL
        },
        AtmosphericPreset.HIGH_WIND: {
            "wind_speed_ms": 25.0,
            "wind_direction_deg": 270.0,
            "temperature_c": 15.0,
            "visibility": VisibilityLevel.CLEAR,
            "stability": AtmosphericStability.UNSTABLE
        },
        AtmosphericPreset.MONSOON_STORM: {
            "wind_speed_ms": 35.0,
            "wind_direction_deg": 225.0,
            "temperature_c": 20.0,
            "visibility": VisibilityLevel.STORM,
            "stability": AtmosphericStability.UNSTABLE
        },
        AtmosphericPreset.DESERT_HAZE: {
            "wind_speed_ms": 12.0,
            "wind_direction_deg": 90.0,
            "temperature_c": 40.0,
            "visibility": VisibilityLevel.HAZE,
            "stability": AtmosphericStability.STABLE
        }
    }
    
    @staticmethod
    def get_conditions(
        preset: Optional[AtmosphericPreset] = None,
        wind_speed_ms: Optional[float] = None,
        wind_direction_deg: Optional[float] = None,
        temperature_c: Optional[float] = None,
        visibility: Optional[VisibilityLevel] = None,
        stability: Optional[AtmosphericStability] = None
    ) -> Dict[str, Any]:
        """
        Get atmospheric conditions (deterministic).
        
        ADVISORY ONLY — Returns environmental parameters for visualization.
        
        Args:
            preset: Optional preset to use (overrides individual parameters)
            wind_speed_ms: Wind speed in m/s
            wind_direction_deg: Wind direction in degrees (0-360)
            temperature_c: Temperature in Celsius
            visibility: Visibility level
            stability: Atmospheric stability
            
        Returns:
            Dictionary with atmospheric conditions
        """
        try:
            # Use preset if provided
            if preset and preset in AtmosphericModel.PRESETS:
                preset_data = AtmosphericModel.PRESETS[preset].copy()
                conditions = {
                    "wind_speed_ms": float(preset_data["wind_speed_ms"]),
                    "wind_direction_deg": float(preset_data["wind_direction_deg"]),
                    "temperature_c": float(preset_data["temperature_c"]),
                    "visibility": preset_data["visibility"],
                    "stability": preset_data["stability"],
                    "preset": preset
                }
            else:
                # Use provided parameters or defaults
                conditions = {
                    "wind_speed_ms": float(wind_speed_ms) if wind_speed_ms is not None else 10.0,
                    "wind_direction_deg": float(wind_direction_deg) if wind_direction_deg is not None else 180.0,
                    "temperature_c": float(temperature_c) if temperature_c is not None else 20.0,
                    "visibility": visibility if visibility else VisibilityLevel.CLEAR,
                    "stability": stability if stability else AtmosphericStability.NEUTRAL,
                    "preset": None
                }
            
            # Normalize wind direction to 0-360
            conditions["wind_direction_deg"] = conditions["wind_direction_deg"] % 360.0
            
            # Add derived parameters
            conditions["temperature_k"] = conditions["temperature_c"] + 273.15
            
            # Add advisory note
            conditions["advisory_note"] = (
                "Advisory Only — Environmental visualization does not modify "
                "engagement decisions or weapon control. Human judgment required."
            )
            
            return conditions
        except Exception:
            # Fail-safe defaults
            return {
                "wind_speed_ms": 10.0,
                "wind_direction_deg": 180.0,
                "temperature_c": 20.0,
                "temperature_k": 293.15,
                "visibility": VisibilityLevel.CLEAR,
                "stability": AtmosphericStability.NEUTRAL,
                "preset": None,
                "advisory_note": "Advisory Only — Environmental visualization does not modify engagement decisions or weapon control. Human judgment required."
            }
    
    @staticmethod
    def calculate_air_density(altitude_meters: float, temperature_k: float) -> float:
        """
        Calculate air density at given altitude and temperature.
        
        ADVISORY ONLY — Mathematical modeling for visualization.
        
        Args:
            altitude_meters: Altitude in meters
            temperature_k: Temperature in Kelvin
            
        Returns:
            Air density in kg/m³
        """
        try:
            altitude_meters = max(0.0, float(altitude_meters))
            temperature_k = max(200.0, min(350.0, float(temperature_k)))
            
            # Calculate pressure using barometric formula
            pressure_pa = AtmosphericModel.SEA_LEVEL_PRESSURE_PA * (
                (temperature_k / AtmosphericModel.SEA_LEVEL_TEMPERATURE_K) ** 
                (AtmosphericModel.GRAVITY_MS2 / (AtmosphericModel.LAPSE_RATE_K_PER_M * AtmosphericModel.GAS_CONSTANT))
            )
            
            # Calculate air density using ideal gas law
            air_density = pressure_pa / (AtmosphericModel.GAS_CONSTANT * temperature_k)
            
            return max(0.1, min(2.0, air_density))  # Clamp to reasonable range
        except Exception:
            return 1.225  # Standard sea level density
    
    @staticmethod
    def get_visibility_confidence_attenuation(visibility: VisibilityLevel) -> float:
        """
        Get confidence attenuation factor based on visibility.
        
        ADVISORY ONLY — Affects visual confidence display only, NOT decisions.
        
        Args:
            visibility: Visibility level
            
        Returns:
            Confidence attenuation factor (0.0-1.0, where 1.0 = no attenuation)
        """
        try:
            attenuation_map = {
                VisibilityLevel.CLEAR: 1.0,
                VisibilityLevel.HAZE: 0.85,
                VisibilityLevel.RAIN: 0.70,
                VisibilityLevel.STORM: 0.50
            }
            return attenuation_map.get(visibility, 1.0)
        except Exception:
            return 1.0
    
    @staticmethod
    def get_radar_propagation_factor(visibility: VisibilityLevel, wind_speed_ms: float) -> float:
        """
        Get radar propagation visualization factor.
        
        ADVISORY ONLY — Affects radar coverage visualization only, NOT detection logic.
        
        Args:
            visibility: Visibility level
            wind_speed_ms: Wind speed in m/s
            
        Returns:
            Propagation factor (0.0-1.0, where 1.0 = full visibility)
        """
        try:
            # Base factor from visibility
            base_factor = AtmosphericModel.get_visibility_confidence_attenuation(visibility)
            
            # Additional attenuation from high wind (turbulence)
            wind_attenuation = 1.0 - min(0.2, wind_speed_ms / 50.0)
            
            return max(0.3, min(1.0, base_factor * wind_attenuation))
        except Exception:
            return 1.0
    
    @staticmethod
    def get_trajectory_uncertainty_factor(stability: AtmosphericStability, wind_speed_ms: float) -> float:
        """
        Get trajectory uncertainty envelope expansion factor.
        
        ADVISORY ONLY — Affects visual uncertainty cone width only, NOT predictive logic.
        
        Args:
            stability: Atmospheric stability
            wind_speed_ms: Wind speed in m/s
            
        Returns:
            Uncertainty expansion factor (1.0 = normal, >1.0 = wider cone)
        """
        try:
            stability_factors = {
                AtmosphericStability.STABLE: 1.0,
                AtmosphericStability.NEUTRAL: 1.2,
                AtmosphericStability.UNSTABLE: 1.5
            }
            base_factor = stability_factors.get(stability, 1.0)
            
            # Additional expansion from wind
            wind_factor = 1.0 + min(0.5, wind_speed_ms / 40.0)
            
            return max(1.0, min(2.5, base_factor * wind_factor))
        except Exception:
            return 1.0
    
    @staticmethod
    def get_interception_environmental_note(conditions: Dict[str, Any]) -> Optional[str]:
        """
        Get environmental annotation text for interception feasibility.
        
        ADVISORY ONLY — Adds annotation text only, NO feasibility math changes.
        
        Args:
            conditions: Atmospheric conditions dictionary
            
        Returns:
            Optional annotation text, or None if conditions are clear
        """
        try:
            visibility = conditions.get("visibility", VisibilityLevel.CLEAR)
            wind_speed_ms = conditions.get("wind_speed_ms", 0.0)
            stability = conditions.get("stability", AtmosphericStability.NEUTRAL)
            
            notes = []
            
            if visibility in [VisibilityLevel.RAIN, VisibilityLevel.STORM]:
                notes.append("Reduced visibility conditions")
            
            if wind_speed_ms > 20.0:
                notes.append("High wind conditions")
            
            if stability == AtmosphericStability.UNSTABLE:
                notes.append("Atmospheric turbulence")
            
            if notes:
                return "Environmental conditions may reduce kinematic margins: " + ", ".join(notes)
            
            return None
        except Exception:
            return None
    
    @staticmethod
    def get_atmospheric_layer_color(visibility: VisibilityLevel) -> str:
        """
        Get color for atmospheric layer visualization.
        
        ADVISORY ONLY — Visual representation only.
        
        Args:
            visibility: Visibility level
            
        Returns:
            Color string (hex or rgba)
        """
        try:
            color_map = {
                VisibilityLevel.CLEAR: "rgba(200, 220, 255, 0.05)",
                VisibilityLevel.HAZE: "rgba(255, 220, 180, 0.15)",
                VisibilityLevel.RAIN: "rgba(150, 150, 200, 0.20)",
                VisibilityLevel.STORM: "rgba(100, 100, 150, 0.25)"
            }
            return color_map.get(visibility, "rgba(200, 220, 255, 0.05)")
        except Exception:
            return "rgba(200, 220, 255, 0.05)"
    
    @staticmethod
    def get_environmental_state_summary(conditions: Dict[str, Any]) -> str:
        """
        Get human-readable environmental state summary.
        
        ADVISORY ONLY — Informational text only.
        
        Args:
            conditions: Atmospheric conditions dictionary
            
        Returns:
            Summary string
        """
        try:
            visibility = conditions.get("visibility", VisibilityLevel.CLEAR)
            wind_speed_ms = conditions.get("wind_speed_ms", 0.0)
            temperature_c = conditions.get("temperature_c", 20.0)
            stability = conditions.get("stability", AtmosphericStability.NEUTRAL)
            
            wind_desc = "Calm" if wind_speed_ms < 5.0 else "Moderate" if wind_speed_ms < 15.0 else "High" if wind_speed_ms < 30.0 else "Very High"
            
            return (
                f"Visibility: {visibility.value}, Wind: {wind_desc} ({wind_speed_ms:.1f} m/s), "
                f"Temp: {temperature_c:.1f}°C, Stability: {stability.value}"
            )
        except Exception:
            return "Environmental conditions: Standard"
    
    @staticmethod
    def calculate_atmospheric_effects(
        altitude_meters: float,
        velocity_ms: float,
        conditions: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Assemble a structured atmospheric effects dictionary for advisory display.

        This is a lightweight wrapper that composes existing AtmosphericModel
        utilities (deterministic, advisory-only). It intentionally does not
        introduce new physics beyond the implemented helpers.

        Args:
            altitude_meters: Altitude in meters where the object is located
            velocity_ms: Object speed in m/s (used for advisory scaling)
            conditions: Optional pre-computed atmospheric conditions

        Returns:
            Dictionary containing air density, pressure, temperature (K),
            drag coefficient (advisory), and a wind effect factor.
        """
        try:
            if conditions is None:
                conditions = AtmosphericModel.get_conditions()

            temperature_k = conditions.get("temperature_k") or (
                conditions.get("temperature_c", 20.0) + 273.15
            )

            wind_speed = float(conditions.get("wind_speed_ms", 0.0))
            visibility = conditions.get("visibility", VisibilityLevel.CLEAR)
            stability = conditions.get("stability", AtmosphericStability.NEUTRAL)

            # Air density (kg/m^3)
            air_density = AtmosphericModel.calculate_air_density(altitude_meters, temperature_k)

            # Pressure via ideal gas law (consistent with calculate_air_density)
            pressure_pa = air_density * AtmosphericModel.GAS_CONSTANT * temperature_k

            # Wind / radar propagation advisory factor
            wind_effect_factor = AtmosphericModel.get_radar_propagation_factor(visibility, wind_speed)

            # Advisory drag coefficient: base conservative value adjusted by
            # trajectory uncertainty factor (uses existing helper).
            traj_uncertainty = AtmosphericModel.get_trajectory_uncertainty_factor(stability, wind_speed)
            base_drag = 0.30
            drag_coefficient = max(0.05, min(3.0, base_drag * traj_uncertainty))

            return {
                "air_density_kg_per_m3": air_density,
                "pressure_pa": pressure_pa,
                "temperature_k": float(temperature_k),
                "drag_coefficient": float(drag_coefficient),
                "wind_effect_factor": float(wind_effect_factor),
            }
        except Exception:
            # Fail-safe advisory values
            return {
                "air_density_kg_per_m3": 1.225,
                "pressure_pa": AtmosphericModel.SEA_LEVEL_PRESSURE_PA,
                "temperature_k": AtmosphericModel.SEA_LEVEL_TEMPERATURE_K,
                "drag_coefficient": 0.30,
                "wind_effect_factor": 1.0,
            }
