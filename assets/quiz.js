/* ═══════════════════════════════════════════════════════════
   Seerah Quiz — Shared Quiz Engine
   ═══════════════════════════════════════════════════════════ */

// ── State ────────────────────────────────────────────────────
let QS = [];          // full question bank for this world
let SESSION = [];     // current session questions (filtered/shuffled)
let CUR = 0;          // current question index
let SCORE = 0;
let ANSWERED = false;
let TOPIC_FILTER = 'all';
let DIFF_FILTER  = 'all';
let WORLD_KEY    = '';  // localStorage key e.g. "seerah-quiz-world1"

// ── Init ─────────────────────────────────────────────────────
function initQuiz(questions, worldKey) {
  QS = questions;
  WORLD_KEY = worldKey;
  renderTopicPills();
  renderStats();
  showScreen('home');
}

// ── Topic pills ───────────────────────────────────────────────
function renderTopicPills() {
  const topics = ['all', ...new Set(QS.map(q => q.topic))].sort((a,b) => a === 'all' ? -1 : a.localeCompare(b));
  const container = document.getElementById('topic-pills');
  if (!container) return;
  container.innerHTML = topics.map(t =>
    `<button class="topic-pill${t === TOPIC_FILTER ? ' active' : ''}" onclick="setTopic('${escHtml(t)}')">${t === 'all' ? 'All Topics' : t.split(' · ').pop()}</button>`
  ).join('');
}

function setTopic(t) {
  TOPIC_FILTER = t;
  renderTopicPills();
}

function setDiff(d) {
  DIFF_FILTER = d;
  document.querySelectorAll('.diff-btn').forEach(b => b.classList.toggle('active', b.dataset.diff === d));
}

// ── Start quiz ────────────────────────────────────────────────
function startQuiz() {
  let pool = QS.slice();
  if (TOPIC_FILTER !== 'all') pool = pool.filter(q => q.topic === TOPIC_FILTER);
  if (DIFF_FILTER  !== 'all') pool = pool.filter(q => q.difficulty === DIFF_FILTER);
  if (pool.length === 0) { alert('No questions match your filters. Try a different selection.'); return; }
  SESSION = shuffle(pool);
  CUR = 0; SCORE = 0; ANSWERED = false;
  showScreen('quiz');
  renderQuestion();
}

// ── Render question ───────────────────────────────────────────
function renderQuestion() {
  if (CUR >= SESSION.length) { showResults(); return; }
  ANSWERED = false;
  const q = SESSION[CUR];
  const pct = Math.round((CUR / SESSION.length) * 100);

  document.getElementById('q-progress-fill').style.width = pct + '%';
  document.getElementById('q-counter').textContent = `${CUR+1} / ${SESSION.length}`;
  document.getElementById('q-topic').textContent = q.topic.split(' · ').pop();
  document.getElementById('q-diff').className = `badge badge-${q.difficulty}`;
  document.getElementById('q-diff').textContent = q.difficulty.charAt(0).toUpperCase() + q.difficulty.slice(1);
  document.getElementById('q-text').textContent = q.q;
  document.getElementById('q-explain').style.display = 'none';
  document.getElementById('q-next-btn').style.display = 'none';

  const letters = ['A','B','C','D'];
  const optsEl = document.getElementById('q-options');
  optsEl.innerHTML = q.opts.map((opt, i) =>
    `<button class="opt-btn" onclick="answer(${i})" id="opt-${i}">
      <span class="opt-letter">${letters[i]}</span>
      <span>${escHtml(opt.replace(/^[A-D]\.\s*/,''))}</span>
    </button>`
  ).join('');
}

// ── Answer ────────────────────────────────────────────────────
function answer(idx) {
  if (ANSWERED) return;
  ANSWERED = true;
  const q = SESSION[CUR];
  const correct = q.correct;

  document.querySelectorAll('.opt-btn').forEach((b,i) => {
    b.disabled = true;
    if (i === correct) b.classList.add('correct');
    else if (i === idx) b.classList.add('wrong');
  });

  if (idx === correct) {
    SCORE++;
  } else {
    document.getElementById('opt-' + idx).classList.add('shake');
  }

  if (q.explain) {
    const el = document.getElementById('q-explain');
    el.textContent = '💡 ' + q.explain;
    el.style.display = 'block';
  }

  document.getElementById('q-next-btn').style.display = 'inline-flex';
  saveProgress();
}

