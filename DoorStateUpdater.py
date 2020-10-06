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
               '   E: ENABLE notifications.\n' +
               '   D: DISABLE notifications.\n' +
               '   H: print this HELP.\n' +
                   '\n(c) by reto271\n')
    m_debugLogger.logMultiLineText(userId, helpText)
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


    # -----
    # The only accessible command if the user is not registered
    if 'Reg' == command:
        m_accessRequestHandler.requestPermission(firstName, lastName, userName, userId)

    # -----
    # User commands
    elif command == 'T':
        if True == m_userAccessList.isUserRegistered(bot, userId):
            bot.sendMessage(userId, str(datetime.datetime.now()))

    elif command == 'G':
        if True == m_userAccessList.isUserRegistered(bot, userId):
            if True == m_doorStateInput.getState():
                m_debugLogger.logText('Door open')
                bot.sendMessage(userId, 'Door state: open')
            else:
                m_debugLogger.logText('Door closed')
                bot.sendMessage(userId, 'Door state: closed')

    elif command == 'H':
        if True == m_userAccessList.isUserRegistered(bot, userId):
            versionAndUsage(bot, userId)

    elif command == 'C':
        if True == m_userAccessList.isUserRegistered(bot, userId):
            if True == m_doorStateInput.getState():
                bot.sendMessage(userId, 'Door closing...')
                m_doorMovementOutput.triggerDoorMovement()
            else:
                bot.sendMessage(userId, 'Door is already closed.')
                m_debugLogger.logText('Door is already closed.')

    elif command == 'O':
        if True == m_userAccessList.isUserRegistered(bot, userId):
            if False == m_doorStateInput.getState():
                bot.sendMessage(userId, 'Door opening...')
                m_doorMovementOutput.triggerDoorMovement()
            else:
                bot.sendMessage(userId, 'Door is already open.')
                m_debugLogger.logText('Door is already open.')

    elif 'E' == command:
        if True == m_userAccessList.isUserRegistered(bot, userId):
            text = 'Notifications enabled'
            m_userNotificationList.addUser(userId)
            m_userNotificationList.storeList()
            bot.sendMessage(userId, text)
            m_debugLogger.logMessageWithUserId(userId, text)

    elif 'D' == command:
        if True == m_userAccessList.isUserRegistered(bot, userId):
            text = 'Notifications disabled'
            m_userNotificationList.removeUser(userId)
            m_userNotificationList.storeList()
            bot.sendMessage(userId, text)
            m_debugLogger.logMessageWithUserId(userId, text)

    # -----
    # Admin commands
    elif 'Y' == command[0]:
        if True == m_accessRequestHandler.isAdmin(userId):
            m_accessRequestHandler.ackNewUser(command[2:])

    elif 'N' == command[0]:
        if True == m_accessRequestHandler.isAdmin(userId):
            m_accessRequestHandler.rejectNewUser(command[2:])

    elif 'Pr' == command:
        if True == m_accessRequestHandler.isAdmin(userId):
            m_accessRequestHandler.showPendingRequests()

    else:
        if True == m_userAccessList.isUserRegistered(bot, userId):
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
        intValue =  tryInt(testDict[keyName], defaultValue)
    m_debugLogger.logText('{' + keyName + '} : ' + str(intValue))
    return intValue


# ------------------------------------------------------------------------------
# Extract int from second level key
def getIntKey2(testDict, keyName, keySubName, defaultValue):
    intValue = defaultValue
    if keyName in testDict:
        if keySubName in testDict[keyName]:
            intValue =  tryInt(testDict[keyName][keySubName], defaultValue)
    m_debugLogger.logText('{' + keyName + ', ' + keySubName + '} : ' + str(intValue))
    return intValue


# ------------------------------------------------------------------------------
# Periodically polls the inputs and sends status updates
def sendStateUpdate():
    if True == m_userNotificationList.isListEmpty():
        m_debugLogger.logText('No registered users to notify')
    else:
        userList = m_userNotificationList.getUserList()
        for userId in userList:
            doorNotification = []
            if True == m_doorStateInput.getState():
                doorNotification = '-> Door state: open'
            else:
                doorNotification = '-> Door state: closed'
            bot.sendMessage(userId, doorNotification)
            m_debugLogger.logMessageWithUserId(userId, doorNotification)


