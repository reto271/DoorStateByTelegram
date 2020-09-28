import sys
import time
import random
import datetime
import telepot

from gpiozero import Button
from time import sleep

# Print version and infos at startup
def versionAndUsage(bot, chatId):
    print('Door State Updater')
    print(VersionNumber)
    print('')
    print('Send the following messages to the bot:')
    print('   T: to get the current time.')
    print('   R: to register yourself. You will get state updates.')
    print('   D: poll the current door state.')
    print('   H: print this help.')
    print('')
    print('(c) by reto271')
    print('')
    if '' != bot:
        bot.sendMessage(chatId, 'Door State Updater\n\n' + VersionNumber +
                        '\n\nSend the following messages to the bot:\n' +
                        '   T: to get the current time.\n' +
                        '   R: to register yourself. You will get state updates.\n' +
                        '   D: poll the current door state.\n' +
                        '   H: print this help.\n' +
                        '\n(c) by reto271\n')


# Message handler for the bot
def handle(msg):
    chat_id = msg['chat']['id']
    command = msg['text']

    #print 'Got cmd: %s' % command
    if command == 'T':
        bot.sendMessage(chat_id, str(datetime.datetime.now()))
    elif command == 'D':
        if False == gpio2.getState():
            print('Door open')
            bot.sendMessage(chat_id, 'Door state: open')
        else:
            print('Door closed')
            bot.sendMessage(chat_id, 'Door state: closed')
    elif command == 'H':
        versionAndUsage(bot, chat_id)
    elif command == 'R':
        print('Register')
        myUserHandler.addUser(msg['chat']['id'])
        myUserHandler.storeList()
        bot.sendMessage(msg['chat']['id'],"Your ID is saved. State updates will be sent automatically.")


# Periodically polls the inputs and sends status updates
def sendStateUpdate():
    print 'Gpio changed to: ' + str(gpio2.getState())
    if True == myUserHandler.isListEmpty():
        print 'No registered users'
    else:
        userList = myUserHandler.getUserList()
        for userId in userList:
            print 'Update user with id: ' + str(userId)
            if True == gpio2.getState():
                bot.sendMessage(userId, '-> Door state: closed')
            else:
                bot.sendMessage(userId, '-> Door state: open')


# Reads the telegram Id of this bot from myId.txt
def readTelegramId():
    try:
        with open('./myId.txt', 'r') as idfile:
            myId=idfile.read().rstrip()
    except IOError:
        myId=''
        print 'No registered users'
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
            for user in self.m_users:
                f.write(str(user) + '\n')

    def loadList(self):
        try:
            with open('./registeredIds.txt', 'r') as idfile:
                usersList = idfile.readlines()
                for user in usersList:
                    self.addUser(int(user.rstrip()))
        except IOError:
            print 'No registered users'

    def getUserList(self):
        return self.m_users


# ------------------------------------------------------------------------------
# Boolean signal encapsulation
class BooleanSignal:
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



# Main program
#VersionNumber='V01.02 B01'
VersionNumber='V01.02'

myTelegramId = readTelegramId()

myUserHandler = UserHandler()
myUserHandler.loadList()

gpio2 = BooleanSignal()
gpio2.initialize(2)

if '' == myTelegramId:
    print 'Internal telegram id not found'
else:

    bot = telepot.Bot(myTelegramId)
    bot.message_loop(handle)

    userList = myUserHandler.getUserList()
    for userId in userList:
        versionAndUsage(bot, userId)

    while 1:
        time.sleep(1)
        gpio2.sample()
        if (True == gpio2.isChanged()):
            sendStateUpdate()
