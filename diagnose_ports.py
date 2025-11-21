import serial.tools.list_ports
import serial
import sys

def list_ports():
    print("Available ports:")
    ports = serial.tools.list_ports.comports()
    for port, desc, hwid in ports:
        print(f"{port}: {desc} [{hwid}]")
    return [p.device for p in ports]

def test_port(port_name):
    print(f"\nTesting {port_name}...")
    try:
        s = serial.Serial(port_name)
        print(f"Successfully opened {port_name}")
        s.close()
        print(f"Successfully closed {port_name}")
    except Exception as e:
        print(f"Failed to open {port_name}: {e}")

if __name__ == "__main__":
    available_ports = list_ports()
    if "COM3" in available_ports:
        test_port("COM3")
    else:
        print("\nCOM3 is NOT in the list of available ports.")
        # Try opening it anyway, sometimes it's hidden or virtual
        test_port("COM3")
