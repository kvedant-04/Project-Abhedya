"""
Training & Simulation Data Generator

Generates realistic, deterministic synthetic data for Training & Simulation Mode.
All data is clearly labeled as simulation/training data.

CRITICAL CONSTRAINTS:
- Physically plausible data only
- Statistically consistent
- Ethically safe
- Deterministic (seed-based)
- Clearly labeled as SIMULATION / TRAINING DATA
"""

import math
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

from abhedya.domain.value_objects import Coordinates, Velocity
import streamlit as st


@dataclass
class SyntheticTrack:
    """Synthetic track data for training mode."""
    track_id: str
    object_type: str  # "AERIAL_DRONE", "AIRCRAFT", "UNKNOWN_OBJECT"
    position: Coordinates
    velocity: Velocity
    altitude_meters: float
    heading_degrees: float
    speed_meters_per_second: float
    confidence: float
    timestamp: datetime


class TrainingDataGenerator:
    """
    Generates realistic synthetic data for Training & Simulation Mode.
    
    All data is deterministic and physically plausible.
    """
    
    def __init__(self, seed: Optional[int] = None):
        """
        Initialize training data generator.
        
        Args:
            seed: Optional random seed for deterministic generation
        """
        self.seed = seed or 42
        self._time_offset = 0.0
        self._track_states = {}
        # Scenario evolution internal parameters
        self._cycle_length = 240.0  # full scenario cycle in seconds
        self._phase_durations = {
            'phase1': 80.0,
            'phase2': 60.0,
            'phase3': 60.0,
            'phase4': 40.0
        }
    
    def generate_tracking_data(
        self,
        num_tracks: int = 3,
        time_offset_seconds: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Generate synthetic tracking data.
        
        Args:
            num_tracks: Number of tracks to generate
            time_offset_seconds: Time offset for animation
            
        Returns:
            List of track dictionaries
        """
        tracks = []
        
        # Determine current scenario phase and progress
        phase, phase_progress = self._phase_from_time(time_offset_seconds)

        for i in range(num_tracks):
            track_id = f"TRAIN_{i+1:03d}"
            
            # Generate deterministic track based on index and time
            # Base circular motion
            base_angle = (i * 2 * math.pi / num_tracks)
            angle = base_angle + (time_offset_seconds * 0.1)
            base_radius = 50000.0 + (i * 10000.0)  # 50-70 km radius

            # Phase-dependent adjustments
            radius = base_radius
            speed = 100.0 + (i * 20.0)
            z = 5000.0 + (i * 1000.0)

            if phase == 'phase2':
                # Loitering: reduce forward speed, add small oscillation
                speed *= 0.5 + 0.25 * (1.0 - phase_progress)
                angle += math.sin(time_offset_seconds * 0.5 + i) * 0.1
                radius += math.cos(time_offset_seconds * 0.3 + i) * 2000.0
            elif phase == 'phase3':
                # Zone probing: slowly reduce radius to probe inner zones
                radius = base_radius * (1.0 - 0.25 * phase_progress)
                speed *= 0.8 + 0.4 * phase_progress
                z = z * (1.0 - 0.1 * phase_progress)
            elif phase == 'phase4':
                # De-escalation: return toward nominal
                radius = base_radius * (1.0 + 0.05 * (1.0 - phase_progress))
                speed *= 0.9

            # Compute positions
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)

            # Velocity based on circular motion approximation
            vx = -speed * math.sin(angle)
            vy = speed * math.cos(angle)
            vz = 0.0
            
            # Object type rotation
            object_types = ["AIRCRAFT", "AERIAL_DRONE", "UNKNOWN_OBJECT"]
            object_type = object_types[i % len(object_types)]
            
            track = {
                "track_id": track_id,
                "object_type": object_type,
                "position": {
                    "x": x,
                    "y": y,
                    "z": z
                },
                "velocity": {
                    "vx": vx,
                    "vy": vy,
                    "vz": vz,
                    "speed": speed
                },
                "altitude_meters": z,
                "heading_degrees": math.degrees(angle + math.pi / 2),
                "speed_meters_per_second": speed,
                # Confidence adjusted by phase (more concern -> slightly lower confidence)
                "confidence": max(0.2, min(0.95, 0.80 - 0.15 * (1 if phase == 'phase3' else 0) + (i * 0.02))),
                "timestamp": (datetime.utcnow() + timedelta(seconds=time_offset_seconds)).isoformat(),
                "is_simulation": True,
                "simulation_label": "SIMULATION / TRAINING DATA"
            }
            
            tracks.append(track)
        
        return tracks
    
    def generate_early_warning_data(
        self,
        time_offset_seconds: float = 0.0
    ) -> Dict[str, Any]:
        """
        Generate synthetic early warning data.
        
        Args:
            time_offset_seconds: Time offset for state transitions
            
        Returns:
            Early warning data dictionary
        """
        phase, phase_progress = self._phase_from_time(time_offset_seconds)

        if phase == 'phase1':
            state = 'NORMAL'
            confidence = 0.85
            reasoning = ['Track behavior within baseline', 'No convergence detected']
        elif phase == 'phase2':
            state = 'ELEVATED'
            confidence = 0.75 + 0.05 * phase_progress
            reasoning = ['Loitering behavior detected', 'Minor velocity anomalies observed']
        elif phase == 'phase3':
            state = 'HIGH'
            confidence = 0.70 + 0.15 * phase_progress
            reasoning = ['Increased proximity to protected zones', 'Convergence patterns strengthening']
        else:
            state = 'NORMAL'
            confidence = 0.80 - 0.1 * phase_progress
            reasoning = ['De-escalation in progress', 'Track dispersing from protected area']

        return {
            'warning_state': state,
            'confidence': max(0.0, min(1.0, confidence)),
            'reasoning': reasoning,
            'is_simulation': True,
            'simulation_label': 'SIMULATION / TRAINING DATA'
        }
    
    def generate_threat_assessment_data(
        self,
        time_offset_seconds: float = 0.0
    ) -> Dict[str, Any]:
        """
        Generate synthetic threat assessment data.
        
        Args:
            time_offset_seconds: Time offset for state transitions
            
        Returns:
            Threat assessment data dictionary
        """
        # Threat assessment coupled to intent probabilities and phase
        phase, phase_progress = self._phase_from_time(time_offset_seconds)
        intent = self.generate_intent_assessment_data(time_offset_seconds)
        hostile_prob = intent.get('intent_probabilities', {}).get('hostile', 0.0)
        surveillance_prob = intent.get('intent_probabilities', {}).get('surveillance', 0.0)

        # Base threat level from phase
        if phase == 'phase1':
            base = 'LOW'
            confidence = 0.75
            reasoning = 'Normal transit pattern'
        elif phase == 'phase2':
            base = 'MEDIUM'
            confidence = 0.70 + 0.1 * phase_progress
            reasoning = 'Loitering and heading changes observed'
        elif phase == 'phase3':
            base = 'HIGH'
            confidence = 0.65 + 0.2 * phase_progress
            reasoning = 'Probing behavior near protected zone'
        else:
            base = 'LOW'
            confidence = 0.70 - 0.1 * phase_progress
            reasoning = 'De-escalation observed'

        # Boost threat confidence if hostile prob increases
        confidence = max(0.0, min(1.0, confidence + 0.25 * hostile_prob))

        # Map base to threat level string
        threat_level = base

        return {
            'threat_level': threat_level,
            'confidence': confidence,
            'reasoning': reasoning,
            'risk_score': {
                'LOW': 0.2,
                'MEDIUM': 0.5,
                'HIGH': 0.8
            }.get(threat_level, 0.2),
            'is_simulation': True,
            'simulation_label': 'SIMULATION / TRAINING DATA'
        }
    
    def generate_intent_assessment_data(
        self,
        time_offset_seconds: float = 0.0
    ) -> Dict[str, Any]:
        """
        Generate synthetic intent assessment data.
        
        Args:
            time_offset_seconds: Time offset for state transitions
            
        Returns:
            Intent assessment data dictionary
        """
        # Deterministic, phase-driven intent probabilities
        phase, phase_progress = self._phase_from_time(time_offset_seconds)

        # Base probabilities per phase
        if phase == 'phase1':
            transit = 0.7
            surveillance = 0.15
            hostile = 0.05
        elif phase == 'phase2':
            transit = 0.4
            surveillance = 0.45 * (0.5 + 0.5 * phase_progress)
            hostile = 0.05 + 0.05 * phase_progress
        elif phase == 'phase3':
            transit = 0.2
            surveillance = 0.4
            hostile = 0.2 + 0.3 * phase_progress
        else:
            transit = 0.6
            surveillance = 0.2
            hostile = 0.05

        # Normalize if needed and smooth edges
        total = transit + surveillance + hostile
        if total > 1.0:
            transit /= total
            surveillance /= total
            hostile /= total

        reasoning = []
        if transit > 0.4:
            reasoning.append('Transit-like speed and trajectory characteristics')
        if surveillance > 0.3:
            reasoning.append('Sustained loitering or surveillance pattern detected')
        if hostile > 0.12:
            reasoning.append('Indicators of potential hostile intent (advisory only)')

        if not reasoning:
            reasoning.append('Insufficient data for detailed intent assessment')

        return {
            'intent_probabilities': {'transit': transit, 'surveillance': surveillance, 'hostile': hostile},
            'intent_confidence': max(0.0, min(1.0, 0.6 + 0.3 * (surveillance + hostile))),
            'reasoning': reasoning,
            'is_training_mode': True,
            'is_simulation': True,
            'simulation_label': 'SIMULATION / TRAINING DATA'
        }
    
    def generate_ew_analysis_data(
        self,
        time_offset_seconds: float = 0.0
    ) -> Dict[str, Any]:
        """
        Generate synthetic electronic warfare analysis data.
        
        Args:
            time_offset_seconds: Time offset for state transitions
            
        Returns:
            EW analysis data dictionary
        """
        # EW analysis influenced by intent (surveillance/hostile) and phase
        phase, phase_progress = self._phase_from_time(time_offset_seconds)
        intent = self.generate_intent_assessment_data(time_offset_seconds)
        surv = intent.get('intent_probabilities', {}).get('surveillance', 0.0)
        hostile = intent.get('intent_probabilities', {}).get('hostile', 0.0)

        # Confidence increases with surveillance and hostile intent
        base_conf = 0.80
        confidence = base_conf + 0.2 * (surv + hostile)

        if surv + hostile > 0.3 or phase == 'phase3':
            ew_state = 'ANOMALOUS'
            reasoning = ['Elevated RF activity correlated with surveillance/hostile indicators', 'Spectral patterns deviate from baseline']
        else:
            ew_state = 'NORMAL'
            reasoning = ['RF spectrum within expected baseline', 'No significant anomalies detected']

        return {
            'ew_state': ew_state,
            'confidence': max(0.0, min(1.0, confidence)),
            'reasoning': reasoning,
            'is_simulation': True,
            'simulation_label': 'SIMULATION / TRAINING DATA'
        }
    
    def generate_cybersecurity_data(
        self,
        time_offset_seconds: float = 0.0
    ) -> Dict[str, Any]:
        """
        Generate synthetic cybersecurity data.
        
        Args:
            time_offset_seconds: Time offset for state transitions
            
        Returns:
            Cybersecurity data dictionary
        """
        # Cyber events weakly correlated with phase and intent
        phase, phase_progress = self._phase_from_time(time_offset_seconds)
        intent = self.generate_intent_assessment_data(time_offset_seconds)
        hostile = intent.get('intent_probabilities', {}).get('hostile', 0.0)

        if phase == 'phase3' and hostile > 0.15:
            cybersecurity_state = 'SUSPICIOUS'
            confidence = 0.60 + 0.2 * hostile
            reasoning = ['Unusual access pattern correlated with elevated hostile indicators', 'Requires human operator review']
        else:
            cybersecurity_state = 'NORMAL'
            confidence = 0.85
            reasoning = ['System logs within normal patterns', 'No integrity violations detected']

        return {
            'cybersecurity_state': cybersecurity_state,
            'confidence': max(0.0, min(1.0, confidence)),
            'reasoning': reasoning,
            'is_simulation': True,
            'simulation_label': 'SIMULATION / TRAINING DATA'
        }
    
    def generate_advisory_state(
        self,
        time_offset_seconds: float = 0.0
    ) -> Dict[str, Any]:
        """
        Generate synthetic advisory system state.
        
        Args:
            time_offset_seconds: Time offset for state transitions
            
        Returns:
            Advisory state dictionary
        """
        phase, phase_progress = self._phase_from_time(time_offset_seconds)

        if phase == 'phase1':
            system_mode = 'MONITORING_ONLY'
            confidence = 0.85
            reasoning = 'System operating in monitoring mode. All assessments within normal parameters.'
        elif phase == 'phase2':
            system_mode = 'ADVISORY_RECOMMENDATION'
            confidence = 0.75 + 0.05 * phase_progress
            reasoning = 'Suspicious behavior observed. Advisory only — human review recommended.'
        elif phase == 'phase3':
            system_mode = 'HUMAN_APPROVAL_REQUIRED'
            confidence = 0.70 + 0.15 * phase_progress
            reasoning = 'Elevated scenario: human operator attention recommended (advisory only).'
        else:
            system_mode = 'MONITORING_ONLY'
            confidence = 0.80 - 0.1 * phase_progress
            reasoning = 'De-escalation observed — returning to monitoring posture.'

        return {
            'system_mode': system_mode,
            'confidence': max(0.0, min(1.0, confidence)),
            'reasoning': reasoning,
            'is_simulation': True,
            'simulation_label': 'SIMULATION / TRAINING DATA'
        }
    
    def get_time_offset(self) -> float:
        """
        Get current time offset for animation.
        
        Returns:
            Time offset in seconds
        """
        if 'simulation_start_time' not in st.session_state:
            st.session_state.simulation_start_time = datetime.now()
        
        elapsed = (datetime.now() - st.session_state.simulation_start_time).total_seconds()
        return elapsed

    def _phase_from_time(self, time_offset_seconds: float) -> Tuple[str, float]:
        """
        Determine scenario phase and normalized progress within the phase.
        Returns: (phase_name, progress_in_phase[0..1])
        """
        # Normalize into cycle
        t = time_offset_seconds % self._cycle_length
        accum = 0.0
        for phase, dur in self._phase_durations.items():
            if t < accum + dur:
                progress = (t - accum) / dur if dur > 0 else 0.0
                return (phase, float(progress))
            accum += dur
        # Fallback to last phase
        last_phase = list(self._phase_durations.keys())[-1]
        return (last_phase, 1.0)

    def generate_all(self, time_offset_seconds: float = 0.0) -> Dict[str, Any]:
        """
        Generate the full, stable training data payload with a strict contract.

        Returns a dict with keys: tracks, threat, intent, early_warning,
        electronic_warfare, cybersecurity. Values are never None.
        """
        tracks = self.generate_tracking_data(num_tracks=3, time_offset_seconds=time_offset_seconds)
        threat = self.generate_threat_assessment_data(time_offset_seconds)
        intent = self.generate_intent_assessment_data(time_offset_seconds)
        early_warning = self.generate_early_warning_data(time_offset_seconds)
        electronic_warfare = self.generate_ew_analysis_data(time_offset_seconds)
        cybersecurity = self.generate_cybersecurity_data(time_offset_seconds)

        return {
            "tracks": tracks or [],
            "threat": threat or {"threat_level": "LOW", "confidence": 0.0, "reasoning": [], "risk_score": 0.0, "is_simulation": True, "simulation_label": "SIMULATION / TRAINING DATA"},
            "intent": intent or {"intent_probabilities": {"transit": 0.0, "surveillance": 0.0, "hostile": 0.0}, "intent_confidence": 0.0, "reasoning": [], "is_simulation": True, "simulation_label": "SIMULATION / TRAINING DATA"},
            "early_warning": early_warning or {"warning_state": "NORMAL", "confidence": 0.0, "reasoning": [], "is_simulation": True, "simulation_label": "SIMULATION / TRAINING DATA"},
            "electronic_warfare": electronic_warfare or {"ew_state": "NORMAL", "confidence": 0.0, "reasoning": [], "is_simulation": True, "simulation_label": "SIMULATION / TRAINING DATA"},
            "cybersecurity": cybersecurity or {"cybersecurity_state": "NORMAL", "confidence": 0.0, "reasoning": [], "is_simulation": True, "simulation_label": "SIMULATION / TRAINING DATA"}
        }


# Global instance (lazy initialization)
_training_generator: Optional[TrainingDataGenerator] = None


def get_training_generator() -> TrainingDataGenerator:
    """
    Get or create training data generator instance.
    
    Returns:
        TrainingDataGenerator instance
    """
    global _training_generator
    if _training_generator is None:
        _training_generator = TrainingDataGenerator(seed=42)
    return _training_generator


