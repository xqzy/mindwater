# Specification - Track: GTD Core Models (v2)

## Overview
Re-implement the core GTD data models (Roles, Ambitions, Tasks) to align with the updated `product.md`. This includes incorporating the 5 Steps of GTD, Core Pillars, and the hierarchical Horizons of Focus.

## Functional Requirements
- **Inbox / Capture Model:**
  - Raw Text String (captured loop)
  - Source Tag (e.g., Todoist, Voice)
  - Captured Timestamp
- **Horizon Models (Hierarchy):**
  - **Horizon 5 (Purpose):** Life mission and core values.
  - **Horizon 4 (Vision):** 3-5 year goals.
  - **Horizon 2 (Roles):** Life areas (e.g., Parent, Developer).
- **Ambition Model (Horizon 1 - Projects):**
  - Defined outcome.
  - Link to Horizon 2 (Role), Horizon 4 (Vision), or Horizon 5 (Purpose).
- **Task Model (Horizon 0 - Next Actions):**
  - Physical Next Action title.
  - Context Tags (e.g., @computer, @calls).
  - Energy Level (Low, Medium, High).
  - Flexible linkage: Can belong to an Ambition or directly to a Role.
- **Review Logic:**
  - Flagging mechanism for Roles with no active projects/ambitions.

## Non-Functional Requirements
- **Ubiquitous Capture:** Model must support rapid, frictionless data entry.
- **Data Integrity:** Maintain hierarchy and flexible mapping between horizons.

## Acceptance Criteria
- All models (H0, H1, H2, H4, H5) are implemented with specified attributes.
- Relationships between horizons are verified through unit tests.
- Logic to identify "empty" roles is functional.

## Out of Scope
- Frontend implementation.
- External Todoist bi-directional sync (to be handled in a later track).
