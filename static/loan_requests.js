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

    // DOM Elements
    const pendingLoansContainer = document.getElementById('pendingLoansContainer');
    const approvedLoansContainer = document.getElementById('approvedLoansContainer');
    const withdrawModal = new bootstrap.Modal(document.getElementById('withdrawModal'));
    const withdrawAmountEl = document.getElementById('withdrawAmount');
    const confirmWithdrawBtn = document.getElementById('confirmWithdraw');
    
    let currentWithdrawLoanId = null;

    // Formatting helpers (delegates to cf utils if available)
    const formatDate = (d) => (window.cf && cf.formatDate) ? cf.formatDate(d) : (d ? new Date(d).toLocaleDateString(undefined, { year:'numeric', month:'short', day:'numeric' }) : 'N/A');
    const formatCurrency = (a) => (window.cf && cf.formatCurrency) ? cf.formatCurrency(a) : ('₹' + parseFloat(a).toFixed(2));

    // Load loan requests
    async function loadLoanRequests() {
        // Skeletons
        pendingLoansContainer.innerHTML = '<div class="skeleton" style="height:48px; margin-bottom:12px"></div><div class="skeleton" style="height:48px"></div>';
        approvedLoansContainer.innerHTML = '<div class="skeleton" style="height:48px; margin-bottom:12px"></div><div class="skeleton" style="height:48px"></div>';
        try {
            // Using legacy-compatible endpoints for listing loans per user
            const [pendingRes, approvedRes] = await Promise.all([
                fetch(`/api/loan/my?user_id=${user.id}&status=pending`),
                fetch(`/api/loan/my?user_id=${user.id}&status=approved`)
            ]);

            const pendingData = await pendingRes.json();
            const approvedData = await approvedRes.json();

            renderLoanRequests(pendingData, pendingLoansContainer, 'pending');
            renderLoanRequests(approvedData, approvedLoansContainer, 'approved');
        } catch (error) {
            console.error('Error loading loan requests:', error);
            pendingLoansContainer.innerHTML = `
                <div class="alert alert-danger">
                    Failed to load loan requests. Please try again later.
                </div>`;
            if (window.cf && cf.showToast) cf.showToast('Error', 'Failed to load loan requests', 'error');
        }
    }

    // Render loan requests
    function renderLoanRequests(loans, container, status) {
        if (!loans || loans.length === 0) {
            container.innerHTML = `
                <div class="list-empty">No ${status} loan requests found.</div>`;
            return;
        }

        let html = `
        <div class="table-responsive">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th>Request Date</th>
                        <th>Group</th>
                        <th>Amount</th>
                        <th>Status</th>
                        <th>Due Date</th>
                        ${status === 'approved' ? '<th>Actions</th>' : ''}
                    </tr>
                </thead>
                <tbody>`;

        loans.forEach(loan => {
            const statusChip = {
                'pending': '<span class="status-chip status-pending"><i class="bi bi-hourglass-split"></i> Pending</span>',
                'approved': '<span class="status-chip status-approved"><i class="bi bi-check2-circle"></i> Approved</span>',
                'rejected': '<span class="status-chip status-rejected"><i class="bi bi-x-circle"></i> Rejected</span>',
                'withdrawn': '<span class="status-chip"><i class="bi bi-arrow-counterclockwise"></i> Withdrawn</span>'
            }[loan.status] || '<span class="status-chip"><i class="bi bi-question-circle"></i> Unknown</span>';

            html += `
                <tr>
                    <td>${formatDate(loan.created_at)}</td>
                    <td>${loan.group_name || 'N/A'}</td>
                    <td>${formatCurrency(loan.amount)}</td>
                    <td>${statusChip}</td>
                    <td>${formatDate(loan.due_date)}</td>
                    ${status === 'approved' ? `
                    <td>
                        <button class="btn btn-sm btn-primary withdraw-btn" 
                                data-loan-id="${loan.id}"
                                data-amount="${loan.amount}">
                            Withdraw
                        </button>
                    </td>` : ''}
                </tr>`;
        });

        html += `
                </tbody>
            </table>
        </div>`;

        container.innerHTML = html;

        // Add event listeners for withdraw buttons
        if (status === 'approved') {
            document.querySelectorAll('.withdraw-btn').forEach(btn => {
                btn.addEventListener('click', function() {
                    const loanId = this.getAttribute('data-loan-id');
                    const amount = this.getAttribute('data-amount');
                    showWithdrawModal(loanId, amount);
                });
            });
        }
    }

    // Show withdraw modal
    function showWithdrawModal(loanId, amount) {
        currentWithdrawLoanId = loanId;
        withdrawAmountEl.textContent = formatCurrency(amount);
        withdrawModal.show();
    }

    // Handle withdraw confirmation
    confirmWithdrawBtn.addEventListener('click', async function() {
        if (!currentWithdrawLoanId) return;

        await (window.cf && cf.withButtonLoading ? cf.withButtonLoading(this, async () => {
            const response = await fetch(`/api/loans/${currentWithdrawLoanId}/withdraw`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({})
            });
            const result = await response.json();
            if (response.ok) {
                if (window.cf && cf.showToast) cf.showToast('Success', 'Loan withdrawn successfully.', 'success');
                withdrawModal.hide();
                loadLoanRequests();
            } else {
                throw new Error(result.detail || 'Failed to withdraw loan');
            }
        }) : Promise.resolve());
        currentWithdrawLoanId = null;
    });

    // Show toast notification
    // Use global cf.showToast now

    // Initialize the page
    loadLoanRequests();
});
