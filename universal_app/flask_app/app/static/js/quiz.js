import { PasetoV4Public } from "paseto-browser/paseto.v4.public.js";
console.log('argon2 methods:', Object.keys(argon2));

let questions, currentIdx = 0, payload;

// читать cookie по имени
    function getCookie(name) {
        return document.cookie
        .split("; ")
        .find(r => r.startsWith(name + "="))
        ?.split("=")[1] || "";
    }

// ─── УПРАВЛЕНИЕ ПАМЯТЬЮ ARGON2 ──────────────────────────────────────────────────

// Пул для управления операциями argon2
class Argon2MemoryManager {
constructor() {
  this.activeOperations = new Set();
  this.maxConcurrentOperations = 2; // Ограничиваем количество одновременных операций
  this.operationQueue = [];
}

// Добавляем операцию в очередь
async queueOperation(operation) {
  return new Promise((resolve, reject) => {
    this.operationQueue.push({ operation, resolve, reject });
    this.processQueue();
  });
}

// Обрабатываем очередь операций
async processQueue() {
  if (this.activeOperations.size >= this.maxConcurrentOperations || this.operationQueue.length === 0) {
    return;
  }

  const { operation, resolve, reject } = this.operationQueue.shift();
  const operationId = Symbol('argon2-operation');
  
  this.activeOperations.add(operationId);

  try {
    const result = await operation();
    resolve(result);
  } catch (error) {
    reject(error);
  } finally {
    this.activeOperations.delete(operationId);
    
    // Принудительная сборка мусора (если доступна)
    this.forceGarbageCollection();
    
    // Обрабатываем следующую операцию в очереди
    setTimeout(() => this.processQueue(), 10);
  }
}

// Принудительная сборка мусора
forceGarbageCollection() {
  // В Chrome DevTools можно включить флаг --enable-precise-memory-info
  if (window.performance && window.performance.memory) {
    console.log('Memory before GC:', window.performance.memory);
  }

  // Попытка принудительной сборки мусора (работает только в некоторых браузерах)
  if (window.gc) {
    window.gc();
  }

  // Альтернативный способ - создание и удаление больших объектов
  let dummy = new ArrayBuffer(25 * 1024 * 1024); // 1MB
  dummy = null;

  if (window.performance && window.performance.memory) {
    console.log('Memory after cleanup:', window.performance.memory);
  }
}

// Очистка всех операций (при выходе из приложения)
cleanup() {
  this.operationQueue.length = 0;
  this.activeOperations.clear();
  this.forceGarbageCollection();
}
}

// Создаем глобальный менеджер памяти
const argon2MemoryManager = new Argon2MemoryManager();


// Переменная номера сессии
let sessionNumber = null;

// ─── ВСПОМОГАТЕЛЬНЫЕ ────────────────────────────────────────────────────────────

// Base64URL → Uint8Array
function b64uToUint8(str) {
const pad = str.length % 4 === 2 ? "==" : str.length % 4 === 3 ? "=" : "";
const b64 = str.replace(/-/g,"+").replace(/_/g,"/") + pad;
return Uint8Array.from(atob(b64), c=>c.charCodeAt(0));
}

// Функция для управления состоянием кнопок
function updateButtonState(isChecking) {
  console.log("updateButtonState", isChecking);
  if (isChecking) {
    // Сохраняем текущее содержимое
    window.originalContent = $('#question-container').html();
    
    // Показываем загрузчик вместо вопроса
    $('#question-container').html(`
      <div class="card">
        <div class="card-body text-center py-5">
        <h4>Проверка хеша ответа</h4>
          <img src="/static/images/Infinityloader.gif" alt="Загрузка..." width="32" height="32">
        <p class="text-muted">Пожалуйста, подождите...</p>
        </div>
      </div>
    `);
    
  } else {
    // Восстанавливаем содержимое
    if (window.originalContent) {
      $('#question-container').html(window.originalContent);
      window.originalContent = null;
    }

  }

}


// цвет кнопки по статусу
function btnClass(q, idx) {
if (q.type === "description")                                  return "btn-outline-info";
if (q.answered && q.correct)                                   return "btn-success";
if (q.answered && q.attemptsLeft < 3 && q.attemptsLeft > 0)    return "btn-warning";
if (q.answered && !q.correct)                                  return "btn-danger";
return "btn-outline-primary";
}

