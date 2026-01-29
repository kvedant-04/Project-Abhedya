"""
Abhedya Air Defense System - Demonstration Script

This script demonstrates the capabilities of the Abhedya system
in a controlled simulation environment.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from abhedya import AbhedyaSystem
from abhedya.sensors import RadarSensor, IFFSensor
from abhedya.assessment import ThreatAssessor
from abhedya.advisory import AdvisoryEngine
from abhedya.interface import HumanInterface
from abhedya.audit import AuditLogger
from abhedya.core.models import Coordinates, Velocity, EntityType


def create_demo_system():
    """Create and configure a demo Abhedya system."""
    
    # Create sensors
    radar = RadarSensor(
        sensor_id="RADAR_001",
        position=Coordinates(x=0.0, y=0.0, z=0.0),
        range_meters=150000.0
    )
    
    iff = IFFSensor(
        sensor_id="IFF_001",
        position=Coordinates(x=0.0, y=0.0, z=0.0),
        range_meters=200000.0
    )
    
    # Create threat assessor
    threat_assessor = ThreatAssessor(
        protected_zone_radius=50000.0,
        critical_zone_radius=20000.0
    )
    
    # Create advisory engine
    advisory_engine = AdvisoryEngine(
        min_confidence=0.5
    )
    
    # Create human interface
    human_interface = HumanInterface(
        auto_approve=False  # Manual approval in demo
    )
    
    # Create audit logger
    audit_logger = AuditLogger(
        log_directory="logs",
        enabled=True
    )
    
    # Create system
    system = AbhedyaSystem(
        sensors=[radar, iff],
        threat_assessor=threat_assessor,
        advisory_engine=advisory_engine,
        human_interface=human_interface,
        audit_logger=audit_logger
    )
    
    return system, radar, iff, human_interface


def simulate_scenario(system, radar, iff, human_interface):
    """Run a demonstration scenario."""
    
    print("\n" + "="*60)
    print("ABHEDYA AIR DEFENSE SYSTEM - DEMONSTRATION")
    print("="*60)
    print("\nThis is a SOFTWARE-ONLY SIMULATION.")
    print("All outputs are ADVISORY and require HUMAN APPROVAL.")
    print("No real actions are executed.\n")
    
    # Scenario 1: Friendly aircraft
    print("\n" + "-"*60)
    print("SCENARIO 1: Friendly Aircraft")
    print("-"*60)
    
    friendly_pos = Coordinates(x=30000.0, y=40000.0, z=10000.0)
    friendly_vel = Velocity(vx=-50.0, vy=-30.0, vz=0.0)
    
    radar.add_simulated_entity(
        position=friendly_pos,
        velocity=friendly_vel,
        entity_id="FRIENDLY_001"
    )
    
    iff.add_simulated_entity(
        position=friendly_pos,
        velocity=friendly_vel,
        entity_id="FRIENDLY_001",
        iff_code="FRIENDLY_CODE_123",
        is_friendly=True
    )
    
    # Run a few cycles
    for i in range(3):
        print(f"\n--- Cycle {i+1} ---")
        system.run_cycle()
        
        # Check for recommendations
        state = system.get_state()
        if state.pending_recommendations:
            for rec in state.pending_recommendations:
                print(f"\nRecommendation generated for track {rec.track_id}")
                print(f"Action: {rec.action.value}")
                print(f"Threat Level: {rec.threat_level.value}")
                
                # Simulate human approval
                human_interface.simulate_human_approval(
                    rec.recommendation_id,
                    approved=True
                )
    
    # Scenario 2: Unknown/Hostile entity
    print("\n" + "-"*60)
    print("SCENARIO 2: Unknown Entity Approaching")
    print("-"*60)
    
    hostile_pos = Coordinates(x=80000.0, y=60000.0, z=5000.0)
    hostile_vel = Velocity(vx=-200.0, vy=-150.0, vz=0.0)  # High speed
    
    radar.add_simulated_entity(
        position=hostile_pos,
        velocity=hostile_vel,
        entity_id="UNKNOWN_001"
    )
    
    # No IFF response (suspicious)
    iff.add_simulated_entity(
        position=hostile_pos,
        velocity=hostile_vel,
        entity_id="UNKNOWN_001",
        iff_code=None,
        is_friendly=False
    )
    
    # Run cycles as entity approaches
    for i in range(5):
        print(f"\n--- Cycle {i+1} ---")
        
        # Update entity position (simulate movement)
        hostile_pos.x += hostile_vel.vx
        hostile_pos.y += hostile_vel.vy
        
        radar.clear_simulated_entities()
        iff.clear_simulated_entities()
        
        radar.add_simulated_entity(
            position=hostile_pos,
            velocity=hostile_vel,
            entity_id="UNKNOWN_001"
        )
        
        iff.add_simulated_entity(
            position=hostile_pos,
            velocity=hostile_vel,
            entity_id="UNKNOWN_001",
            iff_code=None,
            is_friendly=False
        )
        
        system.run_cycle()
        
        # Check tracks
        tracks = system.get_tracks()
        for track in tracks:
            if track.entity_type != EntityType.FRIENDLY:
                print(f"\nTrack {track.track_id}:")
                print(f"  Entity Type: {track.entity_type.value}")
                print(f"  Threat Level: {track.threat_level.value}")
                print(f"  Position: ({track.position.x/1000:.1f}, {track.position.y/1000:.1f}) km")
                print(f"  Distance: {(track.position.x**2 + track.position.y**2)**0.5/1000:.1f} km")
        
        # Check recommendations
        state = system.get_state()
        if state.pending_recommendations:
            for rec in state.pending_recommendations:
                print(f"\n⚠️  RECOMMENDATION:")
                print(f"   Action: {rec.action.value}")
                print(f"   Threat Level: {rec.threat_level.value}")
                print(f"   Confidence: {rec.confidence:.1%}")
                print(f"   Probability: {rec.probability:.1%}")
                print(f"\n   Reasoning:\n{rec.reasoning}")
                
                # In real system, human would review and approve/reject
                # For demo, we simulate approval
                human_interface.simulate_human_approval(
                    rec.recommendation_id,
                    approved=True
                )
    
    # Final summary
    print("\n" + "="*60)
    print("SIMULATION COMPLETE")
    print("="*60)
    
    final_state = system.get_state()
    print(f"\nFinal State:")
    print(f"  Active Tracks: {len(final_state.active_tracks)}")
    print(f"  Pending Recommendations: {len(final_state.pending_recommendations)}")
    print(f"  System Mode: {final_state.system_mode}")
    
    # Show audit trail summary
    if system.audit_logger:
        print(f"\nAudit Log Entries: {len(system.audit_logger.log_entries)}")
        print("\nKey Events:")
        for entry in system.audit_logger.log_entries[-10:]:  # Last 10 events
            print(f"  [{entry['timestamp']}] {entry['event_type']}")


if __name__ == "__main__":
    try:
        system, radar, iff, human_interface = create_demo_system()
        simulate_scenario(system, radar, iff, human_interface)
        
        print("\n" + "="*60)
        print("IMPORTANT REMINDER:")
        print("="*60)
        print("This system is SOFTWARE-ONLY and ADVISORY.")
        print("All recommendations require HUMAN APPROVAL.")
        print("No real-world actions are executed by this system.")
        print("="*60 + "\n")
        
    except KeyboardInterrupt:
        print("\n\nSimulation interrupted by user.")
    except Exception as e:
        print(f"\n\nError during simulation: {e}")
        import traceback
        traceback.print_exc()

