"""
Command and Control Dashboard

Defence-console style professional interface for the Abhedya Air Defense System.
Provides live airspace visualization, threat indicators, and advisory decision support.

ADVISORY ONLY - No autonomous actions.
"""

from abhedya.dashboard.state_manager import DashboardStateManager
from abhedya.dashboard.effects_controller import EffectsController

__all__ = [
    "DashboardStateManager",
    "EffectsController",
]

