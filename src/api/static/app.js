document.addEventListener('DOMContentLoaded', () => {
    // --- State & Constants ---
    let currentInboxItems = [];
    let currentEmailItems = [];
    let currentRoles = [];
    let currentAmbitions = [];
    let currentTasks = [];
    let currentDetailTasks = [];
    let currentDetailAmbitionId = null;
    let editingFromAmbitionId = null;
    let todoistEnabled = false;
    let todoistMaskedToken = "";
    let lastTodoistSync = null;
    let currentTab = 'followup';
    let selectedRoleId = null;
    let showArchivedProjects = false;

    // --- Selectors ---
    const navItems = document.querySelectorAll('.nav-item');
    const tabContents = document.querySelectorAll('.tab-content');
    
    // Modals
    const clarifyModal = document.getElementById('clarify-modal');
    const horizonModal = document.getElementById('horizon-modal');
    const taskEditModal = document.getElementById('task-edit-modal');
    const taskSnoozeModal = document.getElementById('task-snooze-modal');
    const projectRemoveModal = document.getElementById('project-remove-modal');
    
    // Forms
    const clarifyForm = document.getElementById('clarify-form');
    const horizonForm = document.getElementById('horizon-form');
    const taskEditForm = document.getElementById('task-edit-form');
    const taskSnoozeForm = document.getElementById('task-snooze-form');

    // --- Navigation ---
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const tabName = item.getAttribute('data-tab');
            switchTab(tabName);
        });
    });

    const switchTab = async (tabName) => {
        currentTab = tabName;
        navItems.forEach(n => {
            n.classList.remove('active');
            if (n.getAttribute('data-tab') === tabName) n.classList.add('active');
        });

        tabContents.forEach(content => {
            content.classList.remove('active');
            if (content.id === tabName) content.classList.add('active');
        });

        // Refresh data for the active tab (syncing with Todoist on tab open if configured)
        if (tabName === 'followup') fetchEmails();
        if (tabName === 'inbox') {
            if (todoistEnabled) await syncTodoist(true);
            fetchFullInbox();
        }
        if (tabName === 'tasks') {
            if (todoistEnabled) await syncTodoist(true);
            fetchTasks();
        }
        if (tabName === 'projects') fetchHorizons();
        if (tabName === 'review') initReviewWizard();
        if (tabName === 'todoist') loadTodoistTab();
    };

    // --- Global Helpers ---
    const showToast = (message, type = 'success', durationMs = 5500) => {
        const container = document.getElementById('toast-container');
        if (container) {
            const toast = document.createElement('div');
            toast.className = `toast-item ${type}`;
            const icon = type === 'error' ? 'fa-circle-xmark' : (type === 'info' ? 'fa-circle-info' : 'fa-circle-check');
            toast.innerHTML = `
                <i class="fas ${icon}" style="margin-top: 0.15rem; font-size: 1rem;"></i>
                <div style="flex: 1;">${message}</div>
                <button class="btn-icon" style="padding: 0;" onclick="this.parentElement.remove()">&times;</button>
            `;
            container.appendChild(toast);
            setTimeout(() => {
                if (toast.parentElement) toast.remove();
            }, durationMs);
        }

        // Also update the inline feedback banner in the Todoist tab so it is impossible to miss
        const banner = document.getElementById('todoist-action-feedback');
        if (banner) {
            banner.className = `feedback-banner ${type}`;
            banner.style.display = 'flex';
            banner.innerHTML = `
                <div><strong>${type === 'error' ? 'Error:' : (type === 'info' ? 'Status:' : 'Success:')}</strong> ${message}</div>
                <button class="btn-icon" onclick="this.parentElement.style.display='none'">&times;</button>
            `;
        }
    };

    const apiFetch = async (url, options = {}) => {
        try {
            const response = await fetch(url, options);
            if (!response.ok) {
                let errDetail = `API Error: ${response.status}`;
                try {
                    const errJson = await response.json();
                    if (errJson.detail) {
                        errDetail = typeof errJson.detail === 'string'
                            ? errJson.detail
                            : JSON.stringify(errJson.detail);
                    }
                } catch (_) {}
                throw new Error(errDetail);
            }
            return await response.json();
        } catch (error) {
            console.error(error);
            if (!options.silent) {
                showToast(error.message, 'error', 8000);
            }
            return null;
        }
    };

    const updateSelectOptions = (selectId, items, valueField, textField, prompt = "Select...") => {
        const select = document.getElementById(selectId);
        if (!select) return;
        const prevVal = select.value;
        select.innerHTML = `<option value="">${prompt}</option>` + 
            items.map(item => `<option value="${item[valueField]}">${item[textField]}</option>`).join('');
        if (prevVal && items.some(item => String(item[valueField]) === String(prevVal))) {
            select.value = prevVal;
        }
    };

    const filterClarifyAmbitionsByRole = (roleId, selectedAmbitionId = null) => {
        const select = document.getElementById('clarify-ambition');
        if (!select) return;
        const keepAmbitionId = selectedAmbitionId !== null ? selectedAmbitionId : select.value;
        const parsedRoleId = parseInt(roleId);
        const activeAmbitions = (currentAmbitions || []).filter(a => a.status === 'active');

        if (!isNaN(parsedRoleId)) {
            const roleAmbitions = activeAmbitions.filter(a => a.role_id === parsedRoleId);
            const promptText = roleAmbitions.length > 0
                ? 'None (Standalone Task)'
                : 'No projects for this role yet (Standalone Task)';
            select.innerHTML = `<option value="">${promptText}</option>` +
                roleAmbitions.map(a => `<option value="${a.id}">${a.outcome}</option>`).join('');
            if (keepAmbitionId && roleAmbitions.some(a => String(a.id) === String(keepAmbitionId))) {
                select.value = String(keepAmbitionId);
            } else {
                select.value = "";
            }
        } else {
            const unassignedAmbitions = activeAmbitions.filter(a => !a.role_id);
            select.innerHTML = `<option value="">None (Select a Role above to see its projects)</option>` +
                unassignedAmbitions.map(a => `<option value="${a.id}">${a.outcome}</option>`).join('');
            if (keepAmbitionId && unassignedAmbitions.some(a => String(a.id) === String(keepAmbitionId))) {
                select.value = String(keepAmbitionId);
            } else {
                select.value = "";
            }
        }
    };

    const filterEditTaskAmbitionsByRole = (roleId, selectedAmbitionId = null) => {
        const select = document.getElementById('edit-task-ambition');
        if (!select) return;
        const keepAmbitionId = selectedAmbitionId !== null ? selectedAmbitionId : select.value;
        const parsedRoleId = parseInt(roleId);
        const activeAmbitions = (currentAmbitions || []).filter(a => a.status === 'active');
        const matching = !isNaN(parsedRoleId)
            ? activeAmbitions.filter(a => a.role_id === parsedRoleId)
            : activeAmbitions;

        select.innerHTML = `<option value="">None (Standalone)</option>` +
            matching.map(a => `<option value="${a.id}">${a.outcome}</option>`).join('');
        if (keepAmbitionId && matching.some(a => String(a.id) === String(keepAmbitionId))) {
            select.value = String(keepAmbitionId);
        } else {
            select.value = "";
        }
    };

    // Helper for Idea #8 (Urgent / Overdue in Todoist badge) & Idea #7 (Deep-Link Sync Badge)
    const getTodayDateStr = () => {
        const d = new Date();
        return d.toISOString().slice(0, 10);
    };

    const renderTodoistUrgentBadge = (item) => {
        const isP1 = item.todoist_priority && Number(item.todoist_priority) === 4;
        const today = getTodayDateStr();
        const isDueOrOverdue = item.todoist_due_date && item.todoist_due_date.slice(0, 10) <= today;
        if (!isP1 && !isDueOrOverdue) return '';
        const label = isP1 && isDueOrOverdue ? `Urgent • Due ${item.todoist_due_date.slice(0, 10)}` : (isP1 ? 'Urgent (P1)' : `Due ${item.todoist_due_date.slice(0, 10)}`);
        return `<span class="urgent-badge" title="Flagged as urgent or due in Todoist"><i class="fas fa-fire"></i> ${label}</span>`;
    };

    const renderTodoistLinkBadge = (item) => {
        if (!item.todoist_task_id) return '';
        const url = `https://app.todoist.com/app/task/${item.todoist_task_id}`;
        return `<a href="${url}" target="_blank" rel="noopener" class="todoist-badge" onclick="event.stopPropagation();" title="Open in Todoist"><i class="fas fa-check-circle"></i> Todoist <i class="fas fa-arrow-up-right-from-square" style="font-size:0.6rem;"></i></a>`;
    };

    const renderMonitoringBadge = (task) => {
        if (task.status !== 'monitoring') return '';
        return `<span class="monitoring-badge" title="Monitoring: waiting for someone else"><i class="fas fa-eye"></i> Monitoring</span>`;
    };

    const renderDueDateBadge = (task, ambitionId = null) => {
        const dueStr = (task.due_date || task.todoist_due_date || '').slice(0, 10);
        if (!dueStr) return '';
        const today = getTodayDateStr();
        const isOverdue = dueStr < today && task.status !== 'done';
        const isSnoozedFuture = dueStr > today;
        const prefix = isSnoozedFuture ? 'Snoozed until' : (dueStr === today ? 'Due Today' : 'Due');
        const ambArg = ambitionId ? ambitionId : 'null';
        return `<span class="snoozed-badge ${isOverdue ? 'overdue' : ''}" onclick="event.stopPropagation(); openSnoozeModal(${task.id}, '${dueStr}', ${ambArg})" title="Click to snooze or change due date"><i class="fas fa-clock"></i> ${prefix} ${dueStr}</span>`;
    };

    // --- Data Fetching ---
    const fetchConfig = async () => {
        const config = await apiFetch('/config', { silent: true });
        if (config) {
            todoistEnabled = config.todoist_enabled;
            todoistMaskedToken = config.todoist_token_masked || "";
            lastTodoistSync = config.last_todoist_sync || null;
        }
    };

    const syncTodoist = async (silent = false, triggerBtn = null) => {
        const origHtml = triggerBtn ? triggerBtn.innerHTML : null;
        if (triggerBtn) {
            triggerBtn.disabled = true;
            triggerBtn.innerHTML = `<i class="fas fa-spinner fa-spin"></i> &nbsp;Syncing...`;
        } else if (!silent) {
            showToast('Syncing with Todoist...', 'info', 2500);
        }

        const res = await apiFetch('/todoist/sync', { method: 'POST', silent });

        if (triggerBtn) {
            triggerBtn.disabled = false;
            triggerBtn.innerHTML = origHtml;
        }

        if (res && res.status === 'success') {
            lastTodoistSync = res.last_sync;
            if (!silent) {
                showToast(
                    `Todoist Sync Complete! Imported ${res.imported_tasks} to Tasks, ${res.imported_inbox} to Inbox, updated ${res.updated_tasks}, and marked ${res.completed_tasks} done.`,
                    'success',
                    7000
                );
            }
            if (currentTab === 'inbox') fetchFullInbox();
            if (currentTab === 'tasks') fetchTasks();
            if (currentTab === 'todoist') loadTodoistTab();
        }
        return res;
    };

    const inboxSyncBtn = document.getElementById('inbox-sync-todoist-btn');
    if (inboxSyncBtn) inboxSyncBtn.onclick = () => syncTodoist(false, inboxSyncBtn);

    const tasksSyncBtn = document.getElementById('tasks-sync-todoist-btn');
    if (tasksSyncBtn) tasksSyncBtn.onclick = () => syncTodoist(false, tasksSyncBtn);

    const todoistSyncNowBtn = document.getElementById('todoist-sync-now-btn');
    if (todoistSyncNowBtn) todoistSyncNowBtn.onclick = () => syncTodoist(false, todoistSyncNowBtn);

    const fetchRoles = async () => {
        currentRoles = await apiFetch('/roles');
        if (currentRoles) {
            updateSelectOptions('clarify-role', currentRoles, 'id', 'name', 'No specific role');
            updateSelectOptions('filter-role', currentRoles, 'id', 'name', 'All Roles');
            updateSelectOptions('ambition-role-select', currentRoles, 'id', 'name', 'Select Role...');
            updateSelectOptions('edit-task-role', currentRoles, 'id', 'name', 'No specific role');
        }
    };

    const fetchAmbitions = async (statusOverride = null) => {
        const status = statusOverride || (showArchivedProjects ? 'archived' : 'active');
        currentAmbitions = await apiFetch(`/ambitions?status=${status}`);
        if (status === 'active' && currentAmbitions) {
            const clarifyRoleVal = document.getElementById('clarify-role')?.value || "";
            filterClarifyAmbitionsByRole(clarifyRoleVal);
            const editRoleVal = document.getElementById('edit-task-role')?.value || "";
            filterEditTaskAmbitionsByRole(editRoleVal);
        }
    };

    // --- Follow-up Screen ---
    const fetchEmails = async () => {
        const list = document.getElementById('email-list');
        list.innerHTML = '<p class="text-muted" style="text-align:center;">Fetching flagged emails...</p>';
        currentEmailItems = await apiFetch('/emails/flagged');
        renderEmailList();
    };

    const renderEmailList = () => {
        const list = document.getElementById('email-list');
        if (!currentEmailItems || currentEmailItems.length === 0) {
            list.innerHTML = '<p class="text-muted" style="text-align:center; padding: 2rem;">No flagged emails found.</p>';
            return;
        }
        list.innerHTML = currentEmailItems.map(item => `
            <div class="inbox-card">
                <div style="flex: 1;" onclick="openClarifyModalForEmail('${item.id}')">
                    <div class="item-text"><strong>${item.from}</strong>: ${item.subject}</div>
                    <div class="item-meta">${item.date}</div>
                </div>
                <div style="display: flex; gap: 0.5rem;">
                    <button class="clarify-btn" onclick="openClarifyModalForEmail('${item.id}')">Clarify</button>
                    <button class="btn-secondary" onclick="dismissEmail('${item.id}')">Dismiss</button>
                </div>
            </div>
        `).join('');
    };

    window.dismissEmail = async (emailId) => {
        if (confirm('Dismiss this email? It will no longer appear in Follow-up.')) {
            await apiFetch(`/emails/dismiss/${emailId}`, { method: 'POST' });
            currentEmailItems = currentEmailItems.filter(e => e.id !== emailId);
            renderEmailList();
        }
    };

    // --- Capture Screen ---
    const captureBtn = document.getElementById('capture-btn');
    const captureInput = document.getElementById('capture-input');
    const recentItemsList = document.getElementById('recent-items');

    const captureTask = async () => {
        const text = captureInput.value.trim();
        if (!text) return;
        const res = await apiFetch('/capture', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text, source: 'web' })
        });
        if (res) {
            captureInput.value = '';
            fetchRecentItems();
        }
    };

    const fetchRecentItems = async () => {
        const items = await apiFetch('/inbox?limit=5');
        if (items) {
            recentItemsList.innerHTML = items.map(item => `
                <div class="inbox-item">
                    <div class="item-text">${item.raw_text}</div>
                    <button class="btn-icon" onclick="deleteInboxItem(${item.id})"><i class="fas fa-trash-can"></i></button>
                </div>
            `).join('');
        }
    };

    window.deleteInboxItem = async (id) => {
        if (confirm('Delete this item?')) {
            await apiFetch(`/inbox/${id}`, { method: 'DELETE' });
            fetchRecentItems();
        }
    };

    captureBtn.onclick = captureTask;

    // --- Inbox Screen ---
    const fetchFullInbox = async () => {
        currentInboxItems = await apiFetch('/inbox?limit=100');
        renderFullInbox();
    };

    const renderFullInbox = () => {
        const list = document.getElementById('inbox-items-full');
        if (!currentInboxItems || currentInboxItems.length === 0) {
            list.innerHTML = '<p class="text-muted" style="text-align:center; padding: 2rem;">Inbox is empty!</p>';
            return;
        }
        list.innerHTML = currentInboxItems.map(item => `
            <div class="inbox-card" onclick="openClarifyModalForInbox(${item.id})">
                <div>
                    <div class="item-text" style="display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
                        <span>${item.raw_text}</span>
                        ${renderTodoistLinkBadge(item)}
                        ${renderTodoistUrgentBadge(item)}
                    </div>
                    <div class="item-meta">${new Date(item.timestamp).toLocaleString()} ${item.source_tag === 'todoist' ? '• Captured via Todoist' : ''}</div>
                </div>
                <button class="clarify-btn">Clarify</button>
            </div>
        `).join('');
    };

    // --- Clarify Modal Logic ---
    window.openClarifyModalForInbox = (itemId) => {
        const item = currentInboxItems.find(i => i.id === itemId);
        if (!item) return;
        resetClarifyModal();
        document.getElementById('clarify-item-id').value = item.id;
        document.getElementById('clarify-title').value = item.raw_text;
        document.getElementById('clarify-modal-title').innerText = item.todoist_task_id ? "Clarify Todoist Item (Updates Todoist in place)" : "Clarify Inbox Item";
        clarifyModal.classList.add('active');
    };

    window.openClarifyModalForEmail = (emailId) => {
        const email = currentEmailItems.find(e => e.id === emailId);
        if (!email) return;
        resetClarifyModal();
        document.getElementById('clarify-email-id').value = email.id;
        document.getElementById('clarify-title').value = email.subject;
        document.getElementById('clarify-modal-title').innerText = "Clarify Email";
        clarifyModal.classList.add('active');
    };

    const resetClarifyModal = async () => {
        clarifyForm.reset();
        document.getElementById('clarify-item-id').value = "";
        document.getElementById('clarify-email-id').value = "";
        document.getElementById('clarify-type').value = "task";
        document.getElementById('task-fields').style.display = 'block';
        document.querySelectorAll('.toggle-btn').forEach(b => b.classList.remove('active'));
        document.querySelector('.toggle-btn[data-type="task"]').classList.add('active');
        await Promise.all([fetchRoles(), fetchAmbitions('active')]);
        document.getElementById('clarify-role').value = "";
        filterClarifyAmbitionsByRole("", "");
    };

    const clarifyRoleSelect = document.getElementById('clarify-role');
    if (clarifyRoleSelect) {
        clarifyRoleSelect.addEventListener('change', (e) => {
            filterClarifyAmbitionsByRole(e.target.value, "");
        });
    }

    const editTaskRoleSelect = document.getElementById('edit-task-role');
    if (editTaskRoleSelect) {
        editTaskRoleSelect.addEventListener('change', (e) => {
            filterEditTaskAmbitionsByRole(e.target.value, "");
        });
    }

    const inboxAddRoleBtn = document.getElementById('inbox-add-role-btn');
    if (inboxAddRoleBtn) inboxAddRoleBtn.onclick = () => openHorizonModal('role');

    const inboxAddAmbitionBtn = document.getElementById('inbox-add-ambition-btn');
    if (inboxAddAmbitionBtn) inboxAddAmbitionBtn.onclick = () => openHorizonModal('ambition');

    const clarifyAddRoleBtn = document.getElementById('clarify-add-role-btn');
    if (clarifyAddRoleBtn) clarifyAddRoleBtn.onclick = () => openHorizonModal('role');

    const clarifyAddAmbitionBtn = document.getElementById('clarify-add-ambition-btn');
    if (clarifyAddAmbitionBtn) {
        clarifyAddAmbitionBtn.onclick = async () => {
            const chosenRoleId = document.getElementById('clarify-role')?.value || "";
            await openHorizonModal('ambition');
            if (chosenRoleId) {
                const ambRoleSelect = document.getElementById('ambition-role-select');
                if (ambRoleSelect) ambRoleSelect.value = chosenRoleId;
            }
        };
    }

    document.querySelectorAll('.toggle-btn').forEach(btn => {
        btn.onclick = () => {
            document.querySelectorAll('.toggle-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            const type = btn.getAttribute('data-type');
            document.getElementById('clarify-type').value = type;
            document.getElementById('task-fields').style.display = type === 'task' ? 'block' : 'none';
        };
    });

    clarifyForm.onsubmit = async (e) => {
        e.preventDefault();
        const itemId = document.getElementById('clarify-item-id').value || 0;
        const emailId = document.getElementById('clarify-email-id').value || null;
        
        const data = {
            type: document.getElementById('clarify-type').value,
            title: document.getElementById('clarify-title').value,
            role_id: parseInt(document.getElementById('clarify-role').value) || null,
            ambition_id: parseInt(document.getElementById('clarify-ambition').value) || null,
            status: document.getElementById('clarify-status')?.value || 'todo',
            due_date: document.getElementById('clarify-due-date')?.value || null,
            energy_level: document.getElementById('clarify-energy').value,
            estimated_time: parseInt(document.getElementById('clarify-time').value) || 0,
            context_tags: document.getElementById('clarify-contexts').value.split(',').map(t => t.trim()).filter(t => t),
            email_id: emailId
        };

        const res = await apiFetch(`/inbox/${itemId}/clarify`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (res) {
            clarifyModal.classList.remove('active');
            if (currentTab === 'review') {
                loadReviewProjects();
            } else if (emailId) {
                fetchEmails(); 
            } else {
                fetchFullInbox();
            }
        }
    };

    document.getElementById('clarify-delete-btn').onclick = async () => {
        const itemId = document.getElementById('clarify-item-id').value;
        const emailId = document.getElementById('clarify-email-id').value;
        if (itemId && confirm('Delete this inbox item?')) {
            await apiFetch(`/inbox/${itemId}`, { method: 'DELETE' });
            clarifyModal.classList.remove('active');
            fetchFullInbox();
        } else if (emailId) {
            dismissEmail(emailId);
            clarifyModal.classList.remove('active');
        }
    };

    // --- Tasks Screen ---
    const fetchTasks = async () => {
        const role = document.getElementById('filter-role').value;
        const energy = document.getElementById('filter-energy').value;
        const statusFilter = document.getElementById('filter-status')?.value || "";
        const includeCompleted = document.getElementById('filter-completed-tasks')?.checked || false;
        const includeArchived = document.getElementById('filter-archived-tasks')?.checked || false;
        let url = `/tasks?`;
        if (role) url += `role_id=${role}&`;
        if (energy) url += `energy=${energy}&`;
        if (statusFilter) url += `status_filter=${statusFilter}&`;
        if (includeCompleted) url += `include_completed=true&`;
        if (includeArchived) url += `include_archived=true&`;
        
        currentTasks = await apiFetch(url);
        renderTasks();
    };

    const renderTasks = () => {
        const tbody = document.getElementById('tasks-table-body');
        if (!currentTasks || currentTasks.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; padding: 2rem;">No tasks found.</td></tr>';
            return;
        }
        tbody.innerHTML = currentTasks.map(task => {
            const isDone = task.status === 'done';
            const isMonitoring = task.status === 'monitoring';
            const dueVal = (task.due_date || task.todoist_due_date || '').slice(0, 10);
            return `
            <tr>
                <td>
                    <div class="status-circle ${isDone ? 'done' : ''}"
                         title="${isDone ? 'Click to reopen task' : 'Click to mark task as Done (Finalised)'}"
                         onclick="toggleTaskStatus(${task.id}, '${task.status}')"></div>
                </td>
                <td>
                    <div style="font-weight: 500; display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
                        <span style="${isDone ? 'text-decoration: line-through; color: var(--text-muted);' : ''}">${task.title}</span>
                        ${isDone ? '<span class="badge success">Finalised</span>' : ''}
                        ${renderMonitoringBadge(task)}
                        ${task.status === 'archived' ? '<span class="archived-badge">Archived</span>' : ''}
                        ${renderDueDateBadge(task)}
                        ${renderTodoistLinkBadge(task)}
                        ${renderTodoistUrgentBadge(task)}
                    </div>
                    <div class="item-meta">
                        ${task.ambition ? task.ambition.outcome : ''}
                        ${task.estimated_time > 0 ? ` • ${task.estimated_time}m` : ''}
                    </div>
                </td>
                <td><span class="text-muted">${task.role ? task.role.name : '-'}</span></td>
                <td>${task.context_tags ? task.context_tags.map(c => `<small class="text-muted">${c}</small>`).join(' ') : ''}</td>
                <td>
                    <div style="display: flex; gap: 0.25rem; align-items: center;">
                        <button class="btn-icon ${isMonitoring ? 'active-monitor' : ''}" onclick="toggleTaskMonitor(${task.id}, '${task.status}')" title="${isMonitoring ? 'Switch back to Next Action (To Do)' : 'Change status to Monitoring (Someone else to do)'}">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn-icon" onclick="openSnoozeModal(${task.id}, '${dueVal}')" title="Snooze / Set Due Date">
                            <i class="fas fa-clock" style="${dueVal ? 'color: #4f46e5;' : ''}"></i>
                        </button>
                        <button class="btn-icon" onclick="openTaskEditModal(${task.id})" title="Edit Task"><i class="fas fa-pen-to-square"></i></button>
                        ${todoistEnabled ? `<button class="btn-icon" onclick="pushToTodoist(${task.id})" title="${task.todoist_task_id ? 'Update in Todoist' : 'Push to Todoist'}"><i class="fas fa-share-from-square" style="${task.todoist_task_id ? 'color:#e11d48;' : ''}"></i></button>` : ''}
                        <button class="btn-icon btn-danger-icon" onclick="deleteTask(${task.id})" title="Delete Task"><i class="fas fa-trash-can"></i></button>
                    </div>
                </td>
            </tr>
            `;
        }).join('');
    };

    window.toggleTaskStatus = async (id, currentStatus) => {
        const newStatus = currentStatus === 'done' ? 'todo' : 'done';
        const res = await apiFetch(`/tasks/${id}/status?status=${newStatus}`, { method: 'PATCH' });
        if (res) {
            showToast(newStatus === 'done' ? 'Task marked as Finalised (Done)!' : 'Task reopened!', 'success', 3500);
        }
        fetchTasks();
    };

    window.toggleTaskMonitor = async (id, currentStatus, ambitionId = null) => {
        const newStatus = currentStatus === 'monitoring' ? 'todo' : 'monitoring';
        const res = await apiFetch(`/tasks/${id}/status?status=${newStatus}`, { method: 'PATCH' });
        if (res) {
            showToast(
                newStatus === 'monitoring'
                    ? 'Task set to Monitoring (Waiting For).'
                    : 'Task switched to Next Action (To Do).',
                'info',
                3500
            );
        }
        if (ambitionId) {
            await fetchHorizons();
            showAmbitionDetail(ambitionId);
        } else {
            fetchTasks();
        }
    };

    const addDaysToToday = (days) => {
        const d = new Date();
        d.setDate(d.getDate() + Number(days));
        return d.toISOString().slice(0, 10);
    };

    window.openSnoozeModal = (id, currentDueDate = '', ambitionId = null) => {
        const task = (currentTasks || []).find(t => t.id === id) || (currentDetailTasks || []).find(t => t.id === id);
        document.getElementById('snooze-task-id').value = id;
        document.getElementById('snooze-ambition-id').value = ambitionId || '';
        const titleEl = document.getElementById('snooze-task-title');
        if (titleEl) {
            titleEl.innerText = task ? `${task.title}${task.status === 'monitoring' ? ' (Monitoring)' : ''}` : `Task #${id}`;
        }
        const dateInput = document.getElementById('snooze-date-input');
        if (dateInput) {
            dateInput.value = currentDueDate ? currentDueDate.slice(0, 10) : addDaysToToday(1);
        }
        if (taskSnoozeModal) taskSnoozeModal.classList.add('active');
    };

    document.querySelectorAll('.snooze-preset-btn').forEach(btn => {
        btn.onclick = () => {
            const days = parseInt(btn.getAttribute('data-days')) || 1;
            const dateInput = document.getElementById('snooze-date-input');
            if (dateInput) dateInput.value = addDaysToToday(days);
        };
    });

    const saveSnoozeDate = async (dueDateStr) => {
        const id = parseInt(document.getElementById('snooze-task-id').value);
        const ambitionId = parseInt(document.getElementById('snooze-ambition-id').value) || null;
        if (!id) return;
        const res = await apiFetch(`/tasks/${id}/snooze`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ due_date: dueDateStr })
        });
        if (res) {
            if (taskSnoozeModal) taskSnoozeModal.classList.remove('active');
            showToast(dueDateStr ? `Task snoozed / due date set to ${dueDateStr}` : 'Task due date cleared.', 'success', 3500);
            if (ambitionId) {
                await fetchHorizons();
                showAmbitionDetail(ambitionId);
            } else {
                fetchTasks();
            }
        }
    };

    if (taskSnoozeForm) {
        taskSnoozeForm.onsubmit = async (e) => {
            e.preventDefault();
            const dueVal = document.getElementById('snooze-date-input')?.value || '';
            await saveSnoozeDate(dueVal);
        };
    }

    const clearSnoozeBtn = document.getElementById('clear-snooze-btn');
    if (clearSnoozeBtn) {
        clearSnoozeBtn.onclick = async () => {
            await saveSnoozeDate('');
        };
    }

    window.deleteTask = async (id, ambitionId = null) => {
        if (!id) return;
        if (!confirm('Are you sure you want to permanently delete this task?')) return;
        const res = await apiFetch(`/tasks/${id}`, { method: 'DELETE' });
        if (res) {
            taskEditModal.classList.remove('active');
            showToast('Task deleted.', 'info', 3500);
            if (ambitionId) {
                await fetchHorizons();
                showAmbitionDetail(ambitionId);
            } else {
                fetchTasks();
            }
        }
    };

    window.pushToTodoist = async (id) => {
        const res = await apiFetch(`/tasks/${id}/push-todoist`, { method: 'POST' });
        if (res) {
            showToast('Task synced with Todoist!', 'success');
            fetchTasks();
        }
    };

    document.getElementById('filter-role').onchange = fetchTasks;
    document.getElementById('filter-energy').onchange = fetchTasks;
    const filterStatusEl = document.getElementById('filter-status');
    if (filterStatusEl) filterStatusEl.onchange = fetchTasks;
    const filterCompletedTasksEl = document.getElementById('filter-completed-tasks');
    if (filterCompletedTasksEl) filterCompletedTasksEl.onchange = fetchTasks;
    const filterArchivedTasksEl = document.getElementById('filter-archived-tasks');
    if (filterArchivedTasksEl) filterArchivedTasksEl.onchange = fetchTasks;
    document.getElementById('clear-filters').onclick = () => {
        document.getElementById('filter-role').value = "";
        document.getElementById('filter-energy').value = "";
        if (filterStatusEl) filterStatusEl.value = "";
        if (filterCompletedTasksEl) filterCompletedTasksEl.checked = false;
        if (filterArchivedTasksEl) filterArchivedTasksEl.checked = false;
        fetchTasks();
    };

    const deleteTaskBtn = document.getElementById('delete-task-btn');
    if (deleteTaskBtn) {
        deleteTaskBtn.onclick = () => {
            const id = parseInt(document.getElementById('edit-task-id').value);
            if (id) deleteTask(id, editingFromAmbitionId);
        };
    }

    window.openTaskEditModal = async (id, ambitionId = null) => {
        const task = (currentTasks || []).find(t => t.id === id) || (currentDetailTasks || []).find(t => t.id === id);
        if (!task) return;
        editingFromAmbitionId = ambitionId;
        
        await Promise.all([fetchRoles(), fetchAmbitions('active')]);
        
        document.getElementById('edit-task-id').value = task.id;
        document.getElementById('edit-task-title').value = task.title;
        const statusSelect = document.getElementById('edit-task-status');
        if (statusSelect) statusSelect.value = task.status || 'todo';
        const dueInput = document.getElementById('edit-task-due-date');
        if (dueInput) dueInput.value = (task.due_date || task.todoist_due_date || '').slice(0, 10);
        document.getElementById('edit-task-energy').value = task.energy_level || 'Medium';
        document.getElementById('edit-task-time').value = task.estimated_time || 0;
        document.getElementById('edit-task-contexts').value = task.context_tags ? task.context_tags.join(', ') : '';
        
        const fallbackRoleId = task.role_id || (ambitionId ? (currentAmbitions.find(a => a.id === ambitionId)?.role_id || "") : "");
        document.getElementById('edit-task-role').value = fallbackRoleId || "";
        filterEditTaskAmbitionsByRole(fallbackRoleId || "", task.ambition_id || ambitionId || "");
        
        taskEditModal.classList.add('active');
    };

    taskEditForm.onsubmit = async (e) => {
        e.preventDefault();
        const id = document.getElementById('edit-task-id').value;
        const data = {
            title: document.getElementById('edit-task-title').value,
            status: document.getElementById('edit-task-status')?.value || 'todo',
            due_date: document.getElementById('edit-task-due-date')?.value || "",
            role_id: parseInt(document.getElementById('edit-task-role').value) || null,
            ambition_id: parseInt(document.getElementById('edit-task-ambition').value) || null,
            energy_level: document.getElementById('edit-task-energy').value,
            estimated_time: parseInt(document.getElementById('edit-task-time').value) || 0,
            context_tags: document.getElementById('edit-task-contexts').value.split(',').map(t => t.trim()).filter(t => t)
        };
        await apiFetch(`/tasks/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        taskEditModal.classList.remove('active');
        showToast('Task updated!', 'success', 3000);
        if (editingFromAmbitionId || currentTab === 'projects') {
            await fetchHorizons();
            const targetAmbId = editingFromAmbitionId || currentDetailAmbitionId;
            if (targetAmbId) showAmbitionDetail(targetAmbId);
            editingFromAmbitionId = null;
        } else {
            fetchTasks();
        }
    };

    // --- Horizons Screen ---
    const fetchHorizons = async () => {
        await fetchRoles();
        await fetchAmbitions();
        renderHorizons();
    };

    const renderHorizons = () => {
        const rolesList = document.getElementById('roles-list');
        const ambitionsList = document.getElementById('ambitions-list');
        
        // Render Roles Sidebar
        let rolesHtml = `
            <div class="horizon-card role-card ${selectedRoleId === null ? 'active' : ''}" onclick="selectRole(null)">
                <div style="font-weight: 600;">All Projects</div>
                <div class="text-muted" style="font-size: 0.75rem;">Show everything</div>
            </div>
        `;
        
        rolesHtml += currentRoles.map(role => {
            const themeObj = window.getRoleTheme ? window.getRoleTheme(role.theme_key) : null;
            const roleColor = role.color || (themeObj ? themeObj.color : '#0284c7');
            const bgDataUri = window.getRoleThemeDataUri ? window.getRoleThemeDataUri(role.theme_key || 'frozen') : '';
            const isSelected = selectedRoleId === role.id;
            const cardStyle = `border-left: 5px solid ${roleColor}; border-color: ${isSelected ? roleColor : window.hexToRgba(roleColor, 0.35)}; ${isSelected ? `box-shadow: 0 0 0 2px ${roleColor};` : ''}`;

            return `
                <div class="horizon-card role-card themed-role-card ${isSelected ? 'active' : ''}" style="${cardStyle}" onclick="selectRole(${role.id})">
                    <div class="role-card-bg" style="background-image: url('${bgDataUri}');"></div>
                    <div class="role-card-veil"></div>
                    <div class="role-card-content">
                        <div class="role-card-text">
                            <div style="font-weight: 700; color: #0f172a; text-shadow: 0 1px 3px rgba(255,255,255,0.95); white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${role.name}</div>
                            ${themeObj ? `<div style="font-size: 0.68rem; font-weight: 700; color: ${roleColor}; text-shadow: 0 1px 2px rgba(255,255,255,0.95); white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${themeObj.title}</div>` : ''}
                            ${role.todoist_project_name ? `<div style="font-size:0.7rem; font-weight: 600; color: #1e293b; text-shadow: 0 1px 2px rgba(255,255,255,0.9); white-space: nowrap; overflow: hidden; text-overflow: ellipsis;"><i class="fas fa-link"></i> ${role.todoist_project_name}</div>` : ''}
                        </div>
                        <button class="btn-icon" style="flex-shrink: 0; background: rgba(255,255,255,0.9); border: 1px solid rgba(226,232,240,0.95); border-radius: 50%; width: 28px; height: 28px; display: flex; align-items: center; justify-content: center;" onclick="event.stopPropagation(); openHorizonModal('role', ${role.id})">
                            <i class="fas fa-gear" style="font-size: 0.75rem; color: #334155;"></i>
                        </button>
                    </div>
                </div>
            `;
        }).join('');
        rolesList.innerHTML = rolesHtml;

        // Filter and Render Projects
        const sectionTitle = document.getElementById('projects-section-title');
        const toggleArchivedBtn = document.getElementById('toggle-archived-projects-btn');
        if (sectionTitle) sectionTitle.innerText = showArchivedProjects ? 'Archived Projects' : 'Active Projects';
        if (toggleArchivedBtn) toggleArchivedBtn.innerText = showArchivedProjects ? 'Show Active' : 'Show Archived';

        const filteredProjects = selectedRoleId 
            ? currentAmbitions.filter(a => a.role_id === selectedRoleId)
            : currentAmbitions;

        if (filteredProjects.length === 0) {
            ambitionsList.innerHTML = `<div class="text-muted" style="grid-column: 1/-1; text-align: center; padding: 2rem;">No ${showArchivedProjects ? 'archived' : 'active'} projects found for this role.</div>`;
            return;
        }

        ambitionsList.innerHTML = filteredProjects.map((a, idx) => {
            const total = a.todo_count + a.done_count + (a.archived_count || 0);
            const percent = total > 0 ? Math.round((a.done_count / total) * 100) : 0;
            const isStalled = a.todo_count === 0 && a.status === 'active';
            const isArchived = a.status === 'archived';
            const priorityNum = a.priority || (idx + 1);
            const roleObj = currentRoles.find(r => r.id === a.role_id);
            const roleColor = (roleObj && roleObj.color) || a.role_color || '#64748b';
            const tintBg = window.hexToRgba ? window.hexToRgba(roleColor, 0.08) : '#f8fafc';
            const borderTint = window.hexToRgba ? window.hexToRgba(roleColor, 0.35) : '#e2e8f0';
            const badgeBg = window.hexToRgba ? window.hexToRgba(roleColor, 0.14) : '#e0f2fe';
            const badgeBorder = window.hexToRgba ? window.hexToRgba(roleColor, 0.38) : '#bae6fd';
            const projectCardStyle = `border-left: 5px solid ${roleColor}; border-color: ${borderTint}; background: linear-gradient(135deg, ${tintBg} 0%, #ffffff 70%);`;

            return `
                <div class="horizon-card project-card" style="${projectCardStyle}" ${!isArchived ? `draggable="true" data-ambition-id="${a.id}"` : ''} onclick="showAmbitionDetail(${a.id})">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 0.5rem;">
                        <div style="display: flex; align-items: flex-start; gap: 0.45rem;">
                            ${!isArchived ? `
                                <span class="drag-handle" title="Drag card to reorder priority"><i class="fas fa-grip-vertical"></i></span>
                                <span class="priority-badge" style="background: ${badgeBg}; color: ${roleColor}; border-color: ${badgeBorder};" title="Click to change priority number" onclick="editProjectPriorityInline(event, ${a.id}, ${priorityNum})">#${priorityNum}</span>
                            ` : ''}
                            <div>
                                <div class="card-title">${a.outcome}</div>
                                ${a.todoist_label_name ? `<span class="todoist-badge" style="margin-top:0.25rem;"><i class="fas fa-tag"></i> @${a.todoist_label_name}</span>` : ''}
                            </div>
                        </div>
                        ${isArchived ? '<span class="archived-badge">Archived</span>' : (isStalled ? '<span class="stalled-badge">Stalled</span>' : '')}
                    </div>
                    
                    <div style="margin-top: auto;">
                        <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 0.35rem;">
                            <span class="role-pill-badge" style="background: ${badgeBg}; color: ${roleColor}; border: 1px solid ${badgeBorder};">
                                <span style="width: 7px; height: 7px; border-radius: 50%; background: ${roleColor}; display: inline-block;"></span>
                                ${a.role_name || 'Unassigned'}
                            </span>
                            <span class="progress-text">${isArchived ? `${total} task${total === 1 ? '' : 's'} archived` : `${a.done_count}/${total} done`}</span>
                        </div>
                        <div class="progress-container">
                            <div class="progress-bar" style="width: ${percent}%; background: ${roleColor};"></div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');

        // Attach Drag-and-Drop listeners for active project cards
        let draggedAmbitionId = null;
        const draggableCards = Array.from(ambitionsList.querySelectorAll('.project-card[draggable="true"]'));

        const executeReorderDrop = async (sourceId, targetId) => {
            if (!sourceId || !targetId || sourceId === targetId) return;

            const visibleIds = filteredProjects.map(p => p.id);
            const fromIdx = visibleIds.indexOf(sourceId);
            const toIdx = visibleIds.indexOf(targetId);
            if (fromIdx === -1 || toIdx === -1) return;

            visibleIds.splice(fromIdx, 1);
            visibleIds.splice(toIdx, 0, sourceId);

            const res = await apiFetch('/ambitions/reorder', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ordered_ids: visibleIds })
            });

            if (res) {
                if (Array.isArray(res.ambitions)) {
                    currentAmbitions = res.ambitions;
                    renderHorizons();
                } else {
                    await fetchHorizons();
                }
                showToast('Project priority order updated!', 'success');
            }
        };

        draggableCards.forEach(card => {
            card.addEventListener('dragstart', (e) => {
                draggedAmbitionId = parseInt(card.getAttribute('data-ambition-id'));
                setTimeout(() => card.classList.add('dragging'), 0);
                if (e.dataTransfer) {
                    e.dataTransfer.effectAllowed = 'move';
                    e.dataTransfer.setData('text/plain', String(draggedAmbitionId));
                }
            });

            card.addEventListener('dragover', (e) => {
                e.preventDefault();
                e.stopPropagation();
                if (e.dataTransfer) e.dataTransfer.dropEffect = 'move';
                const targetId = parseInt(card.getAttribute('data-ambition-id'));
                if (targetId !== draggedAmbitionId) {
                    draggableCards.forEach(c => {
                        if (c !== card) c.classList.remove('drag-over');
                    });
                    card.classList.add('drag-over');
                }
            });

            card.addEventListener('dragleave', (e) => {
                if (!card.contains(e.relatedTarget)) {
                    card.classList.remove('drag-over');
                }
            });

            card.addEventListener('dragend', () => {
                card.classList.remove('dragging');
                draggableCards.forEach(c => c.classList.remove('drag-over'));
                draggedAmbitionId = null;
            });

            card.addEventListener('drop', async (e) => {
                e.preventDefault();
                e.stopPropagation();
                card.classList.remove('drag-over');

                const sourceId = draggedAmbitionId || parseInt(e.dataTransfer ? e.dataTransfer.getData('text/plain') : '');
                const targetId = parseInt(card.getAttribute('data-ambition-id'));
                await executeReorderDrop(sourceId, targetId);
            });
        });

        ambitionsList.ondragover = (e) => {
            e.preventDefault();
            if (e.dataTransfer) e.dataTransfer.dropEffect = 'move';
        };

        ambitionsList.ondrop = async (e) => {
            e.preventDefault();
            const sourceId = draggedAmbitionId || parseInt(e.dataTransfer ? e.dataTransfer.getData('text/plain') : '');
            const overCard = e.target.closest('.project-card[draggable="true"]');
            if (overCard) {
                const targetId = parseInt(overCard.getAttribute('data-ambition-id'));
                await executeReorderDrop(sourceId, targetId);
            }
        };
    };

    window.editProjectPriorityInline = (event, ambitionId, currentPriority) => {
        event.stopPropagation();
        const badgeEl = event.currentTarget;
        if (badgeEl.querySelector('input')) return;

        const input = document.createElement('input');
        input.type = 'number';
        input.min = '1';
        input.className = 'priority-inline-input';
        input.value = currentPriority;

        const commitPriority = async () => {
            const newPrio = parseInt(input.value);
            if (!isNaN(newPrio) && newPrio >= 1 && newPrio !== currentPriority) {
                const res = await apiFetch(`/ambitions/${ambitionId}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ priority: newPrio })
                });
                if (res) {
                    showToast(`Project moved to priority #${newPrio}`, 'success');
                }
            }
            await fetchHorizons();
        };

        input.addEventListener('click', (e) => e.stopPropagation());
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                input.blur();
            } else if (e.key === 'Escape') {
                fetchHorizons();
            }
        });
        input.addEventListener('blur', commitPriority, { once: true });

        badgeEl.replaceWith(input);
        input.focus();
        input.select();
    };

    const toggleArchivedProjectsBtn = document.getElementById('toggle-archived-projects-btn');
    if (toggleArchivedProjectsBtn) {
        toggleArchivedProjectsBtn.onclick = () => {
            showArchivedProjects = !showArchivedProjects;
            document.getElementById('ambition-detail').style.display = 'none';
            fetchHorizons();
        };
    }

    window.selectRole = (roleId) => {
        selectedRoleId = roleId;
        renderHorizons();
        document.getElementById('ambition-detail').style.display = 'none';
    };

    window.showAmbitionDetail = async (id) => {
        const detailPane = document.getElementById('ambition-detail');
        const ambition = currentAmbitions.find(a => a.id === id);
        if (!ambition) return;

        document.getElementById('detail-title').innerText = ambition.outcome;
        detailPane.style.display = 'block';

        const stats = await apiFetch(`/ambitions/${id}/stats`);
        const tasks = await apiFetch(`/ambitions/${id}/tasks`);
        currentDetailTasks = tasks || [];
        currentDetailAmbitionId = id;

        document.getElementById('detail-stats').innerHTML = `
            <div class="stat-item"><div class="stat-value">${stats.total_hours}h</div><div class="stat-label">Spent</div></div>
            <div class="stat-item"><div class="stat-value">${stats.finished_2w}</div><div class="stat-label">Done (2w)</div></div>
            <div class="stat-item"><div class="stat-value">${stats.total_finished}</div><div class="stat-label">Total Done</div></div>
        `;

        document.getElementById('detail-tasks').innerHTML = (tasks || []).map(t => {
            const isMonitoring = t.status === 'monitoring';
            const dueVal = (t.due_date || t.todoist_due_date || '').slice(0, 10);
            return `
            <div class="mini-task" style="align-items: center;">
                <div class="status-circle ${t.status === 'done' ? 'done' : ''}" title="${t.status === 'done' ? 'Reopen task' : 'Mark as Done'}" onclick="toggleTaskStatusFromDetail(${t.id}, '${t.status}', ${ambition.id})"></div>
                <div style="flex:1; display:flex; align-items:center; gap:0.5rem; flex-wrap:wrap;">
                    <span style="${t.status === 'done' ? 'text-decoration: line-through; color: var(--text-muted);' : ''}">${t.title}</span>
                    ${t.status === 'done' ? '<span class="badge success">Finalised</span>' : ''}
                    ${renderMonitoringBadge(t)}
                    ${t.status === 'archived' ? '<span class="archived-badge">Archived</span>' : ''}
                    ${renderDueDateBadge(t, ambition.id)}
                    ${renderTodoistLinkBadge(t)}
                    ${renderTodoistUrgentBadge(t)}
                </div>
                <div class="text-muted" style="font-size: 0.78rem;">${t.estimated_time > 0 ? `${t.estimated_time}m • ` : ''}${t.energy_level}</div>
                <div style="display: flex; align-items: center; gap: 0.15rem;">
                    <button class="btn-icon ${isMonitoring ? 'active-monitor' : ''}" onclick="toggleTaskMonitor(${t.id}, '${t.status}', ${ambition.id})" title="${isMonitoring ? 'Switch back to Next Action (To Do)' : 'Change status to Monitoring'}">
                        <i class="fas fa-eye" style="font-size: 0.8rem;"></i>
                    </button>
                    <button class="btn-icon" onclick="openSnoozeModal(${t.id}, '${dueVal}', ${ambition.id})" title="Snooze / Set Due Date">
                        <i class="fas fa-clock" style="font-size: 0.8rem; ${dueVal ? 'color: #4f46e5;' : ''}"></i>
                    </button>
                    <button class="btn-icon" onclick="openTaskEditModal(${t.id}, ${ambition.id})" title="Edit Task">
                        <i class="fas fa-pen-to-square" style="font-size: 0.8rem;"></i>
                    </button>
                    <button class="btn-icon btn-danger-icon" onclick="deleteTask(${t.id}, ${ambition.id})" title="Delete Task">
                        <i class="fas fa-trash-can" style="font-size: 0.8rem;"></i>
                    </button>
                </div>
            </div>
            `;
        }).join('');

        document.getElementById('edit-ambition-btn').onclick = (e) => {
            e.stopPropagation();
            openHorizonModal('ambition', ambition.id);
        };

        const removeAmbitionBtn = document.getElementById('remove-ambition-btn');
        if (removeAmbitionBtn) {
            removeAmbitionBtn.onclick = (e) => {
                e.stopPropagation();
                openProjectRemoveModal(ambition.id);
            };
        }

        // Selection highlight
        document.querySelectorAll('#ambitions-list .horizon-card').forEach(c => c.classList.remove('active'));
        const activeCard = Array.from(document.querySelectorAll('#ambitions-list .horizon-card'))
            .find(c => c.innerHTML.includes(ambition.outcome));
        if (activeCard) activeCard.classList.add('active');

        if (window.innerWidth <= 768) {
            detailPane.scrollIntoView({ behavior: 'smooth' });
        }
    };

    window.toggleTaskStatusFromDetail = async (taskId, currentStatus, ambitionId) => {
        const newStatus = currentStatus === 'done' ? 'todo' : 'done';
        await apiFetch(`/tasks/${taskId}/status?status=${newStatus}`, { method: 'PATCH' });
        await fetchHorizons();
        showAmbitionDetail(ambitionId);
    };

    document.querySelector('.close-detail').onclick = () => {
        document.getElementById('ambition-detail').style.display = 'none';
    };

    const renderRoleThemePicker = (selectedThemeKey = 'frozen', customColor = null) => {
        const grid = document.getElementById('role-theme-grid');
        const themeInput = document.getElementById('role-theme-key');
        const colorInput = document.getElementById('role-color-input');
        const hexDisplay = document.getElementById('role-color-hex-display');
        if (!grid || !window.ROLE_THEMES) return;

        const chosenTheme = window.getRoleTheme(selectedThemeKey);
        const activeKey = chosenTheme.key;
        const activeColor = customColor || chosenTheme.color;

        if (themeInput) themeInput.value = activeKey;
        if (colorInput) {
            colorInput.value = activeColor;
            colorInput.oninput = () => {
                if (hexDisplay) hexDisplay.innerText = colorInput.value;
            };
        }
        if (hexDisplay) hexDisplay.innerText = activeColor;

        grid.innerHTML = window.ROLE_THEMES.map(t => {
            const bgUri = window.getRoleThemeDataUri(t.key);
            const isSel = t.key === activeKey;
            return `
                <div class="role-theme-option ${isSel ? 'selected' : ''}"
                     style="border-color: ${isSel ? t.color : '#e2e8f0'};"
                     onclick="selectRoleThemeOption('${t.key}')">
                    <div class="role-card-bg" style="background-image: url('${bgUri}'); opacity: 0.78;"></div>
                    <div class="role-card-veil" style="background: linear-gradient(90deg, rgba(255,255,255,0.75) 0%, rgba(255,255,255,0.18) 100%);"></div>
                    <div style="position: relative; z-index: 2; display: flex; justify-content: space-between; align-items: flex-start;">
                        <span style="font-size: 0.75rem; font-weight: 700; color: #0f172a; text-shadow: 0 1px 2px rgba(255,255,255,0.95); line-height: 1.15;">${t.title}</span>
                        <span style="width: 12px; height: 12px; border-radius: 50%; background: ${t.color}; border: 1.5px solid #fff; box-shadow: 0 1px 2px rgba(0,0,0,0.25); flex-shrink: 0;"></span>
                    </div>
                    <div style="position: relative; z-index: 2; font-size: 0.65rem; font-weight: 700; color: #1e293b; text-shadow: 0 1px 2px rgba(255,255,255,0.95); margin-top: 0.25rem;">
                        ${t.subtitle}
                    </div>
                </div>
            `;
        }).join('');
    };

    window.selectRoleThemeOption = (themeKey) => {
        const theme = window.getRoleTheme(themeKey);
        renderRoleThemePicker(theme.key, theme.color);
    };

    window.openHorizonModal = async (type, id = null) => {
        resetHorizonModal();
        document.getElementById('horizon-type').value = type;
        document.getElementById('horizon-id').value = id || "";
        document.getElementById('horizon-modal-title').innerText = id ? `Edit ${type}` : `Add ${type}`;
        document.getElementById('horizon-label').innerText = type === 'role' ? 'Role Name' : 'Ambition Outcome';
        
        document.getElementById('role-extra-fields').style.display = type === 'role' ? 'block' : 'none';
        document.getElementById('ambition-extra-fields').style.display = type === 'ambition' ? 'block' : 'none';
        
        await fetchRoles();

        if (id) {
            const item = type === 'role' ? currentRoles.find(r => r.id === id) : currentAmbitions.find(a => a.id === id);
            if (item) {
                document.getElementById('horizon-name').value = type === 'role' ? item.name : item.outcome;
                if (type === 'role') {
                    document.getElementById('role-description').value = item.description || "";
                    renderRoleThemePicker(item.theme_key || 'frozen', item.color || null);
                } else {
                    document.getElementById('ambition-role-select').value = item.role_id || "";
                    document.getElementById('ambition-status-select').value = item.status || "active";
                    const prioInput = document.getElementById('ambition-priority-input');
                    if (prioInput) prioInput.value = item.priority || "";
                }
            }
            document.getElementById('horizon-delete-btn').style.display = 'block';
        } else {
            if (type === 'role') {
                const nextTheme = window.ROLE_THEMES
                    ? window.ROLE_THEMES[(currentRoles.length || 0) % window.ROLE_THEMES.length]
                    : { key: 'frozen', color: '#0284c7' };
                renderRoleThemePicker(nextTheme.key, nextTheme.color);
            } else if (type === 'ambition') {
                const prioInput = document.getElementById('ambition-priority-input');
                if (prioInput) prioInput.value = (currentAmbitions.length || 0) + 1;
            }
            document.getElementById('horizon-delete-btn').style.display = 'none';
        }
        
        horizonModal.classList.add('active');
    };

    const resetHorizonModal = () => {
        horizonForm.reset();
    };

    document.getElementById('add-role-btn').onclick = () => openHorizonModal('role');
    document.getElementById('add-ambition-btn').onclick = () => openHorizonModal('ambition');

    horizonForm.onsubmit = async (e) => {
        e.preventDefault();
        const type = document.getElementById('horizon-type').value;
        const id = document.getElementById('horizon-id').value;
        
        let url = type === 'role' ? '/roles' : '/ambitions';
        if (id) url += `/${id}`;
        
        const prioVal = document.getElementById('ambition-priority-input')
            ? parseInt(document.getElementById('ambition-priority-input').value)
            : NaN;

        const data = type === 'role' ? {
            name: document.getElementById('horizon-name').value,
            description: document.getElementById('role-description').value,
            color: document.getElementById('role-color-input') ? document.getElementById('role-color-input').value : '#0284c7',
            theme_key: document.getElementById('role-theme-key') ? document.getElementById('role-theme-key').value : 'frozen'
        } : {
            outcome: document.getElementById('horizon-name').value,
            h2_id: parseInt(document.getElementById('ambition-role-select').value) || null,
            status: document.getElementById('ambition-status-select').value,
            priority: !isNaN(prioVal) && prioVal >= 1 ? prioVal : null
        };

        const res = await apiFetch(url, {
            method: id ? 'PUT' : 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (res) {
            horizonModal.classList.remove('active');
            showToast(id ? `Updated ${type}!` : `Added new ${type}!`, 'success');
            await Promise.all([fetchRoles(), fetchAmbitions('active')]);

            if (clarifyModal.classList.contains('active')) {
                if (type === 'role' && res.id) {
                    document.getElementById('clarify-role').value = String(res.id);
                    filterClarifyAmbitionsByRole(res.id, "");
                } else if (type === 'ambition' && res.id) {
                    const roleVal = res.h2_id ? String(res.h2_id) : (document.getElementById('clarify-role').value || "");
                    document.getElementById('clarify-role').value = roleVal;
                    filterClarifyAmbitionsByRole(roleVal, res.id);
                }
            }

            if (currentTab === 'review') {
                loadReviewAreas();
            } else if (currentTab === 'projects') {
                fetchHorizons();
            }
        }
    };

    document.getElementById('horizon-delete-btn').onclick = async () => {
        const type = document.getElementById('horizon-type').value;
        const id = document.getElementById('horizon-id').value;
        if (type === 'ambition') {
            horizonModal.classList.remove('active');
            openProjectRemoveModal(parseInt(id));
            return;
        }
        if (confirm(`Delete this ${type}?`)) {
            await apiFetch(`/roles/${id}`, { method: 'DELETE' });
            horizonModal.classList.remove('active');
            fetchHorizons();
        }
    };

    window.openProjectRemoveModal = (ambitionId) => {
        const ambition = currentAmbitions.find(a => a.id === ambitionId);
        if (!ambition) return;

        const taskCount = (ambition.todo_count || 0) + (ambition.done_count || 0) + (ambition.archived_count || 0);
        document.getElementById('remove-project-id').value = ambition.id;
        document.getElementById('remove-project-message').innerText =
            `Are you sure you want to remove "${ambition.outcome}" (${taskCount} related task${taskCount === 1 ? '' : 's'})?`;

        const archiveBtn = document.getElementById('confirm-archive-project-btn');
        if (archiveBtn) {
            archiveBtn.style.display = ambition.status === 'archived' ? 'none' : 'inline-block';
        }

        projectRemoveModal.classList.add('active');
    };

    document.getElementById('cancel-remove-project-btn').onclick = () => {
        projectRemoveModal.classList.remove('active');
    };

    document.getElementById('confirm-archive-project-btn').onclick = async () => {
        const id = document.getElementById('remove-project-id').value;
        if (!id) return;
        const res = await apiFetch(`/ambitions/${id}/archive`, { method: 'POST' });
        if (res) {
            projectRemoveModal.classList.remove('active');
            document.getElementById('ambition-detail').style.display = 'none';
            fetchHorizons();
        }
    };

    document.getElementById('confirm-delete-project-btn').onclick = async () => {
        const id = document.getElementById('remove-project-id').value;
        if (!id) return;
        const res = await apiFetch(`/ambitions/${id}`, { method: 'DELETE' });
        if (res) {
            projectRemoveModal.classList.remove('active');
            document.getElementById('ambition-detail').style.display = 'none';
            fetchHorizons();
        }
    };

    // --- Weekly Review Wizard ---
    let reviewStep = 1;
    let reviewStats = { captured: 0, actions: 0, projects: 0 };

    const initReviewWizard = async () => {
        reviewStep = 1;
        reviewStats = { captured: 0, actions: 0, projects: 0 };
        const last = await apiFetch('/review/last');
        document.getElementById('last-review-date').innerText = last && last.timestamp ? 
            `Last review: ${new Date(last.timestamp).toLocaleString()}` : 'No previous reviews recorded.';
        updateWizardUI();
    };

    const updateWizardUI = () => {
        document.querySelectorAll('.wizard-pane').forEach(p => p.classList.remove('active'));
        document.getElementById(`step-${reviewStep}`).classList.add('active');
        
        document.querySelectorAll('.wizard-steps .step').forEach(s => {
            s.classList.remove('active');
            if (parseInt(s.getAttribute('data-step')) === reviewStep) s.classList.add('active');
        });

        document.getElementById('prev-step').style.visibility = reviewStep === 1 ? 'hidden' : 'visible';
        document.getElementById('next-step').innerText = reviewStep === 4 ? 'Complete' : 'Next Step';
        if (reviewStep === 4) document.getElementById('next-step').style.display = 'none';
        else document.getElementById('next-step').style.display = 'block';

        if (reviewStep === 2) loadReviewProjects();
        if (reviewStep === 3) loadReviewAreas();
        if (reviewStep === 4) renderReviewSummary();
    };

    document.getElementById('next-step').onclick = () => {
        if (reviewStep < 4) {
            reviewStep++;
            updateWizardUI();
        }
    };

    document.getElementById('prev-step').onclick = () => {
        if (reviewStep > 1) {
            reviewStep--;
            updateWizardUI();
        }
    };

    const loadReviewProjects = async () => {
        const [ambitions, allTasks, staleTasks] = await Promise.all([
            apiFetch('/ambitions?status=active'),
            apiFetch('/tasks'),
            apiFetch('/review/stale-todoist-tasks', { silent: true })
        ]);

        // Render Idea #10: Stale Todoist tasks (>14 days)
        const staleBox = document.getElementById('review-stale-todoist-box');
        if (staleBox) {
            if (staleTasks && staleTasks.length > 0) {
                staleBox.style.display = 'block';
                staleBox.innerHTML = `
                    <div class="stale-alert-box">
                        <div style="font-weight: 700; margin-bottom: 0.4rem;"><i class="fas fa-triangle-exclamation"></i> Stale in Todoist (&gt;14 Days Old)</div>
                        <div style="font-size: 0.85rem; margin-bottom: 0.5rem;">These tasks have been sitting in your Todoist execution list for over 2 weeks. Consider renegotiating or completing them:</div>
                        <ul style="padding-left: 1.25rem; font-size: 0.85rem;">
                            ${staleTasks.map(st => `<li><strong>${st.title}</strong> ${st.ambition_outcome ? `(${st.ambition_outcome})` : ''}</li>`).join('')}
                        </ul>
                    </div>
                `;
            } else {
                staleBox.style.display = 'none';
            }
        }

        const list = document.getElementById('review-projects-list');
        if (!ambitions) return;
        list.innerHTML = ambitions.map(a => {
            const projTasks = (allTasks || []).filter(t => t.ambition_id === a.id && t.status === 'todo');
            return `
                <div class="inbox-card" style="flex-direction: column; align-items: stretch; gap: 0.75rem; cursor: default;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div class="item-text" style="font-weight: 600;">${a.outcome} ${a.todoist_label_name ? `<span class="todoist-badge"><i class="fas fa-tag"></i> @${a.todoist_label_name}</span>` : ''}</div>
                            <div class="item-meta">${a.todo_count > 0 ? `<span style="color:green;">${a.todo_count} next actions</span>` : `<span style="color:red;">MISSING NEXT ACTION</span>`}</div>
                        </div>
                        <button class="clarify-btn" onclick="openReviewAddTask(${a.id})">Add Action</button>
                    </div>
                    ${projTasks.length > 0 ? `
                        <div style="border-top: 1px solid var(--border); padding-top: 0.5rem; display: flex; flex-direction: column; gap: 0.35rem;">
                            ${projTasks.map(pt => `
                                <label style="display: flex; align-items: center; gap: 0.5rem; font-size: 0.875rem; cursor: pointer;">
                                    <input type="checkbox" class="review-commit-checkbox" value="${pt.id}" ${pt.todoist_task_id ? 'disabled' : ''}>
                                    <span>${pt.title}</span>
                                    ${renderTodoistLinkBadge(pt)}
                                </label>
                            `).join('')}
                        </div>
                    ` : ''}
                </div>
            `;
        }).join('');
    };

    const reviewBatchPushBtn = document.getElementById('review-batch-push-btn');
    if (reviewBatchPushBtn) {
        reviewBatchPushBtn.onclick = async () => {
            const checked = Array.from(document.querySelectorAll('.review-commit-checkbox:checked')).map(cb => parseInt(cb.value));
            if (checked.length === 0) {
                showToast('Select at least one unsynced Next Action to push to Todoist.', 'error');
                return;
            }
            const res = await apiFetch('/tasks/batch-push-todoist', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ task_ids: checked })
            });
            if (res) {
                reviewStats.actions += res.pushed_count || 0;
                showToast(`Committed ${res.pushed_count} task(s) to Todoist for this week!`, 'success');
                loadReviewProjects();
            }
        };
    }

    window.openReviewAddTask = async (ambitionId) => {
        await resetClarifyModal();
        const amb = (currentAmbitions || []).find(a => a.id === ambitionId);
        const roleId = amb && amb.role_id ? String(amb.role_id) : "";
        document.getElementById('clarify-role').value = roleId;
        filterClarifyAmbitionsByRole(roleId, ambitionId);
        clarifyModal.classList.add('active');
    };

    const loadReviewAreas = async () => {
        const summary = await apiFetch('/review/roles-summary');
        const list = document.getElementById('review-roles-list');
        list.innerHTML = summary.map(item => `
            <div class="inbox-card">
                <div>
                    <div class="item-text">${item.role.name}</div>
                    <div class="item-meta">${item.count > 0 ? `${item.count} active projects` : `<span style="color:red;">STAGNANT</span>`}</div>
                </div>
                <button class="clarify-btn" onclick="openReviewAddAmbition(${item.role.id})">Add Project</button>
            </div>
        `).join('');
    };

    window.openReviewAddAmbition = (roleId) => {
        openHorizonModal('ambition');
        document.getElementById('ambition-role-select').value = roleId;
    };

    const renderReviewSummary = () => {
        document.getElementById('review-summary').innerHTML = `
            <p><strong>Review Summary:</strong></p>
            <ul>
                <li>Items Captured: ${reviewStats.captured}</li>
                <li>Actions Committed to Todoist: ${reviewStats.actions}</li>
            </ul>
        `;
    };

    document.getElementById('complete-review-btn').onclick = async () => {
        await apiFetch('/review/complete', { method: 'POST' });
        alert('Weekly Review Recorded!');
        switchTab('tasks');
    };

    document.getElementById('review-capture').addEventListener('keydown', async (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            const text = e.target.value.trim();
            if (text) {
                await apiFetch('/capture', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text, source: 'review' })
                });
                reviewStats.captured++;
                document.getElementById('review-capture-feedback').innerText = `Captured: ${text}`;
                e.target.value = '';
            }
        }
    });

    // --- Todoist Settings & Mapping Tab ---
    let todoistMappingsData = null;

    const loadTodoistTab = async () => {
        await fetchConfig();
        const data = await apiFetch('/todoist/mappings');
        if (!data) return;
        todoistMappingsData = data;

        const statusBadge = document.getElementById('todoist-token-status');
        const lastSyncInfo = document.getElementById('todoist-last-sync-info');

        if (data.configured) {
            statusBadge.className = 'badge success';
            statusBadge.innerText = `Configured (${todoistMaskedToken})`;
        } else {
            statusBadge.className = 'badge warning';
            statusBadge.innerText = 'Not Configured';
        }

        if (lastTodoistSync) {
            lastSyncInfo.innerText = `Last synced: ${new Date(lastTodoistSync).toLocaleString()}`;
        } else {
            lastSyncInfo.innerText = 'Not synced yet.';
        }

        if (data.remote_error) {
            lastSyncInfo.innerText += ` • Remote warning: ${data.remote_error}`;
        }

        renderTodoistRoleMappings(data.roles || [], data.remote_projects || []);
        renderTodoistAmbitionMappings(data.ambitions || [], data.remote_labels || []);
    };

    const saveTodoistTokenBtn = document.getElementById('save-todoist-token-btn');
    if (saveTodoistTokenBtn) {
        saveTodoistTokenBtn.onclick = async () => {
            const input = document.getElementById('todoist-token-input');
            const token = input.value.trim();
            if (!token) {
                showToast('Please paste your Todoist API token in the input field before clicking Save Token.', 'error', 6000);
                return;
            }
            const origText = saveTodoistTokenBtn.innerHTML;
            saveTodoistTokenBtn.disabled = true;
            saveTodoistTokenBtn.innerHTML = `<i class="fas fa-spinner fa-spin"></i> Saving...`;

            const res = await apiFetch('/todoist/settings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ token })
            });

            saveTodoistTokenBtn.disabled = false;
            saveTodoistTokenBtn.innerHTML = origText;

            if (res) {
                input.value = '';
                todoistEnabled = res.configured;
                todoistMaskedToken = res.masked_token;
                await loadTodoistTab();
                if (res.connection_ok) {
                    showToast(res.message || 'Todoist API token saved and verified!', 'success', 6500);
                } else {
                    showToast(res.message || 'Token saved locally, but could not verify connection with Todoist.', 'error', 9000);
                }
            }
        };
    }

    const renderTodoistRoleMappings = (roles, remoteProjects) => {
        const tbody = document.getElementById('todoist-roles-mapping-body');
        if (!tbody) return;
        if (roles.length === 0) {
            tbody.innerHTML = '<tr><td colspan="3" class="text-muted" style="text-align:center;">No Roles created yet.</td></tr>';
            return;
        }
        tbody.innerHTML = roles.map(role => {
            const options = `<option value="">-- Unmapped --</option>` +
                remoteProjects.map(p => `<option value="${p.id}" data-name="${p.name}" ${String(role.todoist_project_id) === String(p.id) ? 'selected' : ''}>${p.name}</option>`).join('') +
                (role.todoist_project_id && !remoteProjects.some(p => String(p.id) === String(role.todoist_project_id))
                    ? `<option value="${role.todoist_project_id}" data-name="${role.todoist_project_name || role.name}" selected>${role.todoist_project_name || role.todoist_project_id}</option>`
                    : '');

            return `
                <tr>
                    <td style="font-weight: 600;">${role.name}</td>
                    <td>
                        <select id="map-role-select-${role.id}" class="mapping-select">
                            ${options}
                        </select>
                    </td>
                    <td>
                        <div style="display: flex; gap: 0.4rem; flex-wrap: wrap;">
                            <button class="btn-primary" style="padding: 0.4rem 0.75rem; font-size: 0.75rem;" onclick="saveRoleMapping(${role.id}, false)">Save</button>
                            <button class="btn-secondary" style="padding: 0.4rem 0.75rem; font-size: 0.75rem;" onclick="saveRoleMapping(${role.id}, true)" title="Create a matching Project in Todoist">1-Click Create</button>
                        </div>
                    </td>
                </tr>
            `;
        }).join('');
    };

    window.saveRoleMapping = async (roleId, createNew = false) => {
        const select = document.getElementById(`map-role-select-${roleId}`);
        const selectedOpt = select ? select.options[select.selectedIndex] : null;
        const projId = select ? select.value : null;
        const projName = selectedOpt ? selectedOpt.getAttribute('data-name') : null;

        const res = await apiFetch('/todoist/mappings/role', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                role_id: roleId,
                todoist_project_id: projId || null,
                todoist_project_name: projName || null,
                create_new: createNew
            })
        });
        if (res) {
            await loadTodoistTab();
            showToast(
                createNew
                    ? `Created Todoist Project "${res.role.todoist_project_name}" and mapped it to Role "${res.role.name}".`
                    : `Updated Todoist mapping for Role "${res.role.name}".`,
                'success'
            );
        }
    };

    const renderTodoistAmbitionMappings = (ambitions, remoteLabels) => {
        const tbody = document.getElementById('todoist-ambitions-mapping-body');
        if (!tbody) return;
        if (ambitions.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="text-muted" style="text-align:center;">No active Projects (Ambitions) found.</td></tr>';
            return;
        }
        tbody.innerHTML = ambitions.map(amb => {
            const options = `<option value="">-- Unmapped --</option>` +
                remoteLabels.map(l => `<option value="${l.name}" data-id="${l.id}" ${(amb.todoist_label_name || '').toLowerCase() === l.name.toLowerCase() ? 'selected' : ''}>@${l.name}</option>`).join('') +
                (amb.todoist_label_name && !remoteLabels.some(l => l.name.toLowerCase() === amb.todoist_label_name.toLowerCase())
                    ? `<option value="${amb.todoist_label_name}" data-id="${amb.todoist_label_id || ''}" selected>@${amb.todoist_label_name}</option>`
                    : '');

            return `
                <tr>
                    <td style="font-weight: 600;">${amb.outcome}</td>
                    <td><span class="text-muted">${amb.role_name || '-'}</span></td>
                    <td>
                        <select id="map-ambition-select-${amb.id}" class="mapping-select">
                            ${options}
                        </select>
                    </td>
                    <td>
                        <div style="display: flex; gap: 0.4rem; flex-wrap: wrap;">
                            <button class="btn-primary" style="padding: 0.4rem 0.75rem; font-size: 0.75rem;" onclick="saveAmbitionMapping(${amb.id}, false)">Save</button>
                            <button class="btn-secondary" style="padding: 0.4rem 0.75rem; font-size: 0.75rem;" onclick="saveAmbitionMapping(${amb.id}, true)" title="Create a matching Label in Todoist">1-Click Create</button>
                        </div>
                    </td>
                </tr>
            `;
        }).join('');
    };

    window.saveAmbitionMapping = async (ambitionId, createNew = false) => {
        const select = document.getElementById(`map-ambition-select-${ambitionId}`);
        const selectedOpt = select ? select.options[select.selectedIndex] : null;
        const labelName = select ? select.value : null;
        const labelId = selectedOpt ? selectedOpt.getAttribute('data-id') : null;

        const res = await apiFetch('/todoist/mappings/ambition', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                ambition_id: ambitionId,
                todoist_label_id: labelId || null,
                todoist_label_name: labelName || null,
                create_new: createNew
            })
        });
        if (res) {
            await loadTodoistTab();
            showToast(
                createNew
                    ? `Created Todoist Label "@${res.ambition.todoist_label_name}" and mapped it to Project "${res.ambition.outcome}".`
                    : `Updated Todoist Label mapping for Project "${res.ambition.outcome}".`,
                'success'
            );
        }
    };

    // --- Modal Closing ---
    document.querySelectorAll('.close-modal').forEach(b => {
        b.onclick = () => {
            const parentModal = b.closest('.modal');
            if (parentModal) {
                parentModal.classList.remove('active');
            } else {
                clarifyModal.classList.remove('active');
                horizonModal.classList.remove('active');
                taskEditModal.classList.remove('active');
                if (projectRemoveModal) projectRemoveModal.classList.remove('active');
            }
        };
    });

    window.onclick = (e) => {
        if (e.target == clarifyModal) clarifyModal.classList.remove('active');
        if (e.target == horizonModal) horizonModal.classList.remove('active');
        if (e.target == taskEditModal) taskEditModal.classList.remove('active');
        if (projectRemoveModal && e.target == projectRemoveModal) projectRemoveModal.classList.remove('active');
    };

    // --- Initial Load ---
    fetchConfig().then(() => {
        fetchRecentItems();
        switchTab('followup'); // Default tab
    });
});
