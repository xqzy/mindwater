import os
import sys

# Optional: ensure root directory is in pythonpath
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from textual.app import App, ComposeResult
from textual.widgets import Input, Static, Header, Footer
from textual.containers import Vertical
from src.services.parser import parse_capture_text
from src.database.firebase import add_to_inbox

class TUICaptureApp(App):
    """A Textual App for rapid capture into GTD Inbox."""
    
    CSS = """
    Screen {
        align: center middle;
    }
    Vertical {
        width: 80%;
        height: auto;
        padding: 1 2;
        border: solid green;
    }
    #feedback {
        margin-top: 1;
        color: yellow;
    }
    """
    
    BINDINGS = [
        ("escape", "app.quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        with Vertical():
            yield Static("Enter task/thought below (use #tag or @context):")
            yield Input(placeholder="e.g. Buy milk #grocery @shop", id="capture_input")
            yield Static("", id="feedback")
        yield Footer()

    def on_mount(self) -> None:
        """Called when app starts."""
        self.query_one(Input).focus()

    async def on_input_submitted(self, message: Input.Submitted) -> None:
        """Handle when the user hits Enter."""
        raw_text = message.value.strip()
        feedback = self.query_one("#feedback", Static)
        
        if not raw_text:
            feedback.update("[red]Please enter some text.[/red]")
            return
            
        try:
            # Show processing
            feedback.update("[yellow]Processing...[/yellow]")
            self.refresh()
            
            # Parse
            parsed_data = parse_capture_text(raw_text)
            
            # Save to Firebase
            doc_id = add_to_inbox(raw_text, parsed_data)
            
            # Update feedback
            feedback.update(f"[green]Successfully captured! ID: {doc_id}[/green]")
            
            # Clear input
            self.query_one(Input).value = ""
        except RuntimeError as e:
            feedback.update(f"[red]Firebase Error: {str(e)}[/red]")
        except Exception as e:
            feedback.update(f"[red]Error: {str(e)}[/red]")

if __name__ == "__main__":
    app = TUICaptureApp()
    app.run()
