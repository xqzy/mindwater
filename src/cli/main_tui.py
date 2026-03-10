import os
import sys

# Ensure root directory is in pythonpath
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Input, DataTable, TabbedContent, TabPane, Select, Button, ContentSwitcher, Label
from textual.containers import Vertical, Center, Horizontal, VerticalScroll
from textual.screen import Screen
from textual import work, on
from src.services.parser import parse_capture_text
from src.database.firebase import add_to_inbox, get_inbox_items, delete_inbox_item
from src.services.todoist import push_task_to_todoist
from src.database.session import SessionLocal, init_db, APP_ENV
from src.database.models import Task
from src.database.crud import (
    get_all_roles, get_all_ambitions, create_task, get_all_tasks,
    update_task_status, create_h2, create_ambition, delete_role, delete_ambition,
    get_filtered_tasks, get_unique_contexts, record_review, get_last_review,
    get_role, get_ambition, update_role, update_ambition, get_ambitions_by_role,
    get_ambition_stats, get_tasks_by_ambition, update_task,
    get_ambitions_with_task_counts, get_roles_with_ambition_counts
)

class EditRoleScreen(Screen):
    """Screen to edit an existing Role."""
    CSS = """
    EditRoleScreen { align: center middle; }
    #dialog { width: 60%; height: auto; padding: 1 2; border: thick $primary; background: $surface; }
    .field-label { margin-top: 1; color: $accent; }
    #actions { margin-top: 1; align: right middle; }
    Button { margin-left: 1; }
    """
    def __init__(self, role_id: int):
        super().__init__()
        self.role_id = role_id

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Static("[bold]Edit Role (Area of Focus)[/bold]")
            yield Static("Name:", classes="field-label")
            yield Input(placeholder="Name", id="role_name")
            yield Static("Description:", classes="field-label")
            yield Input(placeholder="Description", id="role_desc")
            with Horizontal(id="actions"):
                yield Button("Cancel", variant="error", id="cancel_btn")
                yield Button("Save Changes", variant="success", id="save_btn")

    def on_mount(self) -> None:
        db = SessionLocal()
        role = get_role(db, self.role_id)
        db.close()
        if role:
            self.query_one("#role_name", Input).value = role.name
            self.query_one("#role_desc", Input).value = role.description or ""

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel_btn":
            self.app.pop_screen()
        elif event.button.id == "save_btn":
            name = self.query_one("#role_name", Input).value
            desc = self.query_one("#role_desc", Input).value
            if name:
                db = SessionLocal()
                update_role(db, self.role_id, name=name, description=desc)
                db.close()
                self.app.pop_screen()
                self.app.call_after_refresh(self.app.action_refresh_active_view)

class EditAmbitionScreen(Screen):
    """Screen to edit an existing Ambition."""
    CSS = """
    EditAmbitionScreen { align: center middle; }
    #dialog { width: 60%; height: auto; padding: 1 2; border: thick $primary; background: $surface; }
    .field-label { margin-top: 1; color: $accent; }
    #actions { margin-top: 1; align: right middle; }
    Button { margin-left: 1; }
    """
    def __init__(self, ambition_id: int):
        super().__init__()
        self.ambition_id = ambition_id

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Static("[bold]Edit Ambition (Project)[/bold]")
            yield Static("Success Outcome:", classes="field-label")
            yield Input(placeholder="Outcome", id="ambition_outcome")
            yield Static("Status:", classes="field-label")
            yield Select([("Active", "active"), ("Stalled", "stalled"), ("Done", "done")], id="status_select")
            with Horizontal(id="actions"):
                yield Button("Cancel", variant="error", id="cancel_btn")
                yield Button("Save Changes", variant="success", id="save_btn")

    def on_mount(self) -> None:
        db = SessionLocal()
        ambition = get_ambition(db, self.ambition_id)
        db.close()
        if ambition:
            self.query_one("#ambition_outcome", Input).value = ambition.outcome
            self.query_one("#status_select", Select).value = ambition.status

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel_btn":
            self.app.pop_screen()
        elif event.button.id == "save_btn":
            outcome = self.query_one("#ambition_outcome", Input).value
            status = self.query_one("#status_select", Select).value
            if outcome:
                db = SessionLocal()
                update_ambition(db, self.ambition_id, outcome=outcome, status=status)
                db.close()
                self.app.pop_screen()
                self.app.call_after_refresh(self.app.action_refresh_active_view)

class AmbitionStats(Static):
    """A widget to display statistics for an Ambition."""
    def __init__(self, **kwargs):
        super().__init__("Select an ambition to see statistics", **kwargs)

    def update_stats(self, stats: dict) -> None:
        if not stats:
            self.update("No statistics available")
            return

        content = (
            f"[bold]Project Statistics[/bold]\n"
            f"Total Hours Spent: [green]{stats['total_hours']}[/green]h\n"
            f"Tasks Finished (Total): {stats['total_finished']}\n"
            f"Tasks Finished (Last 2 weeks): [cyan]{stats['finished_2w']}[/cyan]\n"
            f"Tasks Finished (Last 6 weeks): [cyan]{stats['finished_6w']}[/cyan]"
        )
        self.update(content)

