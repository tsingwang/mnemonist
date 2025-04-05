import click
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.screen import Screen
from textual.widgets import Header, Footer, Markdown, Button, Collapsible

from ..components import CardList
from ..db import api as db_api
from . import const


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
        self.query_one(CardList).render_table()


class CardScreen(Screen):

    BINDINGS = [
        ("escape", "app.pop_screen", "Pop screen"),
        ("e", "edit", "Edit Card"),
        ("D", "delete", "Delete Card"),
    ]

    def __init__(self, card: dict) -> None:
        super().__init__()
        self.card = card

    def compose(self) -> ComposeResult:
        yield Header()
        yield Collapsible(Markdown(self.card["question"], id="question"),
                          collapsed=False, title="Question", classes="question")
        yield Collapsible(Markdown(self.card["answer"], id="answer"),
                          collapsed=False, title="Answer", classes="answer")
        yield Horizontal(Button("Yes", id="yes", variant="success"),
                         Button("No", id="no", variant="error"),
                         classes="action")
        yield Footer()

    async def on_mount(self) -> None:
        self.query_one("#yes").focus()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "yes":
            self.dismiss(const.CARD_MASTER)
        elif event.button.id == "no":
            self.query_one("#yes").focus()
            self.dismiss(const.CARD_FORGET)

    async def action_edit(self) -> None:
        content = '---\n'.join([self.card["question"], self.card["answer"]])
        self.app._driver.stop_application_mode()
        content = click.edit(content)
        self.app._driver.start_application_mode()
        if content is not None:
            question = content.split('---\n')[0]
            answer = '---\n'.join(content.split('---\n')[1:])
            self.query_one("#question").update(question)
            self.query_one("#answer").update(answer)
            db_api.card_update(self.card["id"], question, answer)

    async def action_delete(self) -> None:
        self.dismiss(const.CARD_DELETE)
