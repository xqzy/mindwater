# Implementation Plan: TUI Capture Interface

## Phase 1: Environment Setup
1. Verify `textual` and `firebase-admin` are available in the project's Python environment.
2. If missing, update `requirements.txt` or `dev.nix` to include these dependencies.
3. Obtain necessary Firebase credentials and store them securely (e.g., in a `.env` file or as a JSON key file).

## Phase 2: Core TUI Development
1. Create `src/cli/tui_capture.py`.
2. Implement a basic **Textual** application structure.
3. Add a single `Input` widget for the capture string.
4. Add a `Static` or `Label` widget for feedback messages.
5. Set up the basic layout and keybindings (e.g., `Esc` to quit, `Enter` to submit).

## Phase 3: Firebase Integration
1. Create a `src/database/firebase.py` module to handle Firestore interactions.
2. Implement an `add_to_inbox` function that takes parsed data and saves it to the `inbox` collection.
3. Ensure proper initialization of the Firebase Admin SDK using credentials.

## Phase 4: Capture & Parse Logic
1. Connect the `on_input_submitted` event in the TUI to the `src/services/parser.py`.
2. Call the `parse_capture_text` function to get structured data.
3. Call the `add_to_inbox` function to save the data to Firebase.
4. Clear the input field and display a success message to the user.

## Phase 5: Testing & Validation
1. Create a unit test for the Firebase integration (using a mock or a test database).
2. Manually test the TUI by running `python -m src.cli.tui_capture`.
3. Verify that items appear in the Firebase 'inbox' collection with the correct fields.
4. Check error handling (e.g., if Firebase is unreachable).

## Success Criteria
- [x] TUI launches without errors.
- [x] Input can be typed and submitted.
- [x] Text is correctly parsed for tags and contexts.
- [x] Data is successfully saved to Firebase.
- [x] User receives clear feedback on success or failure.
