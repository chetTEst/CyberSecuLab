document.addEventListener('DOMContentLoaded', function () {
    const programs = [
        'пусть твоеИмя = спросить("Как тебя зовут?", "Аноним");\nкричалка("Привет, " + твоеИмя + "!");',
        'пусть первоеЧисло = спросить("Введите первое число:", "0");\nпусть второеЧисло = спросить("Введите второе число:", "0");\nпусть сумма = Число(первоеЧисло) + Число(второеЧисло);\nкричалка("Сумма чисел: " + сумма);',
        'пусть число = спросить("Введите число:", "0");\nразвилка (число % 2 === 0) {\n    Сообщить("Число " + число + " является четным!");\n} второй_путь {\n    Сообщить("Число " + число + " является нечетным!");\n}',
        'пусть секретноеЧисло = Математика.округлить(Математика.случайное_число() * 10) + 1;\nпусть попытка = спросить("Угадай число от 1 до 10:", "5");\nразвилка (Число(попытка) === секретноеЧисло) {\n   кричалка("Ты угадал! Это было число " + секретноеЧисло + "!");\n} второй_путь {\n    кричалка("Увы! Правильное число было " + секретноеЧисло + ".");\n}',
        'пусть первоеЧисло = спросить("Введите первое число:", "1");\nпусть второеЧисло = спросить("Введите второе число:", "1");\nпусть произведение = Число(первоеЧисло) * Число(второеЧисло);\nкричалка("Произведение чисел: " + произведение);',
        'пусть годРождения = спросить("В каком году вы родились?", "2000");\nпусть текущийГод = новыйДата().получитьГод();\nпусть возраст = текущийГод - Число(годРождения);\nСообщить("Вам " + возраст + " лет!");',
        'пусть число1 = Математика.округлить(Математика.случайное_число() * 10) + 1;\nпусть число2 = Математика.округлить(Математика.случайное_число() * 10)+ 1;\nразвилка (число1 > число2) {\n    кричалка(число1 + " больше, чем " + число2);\n} развилка (число1 < число2) {\n    кричалка(число1 + " меньше, чем " + число2);\n} второй_путь {\n    кричалка(число1 + " равно " + число2);\n}\n'
    ];

    let currentProgramIndex = 0;

    editor.setValue(programs[currentProgramIndex], -1);  // -1 позволяет установить курсор в начальное положение

    const backButton = document.getElementById('backButton');
    const nextButton = document.getElementById('nextButton');

    backButton.addEventListener('click', function () {
        if (currentProgramIndex > 0) {
            currentProgramIndex--;
            editor.setValue(programs[currentProgramIndex], -1);
            updateButtons();
        }
    });

    nextButton.addEventListener('click', function () {
        if (currentProgramIndex < programs.length - 1) {
            currentProgramIndex++;
            editor.setValue(programs[currentProgramIndex], -1);
            updateButtons();
        }
    });

    function updateProgressBar() {
        let progressBar = '';
        for (let i = 0; i < programs.length; i++) {
            let btnClass = i < currentProgramIndex ? 'btn-outline-info' : i == currentProgramIndex ? 'btn-info' : 'btn-outline-info';
            progressBar += `<button type="button" class="btn ${btnClass} mr-1" data-index="${i}" data-toggle="tooltip" data-placement="top" title="Программа ${i + 1}">${i + 1}</button>`;
        }
        const progressBarElement = document.getElementById('progress-bar');
        progressBarElement.innerHTML = progressBar;

        // Добавляем обработчики событий для кнопок
        progressBarElement.querySelectorAll('button').forEach(btn => {
            btn.addEventListener('click', function() {
                const index = parseInt(this.getAttribute('data-index'));
                currentProgramIndex = index;
                editor.setValue(programs[currentProgramIndex], -1);
                updateButtons();
            });
        });
    }


    function updateButtons() {
        if (currentProgramIndex === 0) {
            backButton.classList.add('disabled');
            backButton.setAttribute('disabled', true);
        } else {
            backButton.classList.remove('disabled');
            backButton.removeAttribute('disabled');
        }

        if (currentProgramIndex === programs.length - 1) {
            nextButton.classList.add('disabled');
            nextButton.setAttribute('disabled', true);
        } else {
            nextButton.classList.remove('disabled');
            nextButton.removeAttribute('disabled');
        }
        updateProgressBar();
    }

    updateButtons();
});