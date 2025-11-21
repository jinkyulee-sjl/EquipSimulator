import sys
import os
import time
import serial
import threading
import logging

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.simulator import Simulator
from devices.scales.cas_ci600a import CasCI600A

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("verification_partial_logs.txt", mode='w'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Verification")

def run_simulator(stop_event):
    sim = Simulator()
    device = CasCI600A("CAS CI-600A", "SCALE_03")
    sim.add_device(device)
    
    device.set_weight(123.45)
    device.set_stable(True)
    device.set_format("Format 1")
    
    logger.info("Starting Simulator on COM3...")
    success = sim.start_device_comm("CAS CI-600A", "COM3")
    if not success:
        logger.error("Failed to start simulator on COM3")
        return

    while not stop_event.is_set():
        time.sleep(0.1)
    
    sim.stop()

def run_client():
    logger.info("Starting Client on COM4...")
    try:
        ser = serial.Serial("COM4", 9600, timeout=1)
        time.sleep(1)
        
        # Test: Send fragmented RW command
        logger.info("Sending fragmented RW command...")
        ser.write(b"01")
        time.sleep(0.1)
        ser.write(b"R")
        time.sleep(0.1)
        ser.write(b"W")
        time.sleep(0.1)
        ser.write(b"\r")
        time.sleep(0.1)
        ser.write(b"\n")
        
        response = ser.read_until(b"\r\n")
        logger.info(f"Received: {response}")
        
        if b"ST,GS,10,   123.4 kg" in response or b"ST.GS.10.   123.4 kg" in response:
             print("PASS: Fragmented RW Command")
        else:
             print(f"FAIL: Fragmented RW Command. Got {response}")

        ser.close()
    except Exception as e:
        logger.error(f"Client error: {e}")

if __name__ == "__main__":
    stop_event = threading.Event()
    sim_thread = threading.Thread(target=run_simulator, args=(stop_event,))
    sim_thread.start()
    
    time.sleep(2)
    
    run_client()
    
    stop_event.set()
    sim_thread.join()
