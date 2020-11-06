import sys
import time
import myUtils

# ------------------------------------------------------------------------------
# User handler, adds users to the list and stores them persistent
class UserListHandler:

    def __init__(self, silentMode = False, debugLogger = []):
        self.m_users = []
        self.m_fileName = []
        self.m_silentMode = silentMode
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
            #self.__printText('Add user: ' + str(userId))

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
            if False == self.m_silentMode:
                self.__printText('--- : ' + self.m_fileName)
            for user in self.m_users:
                f.write(str(user) + '\n')
                if False == self.m_silentMode:
                    self.__printText('Registered user: ' + str(user))
            if False == self.m_silentMode:
                self.__printText('--- : ' + self.m_fileName)

    def loadList(self):
        try:
            with open(self.m_fileName, 'r') as idfile:
                usersList = idfile.readlines()
                if False == self.m_silentMode:
                    self.__printText('--- : ' + self.m_fileName)
                for user in usersList:
                    self.addUser(myUtils.tryInt(user.rstrip()))
                    if False == self.m_silentMode:
                        self.__printText('Registered user: ' + str(user.rstrip()))
                if False == self.m_silentMode:
                    self.__printText('--- : ' + self.m_fileName)
        except IOError:
            self.__printText('No registered users: ' + self.m_fileName)

    def getUserList(self):
        return self.m_users

    def isUserRegistered(self, userId):
        isUserValid = False
        for user in self.m_users:
            if user == userId:
                isUserValid = True
        if False == isUserValid:
            if False == self.m_silentMode:
                self.__printText('You are not authorized. ' + str(userId))
        return isUserValid

    def printList(self):
        self.__printText('--------------------list: ' + self.m_fileName)
        for curUser in self.m_users:
            self.__printText('   ' + str(curUser))
        self.__printText('--------------------list: ' + self.m_fileName)


    def __printText(self, text):
        if self.m_debugLogger:
            self.__printText(text)
        else:
            print(text)
