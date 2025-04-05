from datetime import datetime

import click
from textual import work
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Static, Markdown

from ..components import DeckList
from ..db import api as db_api
from . import const
from .card import CardListScreen, CardScreen


class ReviewScreen(Screen):

    BINDINGS = [
        ("escape", "app.pop_screen", "Pop screen"),
        ("l", "list", "List Card"),
        ("n", "new", "New Card"),
        ("enter", "show_answer", "Show Answer"),
    ]

    def __init__(self, deck_id: int) -> None:
        super().__init__()
        self.deck_id = deck_id
        self.card = None
        self.card_generator = db_api.card_today_list(self.deck_id)
        r = db_api.review_record_get(self.deck_id)
        self.total_master = r.get("total_master", 0) if r else 0
        self.total_forget = r.get("total_forget", 0) if r else 0

    def compose(self) -> ComposeResult:
        yield Header()
        yield Markdown(id="question", classes="question")
        yield Static(id="stats", classes="stats")
        yield Footer()

    async def on_mount(self) -> None:
        await self.next_card()

    async def next_card(self) -> None:
        try:
            self.card = next(self.card_generator)
        except StopIteration:
            self.card = None
            return self.show_today_summary()

        self.query_one("#question").update(self.card["question"])

        stats = "LAST SEEN: {} days ago  MASTER: {}  FORGET: {}".format(
                (datetime.now() - self.card["updated_at"]).days,
                self.card["master_count"], self.card["forget_count"])
        self.query_one("#stats").update(stats)

    def show_today_summary(self) -> None:
        if self.total_master + self.total_forget == 0:
            self.query_one("#question").update("No schedule today.")
            return
        self.query_one("#question").update("Well done! See you tomorrow :)")
        summary = "Accuracy: {}/{} = {:.2f}%".format(
            self.total_master, self.total_master + self.total_forget,
            100 * self.total_master / (self.total_master + self.total_forget)
        )
        self.query_one("#stats").update(summary)

    async def action_list(self) -> None:
        self.app.push_screen(CardListScreen(self.deck_id))

    async def action_new(self) -> None:
        content = '\n\n---\n\n'
        self.app._driver.stop_application_mode()
        content = click.edit(content)
        self.app._driver.start_application_mode()
        if content is not None:
            question = content.split('---\n')[0]
            answer = '---\n'.join(content.split('---\n')[1:])
            db_api.card_new(self.deck_id, question, answer)

    @work
    async def action_show_answer(self) -> None:
        if self.card is None:
            self.app.pop_screen()
            return
        action = await self.app.push_screen_wait(CardScreen(self.card))
        if action == const.CARD_MASTER:
            db_api.card_master(self.card["id"])
            self.total_master += 1
        elif action == const.CARD_FORGET:
            db_api.card_forget(self.card["id"])
        elif action == const.CARD_DELETE:
            db_api.card_delete(self.card["id"])
        await self.next_card()
