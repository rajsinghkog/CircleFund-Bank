document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('signupForm');
    const msgDiv = document.getElementById('signupMsg');

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        msgDiv.textContent = '';
        const data = {
            name: document.getElementById('name').value,
            phone: document.getElementById('phone').value
        };
        if (!data.name || !data.phone) {
            msgDiv.innerHTML = '<div class="alert alert-danger">Please fill all fields.</div>';
            return;
        }
        fetch('/api/signup', {
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
            window.location.href = '/';
        })
        .catch(err => {
            
            msgDiv.innerHTML = `<div class="alert alert-danger">${err.detail || err.message || 'Signup failed.'}</div>`;
        });
    });
}); 