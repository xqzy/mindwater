document.addEventListener('DOMContentLoaded', () => {
    const navItems = document.querySelectorAll('.nav-item');
    const tabContents = document.querySelectorAll('.tab-content');
    
    // Elements for Capture
    const captureInput = document.getElementById('capture-input');
    const captureBtn = document.getElementById('capture-btn');
    const recentItemsList = document.getElementById('recent-items');

    // Elements for Inbox/Clarify
    const inboxListFull = document.getElementById('inbox-items-full');
    const modal = document.getElementById('clarify-modal');
    const closeModal = document.querySelector('.close-modal');
    const clarifyForm = document.getElementById('clarify-form');
    const taskFields = document.getElementById('task-fields');
    const toggleBtns = document.querySelectorAll('.toggle-btn');
    const clarifyType = document.getElementById('clarify-type');
    const roleSelect = document.getElementById('clarify-role');
    const ambitionSelect = document.getElementById('clarify-ambition');
    const deleteBtn = document.getElementById('clarify-delete-btn');

    let currentInboxItems = [];

    // --- Tab Switching ---
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const tabName = item.getAttribute('data-tab');

            navItems.forEach(n => n.classList.remove('active'));
            item.classList.add('active');

            tabContents.forEach(content => {
                content.classList.remove('active');
                if (content.id === tabName) {
                    content.classList.add('active');
                }
            });

            if (tabName === 'inbox') {
                fetchFullInbox();
            }
        });
    });

    // --- Data Fetching ---
    const fetchRoles = async () => {
        const response = await fetch('/roles');
        const roles = await response.json();
        roleSelect.innerHTML = '<option value="">No specific role</option>' + 
            roles.map(r => `<option value="${r.id}">${r.name}</option>`).join('');
    };

    const fetchAmbitions = async () => {
        const response = await fetch('/ambitions');
        const ambitions = await response.json();
        ambitionSelect.innerHTML = '<option value="">None (Standalone Task)</option>' + 
            ambitions.map(a => `<option value="${a.id}">${a.outcome}</option>`).join('');
    };

    const fetchRecentItems = async () => {
        try {
            const response = await fetch('/inbox?limit=5');
            const items = await response.json();
            recentItemsList.innerHTML = renderItems(items, false);
        } catch (error) { console.error(error); }
    };

    const fetchFullInbox = async () => {
        try {
            const response = await fetch('/inbox?limit=100');
            currentInboxItems = await response.json();
            inboxListFull.innerHTML = renderItems(currentInboxItems, true);
        } catch (error) { console.error(error); }
    };

    const renderItems = (items, isFull) => {
        if (items.length === 0) return '<p class="text-muted" style="text-align:center; padding: 2rem;">Inbox is empty!</p>';
        return items.map(item => `
            <div class="${isFull ? 'inbox-card' : 'inbox-item'}" onclick="${isFull ? `openClarifyModal(${item.id})` : ''}">
                <div>
                    <div class="item-text">${item.raw_text}</div>
                    <div class="item-meta">${new Date(item.timestamp).toLocaleString()}</div>
                </div>
                ${isFull ? '<button class="clarify-btn">Clarify</button>' : 
                `<button class="delete-btn" onclick="event.stopPropagation(); deleteItem(${item.id})"><i class="fas fa-trash-can"></i></button>`}
            </div>
        `).join('');
    };

    // --- Capture Logic ---
    const captureTask = async () => {
        const text = captureInput.value.trim();
        if (!text) return;
        const response = await fetch('/capture', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text, source: 'web' })
        });
        if (response.ok) {
            captureInput.value = '';
            fetchRecentItems();
        }
    };

    captureBtn.addEventListener('click', captureTask);
    captureInput.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') captureTask();
    });

    // --- Clarify Logic ---
    window.openClarifyModal = (itemId) => {
        const item = currentInboxItems.find(i => i.id === itemId);
        if (!item) return;

        document.getElementById('clarify-item-id').value = item.id;
        document.getElementById('clarify-title').value = item.raw_text;
        
        fetchRoles();
        fetchAmbitions();
        modal.classList.add('active');
    };

    closeModal.onclick = () => modal.classList.remove('active');
    window.onclick = (e) => { if (e.target == modal) modal.classList.remove('active'); };

    toggleBtns.forEach(btn => {
        btn.onclick = () => {
            toggleBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            const type = btn.getAttribute('data-type');
            clarifyType.value = type;
            taskFields.style.display = type === 'task' ? 'block' : 'none';
        };
    });

    clarifyForm.onsubmit = async (e) => {
        e.preventDefault();
        const id = document.getElementById('clarify-item-id').value;
        const data = {
            type: clarifyType.value,
            title: document.getElementById('clarify-title').value,
            role_id: document.getElementById('clarify-role').value || null,
            ambition_id: document.getElementById('clarify-ambition').value || null,
            energy_level: document.getElementById('clarify-energy').value,
            estimated_time: parseInt(document.getElementById('clarify-time').value) || 0,
            context_tags: document.getElementById('clarify-contexts').value.split(',').map(t => t.trim()).filter(t => t)
        };

        const response = await fetch(`/inbox/${id}/clarify`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            modal.classList.remove('active');
            fetchFullInbox();
        }
    };

    deleteBtn.onclick = async () => {
        const id = document.getElementById('clarify-item-id').value;
        if (confirm('Are you sure you want to delete this item?')) {
            const response = await fetch(`/inbox/${id}`, { method: 'DELETE' });
            if (response.ok) {
                modal.classList.remove('active');
                fetchFullInbox();
            }
        }
    };

    window.deleteItem = async (id) => {
        if (confirm('Delete this item?')) {
            await fetch(`/inbox/${id}`, { method: 'DELETE' });
            fetchRecentItems();
        }
    };

    // Initial Load
    fetchRecentItems();
});