class AddRoleScreen(Screen):

    """Screen to add a new Role."""
    CSS = """
    AddRoleScreen { align: center middle; }
    #dialog { width: 60%; height: auto; padding: 1 2; border: thick $primary; background: $surface; }
    .field-label { margin-top: 1; color: $accent; }
    #actions { margin-top: 1; align: right middle; }
    Button { margin-left: 1; }
    """
    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Static("[bold]Add New Role (Area of Focus)[/bold]")
            yield Static("Name:", classes="field-label")
            yield Input(placeholder="e.g. Health, Career, Family", id="role_name")
            yield Static("Description:", classes="field-label")
            yield Input(placeholder="Optional description", id="role_desc")
            with Horizontal(id="actions"):
                yield Button("Cancel", variant="error", id="cancel_btn")
                yield Button("Add Role", variant="success", id="add_btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel_btn":
            self.app.pop_screen()
        elif event.button.id == "add_btn":
            name = self.query_one("#role_name", Input).value
            desc = self.query_one("#role_desc", Input).value
            if name:
                db = SessionLocal()
                create_h2(db, name=name, description=desc)
                db.close()
                self.app.pop_screen()
                self.app.call_after_refresh(self.app.action_refresh_active_view)

class AddTaskScreen(Screen):
    """Screen to add a new Task directly."""
    CSS = """
    AddTaskScreen { align: center middle; }
    #dialog { width: 70%; height: auto; padding: 1 2; border: thick $primary; background: $surface; }
    .field-label { margin-top: 1; color: $accent; }
    #actions { margin-top: 1; align: right middle; }
    Button { margin-left: 1; }
    """
    
    def __init__(self, initial_role_id: str = None, initial_ambition_id: str = None, on_success: callable = None):
        super().__init__()
        self.initial_role_id = initial_role_id
        self.initial_ambition_id = initial_ambition_id
        self.on_success = on_success

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Static("[bold]Add New Task[/bold]")
            yield Static("Title:", classes="field-label")
            yield Input(placeholder="What needs to be done?", id="task_title")
            
            yield Static("Role:", classes="field-label")
            yield Select([], id="role_select", prompt="Select a Role")
            
            yield Static("Ambition (Optional):", classes="field-label")
            yield Select([], id="ambition_select", prompt="Select an Ambition")
            
            yield Static("Energy Level:", classes="field-label")
            yield Select([("Low", "Low"), ("Medium", "Medium"), ("High", "High")], value="Medium", id="energy_select")
            
            with Horizontal(id="actions"):
                yield Button("Cancel", variant="error", id="cancel_btn")
                yield Button("Add Task", variant="success", id="add_btn")

    def on_mount(self) -> None:
        self.load_options()

    @work(thread=True)
    def load_options(self) -> None:
        db = SessionLocal()
        try:
            roles = get_all_roles(db)
            ambitions = get_all_ambitions(db)
            role_options = [(r.name, str(r.id)) for r in roles]
            ambition_options = [(a.outcome, str(a.id)) for a in ambitions]
            self.app.call_from_thread(self._update_selects, role_options, ambition_options)
        finally:
            db.close()

    def _update_selects(self, role_options, ambition_options) -> None:
        rs = self.query_one("#role_select", Select)
        rs.set_options(role_options)
        if self.initial_role_id:
            rs.value = self.initial_role_id
            
        as_ = self.query_one("#ambition_select", Select)
        as_.set_options(ambition_options)
        if self.initial_ambition_id:
            as_.value = self.initial_ambition_id

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel_btn":
            self.app.pop_screen()
        elif event.button.id == "add_btn":
            self.save_task()

    @work(thread=True)
    def save_task(self) -> None:
        title = self.query_one("#task_title", Input).value
        role_id = self.query_one("#role_select", Select).value
        ambition_id = self.query_one("#ambition_select", Select).value
        energy = self.query_one("#energy_select", Select).value
        
        r_id = int(role_id) if isinstance(role_id, str) else None
        a_id = int(ambition_id) if isinstance(ambition_id, str) else None
        
        if title:
            db = SessionLocal()
            try:
                create_task(db, title=title, role_id=r_id, ambition_id=a_id, energy_level=energy)
                if self.on_success:
                    self.on_success()
                self.app.call_from_thread(self.app.pop_screen)
                self.app.call_after_refresh(self.app.action_refresh_active_view)
            finally:
                db.close()

class AddAmbitionScreen(Screen):
    """Screen to add a new Ambition (Project)."""
    CSS = """
    AddAmbitionScreen { align: center middle; }
    #dialog { width: 60%; height: auto; padding: 1 2; border: thick $primary; background: $surface; }
    .field-label { margin-top: 1; color: $accent; }
    #actions { margin-top: 1; align: right middle; }
    Button { margin-left: 1; }
    """

    def __init__(self, initial_role_id: str = None, on_success: callable = None):
        super().__init__()
        self.initial_role_id = initial_role_id
        self.on_success = on_success

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Static("[bold]Add New Ambition (Project)[/bold]")
            yield Static("Success Outcome:", classes="field-label")
            yield Input(placeholder="e.g. Complete marathon, Launch website", id="ambition_outcome")
            yield Static("Link to Role:", classes="field-label")
            yield Select([], id="role_select", prompt="Select a Role")
            with Horizontal(id="actions"):
                yield Button("Cancel", variant="error", id="cancel_btn")
                yield Button("Add Ambition", variant="success", id="add_btn")

    def on_mount(self) -> None:
        db = SessionLocal()
        roles = get_all_roles(db)
        db.close()
        role_options = [(r.name, str(r.id)) for r in roles]
        rs = self.query_one("#role_select", Select)
        rs.set_options(role_options)
        if self.initial_role_id:
            rs.value = self.initial_role_id

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel_btn":
            self.app.pop_screen()
        elif event.button.id == "add_btn":
            outcome = self.query_one("#ambition_outcome", Input).value
            role_id = self.query_one("#role_select", Select).value
            if outcome:
                r_id = int(role_id) if isinstance(role_id, str) else None
                db = SessionLocal()
                try:
                    create_ambition(db, outcome=outcome, h2_id=r_id)
                    if self.on_success:
                        self.on_success()
                    self.app.pop_screen()
                    self.app.call_after_refresh(self.app.action_refresh_active_view)
                finally:
                    db.close()

class InboxClarifyScreen(Screen):
    """A screen for clarifying an inbox item."""
    
    CSS = """
    InboxClarifyScreen {
        align: center middle;
    }
    #dialog {
        width: 80%;
        height: auto;
        padding: 1 2;
        border: thick $primary;
        background: $surface;
    }
    .field-label {
        margin-top: 1;
        color: $accent;
    }
    #actions {
        margin-top: 1;
        align: right middle;
    }
    Button {
        margin-left: 1;
    }
    """

    def __init__(self, item_data: dict):
        super().__init__()
        self.item_data = item_data
        self.roles = []
        self.ambitions = []

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Static(f"[bold]Clarify:[/bold] {self.item_data.get('raw_text')}")
            
            yield Static("Task Title:", classes="field-label")
            yield Input(value=self.item_data.get('clean_text', ''), id="task_title")
            
            yield Static("Role:", classes="field-label")
            yield Select([], id="role_select", prompt="Select a Role")
            
            yield Static("Ambition (Optional):", classes="field-label")
            yield Select([], id="ambition_select", prompt="Select an Ambition")
            
            yield Static("Energy Level:", classes="field-label")
            yield Select([("Low", "Low"), ("Medium", "Medium"), ("High", "High")], value="Medium", id="energy_select")
            
            with Horizontal(id="actions"):
                yield Button("Cancel", variant="error", id="cancel_btn")
                yield Button("Save & Clarify", variant="success", id="save_btn")

    def on_mount(self) -> None:
        self.load_db_options()

    @work(thread=True)
    def load_db_options(self) -> None:
        db = SessionLocal()
        try:
            roles = get_all_roles(db)
            ambitions = get_all_ambitions(db)
            
            role_options = [(r.name, str(r.id)) for r in roles]
            ambition_options = [(a.outcome, str(a.id)) for a in ambitions]
            
            self.app.call_from_thread(self._update_selects, role_options, ambition_options)
        finally:
            db.close()

    def _update_selects(self, role_options, ambition_options) -> None:
        self.query_one("#role_select", Select).set_options(role_options)
        self.query_one("#ambition_select", Select).set_options(ambition_options)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel_btn":
            self.app.pop_screen()
        elif event.button.id == "save_btn":
            self.save_and_clarify()

    @work(thread=True)
    def save_and_clarify(self) -> None:
        title = self.query_one("#task_title", Input).value
        role_id = self.query_one("#role_select", Select).value
        ambition_id = self.query_one("#ambition_select", Select).value
        energy = self.query_one("#energy_select", Select).value
        
        # Convert IDs back to int. Select values are strings or sentinel objects like Select.BLANK
        r_id = int(role_id) if isinstance(role_id, str) else None
        a_id = int(ambition_id) if isinstance(ambition_id, str) else None
        
        if not title:
            return 

        db = SessionLocal()
        try:
            # 1. Save to SQLite
            create_task(db, title=title, role_id=r_id, ambition_id=a_id, energy_level=energy, context_tags=self.item_data.get('contexts', []))
            
            # 2. Delete from Firebase
            delete_inbox_item(self.item_data['id'])
            
            # 3. Success
            self.app.call_from_thread(self.finish_clarify)
        except Exception as e:
            pass
        finally:
            db.close()

    def finish_clarify(self) -> None:
        self.app.pop_screen()
        # Trigger refresh in the main app
        if hasattr(self.app, 'action_refresh_active_view'):
            self.app.action_refresh_active_view()

class CaptureView(Static):
    """A view for rapid capture into GTD Inbox."""
    
    def compose(self) -> ComposeResult:
        with Vertical(id="capture_container"):
            yield Center(Static("Enter task/thought below (use #tag or @context):", id="prompt"))
            yield Input(placeholder="e.g. Buy milk #grocery @shop", id="capture_input")
            yield Center(Static("", id="feedback"))

    async def on_input_submitted(self, message: Input.Submitted) -> None:
        """Handle when the user hits Enter."""
        raw_text = message.value.strip()
        feedback = self.query_one("#feedback", Static)
        
        if not raw_text:
            feedback.update("[red]Please enter some text.[/red]")
            return
            
        try:
            feedback.update("[yellow]Processing...[/yellow]")
            parsed_data = parse_capture_text(raw_text)
            doc_id = add_to_inbox(raw_text, parsed_data)
            feedback.update(f"[green]Successfully captured! ID: {doc_id}[/green]")
            self.query_one(Input).value = ""
        except Exception as e:
            feedback.update(f"[red]Error: {str(e)}[/red]")

class InboxListView(Static):
    """A view to display GTD Inbox items."""
    BINDINGS = [("d", "delete_selected", "Delete Item")]

    def compose(self) -> ComposeResult:
        yield Static("Loading data from Firebase...", id="loading", classes="status-msg")
        yield Static("Inbox is empty.", id="empty", classes="status-msg")
        yield Static("Error loading data.", id="error", classes="status-msg")
        
        table = DataTable(id="inbox_table")
        table.display = False
        yield table

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("Timestamp", "Task", "Tags", "Contexts")
        table.cursor_type = "row"
        table.zebra_stripes = True
        self.action_refresh_data()

    @work(exclusive=True, thread=True)
    def action_refresh_data(self) -> None:
        """Fetch and populate data."""
        self.app.call_from_thread(self._set_status, "loading")

        try:
            items = get_inbox_items()
            self.app.call_from_thread(self._populate_table, items)
        except Exception as e:
            self.app.call_from_thread(self._set_status, "error", str(e))

    def _set_status(self, status: str, error_msg: str = "") -> None:
        loading = self.query_one("#loading")
        empty = self.query_one("#empty")
        error = self.query_one("#error")
        table = self.query_one(DataTable)

        loading.display = (status == "loading")
        empty.display = (status == "empty")
        error.display = (status == "error")
        table.display = (status == "success")

        if status == "error" and error_msg:
            error.update(f"Error loading data: {error_msg}")

    def _populate_table(self, items: list) -> None:
        table = self.query_one(DataTable)
        table.clear()
        
        if not items:
            self._set_status("empty")
        else:
            self.item_map = {item['id']: item for item in items}
            for item in items:
                ts = item.get("timestamp")
                ts_str = ts.strftime("%Y-%m-%d %H:%M") if hasattr(ts, 'strftime') else str(ts)
                clean_text = item.get("clean_text", "")
                tags = ", ".join(item.get("tags", []))
                contexts = ", ".join(item.get("contexts", []))
                # Use item ID as row key
                table.add_row(ts_str, clean_text, tags, contexts, key=item['id'])
            
            self._set_status("success")
            table.focus()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle item selection to clarify."""
        item_id = event.row_key.value
        item_data = self.item_map.get(item_id)
        if item_data:
            self.app.push_screen(InboxClarifyScreen(item_data))

    def action_delete_selected(self) -> None:
        """Delete the currently selected inbox item."""
        table = self.query_one(DataTable)
        if table.cursor_row is not None:
            # coordinate_to_cell_key gives us the row key for the cursor row
            try:
                row_key = table.coordinate_to_cell_key(table.cursor_coordinate).row_key
                item_id = row_key.value
                
                # Delete from Firebase
                self.delete_item_task(item_id, row_key)
            except Exception:
                pass

    @work(thread=True)
    def delete_item_task(self, item_id: str, row_key) -> None:
        try:
            delete_inbox_item(item_id)
            self.app.call_from_thread(self._remove_row_ui, row_key)
        except Exception as e:
            self.app.notify(f"Failed to delete: {e}", severity="error")

    def _remove_row_ui(self, row_key) -> None:
        table = self.query_one(DataTable)
        table.remove_row(row_key)
        if table.row_count == 0:
            self._set_status("empty")

class TaskEditScreen(Screen):
    """Screen to edit task details."""
    CSS = """
    TaskEditScreen { align: center middle; }
    #dialog { width: 80%; max-height: 90%; border: thick $primary; background: $surface; padding: 0; }
    #form_container { padding: 1 2; height: 1fr; }
    .field-label { margin-top: 1; color: $accent; }
    #actions { padding: 1 2; background: $boost; border-top: solid $primary; align: right middle; height: auto; }
    Button { margin-left: 1; }
    .row { height: auto; }
    .row Vertical { width: 1fr; }
    #edit_header { background: $primary; color: $text; padding: 0 1; }
    """

    def __init__(self, task_data: dict):
        super().__init__()
        self.task_id = task_data['id']
        self.initial_data = task_data

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Static(f" [bold]Edit Task (ID: {self.task_id})[/bold]", id="edit_header")
            
            with VerticalScroll(id="form_container"):
                yield Static("Title:", classes="field-label")
                yield Input(value=self.initial_data.get('title', ''), id="task_title")
                
                with Horizontal(classes="row"):
                    with Vertical():
                        yield Static("Status:", classes="field-label")
                        yield Select([("Todo", "todo"), ("In Progress", "in_progress"), ("Done", "done")], 
                                   value=self.initial_data.get('status', 'todo'), id="status_select")
                    with Vertical():
                        yield Static("Energy Level:", classes="field-label")
                        yield Select([("Low", "Low"), ("Medium", "Medium"), ("High", "High")], 
                                   value=self.initial_data.get('energy', 'Medium'), id="energy_select")

                with Horizontal(classes="row"):
                    with Vertical():
                        yield Static("Role:", classes="field-label")
                        yield Select([], id="role_select", prompt="Select a Role")
                    with Vertical():
                        yield Static("Ambition (Optional):", classes="field-label")
                        yield Select([], id="ambition_select", prompt="Select an Ambition")

                yield Static("Context Tags (comma separated):", classes="field-label")
                yield Input(value=self.initial_data.get('context', ''), id="context_input")

                with Horizontal(classes="row"):
                    with Vertical():
                        yield Static("Planned Date (YYYY-MM-DD):", classes="field-label")
                        pd = self.initial_data.get('planned_date')
                        pd_str = pd.strftime('%Y-%m-%d') if pd and hasattr(pd, 'strftime') else (pd if isinstance(pd, str) else "")
                        yield Input(value=pd_str, placeholder="YYYY-MM-DD", id="planned_date_input")
                    with Vertical():
                        yield Static("Estimated Time (minutes):", classes="field-label")
                        yield Input(value=str(self.initial_data.get('estimated_time', 0)), placeholder="e.g. 30", id="est_time_input")
            
            with Horizontal(id="actions"):
                yield Button("Cancel", variant="error", id="cancel_btn")
                yield Button("Save Changes", variant="success", id="save_btn")

    def on_mount(self) -> None:
        self.load_db_options()

    @work(thread=True)
    def load_db_options(self) -> None:
        db = SessionLocal()
        try:
            roles = get_all_roles(db)
            ambitions = get_all_ambitions(db)
            
            role_options = [(r.name, str(r.id)) for r in roles]
            ambition_options = [(a.outcome, str(a.id)) for a in ambitions]
            
            self.app.call_from_thread(self._update_selects, role_options, ambition_options)
        finally:
            db.close()

    def _update_selects(self, role_options, ambition_options) -> None:
        rs = self.query_one("#role_select", Select)
        rs.set_options(role_options)
        if self.initial_data.get('role_id'):
            rs.value = str(self.initial_data['role_id'])
            
        as_ = self.query_one("#ambition_select", Select)
        as_.set_options(ambition_options)
        if self.initial_data.get('ambition_id'):
            as_.value = str(self.initial_data['ambition_id'])

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel_btn":
            self.app.pop_screen()
        elif event.button.id == "save_btn":
            self.save_task()

    @work(thread=True)
    def save_task(self) -> None:
        from datetime import datetime
        
        title = self.query_one("#task_title", Input).value
        status = self.query_one("#status_select", Select).value
        energy = self.query_one("#energy_select", Select).value
        role_id = self.query_one("#role_select", Select).value
        ambition_id = self.query_one("#ambition_select", Select).value
        contexts_raw = self.query_one("#context_input", Input).value
        pd_str = self.query_one("#planned_date_input", Input).value
        est_str = self.query_one("#est_time_input", Input).value
        
        r_id = int(role_id) if isinstance(role_id, str) else None
        a_id = int(ambition_id) if isinstance(ambition_id, str) else None
        contexts = [c.strip() for c in contexts_raw.split(",") if c.strip()]
        
        planned_date = None
        if pd_str:
            try:
                planned_date = datetime.strptime(pd_str, '%Y-%m-%d')
            except ValueError:
                pass # Invalid date, keep as None or handle error

        try:
            estimated_time = int(est_str)
        except ValueError:
            estimated_time = 0

        db = SessionLocal()
        try:
            update_task(db, self.task_id, 
                       title=title, 
                       status=status, 
                       energy_level=energy, 
                       role_id=r_id, 
                       ambition_id=a_id,
                       context_tags=contexts,
                       planned_date=planned_date,
                       estimated_time=estimated_time)
            self.app.call_from_thread(self.finish_edit)
        finally:
            db.close()

    def finish_edit(self) -> None:
        self.app.pop_screen()
        if hasattr(self.app, 'action_refresh_active_view'):
            self.app.action_refresh_active_view()

from dotenv import load_dotenv
load_dotenv()

class TasksView(Static):
    """A view to display and manage structured GTD tasks."""
    BINDINGS = [
        ("e", "edit_task", "Edit Task"),
        ("p", "push_to_todoist", "Push to Todoist")
    ]
    
    CSS = """
    #filter_bar {
        height: auto;
        padding: 0 1;
        background: $surface;
        border-bottom: solid $primary;
    }
    #filter_bar Select {
        width: 20%;
        margin-right: 1;
    }
    #filter_bar Button {
        margin-left: 1;
    }
    #tasks_table {
        margin-top: 0;
    }
    .status-msg {
        display: none;
    }
    """

    def compose(self) -> ComposeResult:
        with Horizontal(id="filter_bar"):
            yield Select([], id="filter_role", prompt="Filter Role")
            yield Select([], id="filter_context", prompt="Filter Context")
            yield Select([("Low", "Low"), ("Medium", "Medium"), ("High", "High")], id="filter_energy", prompt="Filter Energy")
            yield Button("Clear", variant="default", id="clear_filters_btn")

        yield Static("Loading tasks from local database...", id="loading_tasks", classes="status-msg")
        yield Static("No tasks found matching filters.", id="empty_tasks", classes="status-msg")
        yield Static("Error loading tasks.", id="error_tasks", classes="status-msg")
        
        table = DataTable(id="tasks_table")
        table.display = False
        yield table

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("Status", "Title", "Due", "Role", "Ambition", "Context", "Energy", "Est")
        table.cursor_type = "row"
        table.zebra_stripes = True
        self.load_filter_options()

    @work(thread=True)
    def load_filter_options(self) -> None:
        db = SessionLocal()
        try:
            roles = get_all_roles(db)
            contexts = get_unique_contexts(db)
            role_options = [(r.name, str(r.id)) for r in roles]
            context_options = [(c, c) for c in contexts]
            self.app.call_from_thread(self._update_filter_widgets, role_options, context_options)
        except Exception as e:
            self.app.notify(f"Error loading filters: {e}", severity="error")
        finally:
            db.close()

    def _update_filter_widgets(self, role_options, context_options) -> None:
        self.query_one("#filter_role", Select).set_options(role_options)
        self.query_one("#filter_context", Select).set_options(context_options)

    @work(exclusive=True, thread=True)
    def action_refresh_data(self) -> None:
        """Fetch tasks from SQLite with current filters."""
        self.app.call_from_thread(self._set_status, "loading")
        
        try:
            # Capture current filter values from UI thread if possible, or handle missing widgets
            try:
                role_val = self.query_one("#filter_role", Select).value
                context_val = self.query_one("#filter_context", Select).value
                energy_val = self.query_one("#filter_energy", Select).value
                
                r_id = int(role_val) if isinstance(role_val, str) else None
                c_tag = context_val if isinstance(context_val, str) else None
                e_lvl = energy_val if isinstance(energy_val, str) else None
            except Exception as e:
                # If widgets aren't ready yet, use default values
                r_id = c_tag = e_lvl = None

            db = SessionLocal()
            try:
                tasks = get_filtered_tasks(db, role_id=r_id, context_tag=c_tag, energy_level=e_lvl)
                task_list = []
                for t in tasks:
                    task_list.append({
                        "id": t.id,
                        "status": t.status,
                        "title": t.title,
                        "role": t.role.name if t.role else "",
                        "role_id": t.role_id,
                        "ambition": t.ambition.outcome if t.ambition else "",
                        "ambition_id": t.ambition_id,
                        "context": ", ".join(t.context_tags) if t.context_tags else "",
                        "energy": t.energy_level,
                        "planned_date": t.planned_date,
                        "estimated_time": t.estimated_time
                    })
                self.app.call_from_thread(self._populate_table, task_list)
            except Exception as e:
                self.app.call_from_thread(self._set_status, "error", str(e))
            finally:
                db.close()
        except Exception as e:
            self.app.call_from_thread(self._set_status, "error", str(e))

    def _set_status(self, status: str, error_msg: str = "") -> None:
        loading = self.query_one("#loading_tasks")
        empty = self.query_one("#empty_tasks")
        error = self.query_one("#error_tasks")
        table = self.query_one(DataTable)

        loading.display = (status == "loading")
        empty.display = (status == "empty")
        error.display = (status == "error")
        table.display = (status == "success")
        
        if status == "error" and error_msg:
            error.update(f"Error loading tasks: {error_msg}")


    def _populate_table(self, tasks: list) -> None:
        table = self.query_one(DataTable)
        table.clear()
        
        if not tasks:
            self._set_status("empty")
        else:
            self.task_map = {str(t['id']): t for t in tasks}
            for t in tasks:
                status_icon = "✅" if t['status'] == "done" else "⭕"
                
                # Format due date
                pd = t.get('planned_date')
                pd_str = pd.strftime('%m-%d') if pd and hasattr(pd, 'strftime') else (pd if isinstance(pd, str) else "")
                
                # Truncate role and ambition
                role_short = (t['role'][:8] + "..") if len(t['role']) > 8 else t['role']
                ambition_short = (t['ambition'][:8] + "..") if len(t['ambition']) > 8 else t['ambition']
                
                table.add_row(
                    status_icon,
                    t['title'],
                    pd_str,
                    role_short,
                    ambition_short,
                    t['context'],
                    t['energy'],
                    str(t.get('estimated_time', '')),
                    key=str(t['id'])
                )
            self._set_status("success")
            table.focus()

    @on(Select.Changed)
    def handle_filter_change(self) -> None:
        self.action_refresh_data()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "clear_filters_btn":
            self.query_one("#filter_role", Select).value = Select.BLANK
            self.query_one("#filter_context", Select).value = Select.BLANK
            self.query_one("#filter_energy", Select).value = Select.BLANK
            self.action_refresh_data()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Toggle task completion."""
        task_id = int(event.row_key.value)
        self.toggle_task(task_id)

    def action_edit_task(self) -> None:
        """Open edit screen for the selected task."""
        table = self.query_one(DataTable)
        if table.cursor_row is not None:
            row_key = table.coordinate_to_cell_key(table.cursor_coordinate).row_key.value
            task_data = self.task_map.get(row_key)
            if task_data:
                self.app.push_screen(TaskEditScreen(task_data))

    def action_push_to_todoist(self) -> None:
        """Push the selected task to Todoist."""
        table = self.query_one(DataTable)
        if table.cursor_row is not None:
            try:
                row_key = table.coordinate_to_cell_key(table.cursor_coordinate).row_key.value
                task_data = self.task_map.get(row_key)
                if task_data:
                    self.push_to_todoist_task(task_data)
            except Exception:
                pass

    @work(thread=True)
    def push_to_todoist_task(self, task_data: dict) -> None:
        try:
            task_id = push_task_to_todoist(
                title=task_data['title'],
                due_date=task_data.get('planned_date')
            )
            self.app.call_from_thread(self.app.notify, f"Pushed to Todoist! ID: {task_id}")
        except Exception as e:
            self.app.call_from_thread(self.app.notify, f"Todoist push failed: {e}", severity="error")

    @work(thread=True)
    def toggle_task(self, task_id: int) -> None:
        db = SessionLocal()
        try:
            from src.database.models import Task
            task = db.query(Task).filter(Task.id == task_id).first()
            if task:
                new_status = "done" if task.status != "done" else "todo"
                update_task_status(db, task_id, new_status)
                self.action_refresh_data()
        finally:
            db.close()

