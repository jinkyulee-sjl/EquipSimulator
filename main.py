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
    
    # Register Device Types
    sim.register_device_type("AND AD-4401", ANDScale)
    sim.register_device_type("AND CB Series", ANDScale, model="CB")
    sim.register_device_type("CAS CI-600A", CasCI600A)
    
    try:
        app = MainWindow(sim)
        app.mainloop()
    finally:
        # Cleanup
        sim.stop()

if __name__ == "__main__":
    main()
