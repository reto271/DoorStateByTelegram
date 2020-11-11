import sys
import time
import datetime
from datetime import datetime
from datetime import timedelta
import telepot


# My modules
import myUtils
from UserListHandler import UserListHandler


class DumpToLogAndUser:
    def __init__(self, bot, userId, logger):
        self.m_bot = bot
        self.m_userId = userId
        self.m_logger = logger
        self.m_textLog = ''
        self.m_textBot = ''
        self.m_isEmpty = True

    def reset(self):
        self.m_textLog = ''
        self.m_textBot = ''
        self.m_isEmpty = True

    def setUserId(self, userId):
        self.m_userId = userId

    def addLine(self, text):
        if True == self.m_isEmpty:
            self.m_textLog = list()
            self.m_textLog.append(text)
            self.m_textBot = text
            self.m_isEmpty = False
        else:
            self.m_textLog.append(text)
            self.m_textBot = self.m_textBot + '\n' + text

    def dump(self):
        if 0 != self.m_userId:
            self.m_bot.sendMessage(self.m_userId, self.m_textBot)
        for line in self.m_textLog:
            self.m_logger.logText(line)
