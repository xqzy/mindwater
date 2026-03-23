document.addEventListener('DOMContentLoaded', () => {
    // --- State & Constants ---
    let currentInboxItems = [];
    let currentEmailItems = [];
    let currentRoles = [];
    let currentAmbitions = [];
    let currentTasks = [];
    let todoistEnabled = false;
    let currentTab = 'followup';
    let selectedRoleId = null;

    // --- Selectors ---
    const navItems = document.querySelectorAll('.nav-item');
    const tabContents = document.querySelectorAll('.tab-content');
    
    // Modals
    const clarifyModal = document.getElementById('clarify-modal');
    const horizonModal = document.getElementById('horizon-modal');
    const taskEditModal = document.getElementById('task-edit-modal');
    
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

    const switchTab = (tabName) => {
        currentTab = tabName;
        navItems.forEach(n => {
            n.classList.remove('active');
            if (n.getAttribute('data-tab') === tabName) n.classList.add('active');
        });

        tabContents.forEach(content => {
            content.classList.remove('active');
            if (content.id === tabName) content.classList.add('active');
        });

        // Refresh data for the active tab
        if (tabName === 'followup') fetchEmails();
        if (tabName === 'inbox') fetchFullInbox();
        if (tabName === 'tasks') fetchTasks();
        if (tabName === 'projects') fetchHorizons();
        if (tabName === 'review') initReviewWizard();
    };

    // --- Global Helpers ---
    const apiFetch = async (url, options = {}) => {
        try {
            const response = await fetch(url, options);
            if (!response.ok) throw new Error(`API Error: ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error(error);
            alert(`Error: ${error.message}`);
            return null;
        }
    };

    const updateSelectOptions = (selectId, items, valueField, textField, prompt = "Select...") => {
        const select = document.getElementById(selectId);
        if (!select) return;
        select.innerHTML = `<option value="">${prompt}</option>` + 
            items.map(item => `<option value="${item[valueField]}">${item[textField]}</option>`).join('');
    };

    // --- Data Fetching ---
    const fetchConfig = async () => {
        const config = await apiFetch('/config');
        if (config) todoistEnabled = config.todoist_enabled;
    };

    const fetchRoles = async () => {
        currentRoles = await apiFetch('/roles');
        updateSelectOptions('clarify-role', currentRoles, 'id', 'name', 'No specific role');
        updateSelectOptions('filter-role', currentRoles, 'id', 'name', 'All Roles');
        updateSelectOptions('ambition-role-select', currentRoles, 'id', 'name', 'Select Role...');
        updateSelectOptions('edit-task-role', currentRoles, 'id', 'name', 'No specific role');
    };

    const fetchAmbitions = async () => {
        currentAmbitions = await apiFetch('/ambitions');
        updateSelectOptions('clarify-ambition', currentAmbitions, 'id', 'outcome', 'None (Standalone Task)');
        updateSelectOptions('edit-task-ambition', currentAmbitions, 'id', 'outcome', 'None (Standalone)');
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
                    <div class="item-text">${item.raw_text}</div>
                    <div class="item-meta">${new Date(item.timestamp).toLocaleString()}</div>
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
        document.getElementById('clarify-modal-title').innerText = "Clarify Inbox Item";
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
        fetchAmbitions();
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
        let url = `/tasks?`;
        if (role) url += `role_id=${role}&`;
        if (energy) url += `energy=${energy}&`;
        
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
                <td><div style="font-weight: 500;">${task.title}</div><div class="item-meta">${task.ambition ? task.ambition.outcome : ''}</div></td>
                <td><span class="text-muted">${task.role ? task.role.name : '-'}</span></td>
                <td>${task.context_tags ? task.context_tags.map(c => `<small class="text-muted">${c}</small>`).join(' ') : ''}</td>
                <td>
                    <div style="display: flex; gap: 0.25rem;">
                        <button class="btn-icon" onclick="openTaskEditModal(${task.id})" title="Edit"><i class="fas fa-pen-to-square"></i></button>
                        ${todoistEnabled ? `<button class="btn-icon" onclick="pushToTodoist(${task.id})" title="Push to Todoist"><i class="fas fa-share-from-square"></i></button>` : ''}
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
        if (res) alert('Pushed to Todoist!');
    };

    document.getElementById('filter-role').onchange = fetchTasks;
    document.getElementById('filter-energy').onchange = fetchTasks;
    document.getElementById('clear-filters').onclick = () => {
        document.getElementById('filter-role').value = "";
        document.getElementById('filter-energy').value = "";
        fetchTasks();
    };

    window.openTaskEditModal = async (id) => {
        const task = currentTasks.find(t => t.id === id);
        if (!task) return;
        
        await Promise.all([fetchRoles(), fetchAmbitions()]);
        
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
                    <div style="font-weight: 600;">${role.name}</div>
                    <button class="btn-icon" onclick="event.stopPropagation(); openHorizonModal('role', ${role.id})">
                        <i class="fas fa-gear" style="font-size: 0.75rem;"></i>
                    </button>
                </div>
            </div>
        `).join('');
        rolesList.innerHTML = rolesHtml;

        // Filter and Render Projects
        const filteredProjects = selectedRoleId 
            ? currentAmbitions.filter(a => a.role_id === selectedRoleId)
            : currentAmbitions;

        if (filteredProjects.length === 0) {
            ambitionsList.innerHTML = '<div class="text-muted" style="grid-column: 1/-1; text-align: center; padding: 2rem;">No projects found for this role.</div>';
            return;
        }

        ambitionsList.innerHTML = filteredProjects.map(a => {
            const total = a.todo_count + a.done_count;
            const percent = total > 0 ? Math.round((a.done_count / total) * 100) : 0;
            const isStalled = a.todo_count === 0 && a.status === 'active';

            return `
                <div class="horizon-card project-card" onclick="showAmbitionDetail(${a.id})">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div class="card-title">${a.outcome}</div>
                        ${isStalled ? '<span class="stalled-badge">Stalled</span>' : ''}
                    </div>
                    
                    <div style="margin-top: auto;">
                        <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 0.25rem;">
                            <span class="text-muted" style="font-size: 0.75rem;">${a.role_name}</span>
                            <span class="progress-text">${a.done_count}/${total} done</span>
                        </div>
                        <div class="progress-container">
                            <div class="progress-bar" style="width: ${percent}%"></div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    };

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
                <div class="status-circle ${t.status === 'done' ? 'done' : ''}"></div>
                <div style="flex:1;">${t.title}</div>
                <div class="text-muted">${t.energy_level}</div>
            </div>
        `).join('');

        document.getElementById('edit-ambition-btn').onclick = (e) => {
            e.stopPropagation();
            openHorizonModal('ambition', ambition.id);
        };

        // Selection highlight
        document.querySelectorAll('#ambitions-list .horizon-card').forEach(c => c.classList.remove('active'));
        const activeCard = Array.from(document.querySelectorAll('#ambitions-list .horizon-card'))
            .find(c => c.innerHTML.includes(ambition.outcome)); // Simple check
        if (activeCard) activeCard.classList.add('active');

        // Scroll detail into view if on mobile
        if (window.innerWidth <= 768) {
            detailPane.scrollIntoView({ behavior: 'smooth' });
        }
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
        
        await fetchRoles(); // ensure roles are loaded for the select

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
        if (confirm(`Delete this ${type}?`)) {
            await apiFetch(type === 'role' ? `/roles/${id}` : `/ambitions/${id}`, { method: 'DELETE' });
            horizonModal.classList.remove('active');
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
        document.getElementById('last-review-date').innerText = last.timestamp ? 
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
        const ambitions = await apiFetch('/ambitions');
        const list = document.getElementById('review-projects-list');
        list.innerHTML = ambitions.map(a => `
            <div class="inbox-card">
                <div>
                    <div class="item-text">${a.outcome}</div>
                    <div class="item-meta">${a.todo_count > 0 ? `<span style="color:green;">${a.todo_count} next actions</span>` : `<span style="color:red;">MISSING NEXT ACTION</span>`}</div>
                </div>
                <button class="clarify-btn" onclick="openReviewAddTask(${a.id})">Add Action</button>
            </div>
        `).join('');
    };

    window.openReviewAddTask = (ambitionId) => {
        resetClarifyModal();
        document.getElementById('clarify-ambition').value = ambitionId;
        clarifyModal.classList.add('active');
        // Override onsubmit for review context if needed, or just let it refresh the current view
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

    // --- Modal Closing ---
    document.querySelectorAll('.close-modal').forEach(b => {
        b.onclick = () => {
            clarifyModal.classList.remove('active');
            horizonModal.classList.remove('active');
            taskEditModal.classList.remove('active');
        };
    });

    window.onclick = (e) => {
        if (e.target == clarifyModal) clarifyModal.classList.remove('active');
        if (e.target == horizonModal) horizonModal.classList.remove('active');
        if (e.target == taskEditModal) taskEditModal.classList.remove('active');
    };

    // --- Initial Load ---
    fetchConfig();
    fetchRecentItems();
    switchTab('followup'); // Default tab
});
