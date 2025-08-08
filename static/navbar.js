async function renderNavbar() {
  // Safely detect logged-in user
  let user = null;
  try {
    const raw = localStorage.getItem('user');
    if (raw && raw !== 'undefined' && raw !== 'null') user = JSON.parse(raw);
    else if (raw === 'undefined' || raw === 'null') localStorage.removeItem('user');
  } catch (_) { localStorage.removeItem('user'); }

  // If no user in localStorage, try to recover from auth cookie via /api/me
  if (!user) {
    try {
      const res = await fetch('/api/me');
      const data = await res.json().catch(() => ({}));
      if (res.ok && data && data.user) {
        user = data.user;
        localStorage.setItem('user', JSON.stringify(user));
      }
    } catch (_) { /* ignore */ }
  }
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  const themeIcon = isDark ? 'bi-sun' : 'bi-moon-stars';
  const themeLabel = isDark ? 'Light' : 'Dark';
  const navbarTone = isDark ? 'navbar-dark' : 'navbar-light';
  const toggleBtnClass = isDark ? 'btn-outline-light' : 'btn-outline-dark';
  const path = window.location.pathname;
  let nav = `<nav class="navbar navbar-expand-lg ${navbarTone} bg-transparent glass">
    <div class="container">
      <a class="navbar-brand" href="/">CircleFund Bank</a>
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav ms-auto align-items-lg-center">`;
  if (user) {
    nav += `
      <li class="nav-item"><a class="nav-link ${path==='/'?'active':''}" href="/">Home</a></li>
      <li class="nav-item"><a class="nav-link ${path==='/create_group'?'active':''}" href="/create_group">Create Group</a></li>
      <li class="nav-item"><a class="nav-link ${path==='/join_group'?'active':''}" href="/join_group">Join Group</a></li>
      <li class="nav-item"><a class="nav-link ${path==='/deposit'?'active':''}" href="/deposit">Deposit</a></li>
      <li class="nav-item"><a class="nav-link ${path==='/loan_request'?'active':''}" href="/loan_request">Loan Request</a></li>
      <li class="nav-item"><a class="nav-link ${path==='/voting_dashboard'?'active':''}" href="/voting_dashboard">Voting Dashboard</a></li>
      <li class="nav-item"><a class="nav-link ${path==='/repayment_tracker'?'active':''}" href="/repayment_tracker">Repayment Tracker</a></li>
      <li class="nav-item"><a class="nav-link ${path==='/statement'?'active':''}" href="/statement">My Statement</a></li>
      <li class="nav-item"><a class="nav-link" href="/logout" id="logoutBtn">Logout</a></li>
    `;
  } else {
    nav += `
      <li class="nav-item"><a class="nav-link ${path==='/'?'active':''}" href="/">Home</a></li>
    `;
  }
  nav += `
      <li class="nav-item ms-lg-3">
        <button id="themeToggle" class="btn btn-sm ${toggleBtnClass} d-flex align-items-center gap-2">
          <i class="bi ${themeIcon}"></i><span class="d-none d-sm-inline">${themeLabel} mode</span>
        </button>
      </li>
    </ul></div></div></nav>`;
  document.getElementById('navbar').innerHTML = nav;
  if (user) {
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
      // handled by /logout page
    }
  }

  const themeToggle = document.getElementById('themeToggle');
  if (themeToggle) {
    themeToggle.addEventListener('click', function() {
      const isDarkNow = document.documentElement.getAttribute('data-theme') === 'dark';
      if (isDarkNow) {
        document.documentElement.removeAttribute('data-theme');
        localStorage.setItem('cf-theme', 'light');
      } else {
        document.documentElement.setAttribute('data-theme','dark');
        localStorage.setItem('cf-theme', 'dark');
      }
      renderNavbar();
    });
  }
}
if (document.readyState !== 'loading') {
  renderNavbar();
} else {
  document.addEventListener('DOMContentLoaded', renderNavbar);
}