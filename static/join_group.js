document.addEventListener('DOMContentLoaded', function() {
    const user = JSON.parse(localStorage.getItem('user') || 'null');
    if (!user) {
        window.location.href = '/login';
        return;
    }
    const groupSelect = document.getElementById('group');
    groupSelect.disabled = true;
    const form = document.getElementById('joinGroupForm');
    const msgDiv = document.getElementById('joinGroupMsg');
    const nameInput = document.getElementById('name');
    nameInput.value = user.name || '';
    nameInput.readOnly = true;

    // Skeleton for user's groups
    const userGroupsList = document.getElementById('userGroupsList');
    userGroupsList.innerHTML = '<li class="list-group-item"><div class="skeleton" style="height:18px"></div></li>';

    // Fetch groups for joining
    fetch('/api/groups', { cache: 'no-store' })
        .then(res => res.ok ? res.json() : res.json().then(e => Promise.reject(e)))
        .then(groups => {
            if (!Array.isArray(groups) || groups.length === 0) {
                groupSelect.innerHTML = '<option value="">No groups available yet</option>';
                groupSelect.disabled = true;
                return;
            }
            groupSelect.innerHTML = '<option value="">Select a group</option>';
            groups.forEach(g => {
                groupSelect.innerHTML += `<option value="${g.id}">${g.name} (₹${g.contribution_amount}, ${g.cycle})</option>`;
            });
            groupSelect.disabled = false;
        })
        .catch(() => {
            groupSelect.innerHTML = '<option value="">Failed to load groups</option>';
            groupSelect.disabled = true;
        });

    // Fetch user's groups and display
    fetch(`/api/groups/user?phone=${encodeURIComponent(user.phone)}`, { cache: 'no-store' })
        .then(res => res.json())
        .then(groups => {
            userGroupsList.innerHTML = '';
            if (!groups.length) {
                userGroupsList.innerHTML = '<li class="list-group-item list-empty">You are not part of any groups yet.</li>';
            } else {
                groups.forEach(g => {
                    userGroupsList.innerHTML += `<li class="list-group-item d-flex justify-content-between align-items-center">
                        <span>${g.name} (₹${g.contribution_amount}, ${g.cycle})</span>
                        <span class="status-chip status-approved"><i class="bi bi-people"></i> Member</span>
                    </li>`;
                });
            }
        })
        .catch(() => {
            userGroupsList.innerHTML = '<li class="list-group-item text-danger">Failed to load your groups.</li>';
        });

    // Handle form submit
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        msgDiv.textContent = '';
        const data = {
            group_id: groupSelect.value,
            phone: user.phone
        };
        fetch('/api/groups/join', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        })
        .then(res => res.ok ? res.json() : res.json().then(e => Promise.reject(e)))
        .then(() => {
            msgDiv.innerHTML = '<div class="alert alert-success">Successfully joined group!</div>';
            // Refresh user's groups list
            fetch(`/api/groups/user?phone=${encodeURIComponent(user.phone)}`)
                .then(res => res.json())
                .then(groups => {
                    userGroupsList.innerHTML = '';
                    if (!groups.length) {
                        userGroupsList.innerHTML = '<li class="list-group-item">You are not part of any groups yet.</li>';
                    } else {
                        groups.forEach(g => {
                            userGroupsList.innerHTML += `<li class="list-group-item">${g.name} (₹${g.contribution_amount}, ${g.cycle})</li>`;
                        });
                    }
                })
                .catch(() => {
                    userGroupsList.innerHTML = '<li class="list-group-item text-danger">Failed to load your groups.</li>';
                });
        })
        .catch(err => {
            msgDiv.innerHTML = `<div class="alert alert-danger">${err.detail || 'Failed to join group.'}</div>`;
        });
    });
}); 