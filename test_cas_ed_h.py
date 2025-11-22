import unittest
from devices.scales.cas_ed_h_scale import CasEdHScale

class TestCasEdHScale(unittest.TestCase):
    def setUp(self):
        self.scale = CasEdHScale("TestScale", "01")
        self.scale.set_weight(123.4)

    def test_print_command(self):
        # Command 'P' should return stream packet
        response = self.scale.process_command(b'P')
        self.assertIsNotNone(response)
        # Expected format: ST,GS,+  123.4kg  \r\n (approx)
        # Let's check length and content
        # Length: 22 bytes + 2 (CRLF) = 24 bytes if terminator included?
        # The manual says 22 bytes total including CR LF.
        # My implementation: 
        # [HEAD1(2)][,][HEAD2(2)][,][DATA(8)][UNIT(4)][CR][LF]
        # 2 + 1 + 2 + 1 + 8 + 4 = 18 bytes data + 2 bytes CRLF = 20 bytes?
        # Wait, manual says:
        # HEAD1(2), HEAD2(2), DATA(8), UNIT(4), CR, LF
        # Comma separators?
        # Manual example: "ST,GS,+  0.876 g  "
        # "ST" (2) + "," (1) + "GS" (2) + "," (1) + "+  0.876" (8) + " g  " (4) + CR LF
        # 2+1+2+1+8+4 = 18 bytes. + CR LF = 20 bytes.
        # Manual page 20 says "Format 1 (18 Bytes)" for NT-301A, but for ED-H?
        # Page 29 of ED-H manual:
        # "HEAD1, HEAD2, DATA UNIT CR"
        # "HEAD1 (2 BYTES) HEAD2 (2BYTES)"
        # "DATA (8BYTES)"
        # "UNIT (4BYTE)"
        # Example: "ST,GS,+ 0.876 g 0D 0A"
        # ST(2) ,(1) GS(2) ,(1) + 0.876(8) space(1) g(1) space(2)?
        # Wait, the manual example shows spaces in unit.
        # "g   " -> 4 bytes.
        # So 2+1+2+1+8+4 = 18 bytes + CR(1) + LF(1) = 20 bytes?
        # Page 20 says "22 Byte".
        # Maybe there are spaces between Data and Unit?
        # "DATA (8BYTES) UNIT (4BYTE)"
        # Example: "+ 0.876 g "
        # Let's stick to the example string structure.
        
        resp_str = response.decode('ascii')
        print(f"Response: {repr(resp_str)}")
        self.assertTrue(resp_str.startswith("ST,GS,"))
        self.assertIn("123.4", resp_str)
        self.assertTrue(resp_str.endswith("\r\n"))

    def test_zero_command(self):
        self.scale.process_command(b'Z')
        self.assertEqual(self.scale.current_weight, 0.0)

    def test_tare_command(self):
        self.scale.process_command(b'T')
        self.assertEqual(self.scale.tare_weight, 123.4)

if __name__ == '__main__':
    unittest.main()
