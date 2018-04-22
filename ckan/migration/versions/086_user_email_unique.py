# encoding: utf-8


def upgrade(migrate_engine):
    migrate_engine.execute(
        '''
        ALTER TABLE "user"
        ADD UNIQUE (email);
        '''
    )
