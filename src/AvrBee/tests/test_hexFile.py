import unittest, sys, os
from AvrBee.HexFileFormat import HexFileFormat
import tempfile

class TestHexFileFormat(unittest.TestCase):
    def test_Write(self):
        writer= HexFileFormat( file= sys.stdout )
        instructions = b'Return a file-like object that can be used as a temporary storage area. The file is created using mkstemp(). It will be destroyed as soon as it is closed (including an implicit close when the object is garbage collected). Under Unix, the directory entry for the file is removed immediately after the file is created. Other platforms do not support this; your code should not rely on a temporary file created using this function having or not having a visible name in the file system'
        writer.save_bytes(instructions)


    def test_Read(self):
        reader = HexFileFormat( os.path.join(os.path.dirname(__file__), "MyBlink.cpp.hex" ) )
        instructions = reader.get_bytes();
        self.assertEqual(69, len(instructions))

        addr, bytes = instructions[-1]
        self.assertEqual(0x043A, addr)

        addr, bytes = instructions[2]
        self.assertEqual(0x0020, addr)

if __name__ == '__main__':
    unittest.main()
