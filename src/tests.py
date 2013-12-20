#import glob
import unittest

from AvrBee.tests.test_readHexFile import TestHexFileReader
from AvrBee.tests.test_stkProto import TestStkProto

testSuite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromName('tests'))
text_runner = unittest.TextTestRunner().run(testSuite)