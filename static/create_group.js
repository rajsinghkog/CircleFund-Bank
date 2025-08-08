document.addEventListener('DOMContentLoaded', function() {
  const user = JSON.parse(localStorage.getItem('user') || 'null');
  if (!user) {
    window.location.href = '/login';
    return;
  }

  const form = document.getElementById('createGroupForm');
  const msgDiv = document.getElementById('createGroupMsg');

  form.addEventListener('submit', function(e) {
    e.preventDefault();
    msgDiv.textContent = '';
    const data = {
      name: document.getElementById('groupName').value.trim(),
      contribution_amount: parseFloat(document.getElementById('contributionAmount').value),
      cycle: document.getElementById('cycle').value,
      creator_phone: user.phone
    };
    fetch('/api/groups', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    })
      .then(res => res.ok ? res.json() : res.json().then(e => Promise.reject(e)))
      .then(resp => {
        msgDiv.innerHTML = '<div class="alert alert-success">Group created successfully!</div>';
        // Redirect to join page or clear form
        setTimeout(() => {
          window.location.href = '/join_group';
        }, 800);
      })
      .catch(err => {
        msgDiv.innerHTML = `<div class="alert alert-danger">${err.detail || err.error || 'Failed to create group.'}</div>`;
      });
  });
});


