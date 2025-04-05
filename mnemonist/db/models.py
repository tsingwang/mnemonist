from datetime import date, datetime
from pathlib import Path

from sqlalchemy import (Column, Integer, Float, String, Text, Date, DateTime,
                        ForeignKey, UniqueConstraint, create_engine)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

from ..profile import profile


engine = create_engine("sqlite:///" + str(profile.db_path), echo=False)
Session = sessionmaker(bind=engine)

Base = declarative_base()


class Deck(Base):
    __tablename__ = "decks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), unique=True)
    created_at = Column(DateTime, default=datetime.now())
    cards = relationship("Card", back_populates="deck", lazy="dynamic",
                         cascade="all, delete-orphan")
    review_records = relationship("ReviewRecord", back_populates="deck",
                                  lazy="dynamic", cascade="all, delete-orphan")

    def to_dict(self):
        return dict([(k, v) for k, v in self.__dict__.items() if k[0] != '_'])


class Card(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, autoincrement=True)
    question = Column(Text, default='')
    answer = Column(Text, default='')
    review_count = Column(Integer, default=0)
    master_count = Column(Integer, default=0)   # Continuous mastery
    forget_count = Column(Integer, default=0)
    schedule_day = Column(Date, default=date.today())
    interval = Column(Integer, default=1)   # Current review interval (days)
    ease_factor = Column(Float, default=2.5)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())
    deck_id = Column(Integer, ForeignKey("decks.id", ondelete="CASCADE"))
    deck = relationship("Deck", back_populates="cards")

    def to_dict(self):
        return dict([(k, v) for k, v in self.__dict__.items() if k[0] != '_'])


class ReviewRecord(Base):
    __tablename__ = "review_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, default=date.today())
    total_master = Column(Integer, default=0)
    total_forget = Column(Integer, default=0)
    deck_id = Column(Integer, ForeignKey("decks.id", ondelete="CASCADE"))
    deck = relationship("Deck", back_populates="review_records")
    UniqueConstraint(deck_id, date)

    def to_dict(self):
        return dict([(k, v) for k, v in self.__dict__.items() if k[0] != '_'])


Base.metadata.create_all(engine)
