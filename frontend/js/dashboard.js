/**
 * Dashboard Module (index.html)
 * Dynamically loads statistics, difficulty breakdown, recent attempts, and recommended topics from GET /dashboard/stats.
 */

async function loadDashboard() {
  const loadingBox = document.getElementById('dashboard-loading');
  const errorBox = document.getElementById('dashboard-error');
  const contentBox = document.getElementById('dashboard-content');

  if (loadingBox) loadingBox.style.display = 'block';
  if (errorBox) errorBox.style.display = 'none';
  if (contentBox) contentBox.style.display = 'none';

  try {
    const data = await apiFetch(`/dashboard/stats?student_id=${STUDENT_ID}`);

    // Populate Welcome Header
    const nameEl = document.getElementById('student-welcome-name');
    if (nameEl && data.student) {
      nameEl.textContent = `Welcome back, ${data.student.name}`;
    }
    const roleEl = document.getElementById('student-target-role');
    if (roleEl && data.student) {
      roleEl.textContent = `${data.student.branch} | Class of ${data.student.graduation_year} | Target: ${data.student.target_role}`;
    }

    // Populate KPI Cards
    document.getElementById('stat-total-questions').textContent = data.total_questions;
    document.getElementById('stat-attempted').textContent = data.questions_attempted;
    document.getElementById('stat-completed').textContent = data.questions_completed;
    document.getElementById('stat-avg-quiz').textContent = `${data.average_quiz_score}%`;
    document.getElementById('stat-overall-progress').textContent = `${data.overall_progress_percentage}%`;

    const readinessBadge = document.getElementById('stat-readiness-label');
    if (readinessBadge) {
      readinessBadge.textContent = data.readiness_label;
    }

    const quizMeta = document.getElementById('stat-quiz-meta');
    if (quizMeta) {
      quizMeta.textContent = `${data.quizzes_taken} Quizzes Taken | Best: ${data.best_quiz_score}%`;
    }

    const overallBar = document.getElementById('overall-progress-bar');
    if (overallBar) {
      overallBar.style.width = `${Math.min(100, data.overall_progress_percentage)}%`;
    }

    // Difficulty Breakdown Bars
    const diffContainer = document.getElementById('difficulty-breakdown-container');
    if (diffContainer && data.difficulty_breakdown) {
      const levels = ['Beginner', 'Intermediate', 'Advanced'];
      diffContainer.innerHTML = levels
        .map((lvl) => {
          const item = data.difficulty_breakdown[lvl] || { total: 0, completed: 0 };
          const pct = item.total > 0 ? Math.round((item.completed / item.total) * 100) : 0;
          const barClass = lvl === 'Beginner' ? 'success' : lvl === 'Intermediate' ? 'warning' : '';
          return `
            <div style="margin-bottom: 14px;">
              <div style="display:flex; justify-content:space-between; font-size:0.84rem; margin-bottom:6px;">
                <span>${difficultyBadge(lvl)}</span>
                <span style="font-weight:600; color:var(--text-secondary);">${item.completed} / ${item.total} Completed (${pct}%)</span>
              </div>
              <div class="progress-track">
                <div class="progress-fill ${barClass}" style="width: ${pct}%;"></div>
              </div>
            </div>
          `;
        })
        .join('');
    }

    // Recently Attempted Questions
    const recentContainer = document.getElementById('recent-attempts-list');
    if (recentContainer) {
      const items = data.recently_attempted_questions || [];
      if (items.length === 0) {
        recentContainer.innerHTML = `
          <div class="state-box">
            <p>No questions attempted yet. Start practicing in the Question Bank.</p>
            <a href="questions.html" class="btn btn-primary btn-sm" style="margin-top:10px;">Browse Questions</a>
          </div>
        `;
      } else {
        recentContainer.innerHTML = items
          .map(
            (att) => `
            <div class="activity-item">
              <div>
                <a href="question-detail.html?id=${att.question_id}" style="font-weight:600; color:var(--primary);">
                  #${att.question_id} ${escapeHtml(att.question_title)}
                </a>
                <div style="font-size:0.78rem; color:var(--text-muted); margin-top:3px;">
                  <span class="badge badge-category" style="margin-right:6px;">${escapeHtml(att.category)}</span>
                  ${difficultyBadge(att.difficulty)}
                  <span style="margin-left:8px;">Time: ${att.time_taken_minutes}m | ${formatTimestamp(att.attempted_at)}</span>
                </div>
              </div>
              <div style="display:flex; align-items:center; gap:10px;">
                ${statusBadge(att.status)}
                <a href="question-detail.html?id=${att.question_id}" class="btn btn-secondary btn-sm">Open</a>
              </div>
            </div>
          `
          )
          .join('');
      }
    }

    // Recommended Practice Topics
    const recContainer = document.getElementById('recommended-topics-list');
    if (recContainer) {
      const topics = data.recommended_topics || [];
      recContainer.innerHTML = topics
        .map(
          (t) => `
          <div class="activity-item" style="flex-direction:column; align-items:stretch; gap:8px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <div>
                <strong style="font-size:0.94rem;">${escapeHtml(t.category)}</strong>
                <span class="badge ${t.status === 'Strong' ? 'badge-completed' : t.status === 'In Progress' ? 'badge-attempted' : 'badge-intermediate'}" style="margin-left:8px;">
                  ${escapeHtml(t.status)}
                </span>
              </div>
              <a href="questions.html?category=${encodeURIComponent(t.category)}" class="btn btn-primary btn-sm">
                Practice Topic
              </a>
            </div>
            <div style="display:flex; justify-content:space-between; font-size:0.8rem; color:var(--text-secondary);">
              <span>Solved: ${t.completed_questions}/${t.total_questions} Questions</span>
              <span>Mastery Score: <strong>${t.mastery_score}%</strong></span>
            </div>
            <div class="progress-track">
              <div class="progress-fill" style="width:${Math.min(100, t.mastery_score)}%;"></div>
            </div>
          </div>
        `
        )
        .join('');
    }

    if (loadingBox) loadingBox.style.display = 'none';
    if (contentBox) contentBox.style.display = 'block';
  } catch (err) {
    if (loadingBox) loadingBox.style.display = 'none';
    if (errorBox) {
      errorBox.style.display = 'block';
      errorBox.innerHTML = `
        <h3 style="color:var(--danger); margin-bottom:8px;">Unable to Load Dashboard Data</h3>
        <p>${escapeHtml(err.message)}</p>
        <button class="btn btn-primary btn-sm" style="margin-top:12px;" onclick="loadDashboard()">Retry</button>
      `;
    }
  }
}

document.addEventListener('DOMContentLoaded', loadDashboard);
