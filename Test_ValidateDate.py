#!/usr/bin/env python3
# encoding: utf-8

import unittest
import os
from ValidateDate import ValidateDate

class Test_ValidateDate(unittest.TestCase):
    def __initializeTest(self):
        pass

    def test_correctDate(self):
        self.__initializeTest()
        testDate = ValidateDate("2020-11-12")
        self.assertEqual(True, testDate.isValid())
        self.assertEqual(2020, testDate.getYear())
        self.assertEqual(11, testDate.getMonth())
        self.assertEqual(12, testDate.getDay())

    def test_correctOrderMonthDay(self):
        self.__initializeTest()
        testDate = ValidateDate("2020-12-11")
        self.assertEqual(True, testDate.isValid())
        self.assertEqual(2020, testDate.getYear())
        self.assertEqual(12, testDate.getMonth())
        self.assertEqual(11, testDate.getDay())

    def test_wrongFirstSeparater(self):
        self.__initializeTest()
        testDate = ValidateDate("2020a12-11")
        self.assertEqual(False, testDate.isValid())

    def test_wrongSecondSeparater(self):
        self.__initializeTest()
        testDate = ValidateDate("2020-12_11")
        self.assertEqual(False, testDate.isValid())

    def test_charInYear(self):
        self.__initializeTest()
        testDate = ValidateDate("202a-12-11")
        self.assertEqual(False, testDate.isValid())

    def test_charInMonth(self):
        self.__initializeTest()
        testDate = ValidateDate("2020-d2-11")
        self.assertEqual(False, testDate.isValid())

    def test_charInDay(self):
        self.__initializeTest()
        testDate = ValidateDate("2020-12-1k")
        self.assertEqual(False, testDate.isValid())

    def test_yearOnlyTwoDigit(self):
        self.__initializeTest()
        testDate = ValidateDate("20-04-12")
        self.assertEqual(False, testDate.isValid())

    def test_monthSingleDigit(self):
        self.__initializeTest()
        testDate = ValidateDate("2020-4-12")
        self.assertEqual(False, testDate.isValid())

    def test_daySingleDigit(self):
        self.__initializeTest()
        testDate = ValidateDate("2020-04-1")
        self.assertEqual(False, testDate.isValid())


if __name__ == '__main__':
    import xmlrunner
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'))
    #unittest.main()  # Calling from the command line invokes all tests
