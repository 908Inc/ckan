# encoding: utf-8


def upgrade(migrate_engine):
    migrate_engine.execute('''
CREATE UNIQUE INDEX users_unique_lower_email_idx
ON "user" (lower(email));
    ''')
