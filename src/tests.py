#import glob
import unittest

from AvrBee.tests import *

testSuite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromName('tests'))
text_runner = unittest.TextTestRunner().run(testSuite)