function renderNavbar() {
    const user = localStorage.getItem('user');
    let nav = `<nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container-fluid">
            <a class="navbar-brand" href="/">CircleFund Bank</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">`;
    if (user) {
        nav += `
            <li class="nav-item"><a class="nav-link" href="/join_group">Join Group</a></li>
            <li class="nav-item"><a class="nav-link" href="/deposit">Deposit</a></li>
            <li class="nav-item"><a class="nav-link" href="/loan_request">Loan Request</a></li>
            <li class="nav-item"><a class="nav-link" href="/voting_dashboard">Voting Dashboard</a></li>
            <li class="nav-item"><a class="nav-link" href="/repayment_tracker">Repayment Tracker</a></li>
            <li class="nav-item"><a class="nav-link" href="#" id="logoutBtn">Logout</a></li>
        `;
    } else {
        nav += `
            <li class="nav-item"><a class="nav-link" href="/login">Login</a></li>
            <li class="nav-item"><a class="nav-link" href="/signup">Sign Up</a></li>
        `;
    }
    nav += `</ul></div></div></nav>`;
    document.getElementById('navbar').innerHTML = nav;
    if (user) {
        const logoutBtn = document.getElementById('logoutBtn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', function(e) {
                e.preventDefault();
                localStorage.removeItem('user');
                window.location.href = '/login';
            });
        }
    }
}
document.addEventListener('DOMContentLoaded', renderNavbar); 