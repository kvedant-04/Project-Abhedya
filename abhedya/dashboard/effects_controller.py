"""
Effects Controller

Controls visual and audio effects (advisory indicators only).
"""

import streamlit as st
from typing import Optional, Dict


class EffectsController:
    """
    Controls visual and audio effects.

    All effects are advisory indicators only.
    Audio is optional and disabled by default.
    """

    # -------------------------
    # SAFE STATE INITIALIZATION
    # -------------------------
    @staticmethod
    def _initialize_state():
        # EffectsController must not create or mutate training-mode widgets/state.
        # State defaults are managed centrally (app.py / state_manager).
        return

    # -------------------------
    # TRAINING MODE TOGGLE
    # -------------------------
    @staticmethod
    def render_training_mode_toggle():
        """
        Render training mode toggle EXACTLY ONCE per run.
        """
        # No widgets here. Return current training-mode value for callers that
        # previously expected a boolean. Do not mutate session_state.
        return st.session_state.get("training_mode", False)

    # -------------------------
    # AUDIO TOGGLE
    # -------------------------
    @staticmethod
    def render_audio_toggle():
        """
        Render audio toggle EXACTLY ONCE per run.
        """
        # No widgets in EffectsController. Audio widget is managed by the UI
        # (app.py). Return current audio-enabled state for callers.
        return st.session_state.get("audio_enabled", False)

    # -------------------------
    # AUDIO LOGIC
    # -------------------------
    @staticmethod
    def should_play_audio(severity: str) -> bool:
        if not isinstance(severity, str):
            return False

        if not st.session_state.get("audio_enabled", False):
            return False

        severity = severity.upper()

        if severity in ("ELEVATED", "HIGH"):
            return True

        if severity == "CRITICAL":
            return st.session_state.get("training_mode", False)

        return False

    @staticmethod
    def get_audio_message(severity: str) -> Optional[str]:
        if not EffectsController.should_play_audio(severity):
            return None

        return {
            "ELEVATED": "🔔 Elevated advisory state detected",
            "HIGH": "⚠ High advisory state detected",
            "CRITICAL": "🚨 Critical simulated scenario (Training Mode)",
        }.get(severity.upper())

    @staticmethod
    def render_audio_indicator(severity: str):
        message = EffectsController.get_audio_message(severity)
        if not message:
            return

        st.markdown(
            f"""
            <div style="
                background-color: #FFF7E6;
                border-left: 4px solid #FAAD14;
                padding: 12px;
                border-radius: 4px;
                margin: 12px 0;
            ">
                <strong>{message}</strong><br>
                <small>Advisory indicator only.</small>
            </div>
            """,
            unsafe_allow_html=True
        )

    # -------------------------
    # VISUAL THEMING
    # -------------------------
    @staticmethod
    def apply_visual_theme(severity: str) -> Dict[str, str]:
        try:
            from abhedya.dashboard.visual_components import SeverityThemeController
            return SeverityThemeController.get_theme(
                severity,
                st.session_state.get("training_mode", False)
            )
        except Exception:
            return {
                "primary": "#4A90E2",
                "secondary": "#E3F2FD",
                "text": "#1E3A5F",
            }
