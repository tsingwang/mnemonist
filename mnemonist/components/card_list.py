import click

from ..db import api as db_api
from ..widgets import DataTable


class CardList(DataTable):

    BINDINGS = [
        ("n", "new", "New Card"),
        ("e", "edit", "Edit Card"),
        ("D", "delete", "Delete Card"),
        ("enter", "show", "Show Card"),
    ]

    COLUMNS = [
        {"name": "ID",          "key": "id"},
        {"name": "Question",    "key": "question"},
        {"name": "Answer",      "key": "answer"},
        {"name": "Review",      "key": "review_count"},
        {"name": "Master",      "key": "master_count"},
        {"name": "Forget",      "key": "forget_count"},
        {"name": "Last seen",   "key": "updated_at"},
        {"name": "Schedule",    "key": "schedule_day"},
    ]

    def __init__(self, deck_id: int) -> None:
        super().__init__()
        self.deck_id = deck_id

    def render_table(self) -> None:
        for d in db_api.card_list(self.deck_id):
            row = [
                '{}'.format(d['id']),
                d['question'],
                d['answer'],
                '{}'.format(d['review_count']),
                '{}'.format(d['master_count']),
                '{}'.format(d['forget_count']),
                '{}'.format(d['updated_at'].strftime("%Y-%m-%d")),
                '{}'.format(d['schedule_day']),
            ]
            self.add_row(*row, key=d['id'])

    async def action_new(self) -> None:
        content = '\n\n---\n\n'
        self.app._driver.stop_application_mode()
        content = click.edit(content)
        self.app._driver.start_application_mode()
        if content is not None:
            question = content.split('---\n')[0]
            answer = '---\n'.join(content.split('---\n')[1:])
            db_api.card_new(self.deck_id, question, answer)
        self.refresh_table()

    async def action_edit(self) -> None:
        if not self.is_valid_row_index(self.cursor_row):
            return
        row = self.get_row_at(self.cursor_row)
        content = '---\n'.join([row[1], row[2]])
        self.app._driver.stop_application_mode()
        content = click.edit(content)
        self.app._driver.start_application_mode()
        if content is not None:
            question = content.split('---\n')[0]
            answer = '---\n'.join(content.split('---\n')[1:])
            db_api.card_update(int(row[0]), question, answer)
        self.refresh_table()

    async def action_delete(self) -> None:
        if not self.is_valid_row_index(self.cursor_row):
            return
        row = self.get_row_at(self.cursor_row)
        db_api.card_delete(int(row[0]))
        self.refresh_table()

    async def action_show(self) -> None:
        if not self.is_valid_row_index(self.cursor_row):
            return
        row = self.get_row_at(self.cursor_row)
        from ..views import CardScreen
        card = db_api.card_get(int(row[0]))
        self.app.push_screen(CardScreen(card))
