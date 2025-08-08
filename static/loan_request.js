document.addEventListener('DOMContentLoaded', function() {
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
    const form = document.getElementById('loanRequestForm');
    const msgDiv = document.getElementById('loanRequestMsg');
    const approvalsWrapId = 'myLoanApprovals';

    // Fetch groups
    fetch('/api/groups')
        .then(res => res.json())
        .then(groups => {
            groupSelect.innerHTML = '<option value="">Select a group</option>';
            groups.forEach(g => {
                groupSelect.innerHTML += `<option value="${g.id}">${g.name} (₹${g.contribution_amount}, ${g.cycle})</option>`;
            });
        })
        .catch(() => {
            groupSelect.innerHTML = '<option value="">Failed to load groups</option>';
        });

    // Handle form submit
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        msgDiv.textContent = '';
        const data = {
            amount: parseFloat(document.getElementById('amount').value),
            group_id: groupSelect.value
        };
        if (!data.group_id || !Number.isFinite(data.amount) || data.amount <= 0) {
            msgDiv.innerHTML = '<div class="alert alert-danger">Please select a group and enter a valid amount.</div>';
            return;
        }
        fetch('/api/loan/request', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ...data, phone: user.phone })
        })
        .then(res => res.ok ? res.json() : res.json().then(e => Promise.reject(e)))
        .then(() => {
            msgDiv.innerHTML = '<div class="alert alert-success">Loan request submitted!</div>';
        })
        .catch(err => {
            msgDiv.innerHTML = `<div class="alert alert-danger">${err.detail || 'Failed to request loan.'}</div>`;
        });
    });

    // Sidebar: My loan approvals with vote counts
    function renderMyApprovals(loans){
        let container = document.getElementById(approvalsWrapId);
        if (!container) {
            container = document.createElement('div');
            container.id = approvalsWrapId;
            container.className = 'card mt-4';
            container.innerHTML = '<div class="card-header"><h5 class="mb-0">My Loan Approvals</h5></div><div class="list-group list-group-flush" id="'+approvalsWrapId+'-list"></div>';
            form.parentElement.appendChild(container);
        }
        const list = document.getElementById(approvalsWrapId+'-list');
        if (!loans || loans.length === 0) {
            list.innerHTML = '<div class="list-group-item text-muted">No requests yet.</div>';
            return;
        }
        list.innerHTML = '';
        loans.forEach(l => {
            const statusChip = l.status === 'approved' ? '<span class="status-chip status-approved">Approved</span>' : l.status === 'pending' ? '<span class="status-chip status-pending">Pending</span>' : '<span class="status-chip status-rejected">Rejected</span>';
            list.innerHTML += `<div class="list-group-item d-flex justify-content-between align-items-center">
                <div>
                    <div><strong>${l.group_name || 'Group'}</strong> · ₹${Number(l.amount).toFixed(2)}</div>
                    <small class="text-muted">${new Date(l.created_at).toLocaleDateString()}</small>
                </div>
                <div class="text-end">
                    <div>${l.yes_votes || 0} / ${l.total_members || 0} approved</div>
                    ${statusChip}
                </div>
            </div>`;
        });
    }

    function loadMyApprovals(){
        fetch(`/api/loan/my?user_id=${user.id}`)
            .then(res => res.json())
            .then(renderMyApprovals)
            .catch(() => {/* ignore */});
    }

    loadMyApprovals();
}); 