function checkPortStatus(index, newValue) {
    let portElement = document.getElementById(`port-${index}`);
    let progressContainer = document.getElementById(`progress-${index}`).parentElement;
    if (portElement.classList.contains("badge-success")) {
        // Изменяем классы родительского элемента
        progressContainer.classList.remove("progress-bar-striped", "bg-secondary");
        return newValue;
    } else if (portElement.classList.contains("badge-danger")) {
        // Восстанавливаем классы родительского элемента
        progressContainer.classList.add("progress-bar-striped", "bg-secondary");
        return 0;
    }
    return newValue;
}

function applyVirusEffect(progressBar, value) {
    let index = progressBar.id.split('-')[1];
    let checkbox = document.getElementById(`checkbox-${index}`);
    let tr = checkbox.closest('tr');
    let isVirus = tr.getAttribute("data-is-virus") === "True";
    if (checkbox.checked) {
        if (isVirus) {
            value /= 10;
        } else {
            value /= 1.1;
        }
    }
    return value;
}


function randomChange() {
    // Выбираем случайный прогрессбар от 1 до 10
    let randomIndex = Math.floor(Math.random() * 10) + 1;

    // Получаем элемент прогрессбара
    let progressBar = document.getElementById(`progress-${randomIndex}`);

    // Вычисляем случайное изменение значения от -5 до 5
    let change = Math.floor(Math.random() * 11) - 5;

    // Применяем корректировку из-за статуса data-is-virus и состояния чекбокса
    initialValue = applyVirusEffect(progressBar, progressBar.getAttribute("data-initial-value"));
    // Вычисляем новое значение прогрессбара
    let newValue = parseInt(progressBar.getAttribute("aria-valuenow")) + change;

    // Проверяем, чтобы новое значение не отличалось от первоначального более чем на 10 единиц
    if (newValue < initialValue - 10) {
        newValue = initialValue - 10;
    } else if (newValue > initialValue + 10) {
        newValue = initialValue + 10;
    }

    // Проверяем, чтобы значение не выходило за пределы [0, 100]
    newValue = Math.max(0, Math.min(100, newValue));
    newValue = checkPortStatus(randomIndex, newValue);

    // Устанавливаем новое значение для прогрессбара
    progressBar.style.width = `${newValue}%`;
    progressBar.setAttribute("aria-valuenow", newValue);
}


// Запускаем функцию randomChange каждую секунду
setInterval(randomChange, 50);
