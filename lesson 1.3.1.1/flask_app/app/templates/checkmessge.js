   function checkAnswer(answer) {
      var modificationType = {{ answer }}
      var resultElement = document.getElementById("result");

      if (answer === modificationType) {
        resultElement.textContent = sendAnswer(resultElement);
        resultElement.classList.add("text-success");
        resultElement.classList.remove("text-danger");
      } else {
        sendMessage();
      }
    }

    function sendAnswer() {
    var formData = new FormData();
    formData.append('is_correct', isCorrect);

    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/record-answer', true);
    xhr.onload = function() {
        if (xhr.status === 200) {
            var response = JSON.parse(xhr.responseText);
            if (response.success) {
                console.log("Ответ записан в базу данных.");
            }
        }
    };
    xhr.send(formData);
    return 'Правильно! Ответ записан в базу данных.';
    }

    function sendMessage() {
      var form = document.createElement("form");
      form.method = "POST";
      form.action = "/session{{ session_number }}/resultmessage";

      var input = document.createElement("input");
      input.type = "hidden";
      input.name = "message";
      input.value = "{{ message }}";
      var input = document.createElement("input");
      input.type = "hidden";
      input.name = "va";
      input.value = "va";

      form.appendChild(input);
      document.body.appendChild(form);
      form.submit();
    }
