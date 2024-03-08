import handlers
from client import client
from detect import link
from handlers import messages

link.init()
messages.init()
handlers.init()

client.run()
