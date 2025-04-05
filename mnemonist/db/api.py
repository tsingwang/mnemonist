from datetime import date, timedelta
from typing import Iterator

from .models import Session, Deck, Card, ReviewRecord


def deck_list() -> list:
    decks = []
    with Session.begin() as session:
        for deck in session.query(Deck):
            d = deck.to_dict()
            total_review = sum(card.review_count for card in deck.cards)
            total_forget = sum(card.forget_count for card in deck.cards)
            accuracy = 100 * (total_review - total_forget) / total_review \
                    if total_review != 0 else 0
            d['accuracy'] = accuracy
            d['total'] = deck.cards.count()
            d['today'] = deck.cards.filter(Card.schedule_day <= date.today()).count()
            decks.append(d)
    return decks

def deck_new(name: str) -> None:
    with Session.begin() as session:
        if session.query(Deck).filter_by(name=name).count() > 0:
            return
        session.add(Deck(name=name))

def deck_update(id: int, name: str) -> None:
    with Session.begin() as session:
        deck = session.query(Deck).get(id)
        if deck and deck.name != name \
                and session.query(Deck).filter_by(name=name).count() == 0:
            deck.name = name

def deck_delete(id: int) -> None:
    with Session.begin() as session:
        deck = session.query(Deck).get(id)
        if not deck or deck.cards.count() > 0:
            return
        session.delete(deck)


def card_today_list(deck_id: int) -> Iterator[dict]:
    with Session.begin() as session:
        for card in session.query(Card).filter_by(deck_id=deck_id).\
                filter(Card.schedule_day <= date.today()).order_by("schedule_day"):
            yield card.to_dict()

def card_list(deck_id: int, order: str = "schedule_day",
              offset: int = 0, limit: int = 10000) -> Iterator[dict]:
    with Session.begin() as session:
        for card in session.query(Card).filter_by(deck_id=deck_id).\
                order_by(order).offset(offset).limit(limit):
            yield card.to_dict()

def card_new(deck_id: int, question: str, answer: str) -> None:
    with Session.begin() as session:
        session.add(Card(deck_id=deck_id, question=question, answer=answer))

def card_get(id: int) -> None:
    with Session.begin() as session:
        card = session.query(Card).get(id)
        return card.to_dict() if card else None

def card_update(id: int, question: str, answer: str) -> None:
    with Session.begin() as session:
        card = session.query(Card).get(id)
        card.question = question
        card.answer = answer

def card_delete(id: int) -> None:
    with Session.begin() as session:
        session.query(Card).filter_by(id=id).delete()

def card_master(id: int) -> None:
    with Session.begin() as session:
        card = session.query(Card).get(id)
        if card is None:
            return
        card.review_count += 1
        card.master_count += 1
        card.interval = min(365, int(card.interval * card.ease_factor))
        card.ease_factor = max(1.3, card.ease_factor - 0.1)
        card.schedule_day = date.today() + timedelta(days=card.interval)

        today = date.today()
        r = session.query(ReviewRecord).filter_by(deck_id=card.deck_id,
                                                  date=today).first()
        if r:
            r.total_master += 1
        else:
            session.add(ReviewRecord(date=today, deck_id=card.deck_id,
                                     total_master=1, total_forget=0))

def card_forget(id: int) -> None:
    with Session.begin() as session:
        card = session.query(Card).get(id)
        if card is None:
            return
        card.review_count += 1
        card.forget_count += 1
        card.master_count = 0
        card.interval = 1
        card.ease_factor = min(2.5, card.ease_factor + 0.2)
        card.schedule_day = date.today() + timedelta(days=card.interval)

        today = date.today()
        r = session.query(ReviewRecord).filter_by(deck_id=card.deck_id,
                                                  date=today).first()
        if r:
            r.total_forget += 1
        else:
            session.add(ReviewRecord(date=today, deck_id=card.deck_id,
                                     total_master=0, total_forget=1))


def review_record_get(deck_id: int, date: date = date.today()) -> dict:
    with Session.begin() as session:
        r = session.query(ReviewRecord).filter_by(deck_id=deck_id, date=date).first()
        return r.to_dict() if r else None
