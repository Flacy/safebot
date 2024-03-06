import handlers
from client import client
from handlers import messages

messages.init()
handlers.init()

client.run()
