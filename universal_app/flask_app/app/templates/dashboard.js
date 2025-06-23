import { timingSafeEqual } from "crypto";          // shim в dashboard.html
import nacl from "tweetnacl";                     // для PASETO
import { PasetoV4Public } from "paseto-browser/paseto.v4.public.js";
import argon2 from "argon2-browser";               // для MC/TF/shortanswer (небольшие строки)

// ─── ВСПОМОГАТЕЛЬНЫЕ ────────────────────────────────────────────────────────────

// читать cookie по имени
function getCookie(name) {
  return document.cookie
    .split("; ")
    .find(r => r.startsWith(name + "="))
    ?.split("=")[1] || "";
}

// Base64URL → Uint8Array
function b64uToUint8(str) {
  const pad = str.length % 4 === 2 ? "==" : str.length % 4 === 3 ? "=" : "";
  const b64 = str.replace(/-/g,"+").replace(/_/g,"/") + pad;
  return Uint8Array.from(atob(b64), c=>c.charCodeAt(0));
}

// цвет кнопки по статусу
function btnClass(q, idx) {
  if (q.answered && q.correct)             return "btn-success";
  if (q.answered && !q.correct)            return "btn-danger";
  if (!q.answered && q.attemptsLeft < 3)    return "btn-warning";
  if (q.type === "description")            return "btn-secondary";
  return "btn-outline-primary";
}

// ─── РАЗБОР ТОКЕНА ───────────────────────────────────────────────────────────────

async function loadQuestions() {
  // 1) PASETO
  document.querySelector('meta[name="exam-token"]').content.trim();
  const pk_b64u = document.querySelector('meta[name="exam-pk"]').content.trim();
  const pubKey = b64uToUint8(pk_b64u);
  const verifier = new PasetoV4Public(pubKey);
  let payload;
  try {
    payload = await verifier.decode(token);
  } catch (e) {
    alert("Токен недействителен или истёк — перезагрузите страницу.");
    throw e;
  }
  console.log("Получен токен:", payload);

  // 2) Инициализация state
  return payload.q.map(q => ({
    ...q,
    attemptsLeft: 3,
    answered:   q.answered || false,
    correct:    q.correct   || false
  }));
}

// ─── РЕНДЕРИНГ НАВИГАЦИИ ────────────────────────────────────────────────────────

let questions, currentIdx = 0;

function renderNav() {
  const nav = document.getElementById("nav-buttons");
  nav.innerHTML = "";
  questions.forEach((q, i) => {
    const btn = document.createElement("button");
    btn.className = `btn ${btnClass(q,i)} me-1`;
    btn.textContent = i+1;
    btn.onclick = () => { saveAnswer(); currentIdx = i; renderQuestion(); };
    nav.appendChild(btn);
  });
}

// ─── РЕНДЕРИНГ ВОПРОСА ─────────────────────────────────────────────────────────

function renderQuestion() {
  const q = questions[currentIdx];
  const c = document.getElementById("question-container");
  let html = `<div class="card"><div class="card-body"><h5>Вопрос ${currentIdx+1}</h5>`;
  html += `<p>${q.text}</p>`;

  // по типу вопроса
  if (q.type === "multichoice") {
    q.options.forEach((opt,oidx) => {
      html += `
        <div class="form-check">
          <input class="form-check-input" type="checkbox" id="opt-${oidx}"
                 value="${opt.text}" ${q.answered?"disabled":""}>
          <label class="form-check-label" for="opt-${oidx}">${opt.text}</label>
        </div>`;
    });

  } else if (q.type === "truefalse") {
    ["True","False"].forEach(val => {
      html += `
        <div class="form-check">
          <input class="form-check-input" type="radio" name="tf" id="tf-${val}"
                 value="${val}" ${q.answered?"disabled":""}>
          <label class="form-check-label" for="tf-${val}">${val}</label>
        </div>`;
    });

  } else if (q.type === "missingword") {
    // текст с __{i}__ placeholders
    let txt = q.text;
    q.hashes.forEach((_,i) => {
      txt = txt.replace(`__${i+1}__`,
        `<select id="mw-${i}" class="form-select" ${q.answered?"disabled":""}>
           <option value="">…</option>
           ${q.hashes.map(h=>`<option>${h.text}</option>`).join("")}
         </select>`);
    });
    html += `<p>${txt}</p>`;

  } else if (q.type === "matching") {
    // две колонки: left — текст, right — селект из q.options
    html += `<div class="row">`;
    q.hashes.forEach((pair,i) => {
      const [left] = pair.split("|");
      html += `
        <div class="col-6">${left}</div>
        <div class="col-6">
          <select id="mt-${i}" class="form-select" ${q.answered?"disabled":""}>
            <option value="">…</option>
            ${q.options.map(o=>`<option>${o.split("|")[0]}</option>`).join("")}
          </select>
        </div>`;
    });
    html += `</div>`;

  } else if (q.type === "numerical") {
    html += `<input type="number" step="any" id="num-${q.id}" class="form-control"
                    ${q.answered?"disabled":""}>`;

  } else if (q.type === "shortanswer" || q.type === "essay") {
    html += `<textarea id="txt-${q.id}" class="form-control" rows="${q.type==="essay"?6:2}"
                      ${q.answered?"disabled":""}>${q.answered?answers[q.id]||"":""}</textarea>`;
  }

  // информационная строка
  html += `<p class="mt-2">Попыток осталось: ${q.attemptsLeft}</p>`;

  html += `</div></div>`;
  c.innerHTML = html;
}

