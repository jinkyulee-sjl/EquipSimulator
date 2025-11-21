import unittest
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from devices.scales.cas_ci600a import CasCI600A

class TestCasBuffering(unittest.TestCase):
    def setUp(self):
        self.scale = CasCI600A("Test Scale", "TEST_01")
        self.scale.set_weight(123.4)
        self.scale.set_stable(True)
        self.scale.set_format("Format 1")

    def test_fragmented_command(self):
        # Send "01RW\r\n" in chunks
        
        # Chunk 1: "01"
        resp = self.scale.process_command(b"01")
        self.assertIsNone(resp, "Should return None for incomplete command")
        
        # Chunk 2: "R"
        resp = self.scale.process_command(b"R")
        self.assertIsNone(resp)
        
        # Chunk 3: "W"
        resp = self.scale.process_command(b"W")
        self.assertIsNone(resp)
        
        # Chunk 4: "\r"
        resp = self.scale.process_command(b"\r")
        self.assertIsNone(resp)
        
        # Chunk 5: "\n" (Completes command)
        resp = self.scale.process_command(b"\n")
        self.assertIsNotNone(resp, "Should return response for completed command")
        
        expected_data = "   123.4"
        # Note: My implementation might return bytes, check content
        self.assertTrue(b"ST" in resp)
        self.assertTrue(b"GS" in resp)
        self.assertTrue(b"123.4" in resp)

    def test_multiple_commands(self):
        # Send "01RW\r\n01MZ\r\n"
        # My current implementation only processes the first one and keeps the rest in buffer.
        # Let's verify the first one triggers, and the second one triggers on next call?
        # Wait, process_command only returns ONE response.
        # If I send two commands at once:
        resp = self.scale.process_command(b"01RW\r\n01MZ\r\n")
        self.assertIsNotNone(resp)
        self.assertTrue(b"ST" in resp) # Response to RW
        
        # The buffer should now contain "01MZ\r\n"
        # Calling process_command with empty bytes should trigger the next one?
        # My implementation:
        # self._buffer += command
        # if terminator in buffer: process...
        # It splits, processes first, leaves rest.
        # But it doesn't loop to process *all* in buffer.
        # So if I call process_command(b"") it should process the next one?
        
        resp = self.scale.process_command(b"")
        self.assertIsNotNone(resp)
        self.assertTrue(b"01MZ" in resp) # Echo response for MZ

if __name__ == '__main__':
    unittest.main()
