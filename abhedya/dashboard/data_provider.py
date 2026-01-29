"""
Unified Data Provider

Provides unified interface for data fetching across all modes.
Eliminates branching logic duplication by using a single provider pattern.

ADVISORY ONLY - All data is advisory and informational.
"""

import streamlit as st
from typing import List, Dict, Any, Optional
from datetime import datetime


class UnifiedDataProvider:
    """
    Unified data provider that routes to appropriate source based on mode.
    
    This eliminates branching logic duplication by providing a single interface
    that handles mode detection internally.
    """
    
    @staticmethod
    def get_tracking_data() -> List[Dict[str, Any]]:
        """
        Get tracking data from appropriate source based on mode.
        
        Returns:
            List of track dictionaries (empty if no data available)
        """
        training_mode = st.session_state.get('training_mode', False)
        shadow_mode = st.session_state.get('shadow_mode', False)
        
        if training_mode:
            # Pure simulation mode
            return UnifiedDataProvider._get_simulation_tracking_data()
        elif shadow_mode:
            # Shadow mode: merge live + simulation
            return UnifiedDataProvider._get_shadow_tracking_data()
        else:
            # Live mode: use live stub provider
            return UnifiedDataProvider._get_live_tracking_data()
    
    @staticmethod
    def get_early_warning_data() -> Optional[Dict[str, Any]]:
        """Get early warning data from appropriate source."""
        training_mode = st.session_state.get('training_mode', False)
        shadow_mode = st.session_state.get('shadow_mode', False)
        
        if training_mode:
            return UnifiedDataProvider._get_simulation_early_warning_data()
        elif shadow_mode:
            return UnifiedDataProvider._get_shadow_early_warning_data()
        else:
            return UnifiedDataProvider._get_live_early_warning_data()
    
    @staticmethod
    def get_ew_analysis_data() -> Optional[Dict[str, Any]]:
        """Get EW analysis data from appropriate source."""
        training_mode = st.session_state.get('training_mode', False)
        shadow_mode = st.session_state.get('shadow_mode', False)
        
        if training_mode:
            return UnifiedDataProvider._get_simulation_ew_data()
        elif shadow_mode:
            return UnifiedDataProvider._get_shadow_ew_data()
        else:
            return UnifiedDataProvider._get_live_ew_data()
    
    @staticmethod
    def get_cybersecurity_data() -> Optional[Dict[str, Any]]:
        """Get cybersecurity data from appropriate source."""
        training_mode = st.session_state.get('training_mode', False)
        shadow_mode = st.session_state.get('shadow_mode', False)
        
        if training_mode:
            return UnifiedDataProvider._get_simulation_cybersecurity_data()
        elif shadow_mode:
            return UnifiedDataProvider._get_shadow_cybersecurity_data()
        else:
            return UnifiedDataProvider._get_live_cybersecurity_data()
    
    @staticmethod
    def get_threat_assessment_data() -> Optional[Dict[str, Any]]:
        """Get threat assessment data from appropriate source."""
        training_mode = st.session_state.get('training_mode', False)
        shadow_mode = st.session_state.get('shadow_mode', False)
        
        if training_mode:
            return UnifiedDataProvider._get_simulation_threat_data()
        elif shadow_mode:
            return UnifiedDataProvider._get_shadow_threat_data()
        else:
            return UnifiedDataProvider._get_live_threat_data()
    
    @staticmethod
    def get_intent_assessment_data() -> Optional[Dict[str, Any]]:
        """Get intent assessment data from appropriate source."""
        training_mode = st.session_state.get('training_mode', False)
        shadow_mode = st.session_state.get('shadow_mode', False)
        
        if training_mode:
            return UnifiedDataProvider._get_simulation_intent_data()
        elif shadow_mode:
            return UnifiedDataProvider._get_shadow_intent_data()
        else:
            return UnifiedDataProvider._get_live_intent_data()
    
    @staticmethod
    def get_advisory_state() -> Optional[Dict[str, Any]]:
        """Get advisory state from appropriate source."""
        training_mode = st.session_state.get('training_mode', False)
        shadow_mode = st.session_state.get('shadow_mode', False)
        
        if training_mode:
            return UnifiedDataProvider._get_simulation_advisory_state()
        elif shadow_mode:
            return UnifiedDataProvider._get_shadow_advisory_state()
        else:
            return UnifiedDataProvider._get_live_advisory_state()
    
    # Simulation data methods
    @staticmethod
    def _get_simulation_tracking_data() -> List[Dict[str, Any]]:
        """Get tracking data from simulation engine."""
        try:
            from abhedya.simulation.training_data_generator import get_training_generator
            generator = get_training_generator()
            time_offset = generator.get_time_offset()
            return generator.generate_tracking_data(num_tracks=3, time_offset_seconds=time_offset)
        except Exception:
            return []
    
    @staticmethod
    def _get_simulation_early_warning_data() -> Optional[Dict[str, Any]]:
        """Get early warning data from simulation engine."""
        try:
            from abhedya.simulation.training_data_generator import get_training_generator
            generator = get_training_generator()
            time_offset = generator.get_time_offset()
            return generator.generate_early_warning_data(time_offset)
        except Exception:
            return None
    
    @staticmethod
    def _get_simulation_ew_data() -> Optional[Dict[str, Any]]:
        """Get EW analysis data from simulation engine."""
        try:
            from abhedya.simulation.training_data_generator import get_training_generator
            generator = get_training_generator()
            time_offset = generator.get_time_offset()
            return generator.generate_ew_analysis_data(time_offset)
        except Exception:
            return None
    
    @staticmethod
    def _get_simulation_cybersecurity_data() -> Optional[Dict[str, Any]]:
        """Get cybersecurity data from simulation engine."""
        try:
            from abhedya.simulation.training_data_generator import get_training_generator
            generator = get_training_generator()
            time_offset = generator.get_time_offset()
            return generator.generate_cybersecurity_data(time_offset)
        except Exception:
            return None
    
    @staticmethod
    def _get_simulation_threat_data() -> Optional[Dict[str, Any]]:
        """Get threat assessment data from simulation engine."""
        try:
            from abhedya.simulation.training_data_generator import get_training_generator
            generator = get_training_generator()
            time_offset = generator.get_time_offset()
            return generator.generate_threat_assessment_data(time_offset)
        except Exception:
            return None
    
    @staticmethod
    def _get_simulation_intent_data() -> Optional[Dict[str, Any]]:
        """Get intent assessment data from simulation engine."""
        try:
            from abhedya.simulation.training_data_generator import get_training_generator
            generator = get_training_generator()
            time_offset = generator.get_time_offset()
            return generator.generate_intent_assessment_data(time_offset)
        except Exception:
            return None
    
    @staticmethod
    def _get_simulation_advisory_state() -> Optional[Dict[str, Any]]:
        """Get advisory state from simulation engine."""
        try:
            from abhedya.simulation.training_data_generator import get_training_generator
            generator = get_training_generator()
            time_offset = generator.get_time_offset()
            return generator.generate_advisory_state(time_offset)
        except Exception:
            return None
    
    # Shadow mode methods (merge live + simulation)
    @staticmethod
    def _get_shadow_tracking_data() -> List[Dict[str, Any]]:
        """Get shadow mode tracking data (live + simulation overlay)."""
        try:
            from abhedya.dashboard.live_stub_provider import LiveStubProvider
            from abhedya.simulation.training_data_generator import get_training_generator
            
            # Get live data
            live_data = LiveStubProvider.get_tracking_data()
            
            # Get simulation data
            generator = get_training_generator()
            time_offset = generator.get_time_offset()
            sim_data = generator.generate_tracking_data(num_tracks=3, time_offset_seconds=time_offset)
            
            # Merge: live data first, then simulation overlay
            merged = list(live_data) if live_data else []
            
            # Add simulation tracks with shadow label
            for track in sim_data:
                if isinstance(track, dict):
                    track = track.copy()
                    track['is_shadow'] = True
                    track['shadow_label'] = 'SHADOW MODE — Simulation Overlay'
                    merged.append(track)
            
            return merged
        except Exception:
            return []
    
    @staticmethod
    def _get_shadow_early_warning_data() -> Optional[Dict[str, Any]]:
        """Get shadow mode early warning data."""
        # In shadow mode, prefer live data, fallback to simulation
        try:
            from abhedya.dashboard.live_stub_provider import LiveStubProvider
            live_data = LiveStubProvider.get_early_warning_data()
            if live_data:
                live_data = live_data.copy()
                live_data['is_shadow'] = True
                live_data['shadow_label'] = 'SHADOW MODE — Live Data'
                return live_data
        except Exception:
            pass
        
        # Fallback to simulation
        return UnifiedDataProvider._get_simulation_early_warning_data()
    
    @staticmethod
    def _get_shadow_ew_data() -> Optional[Dict[str, Any]]:
        """Get shadow mode EW analysis data."""
        try:
            from abhedya.dashboard.live_stub_provider import LiveStubProvider
            live_data = LiveStubProvider.get_ew_analysis_data()
            if live_data:
                live_data = live_data.copy()
                live_data['is_shadow'] = True
                live_data['shadow_label'] = 'SHADOW MODE — Live Data'
                return live_data
        except Exception:
            pass
        
        return UnifiedDataProvider._get_simulation_ew_data()
    
    @staticmethod
    def _get_shadow_cybersecurity_data() -> Optional[Dict[str, Any]]:
        """Get shadow mode cybersecurity data."""
        try:
            from abhedya.dashboard.live_stub_provider import LiveStubProvider
            live_data = LiveStubProvider.get_cybersecurity_data()
            if live_data:
                live_data = live_data.copy()
                live_data['is_shadow'] = True
                live_data['shadow_label'] = 'SHADOW MODE — Live Data'
                return live_data
        except Exception:
            pass
        
        return UnifiedDataProvider._get_simulation_cybersecurity_data()
    
    @staticmethod
    def _get_shadow_threat_data() -> Optional[Dict[str, Any]]:
        """Get shadow mode threat assessment data."""
        try:
            from abhedya.dashboard.live_stub_provider import LiveStubProvider
            live_data = LiveStubProvider.get_threat_assessment_data()
            if live_data:
                live_data = live_data.copy()
                live_data['is_shadow'] = True
                live_data['shadow_label'] = 'SHADOW MODE — Live Data'
                return live_data
        except Exception:
            pass
        
        return UnifiedDataProvider._get_simulation_threat_data()
    
    @staticmethod
    def _get_shadow_intent_data() -> Optional[Dict[str, Any]]:
        """Get shadow mode intent assessment data."""
        try:
            from abhedya.dashboard.live_stub_provider import LiveStubProvider
            live_data = LiveStubProvider.get_intent_assessment_data()
            if live_data:
                live_data = live_data.copy()
                live_data['is_shadow'] = True
                live_data['shadow_label'] = 'SHADOW MODE — Live Data'
                return live_data
        except Exception:
            pass
        
        return UnifiedDataProvider._get_simulation_intent_data()
    
    @staticmethod
    def _get_shadow_advisory_state() -> Optional[Dict[str, Any]]:
        """Get shadow mode advisory state."""
        try:
            from abhedya.dashboard.live_stub_provider import LiveStubProvider
            live_data = LiveStubProvider.get_advisory_state()
            if live_data:
                live_data = live_data.copy()
                live_data['is_shadow'] = True
                live_data['shadow_label'] = 'SHADOW MODE — Live Data'
                return live_data
        except Exception:
            pass
        
        return UnifiedDataProvider._get_simulation_advisory_state()
    
    # Live data methods (use live stub provider)
    @staticmethod
    def _get_live_tracking_data() -> List[Dict[str, Any]]:
        """Get live tracking data."""
        try:
            from abhedya.dashboard.live_stub_provider import LiveStubProvider
            return LiveStubProvider.get_tracking_data()
        except Exception:
            return []
    
    @staticmethod
    def _get_live_early_warning_data() -> Optional[Dict[str, Any]]:
        """Get live early warning data."""
        try:
            from abhedya.dashboard.live_stub_provider import LiveStubProvider
            return LiveStubProvider.get_early_warning_data()
        except Exception:
            return None
    
    @staticmethod
    def _get_live_ew_data() -> Optional[Dict[str, Any]]:
        """Get live EW analysis data."""
        try:
            from abhedya.dashboard.live_stub_provider import LiveStubProvider
            return LiveStubProvider.get_ew_analysis_data()
        except Exception:
            return None
    
    @staticmethod
    def _get_live_cybersecurity_data() -> Optional[Dict[str, Any]]:
        """Get live cybersecurity data."""
        try:
            from abhedya.dashboard.live_stub_provider import LiveStubProvider
            return LiveStubProvider.get_cybersecurity_data()
        except Exception:
            return None
    
    @staticmethod
    def _get_live_threat_data() -> Optional[Dict[str, Any]]:
        """Get live threat assessment data."""
        try:
            from abhedya.dashboard.live_stub_provider import LiveStubProvider
            return LiveStubProvider.get_threat_assessment_data()
        except Exception:
            return None
    
    @staticmethod
    def _get_live_intent_data() -> Optional[Dict[str, Any]]:
        """Get live intent assessment data."""
        try:
            from abhedya.dashboard.live_stub_provider import LiveStubProvider
            return LiveStubProvider.get_intent_assessment_data()
        except Exception:
            return None
    
    @staticmethod
    def _get_live_advisory_state() -> Optional[Dict[str, Any]]:
        """Get live advisory state."""
        try:
            from abhedya.dashboard.live_stub_provider import LiveStubProvider
            return LiveStubProvider.get_advisory_state()
        except Exception:
            return None
