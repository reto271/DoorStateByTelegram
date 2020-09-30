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
def versionAndUsage(bot, chatId):
    helpText = str('Garage Door Controller\n\n' + VersionNumber +
               '\n\nSend the following messages to the bot:\n' +
               '   T: to get the current TIME.\n' +
#               '   R: to REGISTER yourself. You will get state updates.\n' +
               '   G: GET the current door state.\n' +
               '   C: CLOSE the door.\n' +
               '   O: OPEN the door.\n' +
               '   H: print this HELP.\n' +
                   '\n(c) by reto271\n')
    print helpText
    if '' != bot:
        bot.sendMessage(chatId, helpText)


# ------------------------------------------------------------------------------
# Message log
def addMsgLogEntry(firstName, lastName, usrId, command):
    print (str(datetime.datetime.now()) +
           ' [' + firstName + ' ' + lastName + '] ' +
           str(usrId) +
           ' : ' + command)


# ------------------------------------------------------------------------------
# Message handler for the bot
def handle(msg):
    chatId = msg['chat']['id']
    command = msg['text']

    #print msg
    addMsgLogEntry(msg['from']['first_name'], msg['from']['last_name'], chatId, command)

    #print 'Got cmd: %s' % command
    if command == 'T':
        bot.sendMessage(chatId, str(datetime.datetime.now()))
    elif command == 'G':
        if True == m_doorStateInput.getState():
            print('Door open')
            bot.sendMessage(chatId, 'Door state: open')
        else:
            print('Door closed')
            bot.sendMessage(chatId, 'Door state: closed')
    elif command == 'H':
        versionAndUsage(bot, chatId)
    elif command == 'Reg':
        myUserHandler.addUser(msg['chat']['id'])
        myUserHandler.storeList()
        bot.sendMessage(msg['chat']['id'],"Your registered now. State updates will be sent automatically.")
    elif command == 'C':
        if True == myUserHandler.isUserRegistered(chatId, bot, chatId):
            if True == m_doorStateInput.getState():
                bot.sendMessage(chatId, 'Door closing...')
                m_doorMovementOutput.triggerDoorMovement()
            else:
                bot.sendMessage(chatId, 'Door is already closed.')
    elif command == 'O':
        if True == myUserHandler.isUserRegistered(chatId, bot, chatId):
            if False == m_doorStateInput.getState():
                bot.sendMessage(chatId, 'Door opening...')
                m_doorMovementOutput.triggerDoorMovement()
            else:
                bot.sendMessage(chatId, 'Door is already open.')
    else:
        bot.sendMessage(chatId, 'Command not supported.')
        print 'Command not supported.'


# ------------------------------------------------------------------------------
# Periodically polls the inputs and sends status updates
def sendStateUpdate():
    print 'Gpio changed to: ' + str(m_doorStateInput.getState())
    if True == myUserHandler.isListEmpty():
        print 'No registered users'
    else:
        userList = myUserHandler.getUserList()
        for userId in userList:
            print 'Update user with id: ' + str(userId)
            if True == m_doorStateInput.getState():
                bot.sendMessage(userId, '-> Door state: open')
            else:
                bot.sendMessage(userId, '-> Door state: closed')


# ------------------------------------------------------------------------------
# Reads the telegram Id of this bot from myId.txt
def readTelegramId():
    try:
        with open('./myId.txt', 'r') as idfile:
            myId=idfile.read().rstrip()
    except IOError:
        myId=''
        print 'File "myId.txt" not found.'
    return myId


# ------------------------------------------------------------------------------
# User handler, adds users to the list and stores them persistent
class UserHandler:
    m_users = []

    def addUser(self, userId):
        isAlreadyInList = 0
        for user in self.m_users:
            if user == userId:
                isAlreadyInList = 1
        if 0 == isAlreadyInList:
            self.m_users.append(userId)
            #print 'Add user: ' + str(userId)

    def isListEmpty(self):
        return not self.m_users

    def storeList(self):
        with open('./registeredIds.txt', 'w') as f:
            print '---'
            for user in self.m_users:
                f.write(str(user) + '\n')
                print 'Registered user: ' + str(user)
            print '---'

    def loadList(self):
        try:
            with open('./registeredIds.txt', 'r') as idfile:
                usersList = idfile.readlines()
                print '---'
                for user in usersList:
                    self.addUser(int(user.rstrip()))
                    print 'Registered user: ' + str(user.rstrip())
                print '---'
        except IOError:
            print 'No registered users'

    def getUserList(self):
        return self.m_users

    def isUserRegistered(self, userId, bot, chatId):
        isUserValid = False
        for user in self.m_users:
            if user == userId:
                isUserValid = True
        if False == isUserValid:
            print 'You are not authorized.'
            bot.sendMessage(chatId, 'You are not authorized.')
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

    def processOutput(self):
        if True == self.m_sendImpulse:
            print 'Output off'
            self.m_output.off()
            self.m_sendImpulse = False

        if True == self.m_requestImpulse:
            print 'Output on'
            self.m_output.on()
            self.m_requestImpulse = False
            self.m_sendImpulse = True


# ------------------------------------------------------------------------------
# Main program
VersionNumber='V01.05 B01'
#VersionNumber='V01.04'

myTelegramId = readTelegramId()

myUserHandler = UserHandler()
myUserHandler.loadList()

# Use GPIO 23
m_doorStateInput = BooleanSignalInput()
m_doorStateInput.initialize(23)

# Use GPIO 24
m_doorMovementOutput = OutputPulseHandler()
m_doorMovementOutput.initialize(24, False)

if '' == myTelegramId:
    print 'Internal telegram id not found. Create a file "myId.txt" containing the ID of the bot.'
else:

    bot = telepot.Bot(myTelegramId)
    bot.message_loop(handle)

    userList = myUserHandler.getUserList()
    for userId in userList:
        versionAndUsage(bot, userId)

    while 1:
        time.sleep(1)
        m_doorStateInput.sample()
        m_doorMovementOutput.processOutput()
        if (True == m_doorStateInput.isChanged()):
            sendStateUpdate()
