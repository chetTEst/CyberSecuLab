  $('#nexttask').removeAttr('hidden').hide()
  function checkVirus(index) {
    var row = document.getElementById("download-btn-" + index).parentNode.parentNode;
    var isVirus = row.getAttribute("data-is-virus") === 'True';
    if (isVirus) {
        $('#virusModal').modal('show');
        return false;
    }
    return true;
  }

  function enableDownload(index) {
    var row = document.getElementById("download-btn-" + index).parentNode.parentNode;
    row.setAttribute("data-checked", "true");

    var downloadButton = document.getElementById("download-btn-" + index);
    downloadButton.classList.remove("disabled");
  }

  function disableDownload(index) {
    var row = document.getElementById("download-btn-" + index).parentNode.parentNode;
    var isChecked = row.getAttribute("data-checked") === 'true';

    if (!isChecked) {
      return;
    }

    var checkbox = document.getElementById("checkbox-" + index);
    var downloadButton = document.getElementById("download-btn-" + index);

    if (checkbox.checked){
     downloadButton.classList.add("disabled");
    }
    else{
     downloadButton.classList.remove("disabled");
    }
  }

 function showToastMessage(message, messageType) {
    var toastElement = $('#toastMessage');
    toastElement.find('.toast-body').text(message);

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

    toastElement.toast({ delay: 15000 });
    toastElement.toast('show');
}
    function checkAnswers() {
        var allCorrect = true;
        $('tr[data-is-virus]').each(function() {
            var isVirus = $(this).attr('data-is-virus') === 'True';
            var isChecked = $(this).find('input[type=checkbox]').is(':checked');
            if (isVirus !== isChecked) {
                allCorrect = false;
                return false;
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
                    showToastMessage("Поздравляем! Все ответы верны. Вы успешно справились с задачей взвода антивируса. КиберХранитель гордиться вами! Так держать.", "success");
                    $('#nexttask').fadeIn().prop('disabled', false);
                    return false;
                },
                error: function() {
                    showToastMessage("Произошла какая-то дичь. Мы уже знаем о ней, возможно даже разбираемся. Но это не точно. Ошибка: при сохранении в базу данных.");
                    return false;
                    }
            });
        } else {
            showToastMessage("Странно, но ответ не правильный. Посмотрите внимательней. Возможно где-то кроется вирус, а может отметили что-то лишнее.", "danger");
            return false;
        }
    }


    $(document).ready(function() {
    $.ajax({
        url: '{{ url_for('get_user_answers') }}',
        type: 'GET',
        success: function(response) {
            if (response.a1){
            $('#nexttask').fadeIn().prop('disabled', false);
            }
        }
        });
    });
    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
    }
    document.addEventListener('DOMContentLoaded', () => {
        const socket = io();
        const sessionId = "{{ session_number }}";
        const username = getCookie('username');
        const first_last_name = getCookie('first_last_name');

        if (!sessionStorage.getItem('joined')) {
            if (username && sessionId) {
                socket.emit('join_session', { session_id: sessionId, username: username, first_last_name: first_last_name });
                sessionStorage.setItem('joined', true);
            }
        }
    });
