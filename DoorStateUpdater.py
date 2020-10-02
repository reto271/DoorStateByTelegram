import sys
import time
import random
import datetime
import telepot

from gpiozero import Button
from gpiozero import LED
from time import sleep


# ------------------------------------------------------------------------------
# Print version and infos at startup
def versionAndUsage(bot, userId):
    helpText = str('Garage Door Controller\n\n' + VersionNumber +
               '\n\nSend the following messages to the bot:\n' +
               '   T: to get the current TIME.\n' +
#               '   Reg: to REGISTER yourself. You will get state updates.\n' +
               '   G: GET the current door state.\n' +
               '   C: CLOSE the door.\n' +
               '   O: OPEN the door.\n' +
               '   H: print this HELP.\n' +
                   '\n(c) by reto271\n')
    m_debugLogger.logMultiLineText(helpText)
    if '' != bot:
        bot.sendMessage(userId, helpText)


# ------------------------------------------------------------------------------
# Message handler for the bot
def handle(msg):
    userId = getIntKey2(msg, 'chat', 'id', -1)
    command = getStringKey1(msg, 'text', '-')
    firstName = getStringKey2(msg, 'from', 'first_name', 'NoFirstName')
    lastName = getStringKey2(msg, 'from', 'last_name', 'NoLastName')
    userName = getStringKey2(msg, 'from', 'username', 'NoUserName')

    m_debugLogger.logText('-------------------------------------------')
    #m_debugLogger.logText(str(msg))
    m_debugLogger.logMessageWithUser(firstName, lastName, userName, userId, command)
    m_debugLogger.logText('-------------------------------------------')

    #m_debugLogger.logText('Got cmd: %s' % command)
    if command == 'T':
        bot.sendMessage(userId, str(datetime.datetime.now()))
    elif command == 'G':
        if True == m_doorStateInput.getState():
            m_debugLogger.logText('Door open')
            bot.sendMessage(userId, 'Door state: open')
        else:
            m_debugLogger.logText('Door closed')
            bot.sendMessage(userId, 'Door state: closed')
    elif command == 'H':
        versionAndUsage(bot, userId)

    elif 'Reg' == command:
        m_accessRequestHandler.requestPermission(firstName, lastName, userName, userId)

    elif 'Y' == command[0]:
        if True == m_accessRequestHandler.isAdmin(userId):
            m_accessRequestHandler.ackNewUser(command[2:])

    elif 'N' == command[0]:
        if True == m_accessRequestHandler.isAdmin(userId):
            m_accessRequestHandler.rejectNewUser(command[2:])

    elif 'Pr' == command:
        if True == m_accessRequestHandler.isAdmin(userId):
            m_accessRequestHandler.showPendingRequests()

    elif command == 'C':
        if True == m_userListHandler.isUserRegistered(bot, userId):
            if True == m_doorStateInput.getState():
                bot.sendMessage(userId, 'Door closing...')
                m_doorMovementOutput.triggerDoorMovement()
            else:
                bot.sendMessage(userId, 'Door is already closed.')
                m_debugLogger.logText('Door is already closed.')
    elif command == 'O':
        if True == m_userListHandler.isUserRegistered(bot, userId):
            if False == m_doorStateInput.getState():
                bot.sendMessage(userId, 'Door opening...')
                m_doorMovementOutput.triggerDoorMovement()
            else:
                bot.sendMessage(userId, 'Door is already open.')
                m_debugLogger.logText('Door is already open.')
    else:
        bot.sendMessage(userId, 'Command not supported.')
        m_debugLogger.logText('Command not supported.')


# ------------------------------------------------------------------------------
# Extract string from first level key
def getStringKey1(testDict, keyName, defaultString):
    strValue = defaultString
    if keyName in testDict:
        strValue =  testDict[keyName]
    m_debugLogger.logText('{' + keyName + '} : ' + str(strValue))
    return strValue


# ------------------------------------------------------------------------------
# Extract string from second level key
def getStringKey2(testDict, keyName, keySubName, defaultString):
    strValue = defaultString
    if keyName in testDict:
        if keySubName in testDict[keyName]:
            strValue =  testDict[keyName][keySubName]
    m_debugLogger.logText('{' + keyName + ', ' + keySubName + '} : ' + strValue)
    return strValue


# ------------------------------------------------------------------------------
# Extract int from first level key
def getIntKey1(testDict, keyName, defaultValue):
    intValue = defaultValue
    if keyName in testDict:
        intValue =  tryInt(testDict[keyName], 10, defaultValue)
    m_debugLogger.logText('{' + keyName + '} : ' + str(intValue))
    return intValue


