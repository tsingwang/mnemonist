from ..db import api as db_api
from ..widgets import DataTable


class DeckList(DataTable):

    BINDINGS = [
        ("n", "app.push_screen('deck_new_screen')", "New Deck"),
        ("e", "edit", "Edit Deck"),
        ("D", "delete", "Delete Deck"),
        ("enter", "review", "Review"),
    ]

    COLUMNS = [
        {"name": "ID",              "key": "id"},
        {"name": "Deck Name",       "key": "name"},
        {"name": "Avg Accuracy",    "key": "accuracy"},
        {"name": "Total Cards",     "key": "total"},
        {"name": "Today",           "key": "today"},
    ]

    def render_table(self) -> None:
        for d in db_api.deck_list():
            row = [
                '{}'.format(d['id']),
                d['name'],
                '{:.2f}%'.format(d['accuracy']),
                '{}'.format(d['total']),
                '{}'.format(d['today']),
            ]
            self.add_row(*row, key=d['id'])

    async def action_edit(self) -> None:
        if not self.is_valid_row_index(self.cursor_row):
            return
        row = self.get_row_at(self.cursor_row)
        from ..views import DeckNewScreen
        self.app.push_screen(DeckNewScreen(int(row[0]), row[1]))

    async def action_delete(self) -> None:
        if not self.is_valid_row_index(self.cursor_row):
            return
        row = self.get_row_at(self.cursor_row)
        db_api.deck_delete(int(row[0]))
        self.refresh_table()

    async def action_review(self) -> None:
        if not self.is_valid_row_index(self.cursor_row):
            return
        row = self.get_row_at(self.cursor_row)
        from ..views import ReviewScreen
        self.app.push_screen(ReviewScreen(int(row[0])))
