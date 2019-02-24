# encoding: utf-8


def upgrade(migrate_engine):
    migrate_engine.execute(
        '''ALTER TABLE premoderation_log ADD COLUMN moderator_id TEXT;
ALTER TABLE premoderation_log ADD CONSTRAINT premoderation_log_user_fkey FOREIGN KEY (moderator_id)
REFERENCES "user" (id) ON UPDATE CASCADE ON DELETE SET NULL;'''
    )
