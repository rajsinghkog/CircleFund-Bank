(function(){
  const cf = {};

  cf.formatDate = function(dateString, options){
    if (!dateString) return 'N/A';
    const opts = options || { year: 'numeric', month: 'short', day: 'numeric' };
    try { return new Date(dateString).toLocaleDateString(undefined, opts); }
    catch(_) { return String(dateString); }
  };

  cf.formatCurrency = function(amount){
    const num = Number(amount);
    if (!Number.isFinite(num)) return '₹0.00';
    return '₹' + num.toFixed(2);
  };

  cf.ensureToastContainer = function(){
    let container = document.getElementById('cf-toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'cf-toast-container';
      container.className = 'toast-container position-fixed top-0 end-0 p-3';
      document.body.appendChild(container);
    }
    return container;
  };

  cf.showToast = function(title, message, type){
    const container = cf.ensureToastContainer();
    const color = type === 'success' ? 'bg-success' : type === 'error' ? 'bg-danger' : type === 'warning' ? 'bg-warning' : 'bg-primary';
    const toastEl = document.createElement('div');
    toastEl.className = `toast text-white ${color} border-0`;
    toastEl.setAttribute('role', 'alert');
    toastEl.setAttribute('aria-live', 'assertive');
    toastEl.setAttribute('aria-atomic', 'true');
    toastEl.innerHTML = `
      <div class="d-flex">
        <div class="toast-body">
          <strong>${title}:</strong> ${message}
        </div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
      </div>`;
    container.appendChild(toastEl);
    try {
      const toast = new bootstrap.Toast(toastEl, { delay: 3500 });
      toast.show();
      toastEl.addEventListener('hidden.bs.toast', function(){ container.removeChild(toastEl); });
    } catch (_) {
      // Fallback if Bootstrap JS is not loaded
      setTimeout(() => container.contains(toastEl) && container.removeChild(toastEl), 4000);
    }
  };

  cf.renderSkeleton = function(container, rows){
    const count = Number(rows) || 3;
    let html = '<div class="card"><div class="card-body">';
    for (let i = 0; i < count; i++) {
      html += '<div class="skeleton" style="height: 18px; margin-bottom: 12px;"></div>';
    }
    html += '</div></div>';
    container.innerHTML = html;
  };

  // --- Auth helpers ---
  cf.getUser = function(){
    try {
      const raw = localStorage.getItem('user');
      if (!raw || raw === 'undefined' || raw === 'null') {
        if (raw === 'undefined' || raw === 'null') localStorage.removeItem('user');
        return null;
      }
      return JSON.parse(raw);
    } catch (_) {
      localStorage.removeItem('user');
      return null;
    }
  };

  cf.setAuth = function(user, token){
    try {
      if (user) localStorage.setItem('user', JSON.stringify(user));
      if (token) localStorage.setItem('token', token);
    } catch (_) {}
  };

  cf.clearAuth = function(){
    try {
      localStorage.removeItem('user');
      localStorage.removeItem('token');
    } catch (_) {}
  };

  cf.hydrateUserFromCookie = async function(){
    try {
      const res = await fetch('/api/me');
      const data = await res.json().catch(() => ({}));
      if (res.ok && data && data.user) {
        cf.setAuth(data.user, null);
        return data.user;
      }
    } catch (_) {}
    return null;
  };

  cf.requireAuth = async function(){
    let user = cf.getUser();
    if (!user) user = await cf.hydrateUserFromCookie();
    if (!user) {
      window.location.href = '/login';
      return null;
    }
    return user;
  };

  cf.fetchJson = async function(url, options){
    const res = await fetch(url, options);
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      const err = new Error(data.detail || data.error || 'Request failed');
      err.data = data; err.status = res.status;
      throw err;
    }
    return data;
  };

  // Simple full-page loader overlay for long-running ops
  cf.showLoader = function(message){
    let overlay = document.getElementById('cf-loader-overlay');
    if (!overlay) {
      overlay = document.createElement('div');
      overlay.id = 'cf-loader-overlay';
      overlay.style.position = 'fixed';
      overlay.style.inset = '0';
      overlay.style.zIndex = '2000';
      overlay.style.backdropFilter = 'blur(2px)';
      overlay.style.background = 'rgba(0,0,0,0.15)';
      overlay.innerHTML = `
        <div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);display:flex;flex-direction:column;align-items:center;gap:12px;">
          <div class="spinner-border text-primary" role="status"></div>
          <div class="text-muted">${message || 'Loading...'}</div>
        </div>`;
      document.body.appendChild(overlay);
    }
  };
  cf.hideLoader = function(){
    const overlay = document.getElementById('cf-loader-overlay');
    if (overlay && overlay.parentNode) overlay.parentNode.removeChild(overlay);
  };

  cf.withButtonLoading = async function(buttonEl, asyncFn){
    if (!buttonEl || typeof asyncFn !== 'function') return;
    const original = buttonEl.innerHTML;
    buttonEl.disabled = true;
    buttonEl.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
    try {
      return await asyncFn();
    } finally {
      buttonEl.disabled = false;
      buttonEl.innerHTML = original;
    }
  };

  window.cf = cf;
})();


