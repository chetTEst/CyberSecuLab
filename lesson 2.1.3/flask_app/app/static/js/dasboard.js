   function EndTest() {
        $('#quiz-form').hide();
        $('#progress-bar').hide();

        // Показываем уведомление в #question-area
        $('#question-area').html(
            '<div class="alert alert-success" role="alert">' +
                '<h4 class="alert-heading">Поздравляем!</h4>' +
                '<p>Вы освоили основные команды языка «Запросик»</p>' +
                '<hr>' +
                '<p class="mb-0">Артур поздравляет вас, вы ответили на все вопросы!<br/>Вы супер-Молодец.</p>' +
            '</div>'
        );
    }

    function loadQuestion() {
        // Загрузка вопроса
        if (currentQuestionIndex < 4) {
            var currentQuestion = questions[currentQuestionIndex];
            $('#question-area').html(currentQuestion.text);
            updateProgressBar();
            }
        else {
            // Иначе все вопросы уже отвечены, скрываем форму и бейджи вопросов
            EndTest();
        }
    }

    function updateProgressBar() {
        var progressBar = '';
        for (var i = 0; i < questions.length; i++) {
            var btnClass = i < currentQuestionIndex ? 'btn-success' : i == currentQuestionIndex ? 'btn-primary' : 'btn-secondary';
            progressBar += '<button type="button" class="btn ' + btnClass + ' mr-1" data-toggle="tooltip" data-placement="top" title="Номер вопроса">' + (i + 1) + '</button>';
        }
        $('#progress-bar').html(progressBar);
    }

    function submitAnswer() {
        // Проверка ответа
        $('#quiz-form').submit(function(e) {
            e.preventDefault();
            var answer = $('#answer').val();
            var questionId = questions[currentQuestionIndex].id;
            $.ajax({
                url: '{{ url_for('check_answer') }}',
                type: 'POST',
                data: {
                    'question_id': questionId,
                    'answer': answer
                },
                success: function(response) {
                var alertClass = response.correct ? 'success' : 'danger';
                var alertMessage = response.correct ? 'Правильный ответ!' : 'Неправильный ответ. Попробуйте еще раз.';

                $('#feedback').html(
                    '<div id ="question_alert" class="alert alert-' + alertClass + ' alert-dismissible fade show" role="alert">' +
                        alertMessage +
                        '<button type="button" class="close" data-dismiss="alert" aria-label="Close">' +
                            '<span aria-hidden="true">&times;</span>' +
                        '</button>' +
                    '</div>'
                );

                // Закрыть уведомление через 2 секунды
                window.setTimeout(function() {
                    $("#question_alert").fadeTo(500, 0).slideUp(500, function(){
                        $(this).remove();
                    });
                }, 2000);


                if (response.correct) {
                    currentQuestionIndex++; // Переходим к следующему вопросу
                    loadQuestion();
                    $('#answer').val(''); // Очищаем поле ответа
                }
            }
            });
        });
    }


    $(document).ready(function() {
    // AJAX запрос к серверу при загрузке страницы
    $.ajax({
        url: '{{ url_for('get_user_answers') }}',  // Маршрут на сервере, который возвращает текущие значения `a`
        type: 'GET',
        success: function(response) {
            // Обновление currentQuestionIndex, чтобы он указывал на первый вопрос, у которого `a` равно `False`
            var answers = [response.a1, response.a2, response.a3, response.a4];
            currentQuestionIndex = answers.findIndex(function(a) {
                return a === false;
            });

            if (currentQuestionIndex !== -1) {
                loadQuestion();
            } else {
               // Иначе все вопросы уже отвечены, скрываем форму и бейджи вопросов
                EndTest();
            }
        }
    });
        submitAnswer();
    });