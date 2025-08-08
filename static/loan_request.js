document.addEventListener('DOMContentLoaded', function() {
    const user = JSON.parse(localStorage.getItem('user') || 'null');
    if (!user) {
        window.location.href = '/login';
        return;
    }
    const groupSelect = document.getElementById('group');
    const form = document.getElementById('loanRequestForm');
    const msgDiv = document.getElementById('loanRequestMsg');

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
            amount: document.getElementById('amount').value,
            group_id: groupSelect.value,
            user_id: user.id
        };
        fetch('/api/loan/request', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        })
        .then(res => res.ok ? res.json() : res.json().then(e => Promise.reject(e)))
        .then(() => {
            msgDiv.innerHTML = '<div class="alert alert-success">Loan request submitted!</div>';
        })
        .catch(err => {
            msgDiv.innerHTML = `<div class="alert alert-danger">${err.detail || 'Failed to request loan.'}</div>`;
        });
    });
}); 