"""
Dashboard State Manager

Manages dashboard state, data fetching, and error handling.
Supports Training & Simulation Mode with synthetic data injection.

ADVISORY ONLY — VISUAL SIMULATION
- No fire / launch / engage commands
- No ROE logic
- No autonomy
- No while True loops
- No time.sleep
- No uncontrolled reruns
- No randomness per rerun
"""

import streamlit as st
from datetime import datetime
from typing import List, Dict, Any, Optional
import traceback
import math


class DashboardStateManager:
    """
    Manages dashboard state and data fetching.
    
    Handles errors gracefully and ensures dashboard never crashes.
    """
    
    @staticmethod
    def initialize_session_state():
        """Initialize session state variables."""
        if 'training_mode' not in st.session_state:
            st.session_state.training_mode = False
        
        if 'shadow_mode' not in st.session_state:
            st.session_state.shadow_mode = False
        
        if 'audio_enabled' not in st.session_state:
            st.session_state.audio_enabled = False
        
        if 'last_update_time' not in st.session_state:
            st.session_state.last_update_time = datetime.now()
        
        if 'acknowledged_items' not in st.session_state:
            st.session_state.acknowledged_items = set()
        
        # Track history for trails (Training Mode only)
        if 'track_history' not in st.session_state:
            st.session_state.track_history = {}  # {track_id: [(timestamp, x, y), ...]}
        
        # Animation state
        if 'animation_start_time' not in st.session_state:
            st.session_state.animation_start_time = datetime.now()
        
        # Previous confidence values for smooth transitions
        if 'previous_confidence_values' not in st.session_state:
            st.session_state.previous_confidence_values = {}
        
        # Persistent simulation state (Training Mode only)
        if 'simulation_tracks' not in st.session_state:
            st.session_state.simulation_tracks = []  # List of track dictionaries
        if 'simulation_last_update' not in st.session_state:
            st.session_state.simulation_last_update = datetime.now()
        if 'simulation_initialized' not in st.session_state:
            st.session_state.simulation_initialized = False
        
        # EW Environment State (selectable in Training Mode, read-only in Live Mode)
        if 'ew_environment_state' not in st.session_state:
            st.session_state.ew_environment_state = 'NONE'  # Default: no EW
    
    @staticmethod
    def get_early_warning_data() -> Optional[Dict[str, Any]]:
        """
        Get early warning system data.
        
        Uses unified data provider to eliminate branching logic duplication.
        
        Returns:
            Early warning data or None if unavailable
        """
        try:
            from abhedya.dashboard.data_provider import UnifiedDataProvider
            return UnifiedDataProvider.get_early_warning_data()
        except Exception:
            # Fail-safe default
            return {
                'warning_state': 'NORMAL',
                'confidence': 0.0,
                'reasoning': [],
                'is_simulation': False,
                'simulation_label': 'MONITORING ONLY'
            }
    
    @staticmethod
    def get_ew_analysis_data() -> Optional[Dict[str, Any]]:
        """
        Get electronic warfare analysis data with persistent simulation state.
        
        Returns:
            EW analysis data or None if unavailable
        """
        try:
            # Check if Training & Simulation Mode is enabled
            if DashboardStateManager.is_training_mode():
                # Ensure simulation is initialized
                if not st.session_state.get('simulation_initialized', False):
                    DashboardStateManager._initialize_simulation_tracks()
                
                # Get EW environment state from session state (user-selectable in training mode)
                ew_state = st.session_state.get('ew_environment_state', 'NONE')
                
                # If using training data generator, get its EW data
                try:
                    from abhedya.simulation.training_data_generator import get_training_generator
                    generator = get_training_generator()
                    time_offset = generator.get_time_offset()
                    ew_data = generator.generate_ew_analysis_data(time_offset)
                    
                    # Override with user-selected EW state if available
                    if ew_data and ew_state != 'NONE':
                        ew_data['ew_state'] = ew_state
                    
                    return ew_data
                except Exception:
                    # Fallback: return state based on session state
                    return {
                        'ew_state': ew_state,
                        'confidence': 0.7 if ew_state != 'NONE' else 1.0,
                        'reasoning': [f'EW environment state: {ew_state} (Training Mode)'],
                        'is_simulation': True,
                        'simulation_label': 'SIMULATION / TRAINING DATA'
                    }
            
            # Real-world mode: In production, this would call: from abhedya.ew_analysis import EWAnalysisEngine
            # For now, return None to show "Insufficient Data" state
            return None
        except Exception:
            st.info("ℹ️ Monitoring Only — Training data initializing")
            return {
                'ew_state': 'NONE',
                'confidence': 0.0,
                'reasoning': [],
                'is_simulation': True,
                'simulation_label': 'SIMULATION / TRAINING DATA'
            }
    
    @staticmethod
    def get_cybersecurity_data() -> Optional[Dict[str, Any]]:
        """
        Get cybersecurity data.
        
        Uses unified data provider to eliminate branching logic duplication.
        
        Returns:
            Cybersecurity data or None if unavailable
        """
        try:
            from abhedya.dashboard.data_provider import UnifiedDataProvider
            return UnifiedDataProvider.get_cybersecurity_data()
        except Exception:
            # Fail-safe default
            return {
                'cybersecurity_state': 'NORMAL',
                'confidence': 0.0,
                'reasoning': [],
                'is_simulation': False,
                'simulation_label': 'MONITORING ONLY'
            }
    
    @staticmethod
    def get_tracking_data() -> Optional[List[Dict[str, Any]]]:
        """
        Get tracking data with persistent simulation state.
        
        Uses unified data provider to eliminate branching logic duplication.
        
        Returns:
            Tracking data or None if unavailable
        """
        try:
            from abhedya.dashboard.data_provider import UnifiedDataProvider
            
            # Get data from unified provider
            data = UnifiedDataProvider.get_tracking_data()
            
            # CRITICAL: Hard mode separation - NEVER return simulation data in Live Mode
            if DashboardStateManager.is_training_mode():
                # TRAINING MODE ONLY: Use simulation_tracks
                if not st.session_state.get('simulation_initialized', False):
                    DashboardStateManager._initialize_simulation_tracks()
                DashboardStateManager._update_simulation_tracks()
                # Return persistent simulation tracks as canonical source
                session_tracks = st.session_state.get('simulation_tracks', [])
                if isinstance(session_tracks, list) and len(session_tracks) > 0:
                    return session_tracks
                # If session tracks are empty but data provider has data, sync it and return
                if data and isinstance(data, list) and len(data) > 0:
                    st.session_state.simulation_tracks = data
                    return data
                # If both are empty, return empty list (caller will handle empty state)
                return []
            else:
                # LIVE MODE: Return live data ONLY, NEVER simulation_tracks
                # If no live data, return empty list or None - this is correct behavior
                return data if isinstance(data, list) else []
        except Exception:
            # Fail-safe default
            return []
    
    @staticmethod
    def _initialize_simulation_tracks():
        """Initialize simulation tracks in session state using selected scenario."""
        try:
            from datetime import datetime
            
            # Get selected scenario (default to civil_air_traffic if not set)
            scenario_key = st.session_state.get("selected_scenario", "civil_air_traffic")
            
            # Try to use scenario presets first
            try:
                from abhedya.dashboard.scenario_presets import ScenarioPresets
                time_offset = 0.0  # Start from beginning
                tracks = ScenarioPresets.get_scenario_tracks(scenario_key, time_offset_seconds=time_offset)
            except Exception:
                # Fallback to training data generator if scenario presets unavailable
                from abhedya.simulation.training_data_generator import get_training_generator
                generator = get_training_generator()
                time_offset = 0.0
                tracks = generator.generate_tracking_data(num_tracks=3, time_offset_seconds=time_offset)
            
            # Store in session state
            st.session_state.simulation_tracks = tracks
            st.session_state.simulation_last_update = datetime.now()
            st.session_state.simulation_initialized = True
            
            # Initialize simulation start time for scenario-based motion
            if 'simulation_start_time' not in st.session_state:
                st.session_state.simulation_start_time = datetime.now()
        except Exception:
            # Initialization failed — provide safe defaults and informational message
            st.info("ℹ️ Monitoring Only — Training data initializing")
            st.session_state.simulation_tracks = []
            st.session_state.simulation_initialized = False
    
    @staticmethod
    def _update_simulation_tracks():
        """
        Update simulation tracks using deterministic kinematics.
        
        KINEMATIC OBJECTS ONLY - Targets are NOT agents:
        - No reactions, no decisions, no autonomous behavior
        - Pure kinematic motion: position(t) = initial_position + velocity × Δt
        - Motion updates only on Streamlit rerun OR Plotly animation frames
        - Δt derived from session timestamp
        - Motion is slow, smooth, professional
        - No acceleration unless explicitly defined
        """
        try:
            from datetime import datetime
            
            if not st.session_state.get('simulation_initialized', False):
                return
            
            # Get current time (session timestamp)
            current_time = datetime.now()
            
            # Get selected scenario (default to civil_air_traffic if not set)
            scenario_key = st.session_state.get("selected_scenario", "civil_air_traffic")
            
            # Try to use scenario presets first (deterministic kinematics)
            try:
                from abhedya.dashboard.scenario_presets import ScenarioPresets
                
                # Calculate Δt from session timestamp (time since scenario start)
                # This ensures deterministic, reproducible motion
                if 'simulation_start_time' not in st.session_state:
                    st.session_state.simulation_start_time = current_time
                
                # Δt = current_time - start_time (in seconds)
                delta_t = (current_time - st.session_state.simulation_start_time).total_seconds()
                
                # Get tracks using deterministic kinematics: position(t) = initial_position + velocity × Δt
                # Targets are kinematic objects - no reactions, no decisions, no autonomous behavior
                tracks = ScenarioPresets.get_scenario_tracks(scenario_key, time_offset_seconds=delta_t)
                
                # Ensure sensor_contributions are present (added by ScenarioPresets)
                # ADVISORY ONLY — READ-ONLY EXTENSION
                for track in tracks:
                    if not isinstance(track, dict):
                        continue
                    if "sensor_contributions" not in track:
                        # Fallback: balanced contributions
                        track["sensor_contributions"] = {
                            "Surveillance Radar": 0.45,
                            "Precision Tracking Radar": 0.35,
                            "Passive RF / ESM": 0.20
                        }
                
                # Store updated tracks
                st.session_state.simulation_tracks = tracks
                st.session_state.simulation_last_update = current_time
                return
            except Exception:
                # Fallback to training data generator if scenario presets unavailable
                from abhedya.simulation.training_data_generator import get_training_generator
                generator = get_training_generator()
                time_offset = generator.get_time_offset()
            
            # Update tracks in-place using incremental motion (avoid teleporting)
            old_tracks = st.session_state.get('simulation_tracks', [])
            updated_tracks = []

            for track in old_tracks:
                if not isinstance(track, dict):
                    continue

                pos = track.get('position', {})
                vel = track.get('velocity', {})

                try:
                    vx = float(vel.get('vx', 0.0)) if isinstance(vel.get('vx'), (int, float)) else 0.0
                    vy = float(vel.get('vy', 0.0)) if isinstance(vel.get('vy'), (int, float)) else 0.0
                    vz = float(vel.get('vz', 0.0)) if isinstance(vel.get('vz'), (int, float)) else 0.0

                    x = float(pos.get('x', 0.0)) if isinstance(pos.get('x'), (int, float)) else 0.0
                    y = float(pos.get('y', 0.0)) if isinstance(pos.get('y'), (int, float)) else 0.0
                    z = float(pos.get('z', 0.0)) if isinstance(pos.get('z'), (int, float)) else 0.0

                    # Incrementally update position
                    new_x = x + vx * elapsed
                    new_y = y + vy * elapsed
                    new_z = z + vz * elapsed

                    track['position'] = {'x': new_x, 'y': new_y, 'z': new_z}
                    track['timestamp'] = current_time.isoformat()

                    # Update heading if possible
                    try:
                        track['heading_degrees'] = (math.degrees(math.atan2(vy, vx)) + 360) % 360
                    except Exception:
                        pass

                    # Preserve confidence and other metadata
                    updated_tracks.append(track)
                except Exception:
                    # On error preserve original track
                    updated_tracks.append(track)

            # If we had no existing tracks, generate a fresh set as fallback
            if not updated_tracks:
                tracks = generator.generate_tracking_data(num_tracks=3, time_offset_seconds=time_offset)
                updated_tracks = tracks
            
            # Ensure sensor_contributions are present for all tracks
            # ADVISORY ONLY — READ-ONLY EXTENSION
            for track in updated_tracks:
                if not isinstance(track, dict):
                    continue
                if "sensor_contributions" not in track:
                    # Fallback: balanced contributions
                    track["sensor_contributions"] = {
                        "Surveillance Radar": 0.45,
                        "Precision Tracking Radar": 0.35,
                        "Passive RF / ESM": 0.20
                    }

            # Update last update time and store tracks
            st.session_state.simulation_last_update = current_time
            st.session_state.simulation_tracks = updated_tracks
        except Exception:
            # Preserve existing tracks and inform user that simulation is initializing
            st.info("ℹ️ Monitoring Only — Training data initializing")
            return
    
    @staticmethod
    def get_threat_assessment_data() -> Optional[Dict[str, Any]]:
        """
        Get threat assessment data.
        
        Uses unified data provider to eliminate branching logic duplication.
        
        Returns:
            Threat assessment data or None if unavailable
        """
        try:
            from abhedya.dashboard.data_provider import UnifiedDataProvider
            return UnifiedDataProvider.get_threat_assessment_data()
        except Exception:
            # Fail-safe default
            return {
                'threat_level': 'LOW',
                'confidence': 0.0,
                'reasoning': [],
                'risk_score': 0.0,
                'is_simulation': False,
                'simulation_label': 'MONITORING ONLY'
            }
    
    @staticmethod
    def get_advisory_state() -> Optional[Dict[str, Any]]:
        """
        Get advisory system state.
        
        Uses unified data provider to eliminate branching logic duplication.
        
        Returns:
            Advisory state or None if unavailable
        """
        try:
            from abhedya.dashboard.data_provider import UnifiedDataProvider
            return UnifiedDataProvider.get_advisory_state()
        except Exception:
            # Fail-safe default
            return {
                'advisory_state': 'MONITORING_ONLY',
                'confidence': 0.0,
                'reasoning': ['Initialization in progress'],
                'is_simulation': False,
                'simulation_label': 'MONITORING ONLY'
            }
    
    @staticmethod
    def get_intent_assessment_data() -> Optional[Dict[str, Any]]:
        """
        Get intent assessment data.
        
        Uses unified data provider to eliminate branching logic duplication.
        
        Returns:
            Intent assessment data or None if unavailable
        """
        try:
            from abhedya.dashboard.data_provider import UnifiedDataProvider
            return UnifiedDataProvider.get_intent_assessment_data()
        except Exception:
            # Fail-safe default
            return {
                'intent_probabilities': {'transit': 0.0, 'surveillance': 0.0, 'hostile': 0.0},
                'intent_confidence': 0.0,
                'reasoning': [],
                'is_simulation': False,
                'simulation_label': 'MONITORING ONLY'
            }
    
    @staticmethod
    def handle_error(error: Exception, context: str = ""):
        """
        Handle errors gracefully.
        
        Args:
            error: Exception that occurred
            context: Context where error occurred
        """
        # Replace hard error presentation with informational initialization message.
        st.info("ℹ️ Monitoring Only — Training data initializing")
        # Log error details for debugging if requested
        if st.session_state.get('debug_mode', False):
            st.code(traceback.format_exc())
    
    @staticmethod
    def is_training_mode() -> bool:
        """Check if training mode is enabled."""
        return st.session_state.get('training_mode', False)
    
    @staticmethod
    def is_shadow_mode() -> bool:
        """Check if shadow mode is enabled."""
        return st.session_state.get('shadow_mode', False)
    
    @staticmethod
    def get_current_mode() -> str:
        """
        Get current operational mode.
        
        Returns:
            'training', 'shadow', or 'live'
        """
        if st.session_state.get('training_mode', False):
            return 'training'
        elif st.session_state.get('shadow_mode', False):
            return 'shadow'
        else:
            return 'live'
    
    @staticmethod
    def is_audio_enabled() -> bool:
        """Check if audio is enabled."""
        return st.session_state.get('audio_enabled', False)
    
    @staticmethod
    def acknowledge_item(item_id: str):
        """
        Acknowledge an item (non-binding).
        
        Args:
            item_id: ID of item to acknowledge
        """
        # Input validation
        if not isinstance(item_id, str) or not item_id:
            return
        
        try:
            if 'acknowledged_items' not in st.session_state:
                st.session_state.acknowledged_items = set()
            st.session_state.acknowledged_items.add(str(item_id))
        except Exception:
            # Fail silently - don't crash dashboard
            pass
    
    @staticmethod
    def is_acknowledged(item_id: str) -> bool:
        """
        Check if an item is acknowledged.
        
        Args:
            item_id: ID of item to check
            
        Returns:
            True if acknowledged, False otherwise (safe default)
        """
        # Input validation
        if not isinstance(item_id, str) or not item_id:
            return False
        
        try:
            return str(item_id) in st.session_state.get('acknowledged_items', set())
        except Exception:
            # Safe default: not acknowledged on error
            return False