class HorizonsView(Static):
    """A view to manage Roles and Ambitions with hierarchical filtering and stats."""
    BINDINGS = [
        ("d", "delete_selected", "Delete Selected"),
        ("e", "edit_selected", "Edit Selected"),
    ]
    CSS = """
    HorizonsView { layout: vertical; }
    .section-header { background: $primary; color: $text; padding: 0 1; margin-top: 1; }
    DataTable { height: 1fr; margin: 0 1; }
    #horizons_actions { padding: 1; align: right middle; height: auto; }
    .tasks-stats-row { height: 1fr; }
    #tasks_section { width: 60%; }
    #stats_section { width: 40%; }
    #ambition_stats { 
        padding: 1; 
        margin: 0 1; 
        border: solid $accent; 
        height: 1fr; 
        background: $surface; 
    }
    """
    def compose(self) -> ComposeResult:
        yield Static("Roles (Areas of Focus)", classes="section-header")
        yield DataTable(id="roles_table")
        yield Static("Ambitions (Projects)", classes="section-header")
        yield DataTable(id="ambitions_table")
        
        with Horizontal(classes="tasks-stats-row"):
            with Vertical(id="tasks_section"):
                yield Static("Tasks for Selected Project", classes="section-header")
                yield DataTable(id="ambition_tasks_table")
            with Vertical(id="stats_section"):
                yield Static("Project Statistics", classes="section-header")
                yield AmbitionStats(id="ambition_stats")

        with Horizontal(id="horizons_actions"):
            yield Button("Add Role", variant="primary", id="add_role_btn")
            yield Button("Add Ambition", variant="primary", id="add_ambition_btn")

    def on_mount(self) -> None:
        rt = self.query_one("#roles_table", DataTable)
        rt.add_columns("ID", "Name", "Description")
        rt.zebra_stripes = True
        rt.cursor_type = "row"
        
        at = self.query_one("#ambitions_table", DataTable)
        at.add_columns("ID", "Outcome", "Role", "Status")
        at.zebra_stripes = True
        at.cursor_type = "row"

        tt = self.query_one("#ambition_tasks_table", DataTable)
        tt.add_columns("Status", "Title", "Due", "Spent", "Energy")
        tt.zebra_stripes = True
        tt.cursor_type = "row"
        
        self.selected_role_id = None
        self.selected_ambition_id = None
        
        self.action_refresh_data()

    @work(thread=True)
    def action_refresh_data(self) -> None:
        db = SessionLocal()
        try:
            roles = get_all_roles(db)
            # If a role is selected, only show ambitions for that role
            if self.selected_role_id:
                ambitions = get_ambitions_by_role(db, self.selected_role_id)
            else:
                ambitions = get_all_ambitions(db)
                
            role_list = [{"id": r.id, "name": r.name, "desc": r.description} for r in roles]
            ambition_list = [{"id": a.id, "outcome": a.outcome, "role": a.role.name if a.role else "", "status": a.status} for a in ambitions]
            
            self.app.call_from_thread(self._populate_tables, role_list, ambition_list)
            
            if self.selected_ambition_id:
                self.load_ambition_tasks(self.selected_ambition_id)
        except Exception:
            pass
        finally:
            db.close()

    def _populate_tables(self, roles, ambitions) -> None:
        rt = self.query_one("#roles_table", DataTable)
        at = self.query_one("#ambitions_table", DataTable)
        rt.clear(); at.clear()
        for r in roles: rt.add_row(str(r['id']), r['name'], r['desc'], key=str(r['id']))
        for a in ambitions: at.add_row(str(a['id']), a['outcome'], a['role'], a['status'], key=str(a['id']))
        
        # Restore selection focus if possible
        if self.selected_role_id:
             try: rt.move_cursor(row=rt.get_row_index(str(self.selected_role_id)))
             except: pass
        if self.selected_ambition_id:
             try: at.move_cursor(row=at.get_row_index(str(self.selected_ambition_id)))
             except: pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "add_role_btn":
            self.app.push_screen(AddRoleScreen())
        elif event.button.id == "add_ambition_btn":
            self.app.push_screen(AddAmbitionScreen(initial_role_id=str(self.selected_role_id) if self.selected_role_id else None))

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        if event.data_table.id == "roles_table":
            try:
                self.selected_role_id = int(event.row_key.value)
                self.selected_ambition_id = None # Clear ambition selection when role changes
                self.query_one("#ambition_tasks_table", DataTable).clear()
                self.query_one("#ambition_stats", AmbitionStats).update("Select an ambition to see statistics")
                self.action_refresh_data()
            except (ValueError, TypeError):
                pass
        elif event.data_table.id == "ambitions_table":
            try:
                self.selected_ambition_id = int(event.row_key.value)
                self.load_ambition_tasks(self.selected_ambition_id)
            except (ValueError, TypeError):
                pass

    @work(thread=True)
    def load_ambition_tasks(self, ambition_id: int) -> None:
        db = SessionLocal()
        try:
            tasks = get_tasks_by_ambition(db, ambition_id)
            task_list = []
            for t in tasks:
                task_list.append({
                    "status": t.status,
                    "title": t.title,
                    "planned_date": t.planned_date,
                    "actual_time": t.actual_time,
                    "estimated_time": t.estimated_time,
                    "energy": t.energy_level
                })
            
            stats = get_ambition_stats(db, ambition_id)
            
            self.app.call_from_thread(self._populate_tasks_table, task_list, stats)
        finally:
            db.close()

    def _populate_tasks_table(self, tasks: list, stats: dict) -> None:
        tt = self.query_one("#ambition_tasks_table", DataTable)
        tt.clear()
        for t in tasks:
            status_icon = "✅" if t['status'] == "done" else "⭕"
            
            pd = t.get('planned_date')
            pd_str = pd.strftime('%m-%d') if pd and hasattr(pd, 'strftime') else (pd if isinstance(pd, str) else "")
            
            spent = t.get('actual_time', 0)
            if spent == 0:
                spent = t.get('estimated_time', 0)
            spent_str = f"{spent}m" if spent > 0 else ""
            
            tt.add_row(status_icon, t['title'], pd_str, spent_str, t['energy'])
            
        self.query_one("#ambition_stats", AmbitionStats).update_stats(stats)

    def action_edit_selected(self) -> None:
        """Edit the selected Role or Ambition."""
        if self.query_one("#roles_table").has_focus:
            table = self.query_one("#roles_table")
            if table.cursor_row is not None:
                try:
                    row_key = table.coordinate_to_cell_key(table.cursor_coordinate).row_key
                    self.app.push_screen(EditRoleScreen(int(row_key.value)))
                except Exception:
                    pass
        elif self.query_one("#ambitions_table").has_focus:
            table = self.query_one("#ambitions_table")
            if table.cursor_row is not None:
                try:
                    row_key = table.coordinate_to_cell_key(table.cursor_coordinate).row_key
                    self.app.push_screen(EditAmbitionScreen(int(row_key.value)))
                except Exception:
                    pass

    def action_delete_selected(self) -> None:
        """Delete the selected Role or Ambition."""
        if self.query_one("#roles_table").has_focus:
            table = self.query_one("#roles_table")
            if table.cursor_row is not None:
                try:
                    row_key = table.coordinate_to_cell_key(table.cursor_coordinate).row_key
                    self.delete_entity("role", row_key)
                except Exception:
                    pass
        elif self.query_one("#ambitions_table").has_focus:
            table = self.query_one("#ambitions_table")
            if table.cursor_row is not None:
                try:
                    row_key = table.coordinate_to_cell_key(table.cursor_coordinate).row_key
                    self.delete_entity("ambition", row_key)
                except Exception:
                    pass

    @work(thread=True)
    def delete_entity(self, entity_type: str, row_key) -> None:
        db = SessionLocal()
        try:
            entity_id = int(row_key.value)
            if entity_type == "role":
                delete_role(db, entity_id)
                if self.selected_role_id == entity_id:
                    self.selected_role_id = None
            else:
                delete_ambition(db, entity_id)
                if self.selected_ambition_id == entity_id:
                    self.selected_ambition_id = None
            self.app.call_from_thread(self._remove_ui_row, entity_type, row_key)
        except Exception as e:
            self.app.notify(f"Delete failed: {e}", severity="error")
        finally:
            db.close()

    def _remove_ui_row(self, entity_type: str, row_key) -> None:
        table_id = "#roles_table" if entity_type == "role" else "#ambitions_table"
        self.query_one(table_id, DataTable).remove_row(row_key)
        if entity_type == "ambition":
            self.query_one("#ambition_tasks_table", DataTable).clear()
            self.query_one("#ambition_stats", AmbitionStats).update("Select an ambition to see statistics")
        elif entity_type == "role":
            self.action_refresh_data() # Refresh ambitions list

