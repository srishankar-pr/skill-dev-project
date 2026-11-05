/**
 * Quiz & Quiz Results Module (quiz.html and results.html)
 * Handles quiz selection, randomized MCQ loading, live timer, submission to POST /quizzes/{id}/submit,
 * and rendering detailed results & history.
 */

let activeQuiz = null;
let selectedAnswers = {};
let quizStartTime = null;
let timerInterval = null;

async function initQuizPage() {
  const catalogEl = document.getElementById('quiz-catalog-section');
  if (!catalogEl) return;

  await loadQuizCatalog();
  await loadRecentQuizHistoryTable('quiz-page-history-body');
}

async function loadQuizCatalog() {
  const grid = document.getElementById('quiz-catalog-grid');
  if (!grid) return;

  grid.innerHTML = `
    <div class="state-box" style="grid-column: 1 / -1;">
      <div class="spinner"></div>
      <p>Loading MCQ quizzes from SQLite...</p>
    </div>
  `;

  try {
    const quizzes = await apiFetch(`/quizzes?student_id=${STUDENT_ID}`);
    grid.innerHTML = quizzes
      .map(
        (qz) => `
        <div class="card" style="display:flex; flex-direction:column; justify-content:space-between;">
          <div class="card-body">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
              <span class="badge badge-category">${escapeHtml(qz.category)}</span>
              ${difficultyBadge(qz.difficulty)}
            </div>
            <h3 style="font-size:1.08rem; margin-bottom:8px;">${escapeHtml(qz.title)}</h3>
            <p style="font-size:0.86rem; color:var(--text-secondary); margin-bottom:14px;">
              ${escapeHtml(qz.description)}
            </p>
            <div style="display:flex; gap:14px; font-size:0.8rem; color:var(--text-muted); flex-wrap:wrap;">
              <span>Questions: ${qz.total_questions} Randomized MCQs</span>
              <span>Duration: ${qz.duration_minutes} Mins</span>
              <span>Pool: ${qz.available_pool_count} Qs</span>
            </div>
          </div>
          <div style="padding:14px 22px; background:var(--bg-subtle); border-top:1px solid var(--border-color); display:flex; justify-content:space-between; align-items:center;">
            <span style="font-size:0.8rem; font-weight:600; color:var(--text-secondary);">
              ${
                qz.best_score_percentage !== null
                  ? `Best Score: <strong style="color:var(--success-text);">${qz.best_score_percentage}%</strong> (${qz.attempts_count}x)`
                  : 'Not attempted yet'
              }
            </span>
            <button class="btn btn-primary btn-sm" onclick="startQuiz(${qz.id})">Start Quiz</button>
          </div>
        </div>
      `
      )
      .join('');
  } catch (err) {
    grid.innerHTML = `
      <div class="state-box" style="grid-column: 1 / -1;">
        <h3 style="color:var(--danger);">Failed to Load Quizzes</h3>
        <p>${escapeHtml(err.message)}</p>
      </div>
    `;
  }
}

async function startQuiz(quizId) {
  const catalogSection = document.getElementById('quiz-catalog-section');
  const runnerSection = document.getElementById('quiz-runner-section');
  const questionsContainer = document.getElementById('quiz-questions-container');

  try {
    const quizData = await apiFetch(`/quizzes/${quizId}?randomize=true`);
    activeQuiz = quizData;
    selectedAnswers = {};
    quizStartTime = Date.now();

    if (catalogSection) catalogSection.style.display = 'none';
    if (runnerSection) runnerSection.style.display = 'block';

    document.getElementById('active-quiz-title').textContent = quizData.title;
    document.getElementById('active-quiz-subtitle').textContent = `${quizData.questions.length} Randomized Questions | Select one option per question`;
    updateAnsweredProgress();

    questionsContainer.innerHTML = quizData.questions
      .map(
        (q, index) => `
        <div class="card" style="margin-bottom: 18px;" id="mcq-card-${q.id}">
          <div class="card-body">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
              <span style="font-weight:700; color:var(--primary); font-size:0.85rem;">
                Question ${index + 1} of ${quizData.questions.length}
              </span>
              <div style="display:flex; gap:6px;">
                <span class="badge badge-category">${escapeHtml(q.category)}</span>
                ${difficultyBadge(q.difficulty)}
              </div>
            </div>
            <h4 style="font-size:1rem; font-weight:600; margin-bottom:12px;">${escapeHtml(q.question_text)}</h4>
            <div class="quiz-option-list">
              ${['A', 'B', 'C', 'D']
                .map((optKey) => {
                  const optText = q[`option_${optKey.toLowerCase()}`];
                  return `
                    <div class="quiz-option-label" id="opt-${q.id}-${optKey}" onclick="selectQuizOption(${q.id}, '${optKey}')">
                      <span class="option-key">${optKey}</span>
                      <span>${escapeHtml(optText)}</span>
                    </div>
                  `;
                })
                .join('')}
            </div>
          </div>
        </div>
      `
      )
      .join('');

    startLiveTimer();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  } catch (err) {
    showToast(err.message, 'error');
  }
}

