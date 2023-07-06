function updateBadges() {
    $.ajax({
        url: "/update_badges",  // URL-адрес Flask-маршрута, который вы создадите
        method: "GET",
        success: function(data) {
            for (var login in data) {
            console.log(data[login]);
                if (data[login]['authenticated']) {
                    $("#" + login + "_login").removeClass("text-bg-secondary").addClass("text-bg-success");
                }
                if (data[login]['two_factor_enabled']) {
                    $("#" + login + "_2fa").removeClass("text-bg-secondary").addClass("text-bg-success");
                }
                if (data[login]['authenticated'] && data[login]['two_factor_enabled']) {
                    $("#" + login + "_2fa_login").removeClass("text-bg-secondary").addClass("text-bg-success");
                }
            }
        }
    });
}

// Запустите функцию сразу после загрузки страницы и каждые 5 секунд
$(document).ready(function() {
    updateBadges();
    setInterval(updateBadges, 5000);
});