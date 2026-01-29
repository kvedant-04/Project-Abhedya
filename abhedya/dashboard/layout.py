"""
Dashboard Layout Components

Authoritative layout and advisory rendering for the Abhedya dashboard.
"""

import streamlit as st
from typing import List, Dict, Any, Optional


class DashboardLayout:
    """Dashboard layout components (UI-only, advisory-only)."""
    
    @staticmethod
    def render_ew_status_indicator(ew_state: str, training_mode: bool = False):
        """
        Render EW status indicator banner.
        
        ADVISORY ONLY — PROFESSIONAL, SUBTLE
        - Small banner or badge (not alarming)
        - NO flashing
        - NO aggressive colors
        - NO game-like effects
        
        Args:
            ew_state: EW environment state (NONE, LOW, MEDIUM, HIGH)
            training_mode: Whether training mode is enabled
        """
        try:
            if not ew_state or ew_state.upper() == 'NONE' or ew_state.upper() == 'NORMAL':
                return  # Don't show indicator if no EW
            
            ew_state_upper = str(ew_state).upper()
            
            # Map to standard states
            if ew_state_upper not in ['LOW', 'MEDIUM', 'HIGH']:
                return
            
            # Color coding (subtle, professional)
            color_map = {
                'LOW': '#FAAD14',      # Amber
                'MEDIUM': '#FF7875',   # Light red
                'HIGH': '#F5222D'      # Red
            }
            bg_color_map = {
                'LOW': '#FFF7E6',      # Light amber background
                'MEDIUM': '#FFE8E8',   # Light red background
                'HIGH': '#FFE8E8'      # Light red background
            }
            
            color = color_map.get(ew_state_upper, '#666666')
            bg_color = bg_color_map.get(ew_state_upper, '#F0F0F0')
            
            # Status text
            status_text = f"Electronic Warfare Environment: {ew_state_upper} — Sensor trust reduced"
            if training_mode:
                status_text += " (SIMULATION / TRAINING DATA)"
            
            st.markdown(
                f"""
                <div style="
                    background-color:{bg_color};
                    border-left:4px solid {color};
                    padding:6px;
                    margin-bottom:8px;
                    border-radius:4px;
                ">
                    <small><strong>⚠️ {status_text}</strong></small><br>
                    <small style="color:#666;">Advisory Only — Confidence visualization adjusted. No autonomous actions.</small>
                </div>
                """,
                unsafe_allow_html=True
            )
        except Exception:
            # Fail silently - don't crash dashboard
            pass

    # ------------------------------------------------------------------
    # GLOBAL / PERSISTENT ELEMENTS
    # ------------------------------------------------------------------

    @staticmethod
    def render_persistent_banner():
        """Render persistent advisory banner on all pages."""
        st.markdown(
            """
            <div style="
                background-color:#F0F0F0;
                border-left:4px solid #4A90E2;
                padding:8px;
                margin-bottom:10px;
                border-radius:4px;
            ">
                <h3 style="margin:0;color:#2c5282;">
                    🛡️ Decision Support System — Advisory Only — No Autonomous Actions
                </h3>
                <p style="margin:6px 0 0 0;color:#555;">
                    All outputs are advisory only. Human operator review and approval required.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    @staticmethod
    def render_mode_awareness_banner():
        """
        Always-visible Mode Awareness Banner.
        
        Shows current operational mode (Live, Training, or Shadow).
        Must be visible at all times to ensure operator awareness.
        """
        training_mode = st.session_state.get("training_mode", False)
        shadow_mode = st.session_state.get("shadow_mode", False)
        
        if training_mode:
            # Training/Simulation Mode
            st.markdown(
                """
                <div style="
                    background:#FFF1F0;
                    border-left:5px solid #F5222D;
                    padding:8px;
                    margin-bottom:10px;
                    border-radius:4px;
                    position:sticky;
                    top:0;
                    z-index:1000;
                ">
                    <strong>⚠️ TRAINING & SIMULATION MODE ACTIVE</strong><br>
                    <small>
                        <strong>SIMULATION / TRAINING DATA</strong> — All displayed data is synthetic.<br>
                        Advisory-only system. No autonomous actions. Confidence values are advisory only.
                    </small>
                </div>
                """,
                unsafe_allow_html=True
            )
        elif shadow_mode:
            # Shadow Mode
            st.markdown(
                """
                <div style="
                    background:#FFF7E6;
                    border-left:5px solid #FAAD14;
                    padding:8px;
                    margin-bottom:10px;
                    border-radius:4px;
                    position:sticky;
                    top:0;
                    z-index:1000;
                ">
                    <strong>🔍 SHADOW MODE ACTIVE</strong><br>
                    <small>
                        Live data with simulation overlay for comparison.<br>
                        Advisory-only system. No autonomous actions. Confidence values are advisory only.
                    </small>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            # Live Mode
            st.markdown(
                """
                <div style="
                    background:#E6F7FF;
                    border-left:5px solid #4A90E2;
                    padding:8px;
                    margin-bottom:10px;
                    border-radius:4px;
                    position:sticky;
                    top:0;
                    z-index:1000;
                ">
                    <strong>📡 LIVE MODE</strong><br>
                    <small>
                        Operating with live data sources.<br>
                        Advisory-only system. No autonomous actions. Confidence values are advisory only.
                    </small>
                </div>
                """,
                unsafe_allow_html=True
            )
    
    @staticmethod
    def render_training_mode_indicator():
        """
        Legacy method for backward compatibility.
        
        Deprecated: Use render_mode_awareness_banner() instead.
        """
        DashboardLayout.render_mode_awareness_banner()

    # ------------------------------------------------------------------
    # 🔧 THIS METHOD FIXES YOUR CRASH (MISSING BEFORE)
    # ------------------------------------------------------------------

    @staticmethod
    def render_operational_context(
        headline: str,
        message: str,
        training_mode: bool = False,
        is_simulation: bool = False
    ):
        """
        Render a standard operational context panel.

        Args:
            headline: Short headline text
            message: Supporting message text
            training_mode: If True, apply training/simulation styling
            is_simulation: If True, show simulation label (non-blocking)

        This method must never raise an exception (UI-only helper).
        """
        try:
            # Use Streamlit primitives instead of nested raw HTML to avoid
            # accidental literal HTML rendering in the page. Keep this helper
            # intentionally defensive and simple so it never raises.
            with st.container():
                # Simulation/training visual cue
                if training_mode or is_simulation:
                    try:
                        st.info("SIMULATION / TRAINING DATA — Advisory Only")
                    except Exception:
                        # best-effort, non-blocking
                        st.write("SIMULATION / TRAINING DATA — Advisory Only")

                # Headline + supporting message (plain text / markdown)
                try:
                    st.markdown(f"**{headline}**")
                    st.write(message)
                except Exception:
                    try:
                        st.write(f"{headline} — {message}")
                    except Exception:
                        pass

                # Non-blocking advisory caption
                try:
                    st.caption("Advisory Only — No Autonomous Actions")
                except Exception:
                    try:
                        st.write("Advisory Only — No Autonomous Actions")
                    except Exception:
                        pass
        except Exception:
            # Fallback: simple, safe text output without HTML
            try:
                st.markdown(f"**{headline}** — {message}")
            except Exception:
                pass

    @staticmethod
    def render_intelligence_narrative(narrative: str, confidence: Optional[float] = None):
        """
        Render a short intelligence narrative summary with optional confidence.

        This is a safe, UI-only helper used by `app.py`. It must not raise.
        """
        try:
            if confidence is not None:
                # Show confidence and narrative in a compact layout
                st.markdown(f"**Narrative:** {narrative}")
                try:
                    st.metric("Confidence", f"{confidence:.1%}")
                except Exception:
                    # Metric rendering is non-critical
                    st.write(f"Confidence: {confidence}")
            else:
                st.markdown(f"**Narrative:** {narrative}")
        except Exception:
            # Last-resort fallback
            try:
                st.write(narrative)
            except Exception:
                pass

    @staticmethod
    def render_insufficient_data_message(context: str = ""):
        """
        Render a non-blocking insufficient data message.
        """
        try:
            msg = "Insufficient Data — Monitoring Only"
            if context:
                msg += f" ({context})"
            st.info(f"ℹ️ {msg}")
        except Exception:
            try:
                st.write("Monitoring only.")
            except Exception:
                pass

    # ------------------------------------------------------------------
    # ADVISORY PANELS
    # ------------------------------------------------------------------

    @staticmethod
    def render_advisory_panel(
        title: str,
        state: str,
        confidence: Optional[float] = None,
        reasoning: Optional[str | List[str]] = None,
        training_mode: bool = False,
        is_simulation: bool = False
    ):
        """Render a generic advisory panel."""
        from abhedya.dashboard.visual_components import SeverityThemeController

        st.subheader(title)

        if training_mode or is_simulation:
            st.info("SIMULATION / TRAINING DATA — Advisory Only")

        SeverityThemeController.render_severity_badge(state, training_mode)

        if confidence is not None:
            st.metric("Confidence", f"{confidence:.1%}")

        if reasoning:
            with st.expander("Reasoning"):
                if isinstance(reasoning, list):
                    for r in reasoning:
                        st.write(f"• {r}")
                else:
                    st.write(reasoning)

        st.caption("Advisory output only. Human operator review required.")

    # ------------------------------------------------------------------
    # INTENT ASSESSMENT
    # ------------------------------------------------------------------

    @staticmethod
    def render_intent_assessment_panel(
        intent_data: Dict[str, Any],
        training_mode: bool = False
    ):
        """Render intent assessment (advisory-only)."""
        st.subheader("Intent Assessment (Advisory Only)")

        if training_mode:
            st.info("SIMULATION DATA — TRAINING MODE")

        probs = intent_data.get("intent_probabilities", {})
        # Use four equal-width columns so all intent percentages render on one row
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

        col1.metric("Transit Intent", f"{probs.get('transit', 0.0):.1%}")
        col2.metric("Surveillance Intent", f"{probs.get('surveillance', 0.0):.1%}")
        col3.metric("Hostile Intent", f"{probs.get('hostile', 0.0):.1%}")
        # Place overall intent confidence in the fourth column to keep all metrics aligned
        col4.metric("Intent Confidence", f"{intent_data.get('intent_confidence', 0.0):.1%}")

        reasoning = intent_data.get("reasoning")
        if reasoning:
            with st.expander("Intent Reasoning"):
                for r in reasoning:
                    st.write(f"• {r}")

        st.caption("No autonomous decisions. Human judgment required.")

    # ------------------------------------------------------------------
    # HUMAN ACKNOWLEDGMENT (NON-BINDING)
    # ------------------------------------------------------------------

    @staticmethod
    def render_human_acknowledgment_panel(items: List[Dict[str, Any]]):
        """Render human acknowledgment controls."""
        st.subheader("Human Acknowledgment (Non-Binding)")

        if not items:
            st.info("No items requiring acknowledgment.")
            return

        acknowledged = st.session_state.setdefault("acknowledged_items", set())

        for idx, item in enumerate(items):
            item_id = item.get("id", f"item_{idx}")
            is_ack = item_id in acknowledged

            with st.expander(f"{item.get('title', 'Item')} {'✓' if is_ack else ''}"):
                st.write(f"**Description:** {item.get('description', 'N/A')}")
                st.write(f"**Severity:** {item.get('severity', 'N/A')}")

                if not is_ack:
                    if st.button("Acknowledge", key=f"ack_{item_id}"):
                        acknowledged.add(item_id)
                        st.success("Acknowledged (non-binding)")
                        st.rerun()
                else:
                    st.success("✓ Acknowledged")

    @staticmethod
    def render_data_freshness(training_mode: bool = False):
        """
        Render a small, non-blocking data freshness indicator using the
        existing `st.session_state['last_update_time']` timestamp.

        This helper is UI-only and must never raise.
        """
        try:
            from datetime import datetime

            # Determine the active tab name (set by the app before calling
            # this helper). Fall back to a global key if not available.
            tab_name = st.session_state.get('_active_tab_name', 'global')
            ts_key = f'last_refresh_ts::{tab_name}'

            # Ensure a timestamp exists for this tab (initialize if missing)
            if ts_key not in st.session_state or st.session_state.get(ts_key) is None:
                st.session_state[ts_key] = datetime.now()

            last = st.session_state.get(ts_key)

            # Normalize possible string values
            if isinstance(last, str):
                try:
                    last = datetime.fromisoformat(last.replace('Z', '+00:00'))
                except Exception:
                    last = datetime.now()

            # Compute elapsed seconds since last refresh for this tab
            elapsed = (datetime.now() - last).total_seconds()

            # Formatting rules
            if elapsed < 2:
                age_str = 'just now'
            elif elapsed < 60:
                age_str = f"{int(elapsed)}s ago"
            else:
                mins = int(elapsed // 60)
                secs = int(elapsed % 60)
                age_str = f"{mins}m {secs}s ago" if mins < 60 else f"{int(elapsed // 3600)}h ago"

            mode = 'live (simulation)' if training_mode else 'live'

            # Render an isolated iframe via `components.html` that performs a
            # client-side, per-second tick based on the server-provided
            # `last_refresh_ts::<tab>` timestamp. The iframe avoids polluting
            # the parent DOM and will continue updating the displayed text
            # without causing Streamlit reruns. If embedding the iframe fails
            # (CSP or environment limitations), fall back to a static server-
            # rendered caption.
            try:
                import streamlit.components.v1 as components

                # Prepare ISO timestamp for client-side clock
                ts_iso = last.isoformat() if hasattr(last, 'isoformat') else str(last)
                safe_id = f"df-{abs(hash(ts_iso))}"
                # Small HTML document isolated inside the iframe. JS is fully
                # encapsulated in an IIFE and uses no globals.
                html = f"""
                <!doctype html>
                <html>
                <head>
                  <meta charset='utf-8'>
                  <meta name='viewport' content='width=device-width, initial-scale=1'>
                  <style>
                    body {{ margin:0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial; }}
                    .freshness {{ color:#6b6b6b; font-size:13px; padding:4px 6px; }}
                  </style>
                </head>
                <body>
                  <div id="{safe_id}" class="freshness">Data freshness: {mode} · Updated {age_str}</div>
                  <script>
                  (function(){{
                    try {{
                      var el = document.getElementById('{safe_id}');
                      if(!el) return;
                      var ts = new Date('{ts_iso}');
                      function fmt(age){{
                        if(age < 2) return 'just now';
                        if(age < 60) return age + 's ago';
                        var mins = Math.floor(age/60);
                        var secs = age % 60;
                        if(mins < 60) return mins + 'm ' + secs + 's ago';
                        return Math.floor(mins/60) + 'h ago';
                      }}
                      function update(){{
                        var now = new Date();
                        var age = Math.floor((now - ts) / 1000);
                        el.textContent = 'Data freshness: {mode} · Updated ' + fmt(age);
                      }}
                      // Initial render and per-second ticking
                      update();
                      var iv = setInterval(update, 1000);
                      // Stop timer when iframe is unloaded
                      window.addEventListener('unload', function(){{ clearInterval(iv); }});
                    }} catch(e){{
                      // Silently fail and leave server-rendered text intact
                      console && console.error && console.error(e);
                    }}
                  }})();
                  </script>
                </body>
                </html>
                """

                col_left, col_right = st.columns([9, 1])
                with col_left:
                    try:
                        components.html(html, height=34, scrolling=False)
                    except Exception:
                        # Embedding failed; fallback to static caption
                        st.markdown(f"<div style='color:#6b6b6b; font-size:0.9em;'>Data freshness: {mode} · Updated {age_str}</div>", unsafe_allow_html=True)
                with col_right:
                    refresh_label = "↻ Refresh data"
                    btn_key = f"refresh_btn::{tab_name}"
                    if st.button(refresh_label, key=btn_key, help="Refresh this tab's data"):
                        st.session_state[ts_key] = datetime.now()
                        try:
                            st.experimental_rerun()
                        except Exception:
                            try:
                                st.rerun()
                            except Exception:
                                pass
            except Exception:
                try:
                    st.markdown(f"<div style='color:#6b6b6b; font-size:0.9em;'>Data freshness: {mode} · Updated {age_str}</div>", unsafe_allow_html=True)
                except Exception:
                    try:
                        st.caption(f"Data freshness: {mode} · Updated {age_str}")
                    except Exception:
                        try:
                            st.write("")
                        except Exception:
                            pass
        except Exception:
            try:
                st.write("")
            except Exception:
                pass