function selectQuizOption(questionId, optionKey) {
  selectedAnswers[String(questionId)] = optionKey;
  ['A', 'B', 'C', 'D'].forEach((k) => {
    const el = document.getElementById(`opt-${questionId}-${k}`);
    if (el) {
      if (k === optionKey) el.classList.add('selected');
      else el.classList.remove('selected');
    }
  });
  updateAnsweredProgress();
}

function updateAnsweredProgress() {
  if (!activeQuiz) return;
  const total = activeQuiz.questions.length;
  const answered = Object.keys(selectedAnswers).length;
  const counterEl = document.getElementById('quiz-answered-counter');
  if (counterEl) {
    counterEl.textContent = `${answered} / ${total} Answered`;
  }
}

function startLiveTimer() {
  clearInterval(timerInterval);
  const timerEl = document.getElementById('quiz-timer-display');
  timerInterval = setInterval(() => {
    if (!quizStartTime || !timerEl) return;
    const elapsedSec = Math.floor((Date.now() - quizStartTime) / 1000);
    const mins = String(Math.floor(elapsedSec / 60)).padStart(2, '0');
    const secs = String(elapsedSec % 60).padStart(2, '0');
    timerEl.textContent = `Time: ${mins}:${secs}`;
  }, 1000);
}

function cancelActiveQuiz() {
  clearInterval(timerInterval);
  activeQuiz = null;
  selectedAnswers = {};
  document.getElementById('quiz-runner-section').style.display = 'none';
  document.getElementById('quiz-catalog-section').style.display = 'block';
}

async function submitActiveQuiz() {
  if (!activeQuiz) return;

  const total = activeQuiz.questions.length;
  const answeredCount = Object.keys(selectedAnswers).length;

  if (answeredCount < total) {
    showToast(`Please answer all ${total} questions before submitting (${answeredCount}/${total} answered).`, 'error');
    return;
  }

  clearInterval(timerInterval);
  const elapsedSeconds = Math.max(1, Math.floor((Date.now() - quizStartTime) / 1000));
  const submitBtn = document.getElementById('btn-submit-quiz');
  if (submitBtn) submitBtn.disabled = true;

  try {
    const result = await apiFetch(`/quizzes/${activeQuiz.id}/submit`, {
      method: 'POST',
      body: JSON.stringify({
        student_id: STUDENT_ID,
        answers: selectedAnswers,
        time_taken_seconds: elapsedSeconds,
      }),
    });

    sessionStorage.setItem('latest_quiz_result', JSON.stringify(result));
    window.location.href = `results.html?attempt_id=${result.attempt_id}`;
  } catch (err) {
    if (submitBtn) submitBtn.disabled = false;
    showToast(err.message, 'error');
  }
}

