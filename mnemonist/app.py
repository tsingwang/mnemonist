from textual.app import App

from .profile import profile
from .views import DeckListScreen, DeckNewScreen


class MnemonistApp(App):

    TITLE = "Mnemonist ({})".format(profile.current_user)

    CSS_PATH = "mnemonist.tcss"

    SCREENS = {
        "deck_list_screen": DeckListScreen,
        "deck_new_screen": DeckNewScreen,
    }

    async def on_mount(self) -> None:
        self.push_screen("deck_list_screen")
