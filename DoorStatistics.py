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
from DumpToLogAndUser import DumpToLogAndUser


class DoorStatistics:
    def __init__(self, bot, logger):
        self.m_bootTime = datetime.now()
        self.m_nrDoorMovementsSinceReboot = 0
        self.m_logMsg = DumpToLogAndUser(bot, 0, logger)
        self.m_nrTotalDoorMovements = 0
        self.__readDoorFile()
        self.m_dumpedAlreadyToDay = False

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

    def run(self):
        now = datetime.now()
        if ((0 == now.min) and (0 == now.hour) and (False == self.m_dumpedAlreadyToDay)):
            self.m_logMsg.setUserId(0)
            self.dumpState()
            self.m_dumpedAlreadyToDay = True
        if ((1 == now.min) and (0 == now.hour)):
            self.m_dumpedAlreadyToDay = False

    def __readDoorFile(self):
        try:
            with open('./doorStats.txt', 'r') as statsFile:
                self.m_nrTotalDoorMovements = myUtils.tryInt(statsFile.read().rstrip())
        except IOError:
            self.m_nrTotalDoorMovements = 0

    def __storeDoorFile(self):
        with open('./doorStats.txt', 'w') as f:
            f.write(str(self.m_nrTotalDoorMovements) + '\n')
