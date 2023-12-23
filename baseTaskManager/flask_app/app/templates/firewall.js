  $(function () {
   $('[data-toggle="popover"]').popover({trigger: 'focus'})
  })

  function enablePort(number){
  var row = document.getElementById("port-" + number).parentNode.parentNode.parentNode;
  row.setAttribute("data-enabled", "false");
  $("#port-"+number).removeClass('badge-danger badge-secondary').addClass('badge-success');
  checkAnswers();
  }

  function disablePort(number){
  var row = document.getElementById("port-" + number).parentNode.parentNode.parentNode;
  row.setAttribute("data-enabled", "true");
  $("#port-"+number).removeClass('badge-success badge-secondary').addClass('badge-danger');
  checkAnswers();
  }

function checkAnswers() {
    var allCorrect = true;
    var userId = getCookie('user_id'); // Получение user_id из cookie
    var salts = splitUserIdIntoSalts(userId); // Разделение user_id на соли
    $('tr[data-is-virus]').each(function(index) {
        var isVirus = $(this).attr('data-is-virus')
        var isChecked = $(this).attr('data-enabled') === 'true';
        var isAnswer = $(this).attr('data-is-answer')

        // Генерация хешей для проверки
        var isVirusHash = generateHash('True', salts[index % 16]);
        var isAnswerHash = generateHash('False', salts[index % 16]);

        if ((isVirus !== isVirusHash || isAnswer !== isAnswerHash) && isChecked) {
            allCorrect = false;
            return false;  // break the loop
        }
    });

    if (allCorrect) {
        $.ajax({
            url: "/check_answer",
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ user_id: '{{ user_id }}' }),
            dataType: 'json'
        });
    }
}

function splitUserIdIntoSalts(userId) {
    var length = userId.length;
    var partLength = Math.floor(length / 16);
    var salts = [];

    for (var i = 0; i < length; i += partLength) {
        salts.push(userId.substring(i, i + partLength));
    }

    return salts;
}

function generateHash(value, salt) {
    var hash = CryptoJS.SHA256(value + salt).toString();
    return hash;
}

function getCookie(name) {
    var value = "; " + document.cookie;
    var parts = value.split("; " + name + "=");
    if (parts.length === 2) {
        return parts.pop().split(";").shift();
    }
    return null;
}

