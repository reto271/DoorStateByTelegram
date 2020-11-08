#!/usr/bin/env python3
# encoding: utf-8

import unittest
import os
from unittest.mock import MagicMock
from DumpToLogAndUser import DumpToLogAndUser

class Mock_bot:
    def sendMessage(self, userId, textToSend):
        pass

class Mock_log:
    def logText(self, textToSend):
        pass


class Test_DumpToLogAndUser(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        mock_bot = Mock_bot()
        mock_log = Mock_log()
        self.m_dut = DumpToLogAndUser(mock_bot, 0, mock_log)

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_isEmpty(self):
        self.assertEqual(True, self.m_dut.m_isEmpty)

    def test_isNotEmpty(self):
        self.m_dut.addLine('Test')
        self.assertEqual(False, self.m_dut.m_isEmpty)

    def test_reset(self):
        self.m_dut.addLine('Test')
        self.assertEqual(False, self.m_dut.m_isEmpty)
        self.m_dut.reset()
        self.assertEqual(True, self.m_dut.m_isEmpty)

    def test_dumpWithId(self):
        self.m_dut.addLine('Test')
        self.assertEqual(False, self.m_dut.m_isEmpty)
        self.m_dut.setUserId(0)
        self.m_dut.dump()

    def test_dumpWithoutId(self):
        self.m_dut.addLine('Test')
        self.assertEqual(False, self.m_dut.m_isEmpty)
        self.m_dut.setUserId(111)
        self.m_dut.dump()

if __name__ == '__main__':
    import xmlrunner
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'))
    #unittest.main()  # Calling from the command line invokes all tests
