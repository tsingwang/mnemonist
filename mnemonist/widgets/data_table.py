from textual.binding import Binding
from textual.widgets import DataTable as _DataTable


class DataTable(_DataTable):

    BINDINGS = [
        Binding("k", "cursor_up", "Cursor up", show=False),
        Binding("j", "cursor_down", "Cursor down", show=False),
        Binding("l", "cursor_right", "Cursor right", show=False),
        Binding("h", "cursor_left", "Cursor left", show=False),
        Binding("ctrl+b", "page_up", "Page up", show=False),
        Binding("ctrl+f", "page_down", "Page down", show=False),
        Binding("g", "scroll_top", "Top", show=False),
        Binding("G", "scroll_bottom", "Bottom", show=False),
        Binding("0", "scroll_home", "Home", show=False),
        Binding("$", "scroll_end", "End", show=False),
    ]

    # Column definition, one column is a dict:
    # "name": required, column display name
    # "key": option, use for sort by column
    # "width": option, column width
    COLUMNS = []

    def __init__(self) -> None:
        super().__init__(cursor_type="row")

    def on_mount(self) -> None:
        self.init_column()
        self.refresh_table()

    def init_column(self) -> None:
        """Init column only once when mount."""
        for col in self.COLUMNS:
            self.add_column(col.get("name", ""), key=col.get("key", None),
                            width=col.get("width", None))

    def render_table(self) -> None:
        raise NotImplementedError("Need provide a render_table() method.")

    def refresh_table(self) -> None:
        cursor_row = self.cursor_row
        self.clear()
        self.render_table()
        self.move_cursor(row=cursor_row)