class ReviewView(VerticalScroll):
    """A guided Weekly Review wizard."""
    CSS = """
    ReviewView { padding: 1 2; }
    ContentSwitcher { height: auto; margin-bottom: 1; }
    .step-container { border: double $primary; padding: 1 2; margin-top: 1; height: auto; min-height: 12; }
    .step-title { color: $accent; text-align: center; margin-bottom: 1; }
    .step-subtitle { margin-top: 1; text-align: center; color: $secondary; }
    .nav-buttons { height: auto; min-height: 3; margin-top: 1; align: center middle; background: $surface; border-top: solid $primary; padding: 1 0; }
    .jump-buttons { margin-top: 1; align: center middle; }
    .jump-buttons Button { margin: 0 1; width: 24; }
    Button { margin: 0 1; }
    .warning { color: red; font-weight: bold; }
    .stat-row { margin-top: 1; }
    #review_ambitions_table, #review_roles_table { height: 10; margin: 1 0; }
    """

    def compose(self) -> ComposeResult:
        yield Label("Weekly Review Wizard", id="review_header")
        with ContentSwitcher(initial="step_start"):
            with Vertical(id="step_start", classes="step-container"):
                yield Static("Welcome to your Weekly Review.", classes="step-title")
                yield Static("This process will help you get clear, current, and creative.", id="last_review_label")
                yield Static("\nSelect a step to begin or jump ahead:", classes="step-subtitle")
                with Vertical(classes="jump-buttons"):
                    yield Button("1. Mind Dump", id="goto_dump", variant="default")
                    yield Button("2. Review Projects", id="goto_projects", variant="default")
                    yield Button("3. Review Roles (Areas)", id="goto_roles", variant="default")

            with Vertical(id="step_dump", classes="step-container"):
                yield Static("1. Mind Dump (Get Clear)", classes="step-title")
                yield Static("Capture everything currently on your mind. Enter one item at a time.")
                yield Input(placeholder="Type an item and press Enter...", id="review_mind_dump")
                yield Static("", id="dump_feedback")

            with Vertical(id="step_projects", classes="step-container"):
                yield Static("2. Review Projects (Get Current)", classes="step-title")
                yield Static("Ensure every project has a Next Action.")
                yield DataTable(id="review_ambitions_table")
                with Horizontal(id="project_actions"):
                    yield Button("Add Next Action", variant="primary", id="btn_review_add_task")

            with Vertical(id="step_roles", classes="step-container"):
                yield Static("3. Review Areas of Focus (Roles)", classes="step-title")
                yield Static("Ensure every life area is moving forward.")
                yield DataTable(id="review_roles_table")
                with Horizontal(id="role_actions"):
                    yield Button("Add Project", variant="primary", id="btn_review_add_ambition")

            with Vertical(id="step_finish", classes="step-container"):
                yield Static("Review Complete!", classes="step-title")
                yield Static("", id="review_summary")
                yield Button("Finish Review", variant="success", id="btn_complete_review")

        with Horizontal(classes="nav-buttons"):
            yield Button("Menu", id="btn_menu")
            yield Button("Back", id="btn_back")
            yield Button("Next", variant="primary", id="btn_next")

    def on_mount(self) -> None:
        self.review_stats = {"captured": 0, "new_tasks": 0, "new_ambitions": 0}
        try:
            db = SessionLocal()
            last = get_last_review(db)
            if last:
                self.query_one("#last_review_label", Static).update(f"Last Review: {last.timestamp.strftime('%Y-%m-%d %H:%M')}")
            db.close()
        except Exception:
            # Table might not exist yet, will be created by init_db
            pass

        at = self.query_one("#review_ambitions_table", DataTable)
        at.add_columns("Outcome", "Role", "Next Actions", "Status")
        at.zebra_stripes = True

        rt = self.query_one("#review_roles_table", DataTable)
        rt.add_columns("Role", "Projects", "Status")
        rt.zebra_stripes = True

    def action_refresh_data(self) -> None:
        self.load_data()

    @work(thread=True)
    def load_data(self) -> None:
        db = SessionLocal()
        try:
            ambitions = get_ambitions_with_task_counts(db)
            roles = get_roles_with_ambition_counts(db)
            self.app.call_from_thread(self._populate_data, ambitions, roles)
        except Exception:
            pass
        finally:
            db.close()

    def _populate_data(self, ambitions, roles) -> None:
        at = self.query_one("#review_ambitions_table", DataTable)
        at.clear()
        for a in ambitions:
            actions_str = f"[green]{a['todo_count']}[/green]" if a['todo_count'] > 0 else "[red]MISSING[/red]"
            at.add_row(a['outcome'], a['role_name'], actions_str, a['status'], key=str(a['id']))

        rt = self.query_one("#review_roles_table", DataTable)
        rt.clear()
        for r, count in roles:
            status = "[green]Healthy[/green]" if count > 0 else "[red]STAGNANT[/red]"
            rt.add_row(r.name, str(count), status, key=str(r.id))

    def increment_new_tasks(self) -> None:
        self.review_stats["new_tasks"] += 1

    def increment_new_ambitions(self) -> None:
        self.review_stats["new_ambitions"] += 1

    @on(Button.Pressed)
    def handle_nav(self, event: Button.Pressed) -> None:
        switcher = self.query_one(ContentSwitcher)
        steps = ["step_start", "step_dump", "step_projects", "step_roles", "step_finish"]
        current_idx = steps.index(switcher.current)

        if event.button.id == "btn_next":
            if current_idx < len(steps) - 1:
                switcher.current = steps[current_idx + 1]
                if switcher.current in ["step_projects", "step_roles"]:
                    self.load_data()
                if switcher.current == "step_finish":
                    self.update_summary()
        elif event.button.id == "btn_back":
            if current_idx > 0:
                switcher.current = steps[current_idx - 1]
        elif event.button.id == "btn_menu":
            switcher.current = "step_start"
        elif event.button.id == "goto_dump":
            switcher.current = "step_dump"
        elif event.button.id == "goto_projects":
            switcher.current = "step_projects"
            self.load_data()
        elif event.button.id == "goto_roles":
            switcher.current = "step_roles"
            self.load_data()
        elif event.button.id == "btn_complete_review":
            self.complete_review()
        elif event.button.id == "btn_review_add_task":
            # Identify which project is selected if any
            table = self.query_one("#review_ambitions_table", DataTable)
            a_id = None
            if table.cursor_row is not None:
                try:
                    row_key = table.coordinate_to_cell_key(table.cursor_coordinate).row_key
                    if row_key:
                        a_id = str(row_key.value)
                except Exception:
                    pass
            self.app.push_screen(AddTaskScreen(initial_ambition_id=a_id, on_success=self.increment_new_tasks))
        elif event.button.id == "btn_review_add_ambition":
            # Identify which role is selected if any
            table = self.query_one("#review_roles_table", DataTable)
            r_id = None
            if table.cursor_row is not None:
                try:
                    row_key = table.coordinate_to_cell_key(table.cursor_coordinate).row_key
                    if row_key:
                        r_id = str(row_key.value)
                except Exception:
                    pass
            self.app.push_screen(AddAmbitionScreen(initial_role_id=r_id, on_success=self.increment_new_ambitions))

    def update_summary(self) -> None:
        summary = (
            f"Items Captured: {self.review_stats['captured']}\n"
            f"New Next Actions: {self.review_stats.get('new_tasks', 0)}\n"
            f"New Projects: {self.review_stats.get('new_ambitions', 0)}"
        )
        self.query_one("#review_summary", Static).update(summary)


    @on(Input.Submitted, "#review_mind_dump")
    async def handle_dump(self, message: Input.Submitted) -> None:
        raw_text = message.value.strip()
        if raw_text:
            parsed_data = parse_capture_text(raw_text)
            add_to_inbox(raw_text, parsed_data)
            self.review_stats["captured"] += 1
            self.query_one("#dump_feedback", Static).update(f"[green]Captured ({self.review_stats['captured']}): {raw_text}[/green]")
            self.query_one("#review_mind_dump", Input).value = ""

    @work(thread=True)
    def complete_review(self) -> None:
        db = SessionLocal()
        try:
            record_review(db)
            self.app.call_from_thread(self.finish_review)
        finally:
            db.close()

    def finish_review(self) -> None:
        self.app.notify("Weekly Review recorded!")
        self.app.action_switch_tab("capture")

