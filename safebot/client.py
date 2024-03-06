from pyrogram import Client

from settings import config

__client_name = "safebot"

if not config.production:
    __client_name += "_dev"

client = Client(
    name=__client_name,
    api_id=config.api_id,
    api_hash=config.api_hash,
    phone_number=config.phone_number,
    workdir="session",
)
