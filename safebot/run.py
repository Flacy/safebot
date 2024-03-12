from safebot import handlers
from safebot.client import client
from safebot.detect import link
from safebot.handlers import emitter

link.init()
emitter.init()
handlers.init()

client.run()
