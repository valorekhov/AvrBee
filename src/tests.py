#import glob
import unittest

from arduinoXbeeProgrammer.tests.test_readHexFile import TestHexFileReader

testSuite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromTestCase(TestHexFileReader))
text_runner = unittest.TextTestRunner().run(testSuite)