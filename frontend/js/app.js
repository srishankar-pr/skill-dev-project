/**
 * Shared Application Utilities, API Client (Fetch API), Theme Manager,
 * Dynamic Student Profile Modal, and UI Helpers
 * Smart Placement Preparation Assistant
 */

const STUDENT_ID = 1;
let currentStudentProfile = null;

// Apply saved theme immediately (defaults to 'dark')
(function initThemeImmediate() {
  const savedTheme = localStorage.getItem('sp_theme') || 'dark';
  document.documentElement.setAttribute('data-theme', savedTheme);
})();

function resolveApiBaseUrl() {
  if (window.location.protocol.startsWith('http') && window.location.port === '8000') {
    return window.location.origin;
  }
  return 'http://127.0.0.1:8000';
}

const API_BASE_URL = resolveApiBaseUrl();

/**
 * Wrapper around Fetch API with JSON parsing and error handling.
 */
async function apiFetch(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  const defaultHeaders = { 'Content-Type': 'application/json' };
  const config = {
    ...options,
    headers: { ...defaultHeaders, ...(options.headers || {}) },
  };

  const response = await fetch(url, config);
  let payload = null;
  try {
    payload = await response.json();
  } catch (_err) {
    payload = null;
  }

  if (!response.ok) {
    const detail =
      (payload && (payload.detail || payload.message)) ||
      `Request failed with status ${response.status}`;
    const errorMsg = Array.isArray(detail)
      ? detail.map((d) => d.msg || JSON.stringify(d)).join('; ')
      : String(detail);
    throw new Error(errorMsg);
  }

  return payload;
}

/**
 * Escape HTML special characters to prevent XSS.
 */
