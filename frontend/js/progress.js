/**
 * Progress Analytics Module (progress.html)
 * Fetches dynamic student analytics from GET /students/{student_id}/progress
 * and renders interactive CSS/SVG charts, weak topic alerts, quiz history, and recent activity.
 */

async function loadProgressAnalytics() {
  const loadingEl = document.getElementById('progress-loading');
  const contentEl = document.getElementById('progress-content');
  const errorEl = document.getElementById('progress-error');

  if (loadingEl) loadingEl.style.display = 'block';
  if (contentEl) contentEl.style.display = 'none';
  if (errorEl) errorEl.style.display = 'none';

  try {
    const data = await apiFetch(`/students/${STUDENT_ID}/progress`);

    // Top Summary Metrics
    document.getElementById('prog-attempted').textContent = `${data.questions_attempted} / ${data.total_questions}`;
    document.getElementById('prog-completed').textContent = `${data.questions_completed} (${data.completion_percentage}%)`;
    document.getElementById('prog-avg-quiz').textContent = `${data.average_quiz_score}%`;
    document.getElementById('prog-readiness').textContent = `${data.overall_readiness_score}%`;
    document.getElementById('prog-study-time').textContent = `${data.total_study_minutes} mins logged`;
    document.getElementById('prog-high-quiz').textContent = `Highest Score: ${data.highest_quiz_score}% (${data.total_quizzes_taken} Quizzes)`;

    // Topic-Wise Performance Bar Chart
    const topicChartEl = document.getElementById('topic-performance-chart');
    if (topicChartEl) {
      topicChartEl.innerHTML = (data.topic_performance || [])
        .map((t) => {
          const fillClass =
            t.mastery_score >= 70 ? 'success' : t.mastery_score >= 40 ? '' : 'warning';
          const quizText =
            t.quiz_accuracy !== null ? `Quiz Acc: ${t.quiz_accuracy}%` : 'Quiz: N/A';
          return `
            <div style="margin-bottom: 16px;">
              <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px; font-size:0.86rem;">
                <div>
                  <strong>${escapeHtml(t.category)}</strong>
                  <span style="color:var(--text-muted); margin-left:8px;">
                    (${t.completed_questions}/${t.total_questions} Solved | ${quizText})
                  </span>
                </div>
                <span style="font-weight:700; color:var(--primary);">${t.mastery_score}% Mastery</span>
              </div>
              <div class="progress-track" style="height:12px;">
                <div class="progress-fill ${fillClass}" style="width:${Math.min(100, t.mastery_score)}%;"></div>
              </div>
            </div>
          `;
        })
        .join('');
    }

    // Weak Topics & Strong Topics
    const weakEl = document.getElementById('weak-topics-container');
    if (weakEl) {
      const weakList = data.weak_topics || [];
      weakEl.innerHTML = weakList
        .map(
          (w) => `
          <div class="activity-item" style="border-left: 4px solid var(--warning);">
            <div>
              <strong>${escapeHtml(w.category)}</strong>
              <div style="font-size:0.8rem; color:var(--text-secondary);">
                Completion: ${w.completion_rate}% (${w.completed_questions}/${w.total_questions}) | Mastery: ${w.mastery_score}%
              </div>
            </div>
            <a href="questions.html?category=${encodeURIComponent(w.category)}" class="btn btn-primary btn-sm">
              Practice Now
            </a>
          </div>
        `
        )
        .join('');
    }

    // Quiz Performance Visual Trend Chart
    const quizTrendEl = document.getElementById('quiz-trend-chart');
    if (quizTrendEl) {
      const history = (data.quiz_history || []).slice(0, 8).reverse();
      if (history.length === 0) {
        quizTrendEl.innerHTML = `<div class="state-box"><p>No quizzes completed yet.</p></div>`;
      } else {
        quizTrendEl.innerHTML = `
          <div style="display:flex; align-items:flex-end; gap:14px; height:190px; padding:20px 10px 10px; border-bottom:1px solid var(--border-color);">
            ${history
              .map(
                (h) => `
                <div style="flex:1; display:flex; flex-direction:column; align-items:center; height:100%; justify-content:flex-end;">
                  <span style="font-size:0.75rem; font-weight:700; margin-bottom:6px; color:var(--primary);">${h.percentage}%</span>
                  <div style="width:100%; max-width:48px; height:${Math.max(12, h.percentage)}%; background:linear-gradient(180deg, var(--primary) 0%, var(--accent) 100%); border-radius:6px 6px 0 0;" title="${escapeHtml(h.quiz_title)}"></div>
                </div>
              `
              )
              .join('')}
          </div>
          <div style="display:flex; gap:14px; padding-top:8px;">
            ${history
              .map(
                (h) => `
                <div style="flex:1; text-align:center; font-size:0.74rem; color:var(--text-muted); overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">
                  #${h.attempt_id} ${escapeHtml(h.category)}
                </div>
              `
              )
              .join('')}
          </div>
        `;
      }
    }

    // Unified Recent Activity Feed
    const activityEl = document.getElementById('recent-activity-feed');
    if (activityEl) {
      const activities = data.recent_activity || [];
      if (activities.length === 0) {
        activityEl.innerHTML = `<div class="state-box"><p>No recent activity recorded.</p></div>`;
      } else {
        activityEl.innerHTML = activities
          .map((act) => {
            const isQuiz = act.activity_type === 'quiz_attempt';
            const tag = isQuiz ? 'QUIZ' : 'CODE';
            const link = isQuiz
              ? `results.html?attempt_id=${act.reference_id}`
              : `question-detail.html?id=${act.reference_id}`;
            return `
              <div class="activity-item">
                <div style="display:flex; align-items:center; gap:12px;">
                  <span class="badge ${isQuiz ? 'badge-intermediate' : 'badge-category'}">${tag}</span>
                  <div>
                    <a href="${link}" style="font-weight:600; color:var(--text-main);">${escapeHtml(act.title)}</a>
                    <div style="font-size:0.78rem; color:var(--text-muted);">
                      ${escapeHtml(act.subtitle)} | ${escapeHtml(act.category)} | ${formatTimestamp(act.timestamp)}
                    </div>
                  </div>
                </div>
                <span class="badge ${isQuiz ? 'badge-category' : 'badge-completed'}">${escapeHtml(act.status_or_score)}</span>
              </div>
            `;
          })
          .join('');
      }
    }

    if (loadingEl) loadingEl.style.display = 'none';
    if (contentEl) contentEl.style.display = 'block';
  } catch (err) {
    if (loadingEl) loadingEl.style.display = 'none';
    if (errorEl) {
      errorEl.style.display = 'block';
      errorEl.innerHTML = `
        <h3 style="color:var(--danger);">Failed to Load Progress Analytics</h3>
        <p>${escapeHtml(err.message)}</p>
      `;
    }
  }
}

document.addEventListener('DOMContentLoaded', loadProgressAnalytics);
