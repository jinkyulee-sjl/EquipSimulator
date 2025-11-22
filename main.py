import sys
import os
import logging

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import MainWindow
from core.simulator import Simulator
from devices.scales.and_scale import ANDScale
from devices.scales.cas_ci600a import CasCI600A
from devices.scales.and_gp_scale import ANDGPScale
from devices.scales.sartorius_bp_scale import SartoriusBPScale
from devices.scales.sartorius_cpa_scale import SartoriusCPAScale
from devices.scales.and_ad4401_scale import ANDAD4401Scale
from devices.scales.cas_nt301a_scale import CasNT301AScale
from devices.scales.cas_nt302a_scale import CasNT302AScale
from devices.scales.cas_ed_h_scale import CasEdHScale

def main():
    logging.basicConfig(level=logging.INFO)
    
    # Initialize Simulator
    sim = Simulator()
    
    # Register Device Types
    sim.register_device_type("AND AD-4401", ANDScale)
    sim.register_device_type("AND CB Series", ANDScale, model="CB")
    sim.register_device_type("CAS CI-600A", CasCI600A)
    sim.register_device_type("AND GP Series", ANDGPScale)
    sim.register_device_type("Sartorius BP", SartoriusBPScale)
    sim.register_device_type("Sartorius CPA", SartoriusCPAScale)
    sim.register_device_type("AND AD-4401 (New)", ANDAD4401Scale) # Renamed to distinguish from existing generic AND
    sim.register_device_type("CAS NT-301A", CasNT301AScale)
    sim.register_device_type("CAS NT-302A", CasNT302AScale)
    sim.register_device_type("CAS EC-D", CasEdHScale)
    sim.register_device_type("CAS ED-H", CasEdHScale)
    
    try:
        app = MainWindow(sim)
        app.mainloop()
    finally:
        # Cleanup
        sim.stop()

if __name__ == "__main__":
    main()
