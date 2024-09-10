from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

engine = create_engine('sqlite:///bot.db')

Base = declarative_base()

class User(Base):
    __tablename__ = 'User'

    id = Column(Integer, primary_key=True)
    user_tg_id = Column(Integer)
    username = Column(String)
    password = Column(String)
    subscriptions = Column(String)


class Mass_media(Base):
    __tablename__ = 'Mass_media'

    id = Column(Integer, primary_key=True)
    media_link = Column(String, nullable=False)
    media_name = Column(String)
    last_message = Column(String)
    subscribers = Column(String)

start_db = Base.metadata.create_all(engine)