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


from string import Formatter
from datetime import timedelta

def strfdelta(tdelta, fmt='{D:02}d {H:02}h {M:02}m {S:02}s', inputtype='timedelta'):
    """Convert a datetime.timedelta object or a regular number to a custom-
    formatted string, just like the stftime() method does for datetime.datetime
    objects.

    The fmt argument allows custom formatting to be specified.  Fields can
    include seconds, minutes, hours, days, and weeks.  Each field is optional.

    Some examples:
        '{D:02}d {H:02}h {M:02}m {S:02}s' --> '05d 08h 04m 02s' (default)
        '{W}w {D}d {H}:{M:02}:{S:02}'     --> '4w 5d 8:04:02'
        '{D:2}d {H:2}:{M:02}:{S:02}'      --> ' 5d  8:04:02'
        '{H}h {S}s'                       --> '72h 800s'

    The inputtype argument allows tdelta to be a regular number instead of the
    default, which is a datetime.timedelta object.  Valid inputtype strings:
        's', 'seconds',
        'm', 'minutes',
        'h', 'hours',
        'd', 'days',
        'w', 'weeks'

    Got it: https://stackoverflow.com/questions/538666/format-timedelta-to-string
    """

    # Convert tdelta to integer seconds.
    if inputtype == 'timedelta':
        remainder = int(tdelta.total_seconds())
    elif inputtype in ['s', 'seconds']:
        remainder = int(tdelta)
    elif inputtype in ['m', 'minutes']:
        remainder = int(tdelta)*60
    elif inputtype in ['h', 'hours']:
        remainder = int(tdelta)*3600
    elif inputtype in ['d', 'days']:
        remainder = int(tdelta)*86400
    elif inputtype in ['w', 'weeks']:
        remainder = int(tdelta)*604800

    f = Formatter()
    desired_fields = [field_tuple[1] for field_tuple in f.parse(fmt)]
    possible_fields = ('W', 'D', 'H', 'M', 'S')
    constants = {'W': 604800, 'D': 86400, 'H': 3600, 'M': 60, 'S': 1}
    values = {}
    for field in possible_fields:
        if field in desired_fields and field in constants:
            values[field], remainder = divmod(remainder, constants[field])
    return f.format(fmt, **values)

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
        runTime = strfdelta(datetime.now() - self.m_bootTime)
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
            with open('./cnfg/doorStats.txt', 'r') as statsFile:
                self.m_nrTotalDoorMovements = myUtils.tryInt(statsFile.read().rstrip())
        except IOError:
            self.m_nrTotalDoorMovements = 0

    def __storeDoorFile(self):
        with open('./cnfg/doorStats.txt', 'w') as f:
            f.write(str(self.m_nrTotalDoorMovements) + '\n')