async function loadRecentQuizHistoryTable(tbodyId) {
  const tbody = document.getElementById(tbodyId);
  if (!tbody) return;

  try {
    const history = await apiFetch(`/students/${STUDENT_ID}/quiz-history`);
    if (history.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; color:var(--text-muted);">No quiz attempts recorded yet.</td></tr>`;
      return;
    }

    tbody.innerHTML = history
      .map(
        (h) => `
        <tr>
          <td><strong>#${h.attempt_id}</strong></td>
          <td>${escapeHtml(h.quiz_title)}</td>
          <td><span class="badge badge-category">${escapeHtml(h.category)}</span></td>
          <td><strong>${h.score} / ${h.total_questions}</strong> (${h.percentage}%)</td>
          <td>${h.time_taken_seconds}s</td>
          <td>
            <a href="results.html?attempt_id=${h.attempt_id}" class="btn btn-secondary btn-sm">Review Answers</a>
          </td>
        </tr>
      `
      )
      .join('');
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="6" style="color:var(--danger);">${escapeHtml(err.message)}</td></tr>`;
  }
}

/* ==========================================================================
   Quiz Results Page Logic (results.html)
   ========================================================================== */

async function initResultsPage() {
  const container = document.getElementById('results-page-container');
  if (!container) return;

  const params = new URLSearchParams(window.location.search);
  const attemptId = params.get('attempt_id');

  let resultData = null;

  try {
    if (attemptId) {
      resultData = await apiFetch(`/quizzes/attempts/${attemptId}`);
    } else {
      const cached = sessionStorage.getItem('latest_quiz_result');
      if (cached) {
        resultData = JSON.parse(cached);
      } else {
        const history = await apiFetch(`/students/${STUDENT_ID}/quiz-history`);
        if (history.length > 0) {
          resultData = await apiFetch(`/quizzes/attempts/${history[0].attempt_id}`);
        }
      }
    }

    if (!resultData) {
      container.innerHTML = `
        <div class="state-box">
          <h3>No Quiz Results Found</h3>
          <p style="margin-top:6px;">Take a quiz first to view your score breakdown and answer explanations.</p>
          <a href="quiz.html" class="btn btn-primary" style="margin-top:14px;">Take a Quiz Now</a>
        </div>
      `;
      return;
    }

    renderQuizResultDetails(resultData);
    await loadRecentQuizHistoryTable('results-history-tbody');
  } catch (err) {
    container.innerHTML = `
      <div class="state-box">
        <h3 style="color:var(--danger);">Unable to Load Quiz Result</h3>
        <p>${escapeHtml(err.message)}</p>
        <a href="quiz.html" class="btn btn-primary btn-sm" style="margin-top:12px;">Back to Quizzes</a>
      </div>
    `;
  }
}

function renderQuizResultDetails(result) {
  document.getElementById('res-quiz-title').textContent = result.quiz_title;
  document.getElementById('res-score-value').textContent = `${result.score} / ${result.total_questions}`;
  document.getElementById('res-percentage').textContent = `${result.percentage}%`;
  document.getElementById('res-grade').textContent = result.grade;
  document.getElementById('res-time').textContent = `${result.time_taken_seconds}s`;

  const reviewList = document.getElementById('res-reviews-list');
  if (!reviewList) return;

  reviewList.innerHTML = (result.reviews || [])
    .map((rev, idx) => {
      const statusClass = rev.is_correct ? 'correct' : 'incorrect';
      const badgeHtml = rev.is_correct
        ? `<span class="badge badge-completed">Correct (+1)</span>`
        : `<span class="badge badge-advanced">Incorrect (0)</span>`;

      const optionMap = {
        A: rev.option_a,
        B: rev.option_b,
        C: rev.option_c,
        D: rev.option_d,
      };

      return `
        <div class="review-card ${statusClass}">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px; flex-wrap:wrap; gap:8px;">
            <span style="font-weight:700; font-size:0.86rem;">Question ${idx + 1} | ${escapeHtml(rev.category)}</span>
            ${badgeHtml}
          </div>
          <h4 style="font-size:0.98rem; margin-bottom:12px;">${escapeHtml(rev.question_text)}</h4>
          <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap:8px; font-size:0.85rem; margin-bottom:12px;">
            ${['A', 'B', 'C', 'D']
              .map((key) => {
                const isCorrectOpt = key === rev.correct_option;
                const isSelectedOpt = key === rev.selected_option;
                let bg = 'var(--bg-subtle)';
                let border = 'var(--border-color)';
                if (isCorrectOpt) {
                  bg = 'var(--success-bg)';
                  border = 'var(--success)';
                } else if (isSelectedOpt && !rev.is_correct) {
                  bg = 'var(--danger-bg)';
                  border = 'var(--danger)';
                }
                return `
                  <div style="padding:8px 12px; border-radius:6px; background:${bg}; border:1px solid ${border};">
                    <strong>${key}.</strong> ${escapeHtml(optionMap[key])}
                    ${isCorrectOpt ? ' <strong style="color:var(--success-text);">(Correct)</strong>' : ''}
                    ${isSelectedOpt && !isCorrectOpt ? ' <strong style="color:var(--danger-text);">(Your Choice)</strong>' : ''}
                  </div>
                `;
              })
              .join('')}
          </div>
          <div class="hint-box" style="margin-top:8px;">
            <strong>Explanation:</strong> ${escapeHtml(rev.explanation)}
          </div>
        </div>
      `;
    })
    .join('');
}

document.addEventListener('DOMContentLoaded', () => {
  initQuizPage();
  initResultsPage();
});
