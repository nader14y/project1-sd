"use strict";

const gameRoot = document.querySelector("#game");
const notice = document.querySelector("#notice");
const boardRoot = document.querySelector("#leaderboard");
const statusLabel = document.querySelector("#game-status");
const fa = new Intl.NumberFormat("fa-IR", { maximumFractionDigits: 1 });
let state = { match: null, leaderboard: [], rules: { rounds: 5, time_limit: 30, points: 10, speed_bonus: 3 } };
let csrf = "";
let busy = false;
let initialized = false;
let showSetup = false;
let renderKey = "";
let deadline = 0;
let names = ["", ""];

function escapeHTML(value) {
  return String(value ?? "").replace(/[&<>"']/g, char => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[char]);
}
const e = escapeHTML;

function message(text, retry = false) {
  notice.replaceChildren(document.createTextNode(text));
  notice.hidden = !text;
  if (retry) {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = "تلاش دوباره";
    button.addEventListener("click", () => sync(true));
    notice.append(button);
  }
}

async function request(path, body) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 10000);
  try {
    const response = await fetch(path, {
      method: body === undefined ? "GET" : "POST",
      headers: body === undefined ? {} : { "Content-Type": "application/json", "X-CSRF-Token": csrf },
      body: body === undefined ? undefined : JSON.stringify(body),
      credentials: "same-origin", cache: "no-store", signal: controller.signal,
    });
    const data = await response.json();
    if (!response.ok) {
      const error = new Error(data.error?.message || "درخواست انجام نشد؛ دوباره تلاش کنید.");
      error.status = response.status;
      throw error;
    }
    return data;
  } catch (error) {
    if (error.status) throw error;
    throw new Error("ارتباط با سرور برقرار نشد. اتصال را بررسی کنید؛ سپس وضعیت بازی را تازه کنید.");
  } finally {
    clearTimeout(timeout);
  }
}

function accept(data) {
  state = { ...state, ...data };
  if (data.csrf_token) csrf = data.csrf_token;
  initialized = true;
  if (state.match?.phase === "answering") {
    deadline = performance.now() + state.match.remaining_seconds * 1000;
  }
  drawBoard();
  draw();
}

async function sync(explicit = false) {
  if (busy) return;
  busy = true;
  try {
    const data = await request("/api/state");
    accept(data);
    if (explicit) message("");
    if (data.expired) message("بازی قبلی منقضی شده است. یک رقابت تازه شروع کنید.");
  } catch (error) {
    message(error.message, true);
    if (!initialized) {
      gameRoot.innerHTML = '<div class="loading"><p>سرور بازی در دسترس نیست.</p><button class="secondary-button" data-action="retry">تلاش دوباره</button></div>';
    }
  } finally {
    busy = false;
    setBusy(false);
  }
}

function setBusy(value) {
  gameRoot.setAttribute("aria-busy", String(value));
  gameRoot.querySelectorAll("button, input").forEach(control => { control.disabled = value; });
}

async function mutate(path, body) {
  if (busy) return;
  busy = true;
  setBusy(true);
  message("");
  try {
    const data = await request(path, body);
    showSetup = false;
    accept(data);
    const heading = gameRoot.querySelector("h2");
    if (heading) { heading.tabIndex = -1; heading.focus({ preventScroll: true }); }
  } catch (error) {
    message(error.message, true);
    // Recover an accepted-but-lost response and refresh stale turns/CSRF tokens.
    if (!error.status || [403, 404, 409].includes(error.status)) {
      try { accept(await request("/api/state")); } catch { /* The retry control stays available. */ }
    }
  } finally {
    busy = false;
    setBusy(false);
  }
}

function setupMarkup() {
  const rules = state.rules;
  return `<div class="setup-content">
    <span class="mini-tag"><span aria-hidden="true">✦</span> یک نبرد تازه</span>
    <h2>رقیب امروزت کیه؟</h2><p class="subtitle">اسم‌هاتون رو بنویسید؛ بقیه‌اش با ما.</p>
    <form id="new-game-form">
      <div class="player-fields">${[0, 1].map(index => `<div class="player-field">
        <label for="player-${index}"><span class="player-dot"></span> بازیکن ${index === 0 ? "اول" : "دوم"}</label>
        <div class="input-wrap"><span class="input-avatar" aria-hidden="true">♙</span><input id="player-${index}" name="player${index + 1}" placeholder="${index === 0 ? "مثلاً: سارا" : "مثلاً: علی"}" value="${e(names[index])}" maxlength="30" required autocomplete="off" spellcheck="false" aria-label="نام بازیکن ${index === 0 ? "اول" : "دوم"}"></div>
      </div>`).join("")}</div>
      <div class="match-facts"><div class="fact"><b>${fa.format(rules.rounds)}</b><small>راند در هر بازی</small></div><div class="fact"><b>${fa.format(rules.time_limit)} <span>ثانیه</span></b><small>فرصت هر پاسخ</small></div><div class="fact"><b>+${fa.format(rules.points)}</b><small>امتیاز پاسخ درست</small></div></div>
      <button class="primary-button" type="submit">شروع رقابت <span class="arrow" aria-hidden="true">←</span></button>
      <p class="form-footnote">نیازی به ثبت‌نام نیست. فقط یک رقیب و کمی اعتمادبه‌نفس!</p>
    </form></div>`;
}

