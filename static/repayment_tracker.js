document.addEventListener('DOMContentLoaded', function() {
    const user = JSON.parse(localStorage.getItem('user') || 'null');
    if (!user) {
        window.location.href = '/login';
        return;
    }
    const repaymentListDiv = document.getElementById('repaymentList');

    // Fetch user's loans
    fetch('/api/loan/my?user_id=' + encodeURIComponent(user.id))
        .then(res => res.json())
        .then(loans => {
            if (!loans.length) {
                repaymentListDiv.innerHTML = '<div class="alert alert-info">No loans to repay.</div>';
                return;
            }
            repaymentListDiv.innerHTML = '';
            loans.forEach(loan => {
                const card = document.createElement('div');
                card.className = 'card mb-3';
                card.innerHTML = `
                    <div class="card-body">
                        <h5 class="card-title">Loan: ₹${loan.amount}</h5>
                        <p class="card-text">Status: ${loan.status}<br>Due: ${loan.due_date}</p>
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
            })
            .catch(() => {
                alert('Failed to repay loan.');
            });
        }
    });
}); 