import sys
import os
import time
import random
import datetime
import telepot

from gpiozero import Button
from gpiozero import LED
from time import sleep

# My modules
import myUtils
import ProjectVersion
from UserListHandler import UserListHandler
from DoorStatistics import DoorStatistics

# ------------------------------------------------------------------------------
# Print software infos
def startupInformation(userId, bot = []):
    helpText = str('\nReboot...\n\n' +
                   'Garage Door Controller\n' + ProjectVersion.ProjectVersionNumber +
                   '\n(c) by reto271\n')
    m_debugLogger.logMultiLineText(userId, helpText)
    if bot:
        bot.sendMessage(userId, helpText)

# ------------------------------------------------------------------------------
# Print software infos
def usageInformation(bot, userId):
    helpText = str('Garage Door Controller - ' + ProjectVersion.ProjectVersionNumber +
               '\n\nSend the following messages to the bot:\n' +
               '   T: to get the current TIME.\n' +
#               '   Reg: to REGISTER yourself. You will get state updates.\n' +
               '   G: GET the current door state.\n' +
               '   C: CLOSE the door.\n' +
               '   O: OPEN the door.\n' +
               '   E: ENABLE notifications.\n' +
               '   D: DISABLE notifications.\n' +
               '   S: STATUS dump.\n' +
               '   H: print this HELP.\n' +
               '   Hw: print the HW version of the Raspberry Pi.\n' +
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
    m_debugLogger.logMessageCommandReceived(firstName, lastName, userName, userId, command)
    m_debugLogger.logText('-------------------------------------------')


    # -----
    # The only accessible command if the user is not registered
    if 'Reg' == command:
        m_accessRequestHandler.requestPermission(firstName, lastName, userName, userId)

    # -----
    # User commands
    elif command == 'T':
        if True == m_userAccessList.isUserRegistered(userId):
            bot.sendMessage(userId, str(datetime.datetime.now()))

    elif command == 'G':
        if True == m_userAccessList.isUserRegistered(userId):
            if True == m_doorStateInput.getState():
                m_debugLogger.logText('Door open')
                bot.sendMessage(userId, 'Door state: open')
            else:
                m_debugLogger.logText('Door closed')
                bot.sendMessage(userId, 'Door state: closed')

    elif command == 'H':
        if True == m_userAccessList.isUserRegistered(userId):
            usageInformation(bot, userId)

    elif command == 'C':
        if True == m_userAccessList.isUserRegistered(userId):
            if True == m_doorStateInput.getState():
                bot.sendMessage(userId, 'Door closing...')
                m_doorMovementOutput.triggerDoorMovement()
            else:
                bot.sendMessage(userId, 'Door is already closed.')
                m_debugLogger.logText('Door is already closed.')

    elif command == 'O':
        if True == m_userAccessList.isUserRegistered(userId):
            if False == m_doorStateInput.getState():
                bot.sendMessage(userId, 'Door opening...')
                m_doorMovementOutput.triggerDoorMovement()
            else:
                bot.sendMessage(userId, 'Door is already open.')
                m_debugLogger.logText('Door is already open.')

    elif 'E' == command:
        if True == m_userAccessList.isUserRegistered(userId):
            text = 'Notifications enabled'
            m_userNotificationList.addUser(userId)
            m_userNotificationList.storeList()
            bot.sendMessage(userId, text)
            m_debugLogger.logMessageWithUserId(userId, text)

    elif 'D' == command:
        if True == m_userAccessList.isUserRegistered(userId):
            text = 'Notifications disabled'
            m_userNotificationList.removeUser(userId)
            m_userNotificationList.storeList()
            bot.sendMessage(userId, text)
            m_debugLogger.logMessageWithUserId(userId, text)

    elif 'Hw' == command:
        if True == m_userAccessList.isUserRegistered(userId):
            hwVersion = getRaspberryPi_HW_Version()
            bot.sendMessage(userId, hwVersion)
            m_debugLogger.logMessageWithUserId(userId, hwVersion)

    elif 'S' == command:
        if True == m_userAccessList.isUserRegistered(userId):
            m_doorStats.dumpState(userId)

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
        if True == m_userAccessList.isUserRegistered(userId):
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
        intValue =  myUtils.tryInt(testDict[keyName], defaultValue)
    m_debugLogger.logText('{' + keyName + '} : ' + str(intValue))
    return intValue


# ------------------------------------------------------------------------------
# Extract int from second level key
def getIntKey2(testDict, keyName, keySubName, defaultValue):
    intValue = defaultValue
    if keyName in testDict:
        if keySubName in testDict[keyName]:
            intValue =  myUtils.tryInt(testDict[keyName][keySubName], defaultValue)
    m_debugLogger.logText('{' + keyName + ', ' + keySubName + '} : ' + str(intValue))
    return intValue


# ------------------------------------------------------------------------------
# Check and eventually create directory
def createDirectory(dirName):
    if not os.path.exists(dirName):
        os.makedirs(dirName)


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
# Reads the telegram Id of this bot from cnfg/botId.txt
def readTelegramId():
    try:
        with open('./cnfg/botId.txt', 'r') as idfile:
            myId=idfile.read().rstrip()
    except IOError:
        myId=''
        m_debugLogger.logText('File "cnfg/botId.txt" not found.')
    return myId


# ------------------------------------------------------------------------------
# Get Raspberry Pi HW Info from the cpuinfo file
def getRaspberryPi_HW_Version():
    myHW_Info = "-"
    try:
        f = open('/proc/cpuinfo','r')
        for line in f:
            if line[0:5]=='Model':
                length=len(line)
                myHW_Info = line[9:length-1]
        f.close()
    except:
        myHW_Info = "unknown"
    return myHW_Info


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
            with open('./cnfg/adminId.txt', 'r') as idfile:
                self.m_adminId = myUtils.tryInt(idfile.read().rstrip())
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
        with open('./cnfg/adminId.txt', 'w') as f:
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
        newUserIdInt = myUtils.tryInt(newUserId)
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
        newUserIdInt = myUtils.tryInt(newUserId)
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
    def logMessageCommandReceived(self, firstName, lastName, userName, usrId, text):
        print (str(datetime.datetime.now()) + ' : ' +
               'Request [' + firstName + ' ' + lastName + ' ' + userName + '] ' +
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

createDirectory('log')
createDirectory('cnfg')

m_debugLogger = DebugLogger()
m_doorStats = []

m_telegramId = readTelegramId()

m_userAccessList = UserListHandler(m_debugLogger)
m_userAccessList.initialize('./cnfg/registeredIds.txt')
m_userAccessList.loadList()
#m_userAccessList.printList()

m_userNotificationList = UserListHandler(m_debugLogger)
m_userNotificationList.initialize('./cnfg/notificationIds.txt')
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
    m_debugLogger.logText('Internal telegram id not found. Create a file "cnfg/botId.txt" containing the ID of the bot.')
else:
    bot = telepot.Bot(m_telegramId)
    m_doorStats = DoorStatistics(bot, m_debugLogger)
    bot.message_loop(handle)

    userList = m_userNotificationList.getUserList()
    for userId in userList:
        startupInformation(userId, bot)
        m_doorStats.dumpState(userId)
    startupInformation(0)               # To the log, if there is no observer.
    m_doorStats.dumpState()

    while 1:
        time.sleep(1)
        m_doorStateInput.sample()
        m_doorMovementOutput.processOutput()
        if (True == m_doorStateInput.isChanged()):
            sendStateUpdate()
            m_doorStats.addDoorMovement()
        m_doorStats.run()