function scoresMarkup(match) {
  return `<div class="score-strip">${match.players.map((name, index) => `${index ? '<span class="versus" aria-hidden="true">VS</span>' : ""}<div class="score-player"><span>${e(name)}</span><b>${fa.format(match.scores[name])}</b></div>`).join("")}</div>
    <div class="round-dots" aria-label="راند ${fa.format(match.round)} از ${fa.format(state.rules.rounds)}">${Array.from({ length: state.rules.rounds }, (_, index) => `<span class="${index + 1 < match.round ? "done" : index + 1 === match.round ? "current" : ""}"></span>`).join("")}</div>`;
}

function resultRows(match) {
  const labels = { correct: "پاسخ درست", wrong: "پاسخ نادرست", too_late: "زمان تمام شد" };
  return `<div class="results-list">${match.players.map(name => {
    const result = match.results[name];
    return `<div class="result-row"><span class="result-name">${e(name)}</span><span class="result-status ${result.status === "correct" ? "correct" : ""}">${labels[result.status]}</span><span class="result-timing">${fa.format(Math.min(result.elapsed, state.rules.time_limit))} ثانیه</span><b class="result-points">+${fa.format(result.points)}</b></div>`;
  }).join("")}</div>`;
}

function readyMarkup(match) {
  return `<div class="play-content">${scoresMarkup(match)}<div class="handoff">
    <div class="big-avatar ${match.player_index ? "player-two" : ""}" aria-hidden="true">${e(match.active_player.slice(0, 1))}</div>
    <h2>${e(match.active_player)}، نوبت توئه!</h2><p>${match.player_index ? "دستگاه رو از رقیبت بگیر. سؤال همین رانده؛ با شروع نوبت، زمانت حساب می‌شه." : "وقتی آماده‌ای، دکمه رو بزن. سؤال و زمان‌سنج با هم شروع می‌شن."}</p>
    <button class="primary-button" data-action="start">آماده‌ام؛ سؤال رو نشون بده <span class="arrow" aria-hidden="true">←</span></button>
    <div class="turn-hint">${fa.format(state.rules.time_limit)} ثانیه برای انتخاب پاسخ درست</div>
    </div></div>`;
}

function questionMarkup(match) {
  return `<div class="play-content">${scoresMarkup(match)}
    <div class="question-header"><span>نوبت ${e(match.active_player)}</span><span id="timer" class="timer" role="timer" aria-label="زمان باقی‌مانده"></span></div>
    ${match.question.power_up === "double" ? '<span class="power-up">✦ سؤال دوبل؛ امتیازها دو برابر!</span>' : ""}
    <h2 class="question-text">${e(match.question.text)}</h2>
    <div class="options" role="group" aria-label="گزینه‌های پاسخ">${match.question.options.map((option, index) => `<button class="option" data-choice="${"ABCD"[index]}"><span class="option-letter" aria-hidden="true">${"ABCD"[index]}</span><span>${e(option)}</span></button>`).join("")}</div>
    <p class="question-hint">با انتخاب گزینه، پاسخ ثبت می‌شود و نوبت به نفر بعد می‌رسد.</p></div>`;
}

function roundMarkup(match) {
  return `<div class="play-content">${scoresMarkup(match)}
    <div class="result-heading"><span class="mini-tag">پایان راند ${fa.format(match.round)}</span><h2>یک قدم نزدیک‌تر به قهرمانی</h2><p>ببینیم این راند چطور گذشت.</p></div>
    <div class="correct-answer">پاسخ درست: <strong>${e(match.correct_text)}</strong> <span dir="ltr">(${match.correct})</span></div>
    ${resultRows(match)}<button class="primary-button" data-action="next">بریم راند بعد <span class="arrow" aria-hidden="true">←</span></button></div>`;
}

function finishedMarkup(match) {
  return `<div class="play-content"><div class="result-heading"><div class="trophy" aria-hidden="true">♜</div><span class="mini-tag">پایان رقابت</span>
    <h2>${match.winner ? `${e(match.winner)}، قهرمان شدی!` : "رقابت پایاپای؛ مساوی شد!"}</h2><p>${match.winner ? "سرعت و دانستنی‌هات، این بار جواب داد." : "این میدان هنوز یک رقابت دیگه طلب داره."}</p></div>
    <div class="final-scores">${match.players.map(name => `<div class="final-player ${name === match.winner ? "winner" : ""}"><p>${e(name)}</p><strong>${fa.format(match.scores[name])}</strong><small>امتیاز نهایی</small></div>`).join("")}</div>
    ${match.warning ? `<div class="inline-warning" role="alert">${e(match.warning)}</div><button class="secondary-button" data-action="retry">تلاش دوباره برای ذخیره</button>` : '<p class="saved-note">نتیجه در تالار قهرمان‌ها ثبت شد.</p>'}
    <button class="primary-button" data-action="rematch">یک رقابت دیگه، با همین بازیکن‌ها <span class="arrow" aria-hidden="true">←</span></button>
    <button class="secondary-button" data-action="setup">بازی با بازیکن‌های تازه</button>
    <details class="round-result-detail"><summary>نتیجهٔ راند آخر</summary><div class="correct-answer">پاسخ درست: ${e(match.correct_text)}</div>${resultRows(match)}</details></div>`;
}

