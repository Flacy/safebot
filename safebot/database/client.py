import peewee_async

from safebot.settings import config

connection = peewee_async.PostgresqlDatabase(
    host=config.postgres_host,
    port=config.postgres_port,
    user=config.postgres_user,
    password=config.postgres_password,
    database=config.postgres_db,
)
manager = peewee_async.Manager(connection)
