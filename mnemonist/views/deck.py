from textual.app import ComposeResult
from textual.screen import Screen, ModalScreen
from textual.widgets import Header, Footer, Input

from ..components import DeckList
from ..db import api as db_api


class DeckListScreen(Screen):

    def compose(self) -> ComposeResult:
        yield Header()
        yield DeckList()
        yield Footer()

    def on_mount(self) -> None:
        self.query_one(DeckList).focus()

    def on_screen_resume(self) -> None:
        self.query_one(DeckList).render_table()


class DeckNewScreen(ModalScreen):

    BINDINGS = [("escape", "app.pop_screen", "Pop screen")]

    def __init__(self, deck_id: int = 0, deck_name: str = '') -> None:
        super().__init__()
        self.deck_id = deck_id
        self.deck_name = deck_name

    def compose(self) -> ComposeResult:
        yield Input(value=self.deck_name, placeholder="New deck name")

    async def on_mount(self) -> None:
        self.query_one(Input).focus()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        name = event.value.strip()
        if name != self.deck_name:
            if self.deck_id:
                db_api.deck_update(self.deck_id, name)
            else:
                db_api.deck_new(name)
        self.dismiss(True)