function escapeHtml(value) {
  if (value === null || value === undefined) return '';
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

/**
 * Compute 2-letter initials from a student name.
 */
function computeInitials(name) {
  const parts = String(name || 'Student')
    .trim()
    .split(/\s+/)
    .filter(Boolean);
  if (parts.length === 0) return 'ST';
  if (parts.length === 1) return parts[0].substring(0, 2).toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}

/**
 * Render difficulty badge HTML.
 */
function difficultyBadge(difficulty) {
  const diff = String(difficulty || 'Beginner');
  const cls =
    diff.toLowerCase() === 'advanced'
      ? 'badge-advanced'
      : diff.toLowerCase() === 'intermediate'
      ? 'badge-intermediate'
      : 'badge-beginner';
  return `<span class="badge ${cls}">${escapeHtml(diff)}</span>`;
}

/**
 * Render question completion status badge HTML.
 */
function statusBadge(status) {
  const st = String(status || 'Not Started');
  if (st === 'Completed') {
    return `<span class="badge badge-completed">Completed</span>`;
  }
  if (st === 'Attempted') {
    return `<span class="badge badge-attempted">Attempted</span>`;
  }
  return `<span class="badge badge-not-started">Not Started</span>`;
}

/**
 * Format SQLite UTC timestamp into readable date string.
 */
function formatTimestamp(ts) {
  if (!ts) return 'Just now';
  try {
    const normalized = ts.includes('T') ? ts : ts.replace(' ', 'T') + 'Z';
    const dt = new Date(normalized);
    if (isNaN(dt.getTime())) return ts;
    return dt.toLocaleString(undefined, {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch (_e) {
    return ts;
  }
}

/**
 * Show non-intrusive toast notification.
 */
function showToast(message, type = 'success') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  const label = type === 'error' ? '[ERROR]' : '[OK]';
  toast.innerHTML = `<strong>${label}</strong><span>${escapeHtml(message)}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 250);
  }, 3600);
}

/**
 * Load student profile dynamically from SQLite and update sidebar + welcome banner.
 */
async function loadAndRenderStudentProfile() {
  try {
    const student = await apiFetch(`/students/${STUDENT_ID}`);
    currentStudentProfile = student;
    applyStudentProfileToDOM(student);
  } catch (_err) {
    // Fallback if offline
  }
}

function applyStudentProfileToDOM(student) {
  if (!student) return;
  const avatarEl = document.getElementById('sidebar-student-avatar');
  const nameEl = document.getElementById('sidebar-student-name');
  const metaEl = document.getElementById('sidebar-student-meta');

  if (avatarEl) avatarEl.textContent = computeInitials(student.name);
  if (nameEl) nameEl.textContent = student.name;
  if (metaEl) metaEl.textContent = `${student.branch} | Batch of ${student.graduation_year}`;

  const welcomeName = document.getElementById('student-welcome-name');
  if (welcomeName) {
    welcomeName.textContent = `Welcome back, ${student.name}`;
  }
  const roleEl = document.getElementById('student-target-role');
  if (roleEl) {
    roleEl.textContent = `${student.branch} | Class of ${student.graduation_year} | Target: ${student.target_role}`;
  }
}

/**
 * Create and open the Edit Student Profile modal dialog.
 */
function ensureProfileModalExists() {
  if (document.getElementById('profile-modal-backdrop')) return;

  const backdrop = document.createElement('div');
  backdrop.id = 'profile-modal-backdrop';
  backdrop.className = 'modal-backdrop';
  backdrop.style.display = 'none';

  backdrop.innerHTML = `
    <div class="modal-card" onclick="event.stopPropagation()">
      <div class="card-header">
        <h3>Edit Student Profile</h3>
        <button type="button" class="btn btn-secondary btn-sm" onclick="closeProfileModal()">Close</button>
      </div>
      <div class="card-body">
        <form id="profile-edit-form" class="modal-body-form">
          <div class="modal-field">
            <label for="prof-name-input">Full Name</label>
            <input type="text" id="prof-name-input" class="form-input" placeholder="Enter your name" required maxlength="100" />
          </div>
          <div class="modal-field">
            <label for="prof-branch-input">Branch / Department</label>
            <input type="text" id="prof-branch-input" class="form-input" placeholder="e.g., Computer Science & Engineering" required maxlength="100" />
          </div>
          <div class="modal-field">
            <label for="prof-year-input">Graduation Year</label>
            <input type="number" id="prof-year-input" class="form-input" min="2020" max="2035" value="2026" required />
          </div>
          <div class="modal-field">
            <label for="prof-role-input">Target Placement Role</label>
            <input type="text" id="prof-role-input" class="form-input" placeholder="e.g., Software Development Engineer" required maxlength="120" />
          </div>
          <div class="modal-field">
            <label for="prof-email-input">Email Address</label>
            <input type="email" id="prof-email-input" class="form-input" placeholder="student@university.edu" required maxlength="120" />
          </div>
          <div style="display:flex; justify-content:flex-end; gap:10px; margin-top:8px;">
            <button type="button" class="btn btn-secondary" onclick="closeProfileModal()">Cancel</button>
            <button type="submit" id="prof-save-btn" class="btn btn-primary">Save Profile</button>
          </div>
        </form>
      </div>
    </div>
  `;

  backdrop.addEventListener('click', closeProfileModal);
  document.body.appendChild(backdrop);

  const form = document.getElementById('profile-edit-form');
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const saveBtn = document.getElementById('prof-save-btn');
    if (saveBtn) saveBtn.disabled = true;

    try {
      const updated = await apiFetch(`/students/${STUDENT_ID}`, {
        method: 'PUT',
        body: JSON.stringify({
          name: document.getElementById('prof-name-input').value.trim(),
          branch: document.getElementById('prof-branch-input').value.trim(),
          graduation_year: parseInt(document.getElementById('prof-year-input').value || '2026', 10),
          target_role: document.getElementById('prof-role-input').value.trim(),
          email: document.getElementById('prof-email-input').value.trim(),
        }),
      });
      currentStudentProfile = updated;
      applyStudentProfileToDOM(updated);
      closeProfileModal();
      showToast(`Profile updated for ${updated.name}`, 'success');
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      if (saveBtn) saveBtn.disabled = false;
    }
  });
}

async function openProfileModal() {
  ensureProfileModalExists();
  if (!currentStudentProfile) {
    await loadAndRenderStudentProfile();
  }
  const s = currentStudentProfile || {
    name: 'Student',
    branch: 'Computer Science',
    graduation_year: 2026,
    target_role: 'Software Development Engineer',
    email: 'student@university.edu',
  };

  document.getElementById('prof-name-input').value = s.name || '';
  document.getElementById('prof-branch-input').value = s.branch || '';
  document.getElementById('prof-year-input').value = s.graduation_year || 2026;
  document.getElementById('prof-role-input').value = s.target_role || '';
  document.getElementById('prof-email-input').value = s.email || '';

  const backdrop = document.getElementById('profile-modal-backdrop');
  if (backdrop) backdrop.style.display = 'flex';
  document.getElementById('prof-name-input').focus();
}

function closeProfileModal() {
  const backdrop = document.getElementById('profile-modal-backdrop');
  if (backdrop) backdrop.style.display = 'none';
}

/**
 * Check FastAPI backend health and update topbar status badge.
 */
async function checkBackendStatus() {
  const statusEl = document.getElementById('api-status-pill');
  if (!statusEl) return;
  try {
    await apiFetch('/');
    statusEl.innerHTML = `<span class="status-dot"></span><span>FastAPI + SQLite Connected</span>`;
  } catch (_err) {
    statusEl.innerHTML = `<span class="status-dot offline"></span><span>Backend Offline</span>`;
    statusEl.style.background = 'var(--danger-bg)';
    statusEl.style.color = 'var(--danger-text)';
    statusEl.style.borderColor = 'var(--danger-border)';
  }
}

/**
 * Inject Edit Profile and Dark / Light Mode toggle buttons in topbar.
 */
function setupTopbarControls() {
  const topbarRight = document.querySelector('.topbar-right');
  if (!topbarRight) return;

  if (!document.getElementById('topbar-profile-btn')) {
    const profBtn = document.createElement('button');
    profBtn.id = 'topbar-profile-btn';
    profBtn.type = 'button';
    profBtn.className = 'btn btn-secondary btn-sm';
    profBtn.textContent = 'Change Name';
    profBtn.addEventListener('click', openProfileModal);
    topbarRight.insertBefore(profBtn, topbarRight.firstChild);
  }

  if (!document.getElementById('theme-toggle-btn')) {
    const btn = document.createElement('button');
    btn.id = 'theme-toggle-btn';
    btn.type = 'button';
    btn.className = 'btn btn-secondary btn-sm';

    const updateButtonLabel = () => {
      const current = document.documentElement.getAttribute('data-theme') || 'dark';
      btn.textContent = current === 'dark' ? 'Theme: Dark' : 'Theme: Light';
    };

    updateButtonLabel();

    btn.addEventListener('click', () => {
      const current = document.documentElement.getAttribute('data-theme') || 'dark';
      const next = current === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', next);
      localStorage.setItem('sp_theme', next);
      updateButtonLabel();
    });

    topbarRight.insertBefore(btn, topbarRight.firstChild);
  }
}

/**
 * Initialize mobile sidebar toggle, profile loader, theme switcher, and backend ping.
 */
document.addEventListener('DOMContentLoaded', () => {
  const menuBtn = document.getElementById('mobile-menu-btn');
  const sidebar = document.getElementById('sidebar');
  if (menuBtn && sidebar) {
    menuBtn.addEventListener('click', () => {
      sidebar.classList.toggle('open');
    });
  }
  setupTopbarControls();
  loadAndRenderStudentProfile();
  checkBackendStatus();
});
