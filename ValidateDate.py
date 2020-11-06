#!/usr/bin/env python3
# encoding: utf-8

import sys
from datetime import date

# My modules
import myUtils
import ProjectVersion


class ValidateDate:
    def __init__(self, dateString):
        self.m_dateString = dateString
        self.m_state = self.__validateDate()
        if True == self.m_state:
            self.__convertDate()

    def __validateDate(self):
        yearStr = self.m_dateString[0:4]
        monthStr = self.m_dateString[5:7]
        dayStr = self.m_dateString[8:10]
        firstSeparater = self.m_dateString[4:5]
        secondSeparater = self.m_dateString[7:8]

        if -1 == myUtils.tryInt(yearStr):
            return False
        if -1 == myUtils.tryInt(monthStr):
            return False
        if -1 == myUtils.tryInt(dayStr):
            return False
        if '-' != firstSeparater:
            return False
        if '-' != secondSeparater:
            return False
        if 4 != len(yearStr):
            return False
        if 2 != len(monthStr):
            return False
        if 2 != len(dayStr):
            return False
        return True

    def __convertDate(self):
        self.m_year = myUtils.tryInt(self.m_dateString[0:4])
        self.m_month = myUtils.tryInt(self.m_dateString[5:7])
        self.m_day = myUtils.tryInt(self.m_dateString[8:10])

    def isValid(self):
        return self.m_state

    def getDay(self):
        return self.m_day

    def getMonth(self):
        return self.m_month

    def getYear(self):
        return self.m_year


#---------------------------------------------------------------------------
if __name__ == '__main__':
    exit(main())
