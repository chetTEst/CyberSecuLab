const phrases = [
    'Приватность: Плащ невидимка. Как у Гарри Поттера, но круче.',
    'Целостность: Суперклей. Держит намертво все вместе.',
    'Доступность: Волшебный портал. Доступ ко всему, что вам нужно.',
    'Фишинг: Глупец на крючке. Киберзлодей ловит рыбу на сочных червей!',
    'Социальная инженерия: Мастер маскировки. Выдает себя за другого человека.',
    'Белые шляпы: Кибергерои. Борются за справедливость.',
    'Черные шляпы: Цифровые проказники. Озорные нарушители порядка. Негодяи.',
    'Брандмауэр: Цифровой щит. Силовое поле, вокруг цифровой крепости.',
    'Антивирус: Усилитель иммунитета. Укрепляет компьютер. Уничтожает вирусы.',
    'Компьютерный вирус: Жук простуженный. Чихает и всех заражает.',
    'Троян: Конь-сюрприз. Гадость спрятанная в подарке.',
    'Бэкдор: Подкоп злодея. Проникнуть в цифровой замок незаметно.',
    'Буткит: Кусочек грязи на твоих ботинках. Портит все впечатление.',
    'Утилиты: Армейский кибер-мультитул. Супер-инструмент с гаджетами. Если не испорчен.'
];


let startButton = document.getElementById('startButton');
let nextButton = document.getElementById('nextButton');
let textOutput = document.getElementById('textOutput');
let instructionText = document.getElementById('instructionText');

startButton.onclick = function() {
    instructionText.style.opacity = '0'
    nextButton.disabled = false;
    updateOutput(getRandomPhrase());
    startButton.style.display = 'none';

}

nextButton.onclick = function() {
    if (phrases.length > 0) {
        updateOutput(getRandomPhrase());
    } else {
        nextButton.disabled = true;
        anime({
        targets: textOutput,
        opacity: 0,
        duration: 1000,  // Продолжительность анимации в миллисекундах
        easing: 'easeOutSine',  // Тип анимации
        complete: function(anim) {
            // После завершения первой анимации
            // Очищаем текущий вывод
            textOutput.innerHTML = '';

            textOutput.textContent = 'Больше карточек нет';

            // Используем anime.js для плавного изменения прозрачности от 0 до 1
            anime({
                targets: textOutput,
                opacity: 1,
                duration: 1000,  // Продолжительность анимации в миллисекундах
                easing: 'easeInSine'  // Тип анимации
            });
        }
    });


    }
}

function getRandomPhrase() {
    let randomIndex = Math.floor(Math.random() * phrases.length);
    let randomPhrase = phrases[randomIndex];
    phrases.splice(randomIndex, 1);

    let splitPhrase = randomPhrase.split(':');
    return {bold: splitPhrase[0], regular: splitPhrase[1]};
}

function updateOutput({bold, regular}) {
    // Создаем новые элементы
    let boldSpan = document.createElement('span');
    boldSpan.textContent = bold;
    boldSpan.className = 'bold-text';

    let regularText = document.createTextNode(':' + regular);

    // Используем anime.js для плавного изменения прозрачности от 1 до 0
    anime({
        targets: textOutput,
        opacity: 0,
        duration: 1000,  // Продолжительность анимации в миллисекундах
        easing: 'easeOutSine',  // Тип анимации
        complete: function(anim) {
            // После завершения первой анимации
            // Очищаем текущий вывод
            textOutput.innerHTML = '';

            // Добавляем новые элементы в вывод
            textOutput.appendChild(boldSpan);
            textOutput.appendChild(regularText);

            // Используем anime.js для плавного изменения прозрачности от 0 до 1
            anime({
                targets: textOutput,
                opacity: 1,
                duration: 1000,  // Продолжительность анимации в миллисекундах
                easing: 'easeInSine'  // Тип анимации
            });
        }
    });
}


