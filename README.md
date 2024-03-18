# Safebot
Secure your cozy little chat room.

### Navigation
1. [What's this?](#-whats-this)
2. [Launch](#-launch)
3. [Features](#-features)
4. [Feedback](#-feedback)
5. [Open-source solution](#-open-source-solution)

# ❓ What's this?
## TL;DR
This is a bot (under the user's account) that filters every message from bots in the chat.
It deletes all messages sent by bots containing any advertisements,
or removes any unsafe content and sends an echo message.

## Why is it needed?
Unfortunately, in the RU segment, there are numerous bots that send advertising messages
(especially in group chats).
This advertising is almost always from second-rate (or third-rate) bots.
They don't provide anything valuable, and serve only to make a profit.

## Why not a bot?
Telegram doesn't allow a bot to track messages from other bots.
In essence, this is the **same bot, but under the user's account**.
It doesn't provide any user interface elements.
It is just an application for ad blocking.

# 🚀 Launch
You can [add this bot](#adding-the-bot) or [create your own](#setting-up-the-bot).

## Adding the bot
Since this is not a bot, but an account, you can't simply invite it to a chat.
First, you need to obtain the link to your chat and then send it to the bot in a
[direct message](https://t.me/safeboto).

> Note: The bot doesn't send any extra messages, so if an error occurs,
  you will have to determine what went wrong by yourself ([why this is so](#-feedback))

## Setting up the bot
Everything you need is in the `Makefile`. Simply run `make build init`,
and add the file `env/.env.prod` filled out based on `env/.env.base`.

The first login to the account (i.e., launching) is quite complicated,
because Docker doesn't provide stdin.
There are two solutions to this problem:
1. Enter `make bash` and manually start the app (the command is provided in `docker-compose.yml`).
   Enter the confirmation code and exit the container.
   The session is saved in the `session` folder and will be available there until you delete it.
2. Run Pyrogram locally and authenticate to obtain the session file.
   Move this file to the `session` folder (it needs to correspond to the client's name).

Enter `make run`.

# ✨ Features
- **Quick scanning**. By default, each message is quickly scanned for unsafe content.
- **Deep scanning**. <*Will it ever be available?*>
- **Echo messages**. If the message is a reply to user and contains advertising, 
  the same message will be sent with removed adv text
- **Silent mode**. You can turn off the messages sent by the bot.

# 💬 Feedback
For communication, you can use [direct messages](https://t.me/safeboto) or
[issues](https://github.com/Flacy/safebot/issues).
If you prefer to communicate within Telegram, please use **Russian** or **English** language.

# 🌐 Open-source solution
I have no intention of monetizing this project, so I'm making it open-source.
This allows others to inspect, deploy, or even *find vulnerabilities* ~~and improve it~~.
I have deployed the bot on a separate server and provided access only to small chats (up to 50 members).

> If you need this bot in chats exceeding the member limit, please wait for paid access.
  Yes, there will be a donation option, but it is only for covering server costs.