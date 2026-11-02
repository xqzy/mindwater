document.addEventListener('DOMContentLoaded', () => {
    // --- State & Constants ---
    let currentInboxItems = [];
    let currentEmailItems = [];
    let currentRoles = [];
    let currentAmbitions = [];
    let currentTasks = [];
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
    const projectRemoveModal = document.getElementById('project-remove-modal');
    
    // Forms
    const clarifyForm = document.getElementById('clarify-form');
    const horizonForm = document.getElementById('horizon-form');
    const taskEditForm = document.getElementById('task-edit-form');

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
        select.innerHTML = `<option value="">${prompt}</option>` + 
            items.map(item => `<option value="${item[valueField]}">${item[textField]}</option>`).join('');
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
            updateSelectOptions('clarify-ambition', currentAmbitions, 'id', 'outcome', 'None (Standalone Task)');
            updateSelectOptions('edit-task-ambition', currentAmbitions, 'id', 'outcome', 'None (Standalone)');
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

    const resetClarifyModal = () => {
        clarifyForm.reset();
        document.getElementById('clarify-item-id').value = "";
        document.getElementById('clarify-email-id').value = "";
        document.getElementById('clarify-type').value = "task";
        document.getElementById('task-fields').style.display = 'block';
        document.querySelectorAll('.toggle-btn').forEach(b => b.classList.remove('active'));
        document.querySelector('.toggle-btn[data-type="task"]').classList.add('active');
        fetchRoles();
        fetchAmbitions('active');
    };

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
        const includeArchived = document.getElementById('filter-archived-tasks')?.checked || false;
        let url = `/tasks?`;
        if (role) url += `role_id=${role}&`;
        if (energy) url += `energy=${energy}&`;
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
        tbody.innerHTML = currentTasks.map(task => `
            <tr>
                <td><div class="status-circle ${task.status === 'done' ? 'done' : ''}" onclick="toggleTaskStatus(${task.id}, '${task.status}')"></div></td>
                <td>
                    <div style="font-weight: 500; display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
                        <span>${task.title}</span>
                        ${task.status === 'archived' ? '<span class="archived-badge">Archived</span>' : ''}
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
                        <button class="btn-icon" onclick="openTaskEditModal(${task.id})" title="Edit"><i class="fas fa-pen-to-square"></i></button>
                        ${todoistEnabled ? `<button class="btn-icon" onclick="pushToTodoist(${task.id})" title="${task.todoist_task_id ? 'Update in Todoist' : 'Push to Todoist'}"><i class="fas fa-share-from-square" style="${task.todoist_task_id ? 'color:#e11d48;' : ''}"></i></button>` : ''}
                    </div>
                </td>
            </tr>
        `).join('');
    };

    window.toggleTaskStatus = async (id, currentStatus) => {
        const newStatus = currentStatus === 'done' ? 'todo' : 'done';
        await apiFetch(`/tasks/${id}/status?status=${newStatus}`, { method: 'PATCH' });
        fetchTasks();
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
    const filterArchivedTasksEl = document.getElementById('filter-archived-tasks');
    if (filterArchivedTasksEl) filterArchivedTasksEl.onchange = fetchTasks;
    document.getElementById('clear-filters').onclick = () => {
        document.getElementById('filter-role').value = "";
        document.getElementById('filter-energy').value = "";
        if (filterArchivedTasksEl) filterArchivedTasksEl.checked = false;
        fetchTasks();
    };

    window.openTaskEditModal = async (id) => {
        const task = currentTasks.find(t => t.id === id);
        if (!task) return;
        
        await Promise.all([fetchRoles(), fetchAmbitions('active')]);
        
        document.getElementById('edit-task-id').value = task.id;
        document.getElementById('edit-task-title').value = task.title;
        document.getElementById('edit-task-energy').value = task.energy_level;
        document.getElementById('edit-task-time').value = task.estimated_time;
        document.getElementById('edit-task-contexts').value = task.context_tags ? task.context_tags.join(', ') : '';
        
        document.getElementById('edit-task-role').value = task.role_id || "";
        document.getElementById('edit-task-ambition').value = task.ambition_id || "";
        
        taskEditModal.classList.add('active');
    };

    taskEditForm.onsubmit = async (e) => {
        e.preventDefault();
        const id = document.getElementById('edit-task-id').value;
        const data = {
            title: document.getElementById('edit-task-title').value,
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
        fetchTasks();
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
        
        rolesHtml += currentRoles.map(role => `
            <div class="horizon-card role-card ${selectedRoleId === role.id ? 'active' : ''}" onclick="selectRole(${role.id})">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-weight: 600;">${role.name}</div>
                        ${role.todoist_project_name ? `<div class="text-muted" style="font-size:0.7rem;"><i class="fas fa-link"></i> ${role.todoist_project_name}</div>` : ''}
                    </div>
                    <button class="btn-icon" onclick="event.stopPropagation(); openHorizonModal('role', ${role.id})">
                        <i class="fas fa-gear" style="font-size: 0.75rem;"></i>
                    </button>
                </div>
            </div>
        `).join('');
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

        ambitionsList.innerHTML = filteredProjects.map(a => {
            const total = a.todo_count + a.done_count + (a.archived_count || 0);
            const percent = total > 0 ? Math.round((a.done_count / total) * 100) : 0;
            const isStalled = a.todo_count === 0 && a.status === 'active';
            const isArchived = a.status === 'archived';

            return `
                <div class="horizon-card project-card" onclick="showAmbitionDetail(${a.id})">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 0.5rem;">
                        <div>
                            <div class="card-title">${a.outcome}</div>
                            ${a.todoist_label_name ? `<span class="todoist-badge" style="margin-top:0.25rem;"><i class="fas fa-tag"></i> @${a.todoist_label_name}</span>` : ''}
                        </div>
                        ${isArchived ? '<span class="archived-badge">Archived</span>' : (isStalled ? '<span class="stalled-badge">Stalled</span>' : '')}
                    </div>
                    
                    <div style="margin-top: auto;">
                        <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 0.25rem;">
                            <span class="text-muted" style="font-size: 0.75rem;">${a.role_name}</span>
                            <span class="progress-text">${isArchived ? `${total} task${total === 1 ? '' : 's'} archived` : `${a.done_count}/${total} done`}</span>
                        </div>
                        <div class="progress-container">
                            <div class="progress-bar" style="width: ${percent}%"></div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
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

        document.getElementById('detail-stats').innerHTML = `
            <div class="stat-item"><div class="stat-value">${stats.total_hours}h</div><div class="stat-label">Spent</div></div>
            <div class="stat-item"><div class="stat-value">${stats.finished_2w}</div><div class="stat-label">Done (2w)</div></div>
            <div class="stat-item"><div class="stat-value">${stats.total_finished}</div><div class="stat-label">Total Done</div></div>
        `;

        document.getElementById('detail-tasks').innerHTML = tasks.map(t => `
            <div class="mini-task">
                <div class="status-circle ${t.status === 'done' ? 'done' : ''}" onclick="toggleTaskStatusFromDetail(${t.id}, '${t.status}', ${ambition.id})"></div>
                <div style="flex:1; display:flex; align-items:center; gap:0.5rem; flex-wrap:wrap;">
                    <span>${t.title}</span>
                    ${t.status === 'archived' ? '<span class="archived-badge">Archived</span>' : ''}
                    ${renderTodoistLinkBadge(t)}
                    ${renderTodoistUrgentBadge(t)}
                </div>
                <div class="text-muted">${t.estimated_time > 0 ? `${t.estimated_time}m • ` : ''}${t.energy_level}</div>
            </div>
        `).join('');

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
                if (type === 'role') document.getElementById('role-description').value = item.description || "";
                else {
                    document.getElementById('ambition-role-select').value = item.role_id || "";
                    document.getElementById('ambition-status-select').value = item.status || "active";
                }
            }
            document.getElementById('horizon-delete-btn').style.display = 'block';
        } else {
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
        
        const data = type === 'role' ? {
            name: document.getElementById('horizon-name').value,
            description: document.getElementById('role-description').value
        } : {
            outcome: document.getElementById('horizon-name').value,
            h2_id: parseInt(document.getElementById('ambition-role-select').value) || null,
            status: document.getElementById('ambition-status-select').value
        };

        const res = await apiFetch(url, {
            method: id ? 'PUT' : 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (res) {
            horizonModal.classList.remove('active');
            if (currentTab === 'review') {
                loadReviewAreas();
            } else {
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

    window.openReviewAddTask = (ambitionId) => {
        resetClarifyModal();
        document.getElementById('clarify-ambition').value = ambitionId;
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
            clarifyModal.classList.remove('active');
            horizonModal.classList.remove('active');
            taskEditModal.classList.remove('active');
            if (projectRemoveModal) projectRemoveModal.classList.remove('active');
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
