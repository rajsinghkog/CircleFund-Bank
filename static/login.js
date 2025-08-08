document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('loginForm');
    const msgDiv = document.getElementById('loginMsg');

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        msgDiv.textContent = '';
        const data = {
            phone: document.getElementById('identifier').value
        };
        if (!data.phone) {
            msgDiv.innerHTML = '<div class="alert alert-danger">Please enter your phone (username).</div>';
            return;
        }
        fetch('/api/signin', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        })
        .then(res => res.ok ? res.json() : res.json().then(e => Promise.reject(e)))
        .then(payload => {
            if (payload && payload.error) {
                throw new Error(payload.error);
            }
            if (payload && payload.user) {
                if (window.cf && cf.setAuth) cf.setAuth(payload.user, null);
                else localStorage.setItem('user', JSON.stringify(payload.user));
            }
            if (!localStorage.getItem('user')) {
                throw new Error('Login failed. Please check your credentials.');
            }
            window.location.href = '/';
        })
        .catch(err => {
            msgDiv.innerHTML = `<div class="alert alert-danger">${err.detail || err.message || 'Login failed.'}</div>`;
        });
    });
});