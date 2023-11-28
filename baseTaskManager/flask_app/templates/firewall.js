  $(function () {
   $('[data-toggle="popover"]').popover({trigger: 'focus'})
  })

  function enablePort(number){
      var row = document.getElementById("port-" + number).parentNode.parentNode.parentNode;
      row.setAttribute("data-enabled", "false");
      $("#port-"+number).removeClass('badge-danger badge-secondary').addClass('badge-success');
  }

  function disablePort(number){
      var row = document.getElementById("port-" + number).parentNode.parentNode.parentNode;
      row.setAttribute("data-enabled", "true");
      $("#port-"+number).removeClass('badge-success badge-secondary').addClass('badge-danger');
  }


 function showToastMessage(message, messageType) {
    var toastElement = $('#toastMessage');
    toastElement.find('.toast-body').text(message);

    // Настройка класса alert и текста заголовка
    var alertClass = "alert ";
    var alertTitle = "";
    if (messageType === "success") {
        alertClass += "alert-success";
        alertTitle = "ОТЛИЧНО!";
    } else if (messageType === "danger") {
        alertClass += "alert-danger";
        alertTitle = "ВНИМАНИЕ!";
    } else {
        alertClass += "alert-info";
        alertTitle = "ИНФОРМАЦИЯ";
    }
    toastElement.find('#toast-header').removeClass('alert alert-success alert-danger alert-info').addClass(alertClass);
    toastElement.find('#toastheader').text(alertTitle);

    // Показать всплывающее сообщение с задержкой в 15 секунд перед автоматическим закрытием
    toastElement.toast({ delay: 15000 });
    toastElement.toast('show');
}
    function checkAnswers() {
        var allCorrect = true;
        $('tr[data-is-virus]').each(function() {
            var isVirus = $(this).attr('data-is-virus') === 'True';
            var isChecked = $(this).attr('data-enabled') === 'true';
            if (isVirus !== isChecked) {
                allCorrect = false;
                return false;  // break the loop
            }
        });

        if (allCorrect) {
            $.ajax({
                url: "/check_answer",
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({ answer: 'a1' }),
                dataType: 'json',
                success: function() {
                    showToastMessage("Поздравляем! Все ответы верны. Вы успешно справились с задачей Корпуса Брандмауэров. КиберХранитель гордиться вами! Так держать.", "success");
                    return false;
                },
                error: function() {
                    showToastMessage("Произошла какая-то дичь. Мы уже знаем о ней, возможно даже разбираемся. Но это не точно. Ошибка: при сохранении в базу данных.");
                    return false;
                    }
            });
        } else {
            showToastMessage("Странно, но ответ не правильный. Посмотрите внимательней. Возможно где-то осталась незакрытая дверь, ну или вы закрыли лишнюю и теперь в курьер не может доставить важную информацию", "danger");
            return false;
        }
    }