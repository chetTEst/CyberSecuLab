  $(document).ready(function() {
    const contentContainer = $('#content_text');
    let originalText = contentContainer.html();
    let parts = {{ parts | tojson }};

    let formattedText = getCookie('formattedText');
    if (!formattedText) {
        formattedText = insertPartsSequentially(originalText, parts);
        setCookie('formattedText', formattedText, 1);
    }

    contentContainer.html(formattedText);
});

function insertPartsSequentially(text, parts) {
    let paragraphs = $(text);
    let currentIndex = 0;

    parts.forEach(part => {
        // Выбор случайного места для вставки части, начиная с currentIndex
        let randomIndex = currentIndex + Math.floor(Math.random() * (paragraphs.length - currentIndex));
        let paragraph = paragraphs.eq(randomIndex);
        paragraph.html(paragraph.html() + part);


        // Обновление currentIndex для следующей части
        currentIndex = randomIndex + 1;
    });

    return paragraphs.prop('outerHTML');
}

function setCookie(name, value, days) {
    let expires = "";
    if (days) {
        let date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + (value || "")  + expires + "; path=/";
}

function getCookie(name) {
    let nameEQ = name + "=";
    let ca = document.cookie.split(';');
    for(let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) === ' ') c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
}
