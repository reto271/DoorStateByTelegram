#!/usr/bin/env python3
# encoding: utf-8

import unittest
import os
from ConfigHandler import ConfigHandler

class Test_ConfigHandler(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        self.m_cnfgHdl = []

    def setUp(self):
        self.m_cnfgHdl = ConfigHandler('cnfg/config.txt')

    def tearDown(self):
        pass

    def test_Option_InvertInput(self):
        option = self.m_cnfgHdl.getOption('InvertInput')
        self.assertEqual('True', option)

    def test_Option_InvertInputBool(self):
        option = self.m_cnfgHdl.getOptionBool('InvertInput')
        self.assertEqual(True, option)


if __name__ == '__main__':
    import xmlrunner
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'))
    #unittest.main()  # Calling from the command line invokes all tests
