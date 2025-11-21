import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from devices.scales.and_scale import ANDScale

def test_and_scale():
    scale = ANDScale("Test Scale", "TEST_01")
    
    # Test 1: Initial State
    print(f"Initial Weight: {scale.current_weight}")
    assert scale.current_weight == 0.0
    
    # Test 2: Set Weight
    scale.set_weight(123.4)
    print(f"Set Weight: {scale.current_weight}")
    assert scale.current_weight == 123.4
    
    # Test 3: 'Q' Command (Stable)
    scale.set_stable(True)
    response = scale.process_command(b'Q')
    print(f"Response (Stable): {response}")
    assert b'ST,GS,+00123.4kg\r\n' in response
    
    # Test 4: 'Q' Command (Unstable)
    scale.set_stable(False)
    response = scale.process_command(b'RW')
    print(f"Response (Unstable): {response}")
    assert b'US,GS,+00123.4kg\r\n' in response

    print("All tests passed!")

if __name__ == "__main__":
    test_and_scale()
