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
        if m_button.is_pressed:
            print('Door open')
            bot.sendMessage(chat_id, 'Door state: open')
        else:
            print('Door closed')
            bot.sendMessage(chat_id, 'Door state: closed')
    elif command == 'H':
        versionAndUsage(bot, chat_id)
    elif command == 'R':
        print('Register')
        with open('./registeredIds.txt', 'w') as f:
            f.write(str(msg['chat']['id']))
        bot.sendMessage(msg['chat']['id'],"Your ID is saved. State updates will be sent automatically.")


# Periodcally polls the inputs and sends status updates
def pollInputs():
    # Digitizes the IO states, not realy necessary...
    if m_button.is_pressed:
        gpioInput = 1
    else:
        gpioInput = 0

    # Is there any state change? If yes and there are registered users, send thy update.
    if gpioInput != pollInputs.oldGpioInput:
        print 'Gpio changed to: ' + str(gpioInput)
        try:
            with open('./registeredIds.txt', 'r') as idfile:
                chat_id=int(idfile.read())
                if pollInputs.oldGpioInput == 2:
                    versionAndUsage(bot, chat_id)
                else:
                    if gpioInput == 1:
                        print('-> Door open')
                        bot.sendMessage(chat_id, '-> Door state: open')
                    else:
                        print('-> Door closed')
                        bot.sendMessage(chat_id, '-> Door state: closed')
        except IOError:
            print 'No registered users'
        pollInputs.oldGpioInput = gpioInput


# Reads the telegram Id of this bot from myId.txt
def readTelegramId():
    try:
        with open('./myId.txt', 'r') as idfile:
            myId=idfile.read().rstrip()
    except IOError:
        myId=''
        print 'No registered users'
    return myId


# Main program
VersionNumber='V01.01 B01'
pollInputs.oldGpioInput = 2
myTelegramId = readTelegramId()

if '' == myTelegramId:
    print 'Internal telegram id not found'
else:
    m_button = Button(2)
    bot = telepot.Bot(myTelegramId)
    bot.message_loop(handle)
    print 'Booted...'

    while 1:
        time.sleep(1)
        pollInputs()
