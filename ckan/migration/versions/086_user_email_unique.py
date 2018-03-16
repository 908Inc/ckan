# encoding: utf-8
from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    metadata = MetaData()
    metadata.bind = migrate_engine
    user_sql = 'ALTER TABLE "user" ADD UNIQUE (email);'
    migrate_engine.execute(user_sql)
