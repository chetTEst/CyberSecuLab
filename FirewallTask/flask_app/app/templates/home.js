  $(document).ready(function() {
    const contentContainer = $('#content_text');
    let parts = ["kaspC", "TF{92", "9f2aa", "87c42", "a}"];

    let formattedText = getCookie('formattedText');
    if (!formattedText) {
        insertPartsSequentially(contentContainer, parts);
        formattedText = contentContainer.html();
        setCookie('formattedText', formattedText, 1);
    }
    else{
        contentContainer.empty();
        contentContainer.append(formattedText);
    }

});

function insertPartsSequentially(textContainer, parts) {
    let paragraphsHTML = $(textContainer).html() //.filter('p');
    paragraphs = $(paragraphsHTML).filter('p');
    textContainer.empty();
    paragraphs.each((index, paragraph) => {
        let $paragraphElement = $(paragraph)
        let paragraphText = $paragraphElement.text();
        let paragraphHtml = $paragraphElement.html();
        let modifiedText = paragraphText;

        // Для первых двух параграфов вставлять по две части, для третьего - одну
        if (index < 2 && parts.length >= 2 * index + 1) {
            let insertPosition1 = Math.floor(Math.random() * (Math.floor(paragraphText.length/2) + 1));
            let insertPosition2 = insertPosition1 + 7 + Math.floor(Math.random() * (paragraphText.length - 7 + 1 - insertPosition1));
            modifiedText = [paragraphText.slice(0, insertPosition1), '<b>' + parts[2 * index] + '</b>', paragraphText.slice(insertPosition1)].join('');
            modifiedText = [modifiedText.slice(0, insertPosition2), '<b>' + parts[2 * index + 1] + '</b>', modifiedText.slice(insertPosition2)].join('');
        } else if (index === 2 && parts.length >= 5) {
            let insertPosition = Math.floor(Math.random() * (paragraphText.length + 1));
            modifiedText = [paragraphText.slice(0, insertPosition), '<b>' + parts[4] + '</b>', paragraphText.slice(insertPosition)].join('');
        }
       paragraph.innerHTML = modifiedText;
       textContainer.append(paragraph);
    });

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
