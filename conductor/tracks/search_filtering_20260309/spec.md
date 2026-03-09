# Specification: Search & Filtering

## Overview
Implement a robust filtering system within the "Tasks" view. This allows users to follow the GTD "Engage" step by filtering their next actions based on their current Context (e.g., @computer), Energy Level (e.g., Low), or a specific Role (Area of Focus).

## Requirements

### 1. Filter Bar
- A horizontal or vertical bar above the Tasks DataTable.
- Includes dropdowns (Select widgets) for:
    - **Context:** Filter by tags like @home, @calls, @computer.
    - **Energy Level:** Filter by Low, Medium, or High.
    - **Role:** Filter by a specific Area of Focus.
- A "Clear Filters" button to reset the view.

### 2. Dynamic Data Fetching
- The `TasksView` should refresh its list immediately when a filter is changed.
- Filtering should be performed at the database level or efficiently in-memory if the dataset is small.

### 3. User Experience
- Clear visual indicators of which filters are active.
- Keyboard navigation between the filter bar and the task list.

## Success Criteria
- [ ] Users can filter tasks by one or more criteria (Context, Energy, Role).
- [ ] The task list updates correctly and quickly.
- [ ] Users can easily reset all filters to see the full list.