# ------------------------------------------------------------------------------
# Extract int from second level key
def getIntKey2(testDict, keyName, keySubName, defaultValue):
    intValue = defaultValue
    if keyName in testDict:
        if keySubName in testDict[keyName]:
            intValue =  tryInt(testDict[keyName][keySubName], 10, defaultValue)
    m_debugLogger.logText('{' + keyName + ', ' + keySubName + '} : ' + str(intValue))
    return intValue


# ------------------------------------------------------------------------------
# Periodically polls the inputs and sends status updates
def sendStateUpdate():
    if True == m_userListHandler.isListEmpty():
        m_debugLogger.logText('No registered users')
    else:
        userList = m_userListHandler.getUserList()
        for userId in userList:
            m_debugLogger.logText('Update user with id: ' + str(userId))
            if True == m_doorStateInput.getState():
                bot.sendMessage(userId, '-> Door state: open')
            else:
                bot.sendMessage(userId, '-> Door state: closed')


# ------------------------------------------------------------------------------
# Try if it is an int and return a default value
def tryInt(s, base=10, val=-1):
  try:
    return int(s, base)
  except ValueError:
    return val


# ------------------------------------------------------------------------------
# Reads the telegram Id of this bot from botId.txt
def readTelegramId():
    try:
        with open('./botId.txt', 'r') as idfile:
            myId=idfile.read().rstrip()
    except IOError:
        myId=''
        m_debugLogger.logText('File "botId.txt" not found.')
    return myId


# ------------------------------------------------------------------------------
# User handler, adds users to the list and stores them persistent
class UserListHandler:
    m_users = []

    def addUser(self, userId):
        isAlreadyInList = 0
        for user in self.m_users:
            if user == userId:
                isAlreadyInList = 1
        if 0 == isAlreadyInList:
            self.m_users.append(userId)
            #m_debugLogger.logText('Add user: ' + str(userId))

    def isListEmpty(self):
        return not self.m_users

    def storeList(self):
        with open('./registeredIds.txt', 'w') as f:
            m_debugLogger.logText('---')
            for user in self.m_users:
                f.write(str(user) + '\n')
                m_debugLogger.logText('Registered user: ' + str(user))
            m_debugLogger.logText('---')

    def loadList(self):
        try:
            with open('./registeredIds.txt', 'r') as idfile:
                usersList = idfile.readlines()
                m_debugLogger.logText('---')
                for user in usersList:
                    self.addUser(tryInt(user.rstrip()))
                    m_debugLogger.logText('Registered user: ' + str(user.rstrip()))
                m_debugLogger.logText('---')
        except IOError:
            m_debugLogger.logText('No registered users')

    def getUserList(self):
        return self.m_users

    def isUserRegistered(self, bot, userId):
        isUserValid = False
        for user in self.m_users:
            if user == userId:
                isUserValid = True
        if False == isUserValid:
            m_debugLogger.logText('You are not authorized. ' + str(userId))
            bot.sendMessage(userId, 'You are not authorized.')
        return isUserValid


# ------------------------------------------------------------------------------
# Boolean input signal encapsulation
class BooleanSignalInput:
    m_state = False
    m_lastState = False
    m_botton = []

    def initialize(self, gpioNumber):
        self.m_button = Button(gpioNumber)
        self.sample()
        self.m_lastState = self.m_state

    def sample(self):
        if self.m_button.is_pressed:
            self.m_state = True
        else:
            self.m_state = False

    def isChanged(self):
        didChange = self.m_state != self.m_lastState
        self.m_lastState = self.m_state
        return didChange

    def getState(self):
        return self.m_state


# ------------------------------------------------------------------------------
# Output impulse handler
class OutputPulseHandler:
    m_output = []
    m_requestImpulse = False
    m_sendImpulse = False

    def initialize(self, gpioNumber, initValue):
        self.m_output = LED(gpioNumber)
        self.m_output.off()

    def triggerDoorMovement(self):
        self.m_requestImpulse = True
        m_debugLogger.logText('Request door movement')

    def processOutput(self):
        if True == self.m_sendImpulse:
            self.m_output.off()
            self.m_sendImpulse = False

        if True == self.m_requestImpulse:
            self.m_output.on()
            self.m_requestImpulse = False
            self.m_sendImpulse = True


