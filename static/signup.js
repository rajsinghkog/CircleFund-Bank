document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('signupForm');
    const msgDiv = document.getElementById('signupMsg');

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        msgDiv.textContent = '';
        const data = {
            name: document.getElementById('name').value,
            email: document.getElementById('email').value,
            phone: document.getElementById('phone').value,
            password: document.getElementById('password').value
        };
        fetch('/api/signup', {
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
            
            msgDiv.innerHTML = `<div class="alert alert-danger">${err.detail || 'Signup failed.'}</div>`;
        });
    });
}); 