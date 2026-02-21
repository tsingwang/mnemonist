import math
from datetime import datetime

import click
from textual import work
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, HorizontalScroll, VerticalScroll
from textual.screen import ModalScreen, Screen
from textual.widgets import Header, Button, Footer, Static, Markdown
from textual_image.widget import Image

from ..const import SEPARATOR
from ..db import api as db_api
from .card import CardListScreen


class AnswerScreen(ModalScreen):

    BINDINGS = [
        ("escape", "app.pop_screen", "Pop screen"),
    ]

    def __init__(self, card: dict) -> None:
        super().__init__()
        self.card = card

    def compose(self) -> ComposeResult:
        yield Header()
        yield Markdown(self.card["answer"])
        with VerticalScroll():
            for s in self.card["answer"].split("file://")[1:]:
                url = s.split(')')[0]
                img = Image(url)
                img.styles.width = math.ceil(img._image_width/25)
                yield img
        yield Footer()


class ReviewScreen(Screen):

    BINDINGS = [
        ("escape", "app.pop_screen", "Pop screen"),
        ("l", "list", "List Card"),
        ("n", "new", "New Card"),
        ("e", "edit", "Edit Card"),
        ("D", "delete", "Delete Card"),
        ("space", "show_answer", "Show Answer"),
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
        with Container(classes="question"):
            yield Markdown(id="question")
            yield HorizontalScroll(id="images")
        yield Static(id="stats", classes="stats")
        yield Horizontal(Button("Yes", id="yes", variant="success"),
                         Button("No", id="no", variant="error"),
                         classes="action")
        yield Footer()

    async def on_mount(self) -> None:
        self.query_one("#yes").focus()
        await self.next_card()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "yes":
            db_api.card_master(self.card["id"])
            self.total_master += 1
        elif event.button.id == "no":
            self.query_one("#yes").focus()
            db_api.card_forget(self.card["id"])
            self.total_forget += 1
        await self.next_card()

    async def next_card(self) -> None:
        try:
            self.card = next(self.card_generator)
        except StopIteration:
            self.card = None
            return self.show_today_summary()

        self.query_one("#question").update(self.card["question"])
        self.query_one("#images").remove_children()
        imgs = []
        for s in self.card["question"].split("file://")[1:]:
            url = s.split(')')[0]
            img = Image(url)
            img.styles.width = math.ceil(img._image_width/25)
            imgs.append(img)
        self.query_one("#images").mount(*imgs)

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
        content = '\n\n{}\n'.format(SEPARATOR)
        self.app._driver.stop_application_mode()
        content = click.edit(content)
        self.app._driver.start_application_mode()
        if content is not None:
            question = content.split(SEPARATOR)[0]
            answer = SEPARATOR.join(content.split(SEPARATOR)[1:])
            db_api.card_new(self.deck_id, question, answer)

    async def action_edit(self) -> None:
        content = SEPARATOR.join([self.card["question"], self.card["answer"]])
        self.app._driver.stop_application_mode()
        content = click.edit(content)
        self.app._driver.start_application_mode()
        if content is not None:
            question = content.split(SEPARATOR)[0]
            answer = SEPARATOR.join(content.split(SEPARATOR)[1:])
            self.card["question"] = question
            self.card["answer"] = answer
            self.query_one("#question").update(question)
            db_api.card_update(self.card["id"], question, answer)

    async def action_delete(self) -> None:
        db_api.card_delete(self.card["id"])
        await self.next_card()

    @work
    async def action_show_answer(self) -> None:
        if self.card is None:
            self.app.pop_screen()
            return
        await self.app.push_screen_wait(AnswerScreen(self.card))
