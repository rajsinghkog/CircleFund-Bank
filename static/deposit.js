document.addEventListener('DOMContentLoaded', function() {
    const user = JSON.parse(localStorage.getItem('user') || 'null');
    if (!user) {
        window.location.href = '/login';
        return;
    }
    
    const groupSelect = document.getElementById('group');
    const form = document.getElementById('depositForm');
    const msgDiv = document.getElementById('depositMsg');
    const pendingDepositsContainer = document.getElementById('pendingDeposits');
    const amountInput = document.getElementById('amount');
    
    let groups = [];
    let pendingDeposits = [];

    // Format date to display
    function formatDate(dateString) {
        const options = { year: 'numeric', month: 'short', day: 'numeric' };
        return new Date(dateString).toLocaleDateString(undefined, options);
    }

    // Load pending deposits
    function loadPendingDeposits(groupId = null) {
        let url = `/api/deposit/pending?phone=${encodeURIComponent(user.phone)}`;
        if (groupId) {
            url += `&group_id=${groupId}`;
        }
        
        fetch(url)
            .then(res => res.json())
            .then(data => {
                if (data.error) {
                    throw new Error(data.error);
                }
                pendingDeposits = Array.isArray(data) ? data : [];
                renderPendingDeposits();
            })
            .catch(err => {
                console.error('Error loading pending deposits:', err);
                pendingDepositsContainer.innerHTML = `
                    <div class="alert alert-warning">
                        Failed to load pending deposits. ${err.message || ''}
                    </div>`;
            });
    }

    // Render pending deposits
    function renderPendingDeposits() {
        if (!pendingDeposits.length) {
            pendingDepositsContainer.innerHTML = `
                <div class="alert alert-info">No pending deposits found.</div>`;
            return;
        }

        let html = `
        <div class="card mb-4">
            <div class="card-header">
                <h5 class="mb-0">Pending Deposits</h5>
            </div>
            <div class="table-responsive">
                <table class="table table-hover mb-0">
                    <thead>
                        <tr>
                            <th>Group</th>
                            <th>Amount</th>
                            <th>Due Date</th>
                            <th>Status</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>`;

        pendingDeposits.forEach(deposit => {
            const isOverdue = deposit.is_overdue;
            const statusClass = isOverdue ? 'danger' : 'warning';
            const statusText = isOverdue ? 'Overdue' : 'Pending';
            
            html += `
                <tr class="${isOverdue ? 'table-danger' : ''}">
                    <td>${deposit.group_name}</td>
                    <td>₹${deposit.amount}</td>
                    <td>${formatDate(deposit.expected_date)}</td>
                    <td><span class="badge bg-${statusClass}">${statusText}</span></td>
                    <td>
                        <button class="btn btn-sm btn-primary pay-now" 
                                data-amount="${deposit.amount}" 
                                data-group-id="${deposit.group_id}"
                                data-expected-id="${deposit.id}">
                            Pay Now
                        </button>
                    </td>
                </tr>`;
        });

        html += `
                    </tbody>
                </table>
            </div>
        </div>`;

        pendingDepositsContainer.innerHTML = html;
        
        // Add event listeners to Pay Now buttons
        document.querySelectorAll('.pay-now').forEach(button => {
            button.addEventListener('click', function() {
                const amount = this.getAttribute('data-amount');
                const groupId = this.getAttribute('data-group-id');
                const expectedId = this.getAttribute('data-expected-id');
                
                // Set the form values
                groupSelect.value = groupId;
                amountInput.value = amount;
                
                // Add expected deposit ID to the form
                const existingInput = document.getElementById('expectedDepositId');
                if (existingInput) {
                    existingInput.value = expectedId;
                } else {
                    const input = document.createElement('input');
                    input.type = 'hidden';
                    input.id = 'expectedDepositId';
                    input.name = 'expected_deposit_id';
                    input.value = expectedId;
                    form.appendChild(input);
                }
                
                // Scroll to the form
                form.scrollIntoView({ behavior: 'smooth' });
            });
        });
    }

    // Fetch groups
    fetch('/api/groups')
        .then(res => res.json())
        .then(data => {
            groups = Array.isArray(data) ? data : [];
            groupSelect.innerHTML = '<option value="">Select a group</option>';
            groups.forEach(g => {
                groupSelect.innerHTML += `<option value="${g.id}">${g.name} (₹${g.contribution_amount}, ${g.cycle})</option>`;
            });
            
            // Load pending deposits for all groups initially
            loadPendingDeposits();
        })
        .catch(() => {
            groupSelect.innerHTML = '<option value="">Failed to load groups</option>';
        });

    // Handle group selection change
    groupSelect.addEventListener('change', function() {
        const groupId = this.value;
        loadPendingDeposits(groupId || null);
        
        // Auto-fill amount based on selected group
        if (groupId) {
            const selectedGroup = groups.find(g => g.id === groupId);
            if (selectedGroup) {
                amountInput.value = selectedGroup.contribution_amount;
            }
        }
    });

    // Handle form submit
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        msgDiv.textContent = '';
        
        const formData = new FormData(form);
        const data = {
            phone: user.phone,
            group_id: formData.get('group'),
            amount: parseFloat(formData.get('amount')),
            expected_deposit_id: formData.get('expected_deposit_id')
        };
        
        if (!data.group_id || isNaN(data.amount) || data.amount <= 0) {
            msgDiv.innerHTML = '<div class="alert alert-danger">Please select a group and enter a valid amount.</div>';
            return;
        }
        
        fetch('/api/deposit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        })
        .then(res => res.ok ? res.json() : res.json().then(e => Promise.reject(e)))
        .then(() => {
            msgDiv.innerHTML = '<div class="alert alert-success">Deposit successful!</div>';
            form.reset();
            
            // Remove the expected deposit ID from the form
            const expectedInput = document.getElementById('expectedDepositId');
            if (expectedInput) {
                expectedInput.remove();
            }
            
            // Reload pending deposits
            loadPendingDeposits(data.group_id || null);
        })
        .catch(err => {
            console.error('Deposit error:', err);
            msgDiv.innerHTML = `
                <div class="alert alert-danger">
                    ${err.detail || err.message || 'Failed to process deposit. Please try again.'}
                </div>`;
        });
    });
});