import sys
import time
import random
import datetime
from datetime import datetime
from datetime import timedelta
import telepot

from gpiozero import Button
from gpiozero import LED
from time import sleep

# My modules
import myUtils
import ProjectVersion
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


class StateLogger:
    def __init__(self, bot, logger):
        self.m_bootTime = datetime.now()
        self.m_nrDoorMovementsSinceReboot = 0
        self.m_logMsg = DumpToLogAndUser(bot, 0, logger)
        self.m_nrTotalDoorMovements = 0
        self.__readDoorFile()

    def dumpState(self, userId = []):
        bootTime = self.m_bootTime.strftime("%d. %B %Y %H:%M:%S")
        runTime = datetime.now() - self.m_bootTime
        self.m_logMsg.reset()
        if userId:
            self.m_logMsg.setUserId(userId)
        else:
            self.m_logMsg.setUserId(0)
        self.m_logMsg.addLine('State Summary:')
        self.m_logMsg.addLine('   Boot: ' + str(bootTime))
        self.m_logMsg.addLine('   Run Time: ' + str(runTime))
        self.m_logMsg.addLine('   Door Move: ' + str(self.m_nrDoorMovementsSinceReboot))
        self.m_logMsg.addLine('   Total Door Move: ' + str(self.m_nrTotalDoorMovements))
        self.m_logMsg.dump()

    def addDoorMovement(self):
        self.m_nrDoorMovementsSinceReboot = self.m_nrDoorMovementsSinceReboot + 1
        self.m_nrTotalDoorMovements = self.m_nrTotalDoorMovements + 1
        self.__storeDoorFile()

    def __readDoorFile(self):
        try:
            with open('./doorStats.txt', 'r') as statsFile:
                self.m_nrTotalDoorMovements = myUtils.tryInt(statsFile.read().rstrip())
        except IOError:
            self.m_nrTotalDoorMovements = 0

    def __storeDoorFile(self):
        with open('./doorStats.txt', 'w') as f:
            f.write(str(self.m_nrTotalDoorMovements) + '\n')
