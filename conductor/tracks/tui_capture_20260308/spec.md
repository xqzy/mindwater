# Specification: TUI Capture Interface

## Overview
Create a Terminal User Interface (TUI) for the 'Capture' phase of the GTD workflow. This interface will allow users to quickly input raw thoughts or tasks, which are then parsed and stored in a Firebase Firestore 'Inbox' collection.

## Requirements

### 1. Interface
- Built with the **Textual** TUI framework.
- Minimalist design focused on speed of entry.
- A single input field for entering text.
- Visual feedback confirming successful capture.

### 2. Capture & Parsing
- Take a string input from the user.
- Utilize the existing `src/services/parser.py` to extract:
  - Cleaned text.
  - Tags (starting with `#`).
  - Contexts (starting with `@`).

### 3. Data Storage
- Store the captured item in **Firebase Firestore**.
- Collection: `inbox`
- Schema:
  - `raw_text`: The original input string.
  - `clean_text`: The text without tags/contexts.
  - `tags`: List of extracted tags.
  - `contexts`: List of extracted contexts.
  - `source`: "tui"
  - `timestamp`: Current date and time.

### 4. Technical Constraints
- Must be a standalone CLI entry point (e.g., `src/cli/tui_capture.py`).
- Should use `firebase-admin` or a similar SDK to interact with Firestore.
- Must handle missing credentials gracefully (e.g., fail with a clear error message).

## User Workflow
1. User runs `python -m src.cli.tui_capture`.
2. A TUI appears with an input box.
3. User types a task: "Buy milk #grocery @shop".
4. User presses Enter.
5. The TUI parses the input and sends it to Firebase.
6. The TUI clears the input or closes, confirming the capture.