// Получить номер сессии из URL
function getSessionNumber() {
const path = window.location.pathname;
const match = path.match(/\/session(\d+)\//);
return match ? match[1] : null;
}

// Загрузить сохраненные данные из localStorage
function loadSavedData() {
if (!sessionNumber) return { answers: {}, questionStates: {} };

const savedAnswers = localStorage.getItem(`quiz_answers_${sessionNumber}`);
const savedStates = localStorage.getItem(`quiz_states_${sessionNumber}`);

return {
  answers: savedAnswers ? JSON.parse(savedAnswers) : {},
  questionStates: savedStates ? JSON.parse(savedStates) : {}
};
}

// Сохранить данные в localStorage
function saveDataToLocal() {
if (!sessionNumber) return;

// Сохраняем ответы
localStorage.setItem(`quiz_answers_${sessionNumber}`, JSON.stringify(answers));

// Сохраняем состояния вопросов
const questionStates = {};
questions.forEach(q => {
  questionStates[q.id] = {
    answered: q.answered,
    correct: q.correct,
    attemptsLeft: q.attemptsLeft
  };
});
localStorage.setItem(`quiz_states_${sessionNumber}`, JSON.stringify(questionStates));
}

// Очистить данные из localStorage
function clearLocalData() {
if (!sessionNumber) return;

localStorage.removeItem(`quiz_answers_${sessionNumber}`);
localStorage.removeItem(`quiz_states_${sessionNumber}`);
}

// Проверить, нужно ли очистить данные (при выходе)
function checkClearFlag() {
const cookies = document.cookie.split(';');
console.log("Получены куки: ", cookies);
const clearFlag = cookies.find(cookie => cookie.trim().startsWith('clear_quiz_data='));
console.log("Значение clearFlag: ", clearFlag)

if (clearFlag && clearFlag.includes('true')) {
  clearLocalData();
  // Удаляем куку
  document.cookie = 'clear_quiz_data=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
}
}

// Восстановить состояние вопросов из localStorage
function restoreQuestionStates() {
const savedData = loadSavedData();

// Восстанавливаем ответы
answers = { ...savedData.answers };

// Восстанавливаем состояния вопросов
questions.forEach(q => {
  const savedState = savedData.questionStates[q.id];
  if (savedState) {
    q.answered = savedState.answered || false;
    q.correct = savedState.correct || false;
    q.attemptsLeft = savedState.attemptsLeft !== undefined ? savedState.attemptsLeft : q.type === "truefalse" ? 1: q.type === "multichoice" ? 2 : 3;
  } else {
    q.answered = false;
    q.correct = false;
    q.attemptsLeft = q.type === "truefalse" ? 1: q.type === "multichoice" ? 2 : 3;
  }
});
}

// ─── РАЗБОР ТОКЕНА ───────────────────────────────────────────────────────────────

async function loadQuestions() {
// 1) PASETO
const token = $('meta[name="exam-token"]').attr('content').trim();
const pk_b64u = $('meta[name="exam-pk"]').attr('content').trim();
const pubKey = b64uToUint8(pk_b64u);
const verifier = new PasetoV4Public(pubKey);
try {
  payload = await verifier.decode(token);
} catch (e) {
  alert("Токен недействителен или истёк — перезагрузите страницу.");
  throw e;
}

// 2) Инициализация state
return payload.q.map(q => ({
  ...q,
  attemptsLeft: q.type === "truefalse" ? 1: q.type === "multichoice" ? 2 : 3,
  answered:   q.answered || false,
  correct:    q.correct   || false,
  isChecking: false,
}));
}

// ─── РЕНДЕРИНГ НАВИГАЦИИ ────────────────────────────────────────────────────────

function renderNav() {
const $nav = $("#nav-buttons");
$nav.empty();

questions.forEach((q, i) => {
  const $btn = $('<button></button>')
    .addClass(`btn ${btnClass(q,i)} ${currentIdx === i ? "btn-lg" : ""} me-1 mr-2`)
    .text(i+1)
    .on('click', function() { 
      saveAnswer(); 
      currentIdx = i;
      renderQuestion();
      renderNav(); 
    });
  $nav.append($btn);
});
}

// ─── РЕНДЕРИНГ ВОПРОСА ─────────────────────────────────────────────────────────

function renderQuestion() {
console.log('Рендер Вопроса');
const q = questions[currentIdx];
const $c = $("#question-container");
let html = `<div class="card"><div class="card-body">`;

if (q.type == "missingword"){
  html += `<h4>Вопрос ${currentIdx+1}</h4>`; 
}
else if (q.type == "essay") {
  html += `<h4>Вопрос с открытм ответом ${currentIdx+1}</h4><p>${q.text}</p>`;
}
else if (q.type == "description") {
  html += `<h4>Информационный блок</h4><p>${q.text}</p>`;
}
else{
  html += `<h4>Вопрос ${currentIdx+1}</h4><p>${q.text}</p>`;
}

// Получаем сохраненный ответ для восстановления состояния
const savedAnswer = answers[q.id];

// по типу вопроса
if (q.type === "multichoice") {
  // Определяем тип элемента управления на основе количества правильных ответов
  const isMultipleCorrect = q.hashes.length > 1;
  const inputType = isMultipleCorrect ? "checkbox" : "radio";
  const inputName = isMultipleCorrect ? "" : `name="mc-${q.id}"`;

  q.options.forEach((opt, oidx) => {
    let checked = "";
    if (savedAnswer) {
      if (isMultipleCorrect) {
        // Для чекбоксов проверяем, есть ли значение в массиве
        checked = Array.isArray(savedAnswer) && savedAnswer.includes(opt.text.toLowerCase()) ? "checked" : "";
      } else {
        // Для радиокнопок проверяем равенство строк
        checked = savedAnswer === opt.text.toLowerCase() ? "checked" : "";
      }
    }

    html += `
      <div class="form-check">
        <input class="form-check-input" type="${inputType}" id="opt-${oidx}"
               value="${opt.text}" ${inputName} ${checked} ${q.answered && q.attemptsLeft == 0 || q.correct ?"disabled":""}>
        <label class="form-check-label" for="opt-${oidx}">${opt.text}</label>
      </div>`;
  });

} else if (q.type === "truefalse") {
  ["Правда","Ложь"].forEach(val => {
    const checked = savedAnswer === val ? "checked" : "";
    html += `
      <div class="form-check">
        <input class="form-check-input" type="radio" name="tf" id="tf-${val}"
               value="${val}" ${checked} ${q.answered && q.attemptsLeft == 0 || q.correct ?"disabled":""}>
        <label class="form-check-label" for="tf-${val}">${val}</label>
      </div>`;
  });

} else if (q.type === "missingword") {
  // текст с __{i}__ placeholders
  let txt = q.text;
  q.hashes.forEach((_,i) => {
    const selectedValue = savedAnswer && Array.isArray(savedAnswer) ? savedAnswer[i] || "" : "";
    const options = q.options.map(h => {
      const selected = h.text.toLowerCase() === selectedValue ? "selected" : "";
      return `<option ${selected}>${h.text}</option>`;
    }).join("");

    txt = txt.replace(/\{\}/g,
      `<select id="mw-${i}" class="form-select" ${q.answered && q.attemptsLeft == 0 || q.correct ? "disabled":""}">
         <option value="">…</option>
         ${options}
       </select>`
       );
  });
  html += `<p>${txt}</p>`;

} else if (q.type === "matching") {
  // две колонки: left — текст, right — селект из q.options
  html += `<div class="row">`;
  q.options.forEach((pair,i) => {
    const [left]= pair.split("|");
    const selectedValue = savedAnswer && Array.isArray(savedAnswer) ? savedAnswer[i] || "" : "";
    const options = q.options
      .map(o => {
        const rightPart = o.split("|")[1];
        return { rightPart, original: o };
      })
      .sort(() => Math.random() - 0.5) // простой shuffle
      .map(({ rightPart }) => {
        const selected = rightPart === selectedValue ? "selected" : "";
        return `<option ${selected}>${rightPart}</option>`;
      })
      .join("");


    html += `
      <div class="col-6">${left}</div>
      <div class="col-6">
        <select id="mt-${i}" class="form-select" ${q.answered && q.attemptsLeft == 0 || q.correct ?"disabled":""}>
          <option value="">…</option>
          ${options}
        </select>
      </div>`;
  });
  html += `</div>`;

} else if (q.type === "numerical") {
  const value = savedAnswer || "";
  html += `<div class="input-group mb-3">
          <div class="input-group-prepend">
              <span class="input-group-text">0.00</span>
          </div>
  <input type="number" step="any" id="num-${q.id}" class="form-control"
         value="${value}" ${q.answered && q.attemptsLeft == 0|| q.correct ?"disabled":""}>
            </div>`;

} else if (q.type === "shortanswer") {
  const value = savedAnswer || "";
  html += `<input type="text" id="sha-${q.id}" class="form-control"
           value="${value}" ${q.answered && q.attemptsLeft == 0|| q.correct ?"disabled":""}>`;

} else if (q.type === "essay") {
  const value = savedAnswer || "";
  html += `<textarea id="es-${q.id}" class="form-control" rows="6"
                    ${q.answered?"disabled":""}>${value}</textarea>`;
}

// информационная строка
if (q.type != "description" && q.type != "essay") {
  html += `<p class="mt-2">Попыток осталось: ${q.attemptsLeft}</p>`;
}

html += `</div></div>`;
$c.html(html);

console.log('Рендер окончен');
}

// ─── СОХРАНЕНИЕ ПОЛЯ ВЫБОРА ─────────────────────────────────────────────────────

let answers = {};

// функция saveAnswer
function saveAnswer() {
const q = questions[currentIdx];
// В начале функции checkAnswer добавьте:
console.log('Сохраняем вопрос:', q.type, 'ID:', q.id);
if (q.answered && q.attemptsLeft == 0) return;

let ans = null;
if (q.type === "multichoice") {
  const isMultipleCorrect = q.hashes.length > 1;
  if (isMultipleCorrect) {
    // Чекбоксы: собираем все отмеченные
    ans = $('input[type="checkbox"]:checked').map(function() {
      return $(this).val().trim().toLowerCase();;
    }).get();
    if (ans.length === 0) ans = null;
  } else {
    // Радиокнопки: одно значение
    const $inp = $('input[name^="mc-"]:checked');
    ans = $inp.length ? $inp.val().trim().toLowerCase() : null;
  }
} else if (q.type === "truefalse") {
  const $inp = $('input[name="tf"]:checked');
  ans = $inp.length ? $inp.val() : null;
} else if (q.type === "shortanswer") {
  const $inp = $(`#sha-${q.id}`);
  ans = $inp.length && $inp.val().trim() ? $inp.val().trim().toLowerCase() : null;
} else if (q.type === "missingword") {
  ans = q.hashes.map((_, i) => {
    const $sel = $(`#mw-${i}`);
    return $sel.length ? $sel.val().trim().toLowerCase() : "";
  });
  if (ans.every(a => !a)) ans = null;
} else if (q.type === "matching") {
  ans = q.options.map((_, i) => {
    const $sel = $(`#mt-${i}`);
    return $sel.length ? $sel.val() : "";
  });
  if (ans.every(a => !a)) ans = null;
} else if (q.type === "numerical") {
  const $inp = $(`#num-${q.id}`);
  ans = $inp.length && $inp.val().trim() ? Number($inp.val().trim()).toFixed(2) : null;
} else if (q.type === "essay") {
  const $inp = $(`#es-${q.id}`);
  ans = $inp.length && $inp.val().trim() ? $inp.val().trim() : null;
}


if (ans !== null) {
  answers[q.id] = ans;
  saveDataToLocal(); // Сохраняем локально
}
console.log('Записан ответ:', ans);
}

// ─── ПРОВЕРКА ОТВЕТА ───────────────────────────────────────────────────────────

// Функция checkAnswer для автосохранения
async function checkAnswer(q) {
let ok = 0;
const ans = answers[q.id];
console.log('Проверяем вопрос:', q.type, 'ID:', q.id);
console.log('Хеши (тип):', typeof q.hashes, q.hashes);
console.log('Ответ:', ans);

if (q.answered && q.attemptsLeft === 0) return ok;

// Оптимизированная функция проверки argon2 с управлением памятью
async function safeArgon2Verify(password, hashObj) {
return await argon2MemoryManager.queueOperation(async () => {
  // Добавляем задержку для освобождения UI
  await new Promise(requestAnimationFrame);
  
  try {
    let hash = hashObj;
    if (typeof hashObj === 'object' && hashObj.text) {
      hash = hashObj.text;
    }

    console.log('Проверяем хеш:', hash);
    
    if (!hash || typeof hash !== 'string' || !hash.startsWith('$argon2')) {
      console.warn('Неправильный формат хеша:', hash);
      return false;
    }

    const passwordStr = password.toString();
    const hashStr = hash;
    
    const result = await argon2.verify({
      pass: passwordStr,
      encoded: hashStr
    });

    console.log('Результат проверки argon2:', result);
    return true;
    
  } catch (e) {
    console.error('Ошибка проверки argon2:', e);
    return false;
  }
});
}


q.isChecking = true;
updateButtonState(true);
await new Promise(requestAnimationFrame);

switch (q.type) {
  case "multichoice":
    if (!ans) break;

    // Определяем количество правильных ответов
    const hashesArray = Array.isArray(q.hashes) ? q.hashes : [q.hashes];
    const isMultipleCorrect = hashesArray.length > 1;

    if (isMultipleCorrect && Array.isArray(ans)) {
      // Для множественного выбора - все выбранные ответы должны быть правильными
      // и количество должно совпадать
      ok = 2;
      if (ans.length !== hashesArray.length) break;

      // Создаем копию массива хешей для отслеживания использованных
      const availableHashes = [...hashesArray];
      let allCorrect = true;

      for (let answer of ans) {
        if (!allCorrect) break;
        let foundIndex = -1;
        
        // Ищем подходящий хеш для текущего ответа
        for (let i = 0; i < availableHashes.length; i++) {
          if (availableHashes[i] === null) continue; // Уже использован
          
          const result = await safeArgon2Verify(answer, availableHashes[i]);
          if (result) {
            foundIndex = i;
            break;
          }
        }
        
        if (foundIndex === -1) {
          allCorrect = false; // Не найден подходящий хеш
        }
        
        // Помечаем хеш как использованный
        availableHashes[foundIndex] = null;
      }

      ok = allCorrect ? 1 : 2;
    } else {
      // Для единственного выбора - проверяем ответ против всех хешей
      const answerToCheck = Array.isArray(ans) ? ans[0] : ans;
      for (let hashObj of hashesArray) {
        const result = await safeArgon2Verify(answerToCheck, hashObj);
        ok = result ? 1: 2;
        break;
        }
      }
    break;

  case "truefalse":
  case "shortanswer":
    if (!ans) break;

    const hashesArrayTF = Array.isArray(q.hashes) ? q.hashes : [q.hashes];
    for (let hashObj of hashesArrayTF) {
      const result = await safeArgon2Verify(ans, hashObj);
        ok = result ? 1: 2;
        break;
    }
    break;

  case "missingword":
    if (!ans || !Array.isArray(ans)) break;

    try {
      const hashesArrayMW = Array.isArray(q.hashes) ? q.hashes : [q.hashes];
      if (ans.length !== hashesArrayMW.length) break;

      const results = await Promise.all(hashesArrayMW.map(async (hashObj, i) => {
        if (!ans[i]) return false;
        return await safeArgon2Verify(ans[i], hashObj);
      }));
      ok = results.every(r => r) ? 1 : 2;
    } catch (e) {
      console.error('Ошибка проверки missingword:', e);
      ok = 0;
    }
    break;

  case "matching":
    if (!ans || !Array.isArray(ans)) break;

    try {
        // Проверяем через хеши
        const results = await Promise.all(q.hashes.map(async (hashObj, i) => {
          if (!ans[i]) return false;
          return await safeArgon2Verify(ans[i], hashObj);
        }));
        ok = results.every(r => r) ? 1: 2;
    } catch (e) {
      console.error('Ошибка проверки matching:', e);
      ok = 0; 
    }
    break;

  case "numerical":
    if (!ans) break;
    ok = 2;
    const normal_ans = Number(ans).toFixed(2);
    try {
      const hashesArrayNum = Array.isArray(q.hashes) ? q.hashes : [q.hashes];

      // Пробуем сначала через argon2
      for (let hashObj of hashesArrayNum) {
        let hash = typeof hashObj === 'object' && hashObj.text ? hashObj.text : hashObj;

        if (typeof hash === 'string' && hash.startsWith('$argon2')) {
          const result = await safeArgon2Verify(normal_ans, hashObj);
          if (result) {
            ok = 1;
            break;
          }
        }
      }

    } catch (e) {
      console.error('Ошибка проверки numerical:', e);
      ok = 0;
    }
    break;

  case "essay":
    // Эссе не проверяется автоматически
    if (!ans) break;
    console.warn('Эссе не проверяется автоматически!');
    ok = 3;
    break;
  case "description":
    ok = 4;
    break;

  default:
    console.warn('Неизвестный тип вопроса:', q.type);
    ok = 5;
}

// Обновляем состояние вопроса
if (ok == 1) {
  q.answered = true;
  q.correct = true;
  console.log('✅ Ответ правильный!');
} else if (q.attemptsLeft === 0) {
  q.answered = true;
  q.correct = false;
  console.log('❌ Ответ неправильный, попытки исчерпаны');
} else if (ok == 2) {
  q.attemptsLeft--;
  console.log('❌ Ответ неправильный, попыток осталось:', q.attemptsLeft);
  q.answered = true;
  q.correct = false;
}
else{
  console.log('ОК из блока 0, 3, 4, 5');
  q.answered = false;
  q.correct = false;
}

// Сохраняем изменения локально
saveDataToLocal();
q.isChecking = false;
updateButtonState(false);
await new Promise(requestAnimationFrame);
renderQuestion();

return ok;
}

async function onSubmitCurrent() {
const q = questions[currentIdx];

saveAnswer();
renderNav();
renderQuestion();

try {
  const ok = await checkAnswer(q);
  let  alertClass = '', alertMessage = "";
  if (ok == 3){
    alertClass = 'primary';
    alertMessage = "Ответ записан";
  }
  else if (ok == 1){
    alertClass = 'success';
    alertMessage = "Правильно! 🎉";
  }
  else if (ok == 2){
    alertClass = 'danger';
    alertMessage = `Неверно. Осталось попыток: ${q.attemptsLeft}`;
  }
  else if (ok == 4){
    alertClass = 'dark';
    alertMessage = "Без понятия что вы хотели этим сказать";
  }
  else if (ok == 5){
    alertClass = 'light';
    alertMessage = "Я не знаю что это!";
  }
  else {
    alertClass = 'warning';
    alertMessage = "И что с этим делать?";
  }

  $('#feedback').html(
      '<div class="alert alert-' + alertClass + ' alert-dismissible fade show" role="alert">' +
          alertMessage +
          '<button type="button" class="close" data-dismiss="alert" aria-label="Close">' +
              '<span aria-hidden="true">&times;</span>' +
          '</button>' +
      '</div>'
  );
  
  // Закрыть уведомление через 2 секунды
  setTimeout(function() {
      $(".alert").fadeTo(500, 0).slideUp(500, function(){
          $(this).remove();
      });
  }, 2000);
  
} catch (e){
  console.error('Ошибка проверки argon2: ', e);
}

// Всегда разблокируем кнопки и обновляем UI
q.isChecking = false;
updateButtonState(false);
renderNav();
renderQuestion();
}

// Отправка ответов на сервер для отображения в интерфейсе учителя
async function onSubmitCurrentAll() {
saveAnswer();

// соберём результат
const results = questions.map(q => {
  const raw = answers[q.id];
  const answer = raw === undefined
    ? ""
    : Array.isArray(raw)
      ? [...raw]
      : raw;
  return {
  question_id: q.id,
  correct: q.correct,
  answer,
  attempts: q.attemptsLeft,
  question_type: q.type
  };
});



// плюс эссе тексты
const essays = {};
for (let q of questions) {
  if (q.type==="essay") essays[q.id] = answers[q.id]||"";
}
const username = getCookie('username');
console.log("JSON.stringify(): ", JSON.stringify({ results, essays, username }));
try {
  const response = await $.ajax({
    url: `/session${payload.session}/submit`,
    method: "POST",
    contentType: "application/json",
    data: JSON.stringify({ results, essays, username })
  });
  alert("Результаты отправлены!");
} catch (error) {
  console.error('Ошибка отправки результатов:', error);
  alert("Ошибка при отправке результатов!");
}
renderNav();
renderQuestion();
}

// ─── СТАРТ ────────────────────────────────────────────────────────────────────

//функция инициализации
async function init() {
try {
  sessionNumber = getSessionNumber();
  checkClearFlag(); // Проверяем, нужно ли очистить данные

  questions = await loadQuestions();

  // Восстанавливаем состояние из localStorage
  restoreQuestionStates();

  renderQuestion();
  renderNav();

  // Привязываем обработчики событий через jQuery
  $(document).off('click', '#submit-current-btn').on('click', '#submit-current-btn', onSubmitCurrent);
  $(document).off('click', '#submit-all-btn').on('click', '#submit-all-btn', onSubmitCurrentAll);

  // Автосохранение при закрытии страницы
  $(window).on('beforeunload', function() {
    saveDataToLocal();
  });

} catch (e) {
  console.error("Ошибка инициализации:", e);
}
}

// Запуск при загрузке DOM
$(document).ready(async function() {
try {
  await init();
} catch (error) {
  console.error('Ошибка инициализации приложения:', error);
  alert('Произошла ошибка при загрузке. Пожалуйста, обновите страницу.');
}
});