// ─── СОХРАНЕНИЕ ПОЛЯ ВЫБОРА ─────────────────────────────────────────────────────

const answers = {};

function saveAnswer() {
  const q = questions[currentIdx];
  if (q.answered) return;
  let val;
  switch (q.type) {
    case "multichoice":
      val = Array.from(
        document.querySelectorAll("input[type=checkbox]:checked")
      ).map(i=>i.value);
      break;
    case "truefalse":
      const sel = document.querySelector("input[type=radio]:checked");
      val = sel? sel.value : "";
      break;
    case "missingword":
      val = Array.from(
        q.hashes.map((_,i)=>document.getElementById(`mw-${i}`))
      ).map(s=>s.value);
      break;
    case "matching":
      val = Array.from(
        q.hashes.map((_,i)=>document.getElementById(`mt-${i}`))
      ).map(s=>s.value);
      break;
    case "numerical":
      val = document.getElementById(`num-${q.id}`).value;
      break;
    case "shortanswer":
    case "essay":
      val = document.getElementById(`txt-${q.id}`).value;
      break;
  }
  answers[q.id] = val;
}

// ─── ПРОВЕРКА ОТВЕТА ───────────────────────────────────────────────────────────

async function checkAnswer(q) {
  const ans = answers[q.id];
  if (q.answered || q.attemptsLeft===0) return;

  let ok = false;
  switch (q.type) {
    case "multichoice":
    case "truefalse":
    case "shortanswer":
      if (!ans) break;
      // argon2.verify возвращает true, если хоть один ответ совпал
      for (let h of q.hashes) {
        if (await argon2.verify({ pass: ans.toString().trim(), encoded: h })) {
          ok = true;
          break;
        }
      }
      break;

    case "missingword":
      // массив строк, проверяем каждую отдельным hash
      ok = q.hashes.every((hObj,i) => argon2.verify({
        pass: ans[i].trim(), encoded: hObj.encoded || hObj.text
      }));
      break;

    case "matching":
      // для matching: сравнить пары “left|selected”
      ok = q.hashes.every(pair => ans.includes(pair.split("|")[0]));
      break;

    case "numerical":
      const num = parseFloat(ans);
      ok = Math.abs(num - parseFloat(q.hashes)) <= (q.tol||0);
      break;

    case "essay":
      // эссе не проверяем автоматически
      ok = null;
      break;
  }

  q.attemptsLeft--;
  if (ok) {
    q.answered = true;
    q.correct  = true;
  } else if (q.attemptsLeft===0) {
    q.answered = true;
    q.correct  = false;
  }
  return ok;
}

// ─── ОБРАБОТЧИКИ КНОПОК ────────────────────────────────────────────────────────

document.getElementById("submit-current-btn").onclick = async () => {
  saveAnswer();
  const q = questions[currentIdx];
  const ok = await checkAnswer(q);
  renderNav();
  renderQuestion();
  alert(ok===null
    ? "Эссе, ответ записан."
    : ok
      ? "Правильно! 🎉"
      : `Неверно. Осталось попыток: ${q.attemptsLeft}`);
};

document.getElementById("submit-all-btn").onclick = async () => {
  saveAnswer();
  for (let q of questions) {
    if (!q.answered) await checkAnswer(q);
  }
  renderNav();
  renderQuestion();
  // соберём результат
  const results = questions.map(q=>({
    question_id: q.id,
    correct: q.correct,
    attempts: 3 - q.attemptsLeft
  }));
  // плюс эссе тексты
  const essays = {};
  for (let q of questions) {
    if (q.type==="essay") essays[q.id] = answers[q.id]||"";
  }
  await fetch(`/session${payload.session}/submit`, {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body: JSON.stringify({ results, essays })
  });
  alert("Результаты отправлены!");
};

// ─── СТАРТ ────────────────────────────────────────────────────────────────────

(async()=>{
  questions = await loadQuestions();
  renderNav();
  renderQuestion();
})();
