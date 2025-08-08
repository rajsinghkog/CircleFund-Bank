(async function(){
  const container = document.getElementById('statementContainer');
  const userInfo = document.getElementById('stmtUser');
  try {
    const user = (window.cf && cf.requireAuth) ? await cf.requireAuth() : null;
    if (!user) return;
    if (userInfo) userInfo.textContent = `${user.name || ''} (${user.phone || ''})`;
    if (container) cf.renderSkeleton(container, 6);
    const data = await cf.fetchJson(`/api/statement?phone=${encodeURIComponent(user.phone)}`);
    const rows = Array.isArray(data?.statement) ? data.statement : Array.isArray(data) ? data : [];
    if (!rows.length) {
      container.innerHTML = '<div class="alert alert-info">No statement entries yet.</div>';
      return;
    }
    let html = '<div class="card"><div class="card-body"><div class="table-responsive"><table class="table table-sm align-middle">';
    html += '<thead><tr><th style="width:120px;">Date</th><th>Type</th><th>Amount</th><th>Group</th><th>Status</th></tr></thead><tbody>';
    for (const row of rows) {
      const date = cf.formatDate(row.date, { year:'numeric', month:'short', day:'numeric', hour:'2-digit', minute:'2-digit' });
      const type = (row.type || '').toString();
      const amount = cf.formatCurrency(row.amount || 0);
      const group = row.group_name || row.group_id || '-';
      const status = row.status || (type === 'deposit' ? 'completed' : (type === 'loan' ? (row.status || '-') : '-'));
      const badgeClass = type === 'deposit' ? 'bg-success-subtle text-success' : (type === 'loan' ? 'bg-warning-subtle text-warning' : 'bg-info-subtle text-info');
      html += `<tr>
        <td>${date}</td>
        <td><span class="badge ${badgeClass}">${type}</span></td>
        <td>${amount}</td>
        <td>${group}</td>
        <td>${status}</td>
      </tr>`;
    }
    html += '</tbody></table></div></div></div>';
    container.innerHTML = html;
  } catch (err) {
    container.innerHTML = `<div class="alert alert-danger">Failed to load statement: ${err?.message || 'Unknown error'}</div>`;
  }
})();


