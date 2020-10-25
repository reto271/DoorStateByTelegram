import sys
import time
import myUtils

# ------------------------------------------------------------------------------
# User handler, adds users to the list and stores them persistent
class UserListHandler:

    def __init__(self, debugLogger):
        self.m_users = []
        self.m_fileName = []
        self.m_debugLogger = debugLogger

    def initialize(self, fileName):
        self.m_fileName = fileName

    def addUser(self, userId):
        isAlreadyInList = False
        for user in self.m_users:
            if user == userId:
                isAlreadyInList = True
        if False == isAlreadyInList:
            self.m_users.append(userId)
            #self.m_debugLogger.logText('Add user: ' + str(userId))

    def removeUser(self, userId):
        isInList = False
        for user in self.m_users:
            if user == userId:
                isInList = True
        if True == isInList:
            self.m_users.remove(userId)

    def isListEmpty(self):
        return not self.m_users

    def storeList(self):
        with open(self.m_fileName, 'w') as f:
            self.m_debugLogger.logText('--- : ' + self.m_fileName)
            for user in self.m_users:
                f.write(str(user) + '\n')
                self.m_debugLogger.logText('Registered user: ' + str(user))
            self.m_debugLogger.logText('--- : ' + self.m_fileName)

    def loadList(self):
        try:
            with open(self.m_fileName, 'r') as idfile:
                usersList = idfile.readlines()
                self.m_debugLogger.logText('--- : ' + self.m_fileName)
                for user in usersList:
                    self.addUser(myUtils.tryInt(user.rstrip()))
                    self.m_debugLogger.logText('Registered user: ' + str(user.rstrip()))
                self.m_debugLogger.logText('--- : ' + self.m_fileName)
        except IOError:
            self.m_debugLogger.logText('No registered users: ' + self.m_fileName)

    def getUserList(self):
        return self.m_users

    def isUserRegistered(self, bot, userId):
        isUserValid = False
        for user in self.m_users:
            if user == userId:
                isUserValid = True
        if False == isUserValid:
            self.m_debugLogger.logText('You are not authorized. ' + str(userId))
#            if True == self.isUserRegistered(bot, userId):
#                bot.sendMessage(userId, 'You are not authorized.')
        return isUserValid

    def printList(self):
        self.m_debugLogger.logText('--------------------list: ' + self.m_fileName)
        for curUser in self.m_users:
            self.m_debugLogger.logText('   ' + str(curUser))
        self.m_debugLogger.logText('--------------------list: ' + self.m_fileName)
