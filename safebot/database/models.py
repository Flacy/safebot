import peewee

from safebot.database.client import connection


class BaseModel(peewee.Model):
    class Meta:
        database = connection


class Chat(BaseModel):
    # Telegram chat ID
    t_id = peewee.BigIntegerField(unique=True)
    # This mode means that every action or error will not be displayed in the chat
    silent_mode = peewee.BooleanField(default=False)
