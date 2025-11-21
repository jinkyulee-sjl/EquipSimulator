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
        logging.FileHandler("verification_logs.txt", mode='w'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Verification")

def run_simulator(stop_event):
    sim = Simulator()
    device = CasCI600A("CAS CI-600A", "SCALE_03")
    sim.add_device(device)
    
    # Set initial state
    device.set_weight(123.45)
    device.set_stable(True)
    device.set_format("Format 1")
    
    # Start on COM3
    logger.info("Starting Simulator on COM3...")
    success = sim.start_device_comm("CAS CI-600A", "COM3")
    if not success:
        logger.error("Failed to start simulator on COM3")
        return

    while not stop_event.is_set():
        time.sleep(0.1)
    
    sim.stop()
    logger.info("Simulator stopped.")

def run_client():
    logger.info("Starting Client on COM4...")
    try:
        ser = serial.Serial("COM4", 9600, timeout=1)
        time.sleep(1) # Wait for connection
        
        # Test 1: RW Command (Format 1)
        logger.info("Sending RW command...")
        ser.write(b"01RW\r\n")
        response = ser.read_until(b"\r\n")
        logger.info(f"Received: {response}")
        
        if b"ST,GS,10,   123.4 kg" in response or b"ST.GS.10.   123.4 kg" in response:
             print("PASS: RW Command Format 1")
        else:
             print(f"FAIL: RW Command Format 1. Got {response}")

        # Test 2: Zero Command
        logger.info("Sending MZ command...")
        ser.write(b"01MZ\r\n")
        response = ser.read_until(b"\r\n")
        logger.info(f"Received: {response}")
        
        # Verify Zero
        ser.write(b"01RW\r\n")
        response = ser.read_until(b"\r\n")
        logger.info(f"Received after Zero: {response}")
        if b"0.0" in response:
            print("PASS: Zero Command")
        else:
            print("FAIL: Zero Command")

        ser.close()
    except Exception as e:
        logger.error(f"Client error: {e}")

if __name__ == "__main__":
    stop_event = threading.Event()
    sim_thread = threading.Thread(target=run_simulator, args=(stop_event,))
    sim_thread.start()
    
    time.sleep(2) # Give simulator time to start
    
    run_client()
    
    stop_event.set()
    sim_thread.join()
