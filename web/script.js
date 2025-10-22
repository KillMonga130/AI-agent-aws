const $ = (s) => document.querySelector(s);
const statusEl = $('#status');
const resultEl = $('#result');
const skeletonEl = $('#skeleton');
const stepsEl = $('#steps');
const opProgressEl = $('#opProgress');
const runBtn = $('#runBtn');
let stepTimer = null;
let stepIndex = 0;

async function getMock() {
  const res = await fetch('sample_response.json');
  return res.json();
}

function badgeClass(level) {
  const L = (level || '').toUpperCase();
  if (L === 'URGENT') return 'urgent';
  if (L === 'WARNING' || L === 'ADVISORY') return 'warn';
  return 'ok';
}

function render(data) {
  resultEl.classList.remove('hidden');
  const level = data.alert?.alert_level || 'INFO';
  const score = typeof data.alert?.risk_score === 'number' ? Math.round(data.alert.risk_score) : '—';
  const cls = badgeClass(level);
  const factors = data.alert?.risk_factors || {};
  const sources = (data.data_sources || []).join(', ') || '—';
  const latency = data.execution_time_seconds ?? '—';
  const timestamp = data.timestamp || '';

  // Build result markup with classes for staggered reveal
  resultEl.innerHTML = `
    <div class="grid stagger">
      <div class="mini-card">
        <div class="label">Alert</div>
        <div><span class="badge ${cls}">${level}</span></div>
      </div>
      <div class="mini-card">
        <div class="label">Risk score</div>
        <div class="progress" aria-label="Risk score"><i data-score="${typeof score === 'number' ? score : 0}"></i></div>
        <div class="meta">${score}/100</div>
      </div>
      <div class="mini-card">
        <div class="label">Latency</div>
        <div class="meta">${latency}s</div>
      </div>
    </div>

    <h4 class="fade-up" style="margin:14px 0 6px">Summary</h4>
    <p id="summaryText" class="typewriter" aria-live="polite"></p>

    <div class="grid stagger" style="margin-top:8px">
      <div class="mini-card"><div class="label">Wave height</div><div>${factors.wave_height || '—'}</div></div>
      <div class="mini-card"><div class="label">Wind speed</div><div>${factors.wind_speed || '—'}</div></div>
      <div class="mini-card"><div class="label">Visibility</div><div>${factors.visibility || '—'}</div></div>
      <div class="mini-card"><div class="label">Currents</div><div>${factors.currents || '—'}</div></div>
    </div>

    <h4 class="fade-up" style="margin:14px 0 6px">Recommendations</h4>
    <ul class="stagger">
      ${(data.alert?.recommendations || []).map(r => `<li>${r}</li>`).join('') || '<li>—</li>'}
    </ul>

    <div class="meta fade-up" style="margin-top:10px">Sources: ${sources} ${timestamp ? '• ' + timestamp : ''}</div>

    <details class="fade-up" style="margin-top:12px">
      <summary>Raw response</summary>
      <pre>${JSON.stringify(data, null, 2)}</pre>
    </details>
  `;

  // Animate risk bar fill after render using CSS transition
  const bar = resultEl.querySelector('.progress > i');
  const target = Number(bar?.dataset?.score || 0);
  requestAnimationFrame(() => {
    requestAnimationFrame(() => { if (bar) bar.style.width = `${target}%`; });
  });

  // Typewriter effect for the summary text
  typeText($('#summaryText'), data.response || '—', 12);
}

function setLoading(v) {
  if (v) {
    runBtn.disabled = true;
    runBtn.querySelector('.spinner').style.display = 'inline-block';
    skeletonEl.classList.remove('hidden');
    resultEl.classList.add('hidden');
    stepsEl.classList.remove('hidden');
    opProgressEl.classList.remove('hidden');
    startSteps();
  } else {
    runBtn.disabled = false;
    runBtn.querySelector('.spinner').style.display = 'none';
    skeletonEl.classList.add('hidden');
    stopSteps(true);
    stepsEl.classList.add('hidden');
    opProgressEl.classList.add('hidden');
  }
}

function startSteps() {
  // Reset
  stepIndex = 0;
  const items = stepsEl.querySelectorAll('.step');
  items.forEach((el, i) => el.classList.toggle('active', i === 0));
  setProgress(5);
  // Step through
  clearInterval(stepTimer);
  stepTimer = setInterval(() => {
    if (stepIndex < items.length - 1) {
      items[stepIndex]?.classList.remove('active');
      stepIndex++;
      items[stepIndex]?.classList.add('active');
      setProgress(Math.min(90, (stepIndex + 1) * Math.floor(100 / items.length)));
    }
  }, 700);
}

function stopSteps(finalize = false) {
  clearInterval(stepTimer);
  stepTimer = null;
  if (finalize) setProgress(100);
}

function setProgress(pct) {
  const bar = opProgressEl.querySelector('i');
  if (bar) bar.style.width = `${Math.max(0, Math.min(100, pct))}%`;
}

function typeText(el, text, cps = 12) {
  if (!el) return;
  el.textContent = '';
  let i = 0;
  const delay = Math.max(8, 1000 / cps);
  function tick() {
    if (i <= text.length) {
      el.textContent = text.slice(0, i);
      i += Math.ceil(Math.random() * 2); // slightly irregular typing
      setTimeout(tick, delay);
    }
  }
  tick();
}

async function run() {
  const query = $('#query').value.trim();
  const useMock = $('#useMock').checked;
  const endpoint = $('#apiEndpoint').value.trim();

  if (!query) {
    $('#query').value = 'Is it safe to sail from Cape Town to Mossel Bay tomorrow?';
  }

  statusEl.textContent = useMock ? 'Using mock data…' : 'Calling API…';
  setLoading(true);

  try {
    let data;
    if (useMock || !endpoint) {
      data = await getMock();
    } else {
      const res = await fetch(`${endpoint.replace(/\/$/, '')}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: query || 'Is it safe to sail…', session_id: 'demo' })
      });
      if (!res.ok) throw new Error(`API ${res.status}`);
      data = await res.json();
    }
    render(data);
    statusEl.textContent = 'Done';
  } catch (e) {
    statusEl.textContent = 'Fell back to mock (API error)';
    try {
      render(await getMock());
    } catch (_) {
      resultEl.classList.remove('hidden');
      resultEl.textContent = 'Unable to load demo data.';
    }
  } finally {
    setLoading(false);
  }
}

runBtn.addEventListener('click', run);

// Quick example chips
document.querySelectorAll('.pill[data-example]')?.forEach(el => {
  el.addEventListener('click', () => {
    $('#query').value = el.getAttribute('data-example');
    run();
  });
});

// Prefill endpoint from env-like global (optional) or querystring
(function init() {
  const params = new URLSearchParams(location.search);
  const qsEndpoint = params.get('endpoint');
  if (qsEndpoint) $('#apiEndpoint').value = qsEndpoint;
  const defaultEndpoint = window.API_ENDPOINT || '';
  if (defaultEndpoint) $('#apiEndpoint').value = defaultEndpoint;
  // Auto-run once to show something
  run();
})();
