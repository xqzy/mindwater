import os
import sys

# Optional: ensure root directory is in pythonpath
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Static
from src.database.firebase import get_inbox_items

class TUIInboxApp(App):
    """A Textual App to view GTD Inbox."""
    
    CSS = """
    Screen {
        layout: vertical;
    }
    DataTable {
        height: 1fr;
        margin: 1 2;
    }
    .status-msg {
        content-align: center middle;
        height: 1fr;
    }
    #loading {
        color: yellow;
    }
    #empty {
        color: green;
        display: none;
    }
    #error {
        color: red;
        display: none;
    }
    """
    
    BINDINGS = [
        ("escape", "app.quit", "Quit"),
        ("q", "app.quit", "Quit"),
        ("r", "refresh_data", "Refresh"),
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Static("Loading data from Firebase...", id="loading", classes="status-msg")
        yield Static("Inbox is empty.", id="empty", classes="status-msg")
        yield Static("Error loading data.", id="error", classes="status-msg")
        
        table = DataTable(id="inbox_table")
        table.display = False
        yield table
        
        yield Footer()

    async def on_mount(self) -> None:
        """Called when app starts."""
        table = self.query_one(DataTable)
        table.add_columns("Timestamp", "Task", "Tags", "Contexts")
        table.cursor_type = "row"
        table.zebra_stripes = True
        
        # Start data fetch
        self.call_after_refresh(self.action_refresh_data)

    async def action_refresh_data(self) -> None:
        """Fetch and populate data."""
        loading = self.query_one("#loading")
        empty = self.query_one("#empty")
        error = self.query_one("#error")
        table = self.query_one(DataTable)

        loading.display = True
        empty.display = False
        error.display = False
        table.display = False

        try:
            # Note: get_inbox_items makes a synchronous network request.
            # In a real async app we might run it in a worker thread,
            # but for this CLI it is acceptable.
            items = get_inbox_items()
            table.clear()
            
            if not items:
                loading.display = False
                empty.display = True
            else:
                for item in items:
                    ts = item.get("timestamp")
                    if hasattr(ts, 'strftime'):
                        ts_str = ts.strftime("%Y-%m-%d %H:%M")
                    else:
                        ts_str = str(ts)
                        
                    clean_text = item.get("clean_text", "")
                    tags = ", ".join(item.get("tags", []))
                    contexts = ", ".join(item.get("contexts", []))
                    
                    table.add_row(ts_str, clean_text, tags, contexts)
                
                loading.display = False
                table.display = True
                table.focus()
                
        except Exception as e:
            loading.display = False
            error.update(f"Error loading data: {e}")
            error.display = True


if __name__ == "__main__":
    app = TUIInboxApp()
    app.run()
