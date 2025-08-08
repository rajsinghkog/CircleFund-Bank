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
    const pendingLoansDiv = document.getElementById('pendingLoans');

    // Skeleton
    pendingLoansDiv.innerHTML = '<div class="skeleton" style="height:56px; margin-bottom:12px"></div><div class="skeleton" style="height:56px"></div>';

    // Fetch pending loans for user's group(s) - using legacy-compatible endpoint if available
    fetch('/api/loan/pending?user_id=' + encodeURIComponent(user.id))
        .then(res => res.json())
        .then(loans => {
            if (!loans.length) {
                pendingLoansDiv.innerHTML = '<div class="list-empty">No pending loan requests.</div>';
                return;
            }
            pendingLoansDiv.innerHTML = '';
            loans.forEach(loan => {
                const card = document.createElement('div');
                card.className = 'card mb-3';
                card.innerHTML = `
                    <div class="card-body">
                        <h5 class="card-title">Loan Request: ${window.cf && cf.formatCurrency ? cf.formatCurrency(loan.amount) : '₹' + Number(loan.amount).toFixed(2)}</h5>
                        <p class="card-text">Requested by: ${loan.user_name || loan.user_id}<br>Group: ${loan.group_name || loan.group_id}<br>Due: ${(window.cf && cf.formatDate) ? cf.formatDate(loan.due_date) : loan.due_date}</p>
                        <div class="mb-3"><span class="status-chip status-pending"><i class="bi bi-hourglass-split"></i> Pending</span></div>
                        <button class="btn btn-success btn-sm me-2" data-vote="yes" data-loan="${loan.id}">Yes</button>
                        <button class="btn btn-danger btn-sm" data-vote="no" data-loan="${loan.id}">No</button>
                    </div>
                `;
                pendingLoansDiv.appendChild(card);
            });
        })
        .catch(() => {
            pendingLoansDiv.innerHTML = '<div class="alert alert-danger">Failed to load pending loans.</div>';
        });

    // Handle voting
    pendingLoansDiv.addEventListener('click', function(e) {
        if (e.target.tagName === 'BUTTON' && e.target.dataset.vote) {
            const loanId = e.target.dataset.loan;
            const vote = e.target.dataset.vote;
            fetch(`/api/loan/${loanId}/vote`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ vote: vote === 'yes' ? 'approve' : 'reject', voter_phone: user.phone })
            })
            .then(res => res.ok ? res.json() : res.json().then(e => Promise.reject(e)))
            .then(() => {
                e.target.closest('.card').remove();
                if (window.cf && cf.showToast) cf.showToast('Success', 'Vote submitted', 'success');
            })
            .catch(() => {
                if (window.cf && cf.showToast) {
                    cf.showToast('Error', 'Failed to submit vote', 'error');
                } else {
                    alert('Failed to submit vote.');
                }
            });
        }
    });
}); 