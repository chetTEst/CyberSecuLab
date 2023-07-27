function updateBadges() {
    $.ajax({
        url: "/update_badges?session_id={{ session_link }}",
        method: "GET",
        success: function(data) {
            for (var login in data) {
                if (data[login]['a1']) {
                    $("#" + login + "_a1").removeClass("bg-secondary").addClass("bg-success");
                }
                if (data[login]['a2']) {
                    $("#" + login + "_a2").removeClass("bg-secondary").addClass("bg-success");
                }
            }
        }
    });
}

// Запуск функции сразу после загрузки страницы и каждые 10 секунд
$(document).ready(function() {
    updateBadges();
    setInterval(updateBadges, 10000);
});