class MindWaterApp(App):
    """The main GTD application."""
    
    TITLE = "MindWater GTD"
    SUB_TITLE = f"DB: {APP_ENV.capitalize()}"
    
    CSS = """
    #capture_container {
        padding: 2 4;
        height: auto;
        border: solid green;
        margin: 4 8;
    }
    #prompt {
        margin-bottom: 1;
    }
    #feedback {
        margin-top: 1;
        color: yellow;
    }
    .status-msg {
        content-align: center middle;
        height: 1fr;
    }
    #loading, #loading_tasks { color: yellow; }
    #empty, #empty_tasks { color: green; display: none; }
    #error { color: red; display: none; }
    
    DataTable {
        height: 1fr;
        margin: 0 2;
    }
    """
    
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("ctrl+c", "switch_tab('capture')", "Capture"),
        ("ctrl+l", "switch_tab('inbox')", "Inbox"),
        ("ctrl+t", "switch_tab('tasks')", "Tasks"),
        ("ctrl+h", "switch_tab('horizons')", "Horizons"),
        ("ctrl+w", "switch_tab('review')", "Review"),
        ("r", "refresh_active_view", "Refresh"),
    ]

    def on_mount(self) -> None:
        """Called when app starts."""
        # Initial refresh for all views to ensure data is loaded
        self.call_after_refresh(self.action_refresh_all_views)

    def action_refresh_all_views(self) -> None:
        """Refreshes data in all views."""
        try:
            self.query_one(InboxListView).action_refresh_data()
            self.query_one(TasksView).action_refresh_data()
            self.query_one(TasksView).load_filter_options()
            self.query_one(HorizonsView).action_refresh_data()
            self.query_one(ReviewView).action_refresh_data()
        except Exception:
            # Some views might not be fully mounted yet, ignore
            pass

    def compose(self) -> ComposeResult:
        yield Header()
        with TabbedContent(initial="capture", id="main_tabs"):
            with TabPane("Capture", id="capture"):
                yield CaptureView()
            with TabPane("Inbox", id="inbox"):
                yield InboxListView()
            with TabPane("Tasks", id="tasks"):
                yield TasksView()
            with TabPane("Horizons", id="horizons"):
                yield HorizonsView()
            with TabPane("Review", id="review"):
                yield ReviewView()
        yield Footer()

    def action_switch_tab(self, tab_id: str) -> None:
        self.query_one(TabbedContent).active = tab_id

    def action_refresh_active_view(self) -> None:
        active_tab = self.query_one(TabbedContent).active
        if active_tab == "inbox":
            self.query_one(InboxListView).action_refresh_data()
        elif active_tab == "tasks":
            self.query_one(TasksView).action_refresh_data()
        elif active_tab == "horizons":
            self.query_one(HorizonsView).action_refresh_data()
        elif active_tab == "review":
            self.query_one(ReviewView).action_refresh_data()

    def on_tabbed_content_tab_activated(self, event: TabbedContent.TabActivated) -> None:
        if event.tab.id == "inbox":
            self.query_one(InboxListView).action_refresh_data()
        elif event.tab.id == "tasks":
            self.query_one(TasksView).action_refresh_data()
            self.query_one(TasksView).load_filter_options()
        elif event.tab.id == "horizons":
            self.query_one(HorizonsView).action_refresh_data()
        elif event.tab.id == "review":
            self.query_one(ReviewView).action_refresh_data()
        elif event.tab.id == "capture":
             self.query_one(Input).focus()

if __name__ == "__main__":
    init_db()
    app = MindWaterApp()
    app.run()
