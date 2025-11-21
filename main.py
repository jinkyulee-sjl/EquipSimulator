import sys
import os
import logging

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import MainWindow
from core.simulator import Simulator
from devices.scales.and_scale import ANDScale
from devices.scales.cas_ci600a import CasCI600A

def main():
    logging.basicConfig(level=logging.INFO)
    
    # Initialize Simulator
    sim = Simulator()
    
    # Add Devices (Phase 1)
    # Scenario: 6 Identical Scales
    for i in range(1, 7):
        sim.add_device(ANDScale(f"AND AD-4401 #{i}", f"SCALE_{i:02d}"))
    
    # Optional: Keep other types if needed
    # sim.add_device(CasCI600A("CAS CI-600A", "SCALE_99"))
    
    try:
        app = MainWindow(sim)
        app.mainloop()
    finally:
        # Cleanup
        sim.stop()

if __name__ == "__main__":
    main()