# ------------------------------------------------------------------------------
# Register Users, the admin shall aprove new users.
class AccesRequestHandler:
    m_adminId = 0
    m_pendingReqList = []

    def initialize(self):
        try:
            with open('./adminId.txt', 'r') as idfile:
                self.m_adminId = tryInt(idfile.read().rstrip())
                m_debugLogger.logText('Admin Id: ' + str(self.m_adminId))
        except IOError:
            m_debugLogger.logText('Admin not yet defined.')

    def requestPermission(self, newUserFirstName, newUserLastName, newUserName, newUserId):
        if 0 == self.m_adminId:
            m_debugLogger.logText('admin not yet defined...')
            self.setNewAdmin(newUserId)
            m_userListHandler.addUser(newUserId)
            m_userListHandler.storeList()
        else:
            m_debugLogger.logText('admin already defined...')
            self.sendRequestToAdmin(newUserFirstName, newUserLastName, newUserName, newUserId)
            self.addRequestToList(newUserId)

    def setNewAdmin(self, newUserId):
        with open('./adminId.txt', 'w') as f:
            f.write(str(newUserId) + '\n')
            m_debugLogger.logText('Registered admin: ' + str(newUserId))
            self.m_adminId = newUserId

    def sendRequestToAdmin(self, newUserFirstName, newUserLastName, newUserName, newUserId):
        reqText = 'User [' + newUserFirstName + ' ' + newUserLastName + ' ' + newUserName + '] (ID: ' + str(newUserId) + ') requests access.'
        bot.sendMessage(self.m_adminId, reqText)
        m_debugLogger.logText(reqText)

    def addRequestToList(self, newUserId):
        self.m_pendingReqList.append(newUserId)

    def ackNewUser(self, newUserId):
        newUserIdInt = tryInt(newUserId)
        if True == self.isFeedbackCorrect(newUserIdInt):
            self.m_pendingReqList.remove(newUserIdInt)
            m_userListHandler.addUser(newUserIdInt)
            m_userListHandler.storeList()
            ackText = 'Your request was approved.'
            bot.sendMessage(newUserIdInt, ackText)
            m_debugLogger.logText(ackText + ' (' + newUserId + ')')

    def rejectNewUser(self, newUserId):
        newUserIdInt = tryInt(newUserId)
        if True == self.isFeedbackCorrect(newUserIdInt):
            self.m_pendingReqList.remove(newUserIdInt)
            rejectText = 'Your request was rejected.'
            bot.sendMessage(newUserIdInt, rejectText)
            m_debugLogger.logText(rejectText + ' (' + newUserId + ')')

    def isFeedbackCorrect(self, newUserId):
        requestFound = False
        for user in self.m_pendingReqList:
            if user == newUserId:
                requestFound = True
        if False == requestFound:
            respText = 'No request pending to req: ' + str(newUserId)
            m_debugLogger.logText(respText)
            bot.sendMessage(self.m_adminId, respText)
        return requestFound

    def showPendingRequests(self):
        testPendingReq = 'Pending req:\n'
        m_debugLogger.logText('Pending Requests >>>')
        for req in self.m_pendingReqList:
            m_debugLogger.logText(str(req))
            testPendingReq = testPendingReq + str(req) + '\n'
        m_debugLogger.logText('Pending Requests <<<')
        bot.sendMessage(self.m_adminId, testPendingReq)

    def isAdmin(self, userId):
        retValue = False
        m_debugLogger.logText('isAdmin')
        if userId == self.m_adminId:
            retValue = True
        else:
            responseText = 'Command requires admin previdges'
            m_debugLogger.logText(responseText)
            bot.sendMessage(self.m_adminId, responseText)
        return retValue

# ------------------------------------------------------------------------------
# Logger
class DebugLogger:
    def logMessageWithUser(self, firstName, lastName, userName, usrId, command):
        print (str(datetime.datetime.now()) +
               ' [' + firstName + ' ' + lastName + ' ' + userName + '] ' +
               str(usrId) + ' : ' + command)

    def logText(self, text):
        print (str(datetime.datetime.now()) +
               ' : ' + text)

    def logMultiLineText(self, text):
        print (str(datetime.datetime.now()) +
               ' : >>>\n' + text + '\n<<<\n')


# ------------------------------------------------------------------------------
# Main program
VersionNumber='V01.07 B04'
#VersionNumber='V01.06'

m_debugLogger = DebugLogger()

m_telegramId = readTelegramId()

m_userListHandler = UserListHandler()
m_userListHandler.loadList()

m_accessRequestHandler = AccesRequestHandler()
m_accessRequestHandler.initialize()

# Use GPIO 23
m_doorStateInput = BooleanSignalInput()
m_doorStateInput.initialize(23)

# Use GPIO 24
m_doorMovementOutput = OutputPulseHandler()
m_doorMovementOutput.initialize(24, False)

if '' == m_telegramId:
    m_debugLogger.logText('Internal telegram id not found. Create a file "botId.txt" containing the ID of the bot.')
else:
    bot = telepot.Bot(m_telegramId)
    bot.message_loop(handle)

    userList = m_userListHandler.getUserList()
    for userId in userList:
        versionAndUsage(bot, userId)

    while 1:
        time.sleep(1)
        m_doorStateInput.sample()
        m_doorMovementOutput.processOutput()
        if (True == m_doorStateInput.isChanged()):
            sendStateUpdate()
