import math

import click
from textual import events
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, HorizontalScroll, VerticalScroll
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Header, Footer, Markdown, Button, Collapsible
from textual_image.widget import Image

from ..components import CardList
from ..const import CARD_MASTER, CARD_FORGET, CARD_DELETE, SEPARATOR
from ..db import api as db_api


class CardListScreen(Screen):

    BINDINGS = [
        ("escape", "app.pop_screen", "Pop screen"),
    ]

    def __init__(self, deck_id: int) -> None:
        super().__init__()
        self.deck_id = deck_id

    def compose(self) -> ComposeResult:
        yield Header()
        yield CardList(self.deck_id)
        yield Footer()

    def on_mount(self) -> None:
        self.query_one(CardList).focus()

    def on_screen_resume(self) -> None:
        self.query_one(CardList).refresh_table()


class CardScreen(Screen):

    BINDINGS = [
        ("escape", "app.pop_screen", "Pop screen"),
        ("e", "edit", "Edit Card"),
        ("D", "delete", "Delete Card"),
    ]

    is_horizontal = reactive(0, recompose=True)

    def __init__(self, card: dict) -> None:
        super().__init__()
        self.card = card

    def compose(self) -> ComposeResult:
        yield Header()
        display_class = Horizontal if self.is_horizontal else Vertical
        image_class = VerticalScroll if self.is_horizontal else HorizontalScroll
        with display_class():
            with Collapsible(collapsed=False, title="Question", classes="question"):
                yield Markdown(self.card["question"], id="question")
                with image_class():
                    for s in self.card["question"].split("file://")[1:]:
                        url = s.split(')')[0]
                        img = Image(url)
                        img.styles.width = math.ceil(img._image_width/25)
                        yield img

            with Collapsible(collapsed=False, title="Answer", classes="answer"):
                yield Markdown(self.card["answer"], id="answer")
                with image_class():
                    for s in self.card["answer"].split("file://")[1:]:
                        url = s.split(')')[0]
                        img = Image(url)
                        img.styles.width = math.ceil(img._image_width/25)
                        yield img
        yield Horizontal(Button("Yes", id="yes", variant="success"),
                         Button("No", id="no", variant="error"),
                         classes="action")
        yield Footer()

    async def on_mount(self) -> None:
        self.query_one("#yes").focus()

    async def on_key(self, event: events.Key) -> None:
        if event.key == "space":
            self.is_horizontal = 0 if self.is_horizontal else 1

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "yes":
            self.dismiss(CARD_MASTER)
        elif event.button.id == "no":
            self.query_one("#yes").focus()
            self.dismiss(CARD_FORGET)

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
            self.query_one("#answer").update(answer)
            db_api.card_update(self.card["id"], question, answer)

    async def action_delete(self) -> None:
        self.dismiss(CARD_DELETE)
