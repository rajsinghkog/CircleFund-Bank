function initJoinGroup(){
    // Safely parse stored user (handle 'undefined'/'null' strings)
    function getStoredUser(){
        try {
            const raw = localStorage.getItem('user');
            if (!raw || raw === 'undefined' || raw === 'null') {
                if (raw === 'undefined' || raw === 'null') localStorage.removeItem('user');
                return null;
            }
            return JSON.parse(raw);
        } catch (_) {
            localStorage.removeItem('user');
            return null;
        }
    }
    const user = getStoredUser();
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

    // Fetch groups for joining with a timeout safeguard
    (function loadGroupsWithTimeout(){
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 8000);
        fetch('/api/groups', { cache: 'no-store', signal: controller.signal })
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
            .catch((err) => {
                const isTimeout = err && (err.name === 'AbortError');
                groupSelect.innerHTML = `<option value="">${isTimeout ? 'Timed out loading groups' : 'Failed to load groups'}</option>`;
                groupSelect.disabled = true;
            })
            .finally(() => clearTimeout(timeoutId));
    })();

    // Fetch user's groups and display with timeout safeguard
    (function loadUserGroupsWithTimeout(){
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 8000);
        fetch(`/api/groups/user?phone=${encodeURIComponent(user.phone)}`, { cache: 'no-store', signal: controller.signal })
            .then(res => res.ok ? res.json() : res.json().then(e => Promise.reject(e)))
            .then(groups => {
                userGroupsList.innerHTML = '';
                if (!Array.isArray(groups) || !groups.length) {
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
            .catch((err) => {
                const isTimeout = err && (err.name === 'AbortError');
                userGroupsList.innerHTML = `<li class="list-group-item text-danger">${isTimeout ? 'Timed out loading your groups.' : 'Failed to load your groups.'}</li>`;
            })
            .finally(() => clearTimeout(timeoutId));
    })();

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
}

if (document.readyState !== 'loading') {
  initJoinGroup();
} else {
  document.addEventListener('DOMContentLoaded', initJoinGroup);
}