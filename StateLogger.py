import sys
import time
import random
import datetime
from datetime import datetime
import telepot

from gpiozero import Button
from gpiozero import LED
from time import sleep

# My modules
import myUtils
import ProjectVersion
from UserListHandler import UserListHandler


class StateLogger:
    def __init__(self, logger = []):
        self.m_bootTime = datetime.now()
        self.m_logger = logger
        self.m_logger.logText('StateLogger init')

    def dumpState(self):
        self.m_logger.logText('--- State Summary --------')
        self.m_logger.logText('--- State Summary --------')
