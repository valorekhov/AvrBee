import unittest, sys, os
from arduinoXbeeProgrammer.FileReader import HexFileReader

class TestHexFileReader(unittest.TestCase):
    def test_Read(self):
        reader = HexFileReader( os.path.join(os.path.dirname(__file__), "MyBlink.cpp.hex" ) )
        instructions = reader.get_bytes();
        self.assertEqual(69, len(instructions))

        addr, bytes = instructions[-1]
        self.assertEqual(0x043A, addr)

        addr, bytes = instructions[2]
        self.assertEqual(0x0020, addr)

if __name__ == '__main__':
    unittest.main()