function draw() {
  const match = showSetup ? null : state.match;
  // Polls update the clock without replacing focused inputs/options.
  const keyData = match ? { ...match, remaining_seconds: undefined } : null;
  const key = JSON.stringify({ match: keyData, showSetup });
  if (key === renderKey) { updateTimer(); return; }
  renderKey = key;
  statusLabel.textContent = match ? (match.phase === "finished" ? "رقابت تمام شد" : `راند ${fa.format(match.round)} از ${fa.format(state.rules.rounds)}`) : "رقابت دونفره";
  const views = { ready: readyMarkup, answering: questionMarkup, round_result: roundMarkup, finished: finishedMarkup };
  gameRoot.innerHTML = match ? views[match.phase](match) : setupMarkup();
  gameRoot.setAttribute("aria-busy", "false");
  updateTimer();
}

function drawBoard() {
  if (!state.leaderboard.length) {
    boardRoot.innerHTML = '<li class="empty-board"><span class="empty-icon" aria-hidden="true">♜</span><p>جای اولین قهرمان خالیه.</p><small>اولین رقابت رو شروع کن و اینجا بدرخش!</small></li>';
    return;
  }
  boardRoot.innerHTML = state.leaderboard.map((player, index) => `<li><span class="rank">${fa.format(index + 1)}</span><span class="avatar" aria-hidden="true">${e(player.name.slice(0, 1))}</span><span class="leader-name">${e(player.name)}</span><span class="leader-stats">${fa.format(player.wins)} <span>برد</span> / ${fa.format(player.points)}</span></li>`).join("");
}

function updateTimer() {
  const timer = document.querySelector("#timer");
  if (!timer || state.match?.phase !== "answering" || showSetup) return;
  const remaining = Math.max(0, Math.ceil((deadline - performance.now()) / 1000));
  timer.textContent = `${fa.format(remaining)} ث`;
  timer.classList.toggle("urgent", remaining <= 7);
  timer.setAttribute("aria-label", `${fa.format(remaining)} ثانیه باقی‌مانده`);
  if (remaining === 0 && !busy && !document.hidden) sync();
}

gameRoot.addEventListener("submit", event => {
  if (event.target.id !== "new-game-form") return;
  event.preventDefault();
  names = [0, 1].map(index => document.querySelector(`#player-${index}`).value.trim());
  if (!names[0] || !names[1]) { message("نام هر دو بازیکن را وارد کنید."); return; }
  if (names[0].normalize("NFKC").toLowerCase() === names[1].normalize("NFKC").toLowerCase()) {
    message("برای بازیکن‌ها دو نام متفاوت انتخاب کنید."); return;
  }
  mutate("/api/matches", { players: names });
});

gameRoot.addEventListener("click", event => {
  const button = event.target.closest("button");
  if (!button || busy) return;
  const match = state.match;
  if (button.dataset.choice) mutate("/api/match/answer", { turn: match.turn, choice: button.dataset.choice });
  if (button.dataset.action === "start") mutate("/api/match/start", { turn: match.turn });
  if (button.dataset.action === "next") mutate("/api/match/next", { turn: match.turn });
  if (button.dataset.action === "rematch") mutate("/api/matches", { players: match.players });
  if (button.dataset.action === "retry") sync(true);
  if (button.dataset.action === "setup") { showSetup = true; names = ["", ""]; message(""); draw(); document.querySelector("#player-0").focus(); }
});

const rulesDialog = document.querySelector("#rules-dialog");
document.querySelector("#rules-button").addEventListener("click", () => rulesDialog.showModal());
document.querySelector("#close-rules").addEventListener("click", () => rulesDialog.close());
document.querySelector("#understood-rules").addEventListener("click", () => rulesDialog.close());
rulesDialog.addEventListener("click", event => { if (event.target === rulesDialog) { const bounds = rulesDialog.getBoundingClientRect(); if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) rulesDialog.close(); } });
document.addEventListener("visibilitychange", () => { if (!document.hidden) sync(); });
window.addEventListener("online", () => sync(true));
window.addEventListener("pageshow", event => { if (event.persisted) sync(); });
setInterval(updateTimer, 250);
setInterval(() => {
  if (!document.hidden && state.match && !showSetup && state.match.phase !== "finished") sync();
}, 5000);
sync();
