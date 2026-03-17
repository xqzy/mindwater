document.addEventListener('DOMContentLoaded', () => {
    const navItems = document.querySelectorAll('.nav-item');
    const tabContents = document.querySelectorAll('.tab-content');
    const captureInput = document.getElementById('capture-input');
    const captureBtn = document.getElementById('capture-btn');
    const recentItemsList = document.getElementById('recent-items');

    // Tab Switching
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const tabName = item.getAttribute('data-tab');

            // Toggle active state for nav items
            navItems.forEach(n => n.classList.remove('active'));
            item.classList.add('active');

            // Show current tab content
            tabContents.forEach(content => {
                content.classList.remove('active');
                if (content.id === tabName) {
                    content.classList.add('active');
                }
            });

            // If switching to inbox, fetch items (not implemented yet)
        });
    });

    // Capture Logic
    const captureTask = async () => {
        const text = captureInput.value.trim();
        if (!text) return;

        try {
            const response = await fetch('/capture', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text, source: 'web' })
            });

            if (response.ok) {
                captureInput.value = '';
                fetchRecentItems();
            } else {
                alert('Error capturing item.');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Could not connect to server.');
        }
    };

    captureBtn.addEventListener('click', captureTask);

    // Keyboard Shortcut (Ctrl+Enter or Cmd+Enter)
    captureInput.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            captureTask();
        }
    });

    // Fetch Recent Items
    const fetchRecentItems = async () => {
        try {
            const response = await fetch('/inbox?limit=5');
            const items = await response.json();
            
            recentItemsList.innerHTML = items.map(item => `
                <div class="inbox-item" data-id="${item.id}">
                    <div>
                        <div class="item-text">${item.raw_text}</div>
                        <div class="item-meta">${new Date(item.timestamp).toLocaleString()}</div>
                    </div>
                    <button class="delete-btn" onclick="deleteItem(${item.id})">
                        <i class="fas fa-trash-can"></i>
                    </button>
                </div>
            `).join('') || '<p style="color: var(--text-muted); text-align: center; margin-top: 2rem;">No recent captures.</p>';
        } catch (error) {
            console.error('Error:', error);
        }
    };

    // Global Delete Function (Exposed for inline onclick)
    window.deleteItem = async (id) => {
        if (!confirm('Are you sure you want to delete this?')) return;
        
        try {
            const response = await fetch(`/inbox/${id}`, { method: 'DELETE' });
            if (response.ok) {
                fetchRecentItems();
            }
        } catch (error) {
            console.error('Error:', error);
        }
    };

    // Initial Load
    fetchRecentItems();
});
