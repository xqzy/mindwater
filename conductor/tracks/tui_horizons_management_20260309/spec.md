# Specification: TUI Role & Ambition Management

## Overview
Currently, the system crashes or remains empty if no Roles or Ambitions exist. Users need a way to build their "Horizons of Focus" by creating Roles (Horizon 2) and Ambitions (Horizon 1 - Projects) directly from the TUI.

## Requirements

### 1. Interface
- A new "Horizons" tab or a "Settings" area to manage these.
- For now, let's add a "Horizons" tab.
- It should show two lists: Roles and Ambitions.

### 2. Creation
- Buttons to "Add Role" and "Add Ambition".
- Simple dialogs/screens to input the Name/Outcome and link them appropriately (Ambitions link to Roles).

### 3. Integration
- Save to local SQLite database using existing CRUD functions.
- Ensure the "Clarify" screen refreshes its dropdowns when new ones are added.

## Success Criteria
- [ ] Users can create new Roles.
- [ ] Users can create new Ambitions and link them to Roles.
- [ ] The "Clarify" screen correctly displays these new options in the dropdowns.
