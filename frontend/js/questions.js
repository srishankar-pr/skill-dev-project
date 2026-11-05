/**
 * Questions Module (questions.html and question-detail.html)
 * Handles browsing, searching, filtering, viewing details, and submitting attempts/completions via Fetch API.
 */

let allQuestionsCache = [];

async function initQuestionBankPage() {
  const grid = document.getElementById('questions-grid');
  if (!grid) return;

  // Pre-fill category from query parameter if navigated from Dashboard
  const params = new URLSearchParams(window.location.search);
  const initialCat = params.get('category');
  const categorySelect = document.getElementById('filter-category');
  if (initialCat && categorySelect) {
    categorySelect.value = initialCat;
  }

  const searchInput = document.getElementById('filter-search');
  const difficultySelect = document.getElementById('filter-difficulty');
  const statusSelect = document.getElementById('filter-status');
  const resetBtn = document.getElementById('reset-filters-btn');

  let debounceTimer = null;
  if (searchInput) {
    searchInput.addEventListener('input', () => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(fetchAndRenderQuestions, 220);
    });
  }
  if (categorySelect) categorySelect.addEventListener('change', fetchAndRenderQuestions);
  if (difficultySelect) difficultySelect.addEventListener('change', fetchAndRenderQuestions);
  if (statusSelect) statusSelect.addEventListener('change', fetchAndRenderQuestions);

  if (resetBtn) {
    resetBtn.addEventListener('click', () => {
      if (searchInput) searchInput.value = '';
      if (categorySelect) categorySelect.value = 'all';
      if (difficultySelect) difficultySelect.value = 'all';
      if (statusSelect) statusSelect.value = 'all';
      fetchAndRenderQuestions();
    });
  }

  await fetchAndRenderQuestions();
}

async function fetchAndRenderQuestions() {
  const grid = document.getElementById('questions-grid');
  const countLabel = document.getElementById('questions-count-label');
  if (!grid) return;

  const search = (document.getElementById('filter-search')?.value || '').trim();
  const category = document.getElementById('filter-category')?.value || 'all';
  const difficulty = document.getElementById('filter-difficulty')?.value || 'all';
  const status = document.getElementById('filter-status')?.value || 'all';

  grid.innerHTML = `
    <div class="state-box" style="grid-column: 1 / -1;">
      <div class="spinner"></div>
      <p>Fetching questions from SQLite...</p>
    </div>
  `;

  try {
    const qs = new URLSearchParams({ student_id: STUDENT_ID });
    if (category !== 'all') qs.set('category', category);
    if (difficulty !== 'all') qs.set('difficulty', difficulty);
    if (search) qs.set('search', search);
    if (status !== 'all') qs.set('status', status);

    const questions = await apiFetch(`/questions?${qs.toString()}`);
    allQuestionsCache = questions;

    if (countLabel) {
      const completedCount = questions.filter((q) => q.status === 'Completed').length;
      countLabel.textContent = `Showing ${questions.length} questions (${completedCount} completed)`;
    }

    if (questions.length === 0) {
      grid.innerHTML = `
        <div class="state-box" style="grid-column: 1 / -1;">
          <h3>No matching questions found</h3>
          <p style="margin-top:6px;">Try clearing your search filter or selecting a different category.</p>
        </div>
      `;
      return;
    }

    grid.innerHTML = questions
      .map(
        (q) => `
        <div class="question-card">
          <div>
            <div class="question-card-top">
              <span class="question-id-tag">#Q-${String(q.id).padStart(2, '0')}</span>
              <div style="display:flex; gap:6px; align-items:center;">
                <span class="badge badge-category">${escapeHtml(q.category)}</span>
                ${difficultyBadge(q.difficulty)}
              </div>
            </div>
            <h3>
              <a href="question-detail.html?id=${q.id}">${escapeHtml(q.title)}</a>
            </h3>
            <p>${escapeHtml(q.description)}</p>
          </div>
          <div class="question-card-footer">
            <div>${statusBadge(q.status)}</div>
            <div style="display:flex; gap:8px;">
              ${
                q.status !== 'Completed'
                  ? `<button class="btn btn-secondary btn-sm" onclick="quickMarkCompleted(${q.id})">Mark Done</button>`
                  : ''
              }
              <a href="question-detail.html?id=${q.id}" class="btn btn-primary btn-sm">Solve</a>
            </div>
          </div>
        </div>
      `
      )
      .join('');
  } catch (err) {
    grid.innerHTML = `
      <div class="state-box" style="grid-column: 1 / -1;">
        <h3 style="color:var(--danger);">Error Loading Questions</h3>
        <p>${escapeHtml(err.message)}</p>
      </div>
    `;
  }
}

