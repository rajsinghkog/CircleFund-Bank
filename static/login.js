document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('loginForm');
    const msgDiv = document.getElementById('loginMsg');

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        msgDiv.textContent = '';
        const data = {
            phone: document.getElementById('identifier').value,
            password: document.getElementById('password').value
        };
        if (!data.phone || !data.password) {
            msgDiv.innerHTML = '<div class="alert alert-danger">Please enter your email/phone and password.</div>';
            return;
        }
        fetch('/api/signin', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        })
        .then(res => res.ok ? res.json() : res.json().then(e => Promise.reject(e)))
        .then(user => {
            localStorage.setItem('user', JSON.stringify(user.user));
            window.location.href = '/';
        })
        .catch(err => {
            msgDiv.innerHTML = `<div class="alert alert-danger">${err.detail || 'Login failed.'}</div>`;
        });
    });
}); 