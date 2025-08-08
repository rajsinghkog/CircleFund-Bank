document.addEventListener('DOMContentLoaded', function() {
    const user = JSON.parse(localStorage.getItem('user') || 'null');
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

    // Format date
    function formatDate(dateString) {
        if (!dateString) return 'N/A';
        const options = { year: 'numeric', month: 'short', day: 'numeric' };
        return new Date(dateString).toLocaleDateString(undefined, options);
    }

    // Format currency
    function formatCurrency(amount) {
        return '₹' + parseFloat(amount).toFixed(2);
    }

    // Load loan requests
    async function loadLoanRequests() {
        try {
            const [pendingRes, approvedRes] = await Promise.all([
                fetch(`/api/loans?user_id=${user.id}&status=pending`),
                fetch(`/api/loans?user_id=${user.id}&status=approved`)
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
        }
    }

    // Render loan requests
    function renderLoanRequests(loans, container, status) {
        if (!loans || loans.length === 0) {
            container.innerHTML = `
                <div class="alert alert-info">
                    No ${status} loan requests found.
                </div>`;
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
            const statusClass = {
                'pending': 'bg-warning',
                'approved': 'bg-success',
                'rejected': 'bg-danger',
                'withdrawn': 'bg-secondary'
            }[loan.status] || 'bg-secondary';

            html += `
                <tr>
                    <td>${formatDate(loan.created_at)}</td>
                    <td>${loan.group_name || 'N/A'}</td>
                    <td>${formatCurrency(loan.amount)}</td>
                    <td><span class="badge ${statusClass}">${loan.status}</span></td>
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

        const btn = this;
        const originalText = btn.innerHTML;
        
        try {
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
            
            const response = await fetch(`/api/loans/${currentWithdrawLoanId}/withdraw`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: user.id })
            });

            const result = await response.json();
            
            if (response.ok) {
                showToast('Success', 'Loan amount has been withdrawn successfully.', 'success');
                withdrawModal.hide();
                loadLoanRequests(); // Refresh the list
            } else {
                throw new Error(result.detail || 'Failed to withdraw loan');
            }
        } catch (error) {
            console.error('Withdrawal failed:', error);
            showToast('Error', error.message, 'error');
        } finally {
            btn.disabled = false;
            btn.innerHTML = originalText;
            currentWithdrawLoanId = null;
        }
    });

    // Show toast notification
    function showToast(title, message, type = 'info') {
        const toastContainer = document.createElement('div');
        toastContainer.className = `toast align-items-center text-white bg-${type} border-0`;
        toastContainer.setAttribute('role', 'alert');
        toastContainer.setAttribute('aria-live', 'assertive');
        toastContainer.setAttribute('aria-atomic', 'true');
        
        toastContainer.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <strong>${title}:</strong> ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>`;
        
        document.body.appendChild(toastContainer);
        const toast = new bootstrap.Toast(toastContainer);
        toast.show();
        
        // Remove the toast after it's hidden
        toastContainer.addEventListener('hidden.bs.toast', function() {
            document.body.removeChild(toastContainer);
        });
    }

    // Initialize the page
    loadLoanRequests();
});
