# Specification: Bi-Directional Todoist Integration & Mapping

## Goal
Connect Mindwater (the weekly/monthly GTD planning system) with Todoist (the urgent capture and daily execution tool) via bi-directional synchronization, a configurable Role/Project mapping table, and sticky UI token configuration stored safely outside of Git.

## Requirements

### 1. Sticky API Token Storage in UI (Out of Code/Git)
- Store the Todoist API token in a new `app_setting` table (`key = "todoist_api_token"`) inside the local SQLite database (`/app/data/gtd.db` or `gtd_dev.db`), with fallback to `TODOIST_API_TOKEN` in `.env`.
- Provide a sticky configuration bar in the **Todoist** tab where the user enters the token once. Once saved, display a masked preview (`••••••••abcd`) and connection status.

### 2. Hierarchy Mapping Table (Roles $\leftrightarrow$ Todoist Projects, Ambitions $\leftrightarrow$ Todoist Labels)
- **Mindwater Roles (H2) $\leftrightarrow$ Todoist Projects**:
  - Each `Horizon2` (Role) can be mapped to a `todoist_project_id` and `todoist_project_name`.
  - Renaming a Role in Mindwater updates the linked Todoist Project name.
- **Mindwater Projects / Ambitions (H1) $\leftrightarrow$ Todoist Labels**:
  - Each `Ambition` (Project) can be mapped to a `todoist_label_name` (and `todoist_label_id`).
  - Provide an interactive **Mapping Table** in the UI where the user can map any Mindwater Role to a Todoist Project (or create one in 1 click) and map any Mindwater Project (Ambition) to a Todoist Label (or create one in 1 click).
- **Lifecycle Propagation (Idea #3)**:
  - Renaming a mapped Mindwater Project updates the Todoist Label name.
  - Archiving or deleting a Mindwater Project closes/removes its synced tasks in Todoist.

### 3. Incoming Todoist Task Routing & Clarify-in-Place (Core + Idea #6)
- **Sync Trigger**: Runs automatically when opening the Inbox, Tasks, or Todoist tabs, and whenever the user clicks the **"Sync with Todoist"** button.
- **Filtering Out Welcome, Archived & Deleted Items**:
  - Automatically filter out Todoist's built-in `Welcome 👋` onboarding project (`utm_campaign=welcome_project` / project name starting with `welcome`), archived or deleted projects (`is_archived=True` or `is_deleted=True`), and checked/deleted tasks (`checked=True`, `is_completed=True`, `is_deleted=True`). Any previously imported items from filtered projects are automatically cleaned from the Mindwater Inbox on sync.
- **Mapped Tasks $\rightarrow$ Mindwater Tasks**:
  - Active Todoist tasks that have a mapped Todoist Label (or mapped Todoist Project) are automatically created or updated in Mindwater's `Task` table under the mapped Mindwater Project (`ambition_id`) and Role (`role_id`).
- **Unmapped Tasks $\rightarrow$ Mindwater Inbox**:
  - Active Todoist tasks without a mapped label/project are imported into Mindwater's `Inbox` table (`source_tag="todoist"`, `todoist_task_id`).
- **Clarify in Place (Idea #6)**:
  - When a Todoist-sourced Inbox item is clarified in Mindwater into a Task with a Role and/or Project, Mindwater updates the existing Todoist task (`content`, `project_id`, `labels`, `duration`) and transfers `todoist_task_id` to the newly created Mindwater `Task` record.

### 4. Two-Way Completion & Duration Sync (Core + Ideas #1 & #5)
- **Mindwater $\rightarrow$ Todoist**:
  - Marking a synced task `done` in Mindwater closes the task in Todoist (`POST /api/v1/tasks/{id}/close`). Marking it back to `todo` reopens it in Todoist (`POST /api/v1/tasks/{id}/reopen`).
  - Exporting/updating a task from Mindwater to Todoist sends its `title`, mapped `project_id` (from Role), mapped `labels` (from Ambition), `due_date`, and `duration` (`estimated_time` in minutes).
- **Todoist $\rightarrow$ Mindwater**:
  - If a Mindwater task has a `todoist_task_id` and `status == "todo"`, and the task is completed (no longer in Todoist's active tasks list), Mindwater marks the task `done` with `completed_at = datetime.now(UTC)`, automatically updating Horizons throughput statistics.
  - If a Todoist task has a `duration` (in minutes), it syncs to `Task.estimated_time` in Mindwater.

### 5. Visual Badges, Urgent Highlights & Deep Links (Ideas #7 & #8)
- **Sync Badge & Deep Link (Idea #7)**:
  - Tasks synced with Todoist display a Todoist badge that links directly to `https://app.todoist.com/app/task/{todoist_task_id}`. Unsynced tasks display a 1-click **Push to Todoist** button.
- **Urgent / Due Today Highlight (Idea #8)**:
  - Tasks or Inbox items from Todoist that are overdue, due today, or marked Priority 1 (`priority == 4` in Todoist API) display an **Urgent / Due** badge in Mindwater.

### 6. Weekly Review Integration (Ideas #2 & #10)
- **Batch Push ("Commit to This Week" - Idea #2)**:
  - In Step 2 (Review Projects) of the Weekly Review wizard, list each project's `todo` Next Actions with checkboxes and a **"Push Selected to Todoist"** button to batch-export weekly actions.
- **Orphaned / Stale in Todoist Check (Idea #10)**:
  - In Step 2 of the Weekly Review wizard, flag any active Todoist-synced tasks that were created in Todoist more than 14 days ago so the user can review or archive stale commitments.

## Non-Regressions
- Existing local-only tasks, projects, roles, and inbox items must work identically when no Todoist token is configured or when offline.
- Auto-migrations must safely add new columns to existing SQLite databases (`gtd_dev.db` and `gtd.db`) without data loss.

