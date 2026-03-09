# Specification: Project Management (Roles & Ambitions)

## Overview
Implement a comprehensive view for managing "Projects" (GTD Horizon 1, referred to as Ambitions in the codebase) and "Areas of Focus" (GTD Horizon 2, referred to as Roles). This allows users to build the structure necessary for clarifying captured items.

## Requirements

### 1. Horizons Tab
- A new "Horizons" tab in the `MindWaterApp`.
- Split view or two distinct sections:
    - **Roles (Areas of Focus):** Manage high-level life areas (e.g., Career, Health, Family).
    - **Ambitions (Projects):** Manage multi-step outcomes that require one or more tasks to complete.

### 2. Role Management
- List existing Roles.
- "Add Role" functionality (Name, Description).
- Delete/Edit Role.

### 3. Ambition Management
- List existing Ambitions.
- "Add Ambition" functionality:
    - Define Success Outcome (Title).
    - **Link to a Role** (mandatory or optional).
    - Set Status (Active, On Hold, Completed).
- View tasks associated with an Ambition.

### 4. Technical Integration
- Use local SQLite database via `src/database/crud.py`.
- Ensure UI updates immediately upon creation of a new entity.

## Success Criteria
- [ ] User can create and view Roles in the TUI.
- [ ] User can create and view Ambitions in the TUI.
- [ ] Ambitions can be linked to Roles.
- [ ] These newly created entities appear as options in the "Clarify" screen.