function nextQuestion() {
  CUR++;
  renderQuestion();
}

// ── Results ───────────────────────────────────────────────────
function showResults() {
  showScreen('results');
  const pct = Math.round((SCORE / SESSION.length) * 100);
  document.getElementById('res-score').textContent = pct + '%';
  document.getElementById('res-correct').textContent = SCORE;
  document.getElementById('res-total').textContent = SESSION.length;

  let msg = pct >= 90 ? '🌟 Excellent! Masha\'Allah!' :
            pct >= 70 ? '✅ Well done! Keep going!' :
            pct >= 50 ? '📖 Good effort. Review and retry!' :
                        '💪 Keep studying. You\'ll get there!';
  document.getElementById('res-msg').textContent = msg;

  // Save completion if score >= 70%
  if (pct >= 70) markCompleted(pct);
}

// ── Progress & completion ─────────────────────────────────────
function saveProgress() {
  const data = getStoredData();
  data.lastScore = SCORE;
  data.lastTotal = SESSION.length;
  localStorage.setItem(WORLD_KEY, JSON.stringify(data));
}

function markCompleted(pct) {
  const data = getStoredData();
  if (!data.completed || pct > (data.bestScore || 0)) {
    data.completed = true;
    data.bestScore = pct;
    data.completedDate = new Date().toLocaleDateString('en-GB', {day:'numeric',month:'long',year:'numeric'});
    localStorage.setItem(WORLD_KEY, JSON.stringify(data));
  }
}

function getStoredData() {
  try { return JSON.parse(localStorage.getItem(WORLD_KEY)) || {}; }
  catch { return {}; }
}

function renderStats() {
  const data = getStoredData();
  const el = document.getElementById('home-stats');
  if (!el) return;
  if (data.completed) {
    el.innerHTML = `<div class="badge badge-gold">✓ Completed · Best: ${data.bestScore}%</div>`;
  } else if (data.lastScore !== undefined) {
    el.innerHTML = `<div class="muted" style="font-size:0.85rem">Last score: ${Math.round(data.lastScore/data.lastTotal*100)}%</div>`;
  }
}

// ── Certificate ───────────────────────────────────────────────
function showCertificate() {
  const name = prompt('Enter your name for the certificate:', localStorage.getItem('sq-student-name') || '');
  if (!name) return;
  localStorage.setItem('sq-student-name', name);

  const data = getStoredData();
  const pct  = data.bestScore || Math.round((SCORE / SESSION.length) * 100);
  const date = data.completedDate || new Date().toLocaleDateString('en-GB', {day:'numeric',month:'long',year:'numeric'});

  document.getElementById('cert-wrapper').style.display = 'block';
  generateCertificate({
    name:       name,
    worldName:  WORLD_NAME,
    worldEmoji: WORLD_EMOJI,
    score:      pct,
    total:      SESSION.length || QS.length,
    date:       date,
    canvasId:   'cert-canvas'
  });

  document.getElementById('cert-wrapper').scrollIntoView({behavior:'smooth'});
}

function downloadCert() {
  const name = (localStorage.getItem('sq-student-name') || 'student').replace(/\s+/g,'-').toLowerCase();
  downloadCertificate('cert-canvas', `certificate-${WORLD_NAME.toLowerCase().replace(/\s+/g,'-')}-${name}.png`);
}

// ── Screen management ─────────────────────────────────────────
function showScreen(id) {
  document.querySelectorAll('.screen').forEach(s => s.style.display = 'none');
  const el = document.getElementById('screen-' + id);
  if (el) { el.style.display = 'block'; el.classList.add('fade-in'); }
}

// ── Utilities ─────────────────────────────────────────────────
function shuffle(arr) {
  const a = arr.slice();
  for (let i = a.length-1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i+1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

function escHtml(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
