import handlers
from client import client
from detect import link
from handlers import emitter

link.init()
emitter.init()
handlers.init()

client.run()
