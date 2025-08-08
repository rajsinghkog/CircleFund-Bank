document.addEventListener('DOMContentLoaded', function() {
    const user = JSON.parse(localStorage.getItem('user') || 'null');
    if (!user) {
        window.location.href = '/login';
        return;
    }
    const repaymentListDiv = document.getElementById('repaymentList');

    // Skeleton
    repaymentListDiv.innerHTML = '<div class="skeleton" style="height:56px; margin-bottom:12px"></div><div class="skeleton" style="height:56px"></div>';

    // Fetch user's loans
    fetch('/api/loan/my?user_id=' + encodeURIComponent(user.id))
        .then(res => res.json())
        .then(loans => {
            if (!loans.length) {
                repaymentListDiv.innerHTML = '<div class="list-empty">No loans to repay.</div>';
                return;
            }
            repaymentListDiv.innerHTML = '';
            loans.forEach(loan => {
                const card = document.createElement('div');
                card.className = 'card mb-3';
                const amountStr = (window.cf && cf.formatCurrency) ? cf.formatCurrency(loan.amount) : '₹' + Number(loan.amount).toFixed(2);
                const dueStr = (window.cf && cf.formatDate) ? cf.formatDate(loan.due_date) : loan.due_date;
                card.innerHTML = `
                    <div class="card-body">
                        <h5 class="card-title">Loan: ${amountStr}</h5>
                        <div class="mb-2">Due: ${dueStr}</div>
                        <div class="mb-3">
                            ${loan.status === 'approved' ? '<span class="status-chip status-approved"><i class="bi bi-check2-circle"></i> Approved</span>' : ''}
                            ${loan.status === 'pending' ? '<span class="status-chip status-pending"><i class="bi bi-hourglass-split"></i> Pending</span>' : ''}
                            ${loan.status === 'rejected' ? '<span class="status-chip status-rejected"><i class="bi bi-x-circle"></i> Rejected</span>' : ''}
                        </div>
                        <button class="btn btn-primary btn-sm" data-loan="${loan.id}">Repay</button>
                    </div>
                `;
                repaymentListDiv.appendChild(card);
            });
        })
        .catch(() => {
            repaymentListDiv.innerHTML = '<div class="alert alert-danger">Failed to load your loans.</div>';
        });

    // Handle repayment
    repaymentListDiv.addEventListener('click', function(e) {
        if (e.target.tagName === 'BUTTON' && e.target.dataset.loan) {
            const loanId = e.target.dataset.loan;
            fetch(`/api/loan/${loanId}/repay`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ amount: 0, user_id: user.id }) // In a real app, prompt for amount
            })
            .then(res => res.ok ? res.json() : res.json().then(e => Promise.reject(e)))
            .then(() => {
                e.target.closest('.card').remove();
                if (window.cf && cf.showToast) cf.showToast('Success', 'Repayment submitted', 'success');
            })
            .catch(() => {
                if (window.cf && cf.showToast) {
                    cf.showToast('Error', 'Failed to repay loan', 'error');
                } else {
                    alert('Failed to repay loan.');
                }
            });
        }
    });
}); 