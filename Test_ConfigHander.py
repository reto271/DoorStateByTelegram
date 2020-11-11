#!/usr/bin/env python3
# encoding: utf-8

import unittest
import os
from ConfigHandler import ConfigHandler

class Test_ConfigHandler(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        self.m_cnfgHdl = []
        if not os.path.exists('./tmp'):
            os.makedirs('./tmp')
        if os.path.exists('./tmp/config.txt'):
            os.remove('./tmp/config.txt')
        with open('./tmp/config.txt', 'w') as f:
            f.write('[DoorConfig]\nInvertInput = True\nDummyProperty=7')

    def setUp(self):
        self.m_cnfgHdl = ConfigHandler('tmp/config.txt')

    def tearDown(self):
        pass

    def test_Option_InvertInput(self):
        option = self.m_cnfgHdl.getOption('InvertInput')
        self.assertEqual('True', option)

    def test_Option_InvertInputBool(self):
        option = self.m_cnfgHdl.getOptionBool('InvertInput')
        self.assertEqual(True, option)

    def test_missingFile(self):
        cnfgHdl = ConfigHandler('tmp/config_not_exist.txt')
        self.assertEqual(False, cnfgHdl.optionFileFound())

    def test_existingFile(self):
        cnfgHdl = ConfigHandler('tmp/config.txt')
        self.assertEqual(True, cnfgHdl.optionFileFound())


if __name__ == '__main__':
    import xmlrunner
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'))
    #unittest.main()  # Calling from the command line invokes all tests
