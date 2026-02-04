import threading

from sqlalchemy import TEXT, Column, Numeric, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from config import DB_URI


def start() -> scoped_session:
    engine = create_engine(DB_URI, client_encoding="utf8")
    BASE.metadata.bind = engine
    BASE.metadata.create_all(engine)
    return scoped_session(sessionmaker(bind=engine, autoflush=False))


BASE = declarative_base()
SESSION = start()

INSERTION_LOCK = threading.RLock()


class Broadcast(BASE):
    __tablename__ = "broadcast"
    id = Column(Numeric, primary_key=True)
    user_name = Column(TEXT)

    def __init__(self, id, user_name):
        self.id = id
        self.user_name = user_name


Broadcast.__table__.create(checkfirst=True)


class BannedUser(BASE):
    __tablename__ = "banned_users"
    id = Column(Numeric, primary_key=True)
    user_name = Column(TEXT)
    reason = Column(TEXT)

    def __init__(self, id, user_name, reason=None):
        self.id = id
        self.user_name = user_name
        self.reason = reason


BannedUser.__table__.create(checkfirst=True)


#  Add user details -
async def add_user(id, user_name):
    with INSERTION_LOCK:
        msg = SESSION.query(Broadcast).get(id)
        if not msg:
            usr = Broadcast(id, user_name)
            SESSION.add(usr)
            SESSION.commit()


async def delete_user(id):
    with INSERTION_LOCK:
        SESSION.query(Broadcast).filter(Broadcast.id == id).delete()
        SESSION.commit()


async def full_userbase():
    users = SESSION.query(Broadcast).all()
    SESSION.close()
    return users


async def query_msg():
    try:
        return SESSION.query(Broadcast.id).order_by(Broadcast.id)
    finally:
        SESSION.close()


async def ban_user(id, user_name=None, reason=None):
    with INSERTION_LOCK:
        entry = SESSION.query(BannedUser).get(id)
        if entry:
            entry.user_name = user_name
            entry.reason = reason
        else:
            entry = BannedUser(id, user_name, reason)
            SESSION.add(entry)
        SESSION.commit()


async def unban_user(id):
    with INSERTION_LOCK:
        SESSION.query(BannedUser).filter(BannedUser.id == id).delete()
        SESSION.commit()


async def is_banned(id):
    try:
        return SESSION.query(BannedUser).get(id) is not None
    finally:
        SESSION.close()


async def get_banned_user(id):
    try:
        return SESSION.query(BannedUser).get(id)
    finally:
        SESSION.close()
