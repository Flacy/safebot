import handlers
from client import client
from detect import link
from handlers import sender

link.init()
sender.init()
handlers.init()

client.run()
