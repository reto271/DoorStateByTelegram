# Door State Updates by Telegram
Sends messages about the door state by telegram

## Preparation
1. sudo apt update && sudo apt upgrade
1. sudo apt-get install python-pip
1. sudo pip install telepot
1. sudo apt install python-gpiozero
1. Create bot in telegram, use the Chat 'BotFather' and type the command /newbot.
1. Enter bot name, e.g. "This is my Bot"
1. Enter bot Id, e.g. this_is_my_bot
1. You will get a bot ID
1. Write a file 'cnfg/botId.txt' to the root directory of this project. Write your bot id to this file.

The bot id suffice the following format.

    1234567890:aAbBcCdDeEfFgGhHiIjJkKlLmMoOpPqQrRs

Write this ID only to the cnfg/botId.txt.

## Acknowledgments
To create a bot and send some messages I found a useful description. See https://www.instructables.com/id/Set-up-Telegram-Bot-on-Raspberry-Pi/. Many thanks to NickL17.