# ------------------------------------------------------------------------------
# Try if it is an int and return a default value
def tryInt(s, val=-1):
  try:
    return int(s)
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

    def __init__(self):
        self.m_users = []
        self.m_fileName = []

    def initialize(self, fileName):
        self.m_fileName = fileName

    def addUser(self, userId):
        isAlreadyInList = False
        for user in self.m_users:
            if user == userId:
                isAlreadyInList = True
        if False == isAlreadyInList:
            self.m_users.append(userId)
            #m_debugLogger.logText('Add user: ' + str(userId))

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
            m_debugLogger.logText('--- : ' + self.m_fileName)
            for user in self.m_users:
                f.write(str(user) + '\n')
                m_debugLogger.logText('Registered user: ' + str(user))
            m_debugLogger.logText('--- : ' + self.m_fileName)

    def loadList(self):
        try:
            with open(self.m_fileName, 'r') as idfile:
                usersList = idfile.readlines()
                m_debugLogger.logText('--- : ' + self.m_fileName)
                for user in usersList:
                    self.addUser(tryInt(user.rstrip()))
                    m_debugLogger.logText('Registered user: ' + str(user.rstrip()))
                m_debugLogger.logText('--- : ' + self.m_fileName)
        except IOError:
            m_debugLogger.logText('No registered users: ' + self.m_fileName)

    def getUserList(self):
        return self.m_users

    def isUserRegistered(self, bot, userId):
        isUserValid = False
        for user in self.m_users:
            if user == userId:
                isUserValid = True
        if False == isUserValid:
            m_debugLogger.logText('You are not authorized. ' + str(userId))
#            if True == self.isUserRegistered(bot, userId):
#                bot.sendMessage(userId, 'You are not authorized.')
        return isUserValid

    def printList(self):
        m_debugLogger.logText('--------------------list: ' + self.m_fileName)
        for curUser in self.m_users:
            m_debugLogger.logText('   ' + str(curUser))
        m_debugLogger.logText('--------------------list: ' + self.m_fileName)


# ------------------------------------------------------------------------------
# Boolean input signal encapsulation
class BooleanSignalInput:

    def __init__(self):
        self.m_state = False
        self.m_lastState = False
        self.m_botton = []

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

    def __init__(self):
        self.m_output = []
        self.m_requestImpulse = False
        self.m_sendImpulse = False

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

    def __init__(self):
        self.m_adminId = 0
        self.m_pendingReqList = []

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
            m_userAccessList.addUser(newUserId)
            m_userAccessList.storeList()
            m_userNotificationList.addUser(newUserId)
            m_userNotificationList.storeList()
        else:
            m_debugLogger.logText('admin already defined...')
            self.sendRequestToAdmin(newUserFirstName, newUserLastName, newUserName, newUserId)
            self.addRequestToList(newUserId)

    def setNewAdmin(self, newUserId):
        with open('./adminId.txt', 'w') as f:
            f.write(str(newUserId) + '\n')
            self.m_adminId = newUserId
            m_debugLogger.logText('New registered admin: ' + str(newUserId))
            bot.sendMessage(self.m_adminId, 'You are registered as admin')

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
            m_userAccessList.addUser(newUserIdInt)
            m_userAccessList.storeList()
            m_userNotificationList.addUser(newUserIdInt)
            m_userNotificationList.storeList()
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
    def logMessageWithUser(self, firstName, lastName, userName, usrId, text):
        print (str(datetime.datetime.now()) + ' : ' +
               '[' + firstName + ' ' + lastName + ' ' + userName + '] ' +
               str(usrId) + ' : ' + text)

    def logMessageWithUserId(self, usrId, text):
        print (str(datetime.datetime.now()) + " : " +
               str(usrId) + ' : ' + text)

    def logText(self, text):
        print (str(datetime.datetime.now()) + ' : ' +
               text)

    def logMultiLineText(self, userId, text):
        print (str(datetime.datetime.now()) +
               ' : ' +str(userId) + ' >>>\n' +
               text + '\n<<<\n')


# ------------------------------------------------------------------------------
# Main program
VersionNumber='V01.09 B01'
#VersionNumber='V01.08'

m_debugLogger = DebugLogger()

m_telegramId = readTelegramId()

m_userAccessList = UserListHandler()
m_userAccessList.initialize('./registeredIds.txt')
m_userAccessList.loadList()
#m_userAccessList.printList()

m_userNotificationList = UserListHandler()
m_userNotificationList.initialize('./notificationIds.txt')
m_userNotificationList.loadList()
#m_userNotificationList.printList()

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

    userList = m_userNotificationList.getUserList()
    for userId in userList:
        versionAndUsage(bot, userId)

    while 1:
        time.sleep(1)
        m_doorStateInput.sample()
        m_doorMovementOutput.processOutput()
        if (True == m_doorStateInput.isChanged()):
            sendStateUpdate()