async function quickMarkCompleted(questionId) {
  try {
    const q = allQuestionsCache.find((item) => item.id === questionId);
    await apiFetch('/attempts', {
      method: 'POST',
      body: JSON.stringify({
        student_id: STUDENT_ID,
        question_id: questionId,
        submitted_code: (q && q.starter_code) || '# Completed via Quick Mark',
        status: 'Completed',
        notes: 'Marked as completed from Question Bank.',
        time_taken_minutes: 10,
      }),
    });
    showToast(`Question #${questionId} marked as Completed!`, 'success');
    await fetchAndRenderQuestions();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

/* ==========================================================================
   Question Detail Page Logic (question-detail.html)
   ========================================================================== */

let currentQuestion = null;

async function initQuestionDetailPage() {
  const detailContainer = document.getElementById('question-detail-workspace');
  if (!detailContainer) return;

  const params = new URLSearchParams(window.location.search);
  const questionId = parseInt(params.get('id') || '1', 10);

  await loadQuestionDetail(questionId);

  const saveAttemptBtn = document.getElementById('btn-save-attempt');
  const markCompleteBtn = document.getElementById('btn-mark-completed');
  const toggleHintBtn = document.getElementById('btn-toggle-hint');

  if (saveAttemptBtn) {
    saveAttemptBtn.addEventListener('click', () => submitQuestionAttempt(questionId, 'Attempted'));
  }
  if (markCompleteBtn) {
    markCompleteBtn.addEventListener('click', () => submitQuestionAttempt(questionId, 'Completed'));
  }
  if (toggleHintBtn) {
    toggleHintBtn.addEventListener('click', () => {
      const box = document.getElementById('explanation-box');
      if (box) {
        const isHidden = box.style.display === 'none';
        box.style.display = isHidden ? 'block' : 'none';
        toggleHintBtn.textContent = isHidden ? 'Hide Approach and Hint' : 'Show Approach and Hint';
      }
    });
  }
}

async function loadQuestionDetail(questionId) {
  const loadingEl = document.getElementById('detail-loading');
  const workspaceEl = document.getElementById('question-detail-workspace');
  const errorEl = document.getElementById('detail-error');

  if (loadingEl) loadingEl.style.display = 'block';
  if (workspaceEl) workspaceEl.style.display = 'none';
  if (errorEl) errorEl.style.display = 'none';

  try {
    const q = await apiFetch(`/questions/${questionId}?student_id=${STUDENT_ID}`);
    currentQuestion = q;

    document.getElementById('q-id-label').textContent = `Question #${q.id}`;
    document.getElementById('q-title').textContent = q.title;
    document.getElementById('q-category-badge').textContent = q.category;
    document.getElementById('q-difficulty-slot').innerHTML = difficultyBadge(q.difficulty);
    document.getElementById('q-status-slot').innerHTML = statusBadge(q.status);
    document.getElementById('q-attempts-count').textContent = `${q.attempts_count} attempt(s) logged`;
    document.getElementById('q-description').textContent = q.description;
    document.getElementById('q-sample-input').textContent = q.sample_input;
    document.getElementById('q-expected-output').textContent = q.expected_output;
    document.getElementById('q-explanation').textContent = q.explanation;

    const codeEditor = document.getElementById('solution-code');
    if (codeEditor) {
      codeEditor.value = q.latest_code || q.starter_code || '# Write your Python solution here\n';
    }
    const notesInput = document.getElementById('solution-notes');
    if (notesInput) {
      notesInput.value = q.latest_notes || '';
    }

    // Prev / Next navigation buttons
    const prevLink = document.getElementById('prev-question-link');
    const nextLink = document.getElementById('next-question-link');
    if (prevLink) {
      if (q.id > 1) {
        prevLink.href = `question-detail.html?id=${q.id - 1}`;
        prevLink.style.visibility = 'visible';
      } else {
        prevLink.style.visibility = 'hidden';
      }
    }
    if (nextLink) {
      if (q.id < 32) {
        nextLink.href = `question-detail.html?id=${q.id + 1}`;
        nextLink.style.visibility = 'visible';
      } else {
        nextLink.style.visibility = 'hidden';
      }
    }

    if (loadingEl) loadingEl.style.display = 'none';
    if (workspaceEl) workspaceEl.style.display = 'grid';
  } catch (err) {
    if (loadingEl) loadingEl.style.display = 'none';
    if (errorEl) {
      errorEl.style.display = 'block';
      errorEl.innerHTML = `
        <h3 style="color:var(--danger);">Question Not Found</h3>
        <p style="margin-top:6px;">${escapeHtml(err.message)}</p>
        <a href="questions.html" class="btn btn-primary btn-sm" style="margin-top:12px;">Back to Question Bank</a>
      `;
    }
  }
}

async function submitQuestionAttempt(questionId, statusValue) {
  const code = document.getElementById('solution-code')?.value || '';
  const notes = document.getElementById('solution-notes')?.value || '';
  const timeMinutes = parseInt(document.getElementById('solution-time')?.value || '10', 10);

  if (!code.trim()) {
    showToast('Please write or keep starter Python code before submitting.', 'error');
    return;
  }

  try {
    await apiFetch('/attempts', {
      method: 'POST',
      body: JSON.stringify({
        student_id: STUDENT_ID,
        question_id: questionId,
        submitted_code: code,
        status: statusValue,
        notes: notes,
        time_taken_minutes: isNaN(timeMinutes) || timeMinutes < 1 ? 10 : timeMinutes,
      }),
    });

    showToast(
      statusValue === 'Completed'
        ? 'Solution saved and question marked as Completed!'
        : 'Attempt saved to SQLite database!',
      'success'
    );
    await loadQuestionDetail(questionId);
  } catch (err) {
    showToast(err.message, 'error');
  }
}

document.addEventListener('DOMContentLoaded', () => {
  initQuestionBankPage();
  initQuestionDetailPage();
});
