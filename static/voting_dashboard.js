document.addEventListener('DOMContentLoaded', function() {
    const user = JSON.parse(localStorage.getItem('user') || 'null');
    if (!user) {
        window.location.href = '/login';
        return;
    }
    const pendingLoansDiv = document.getElementById('pendingLoans');

    // Fetch pending loans for user's group(s)
    fetch('/api/loan/pending?user_id=' + encodeURIComponent(user.id))
        .then(res => res.json())
        .then(loans => {
            if (!loans.length) {
                pendingLoansDiv.innerHTML = '<div class="alert alert-info">No pending loan requests.</div>';
                return;
            }
            pendingLoansDiv.innerHTML = '';
            loans.forEach(loan => {
                const card = document.createElement('div');
                card.className = 'card mb-3';
                card.innerHTML = `
                    <div class="card-body">
                        <h5 class="card-title">Loan Request: ₹${loan.amount}</h5>
                        <p class="card-text">Requested by: ${loan.user_name || loan.user_id}<br>Group: ${loan.group_name || loan.group_id}<br>Status: ${loan.status}<br>Due: ${loan.due_date}</p>
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
                body: JSON.stringify({ vote, voter_id: user.id })
            })
            .then(res => res.ok ? res.json() : res.json().then(e => Promise.reject(e)))
            .then(() => {
                e.target.closest('.card').remove();
            })
            .catch(() => {
                alert('Failed to submit vote.');
            });
        }
    });
}); 