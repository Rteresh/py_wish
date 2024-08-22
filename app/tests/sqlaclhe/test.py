from sqlalchemy import event
from sqlalchemy.future import engine
from sqlalchemy.testing.plugin.plugin_base import logging


@event.listens_for(engine, "checkout")
def checkout(dbapi_connection, connection_record, connection_proxy):
    logging.info("Connection checked out: %s", dbapi_connection)


@event.listens_for(engine, "checkin")
def checkin(dbapi_connection, connection_record):
    logging.info("Connection returned to pool: %s", dbapi_connection)
