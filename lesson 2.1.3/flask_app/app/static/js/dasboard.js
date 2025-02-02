    $('#nexttask').removeAttr('hidden').hide() // Кнопка перехода к новому заданию
    // Загрузите необходимые модули
    var oop = ace.require("ace/lib/oop");
    var MysqlHighlightRules = ace.require("ace/mode/mysql_highlight_rules").MysqlHighlightRules;
    var TextMode = ace.require("ace/mode/text").Mode;

    // Создайте кастомные правила подсветки на основе правил MySQL
    function CustomHighlightRules() {
        MysqlHighlightRules.call(this);

        // Ваши кастомные ключевые слова
        var customKeywords = "выбрать|где|значение|изхранилища|обновить|положитьв|удалить|установить|ВЫБРАТЬ|ГДЕ|ЗНАЧЕНИЕ|ИзХранилища|ОБНОВИТЬ|ПоложитьВ|ПОЛОЖИТЬВ|УДАЛИТЬ|УСТАНОВИТЬ";

        // Создайте новое правило для кастомных ключевых слов
        var customRule = {
            token: "keyword",
            regex: customKeywords
        };

        // Добавить кастомное правило в начало массива правил
        this.$rules.start.unshift(customRule);
    }

    oop.inherits(CustomHighlightRules, MysqlHighlightRules);

    // Создайте кастомный режим на основе режима MySQL
    function CustomMode() {
        TextMode.call(this);
        this.HighlightRules = CustomHighlightRules;
    }

    oop.inherits(CustomMode, TextMode);

    // Устанавливаем режим для редактора
    var editor = ace.edit("editor");
    editor.session.setMode(new CustomMode());
    editor.setTheme("ace/theme/github");



    var questions = {{ questions|tojson }}; // Это список вопросов
    var currentQuestionIndex = 0; // Это индекс текущего вопроса в массиве вопросов
    function EndTest() {
        $('#quiz-form').hide();
        $('#progress-bar').hide();
        $('#table-head').hide();
        $('#table-task').hide();

        // Показываем уведомление в #question-area
        $('#question-area').html(
            '<div class="alert alert-success" role="alert">' +
                '<h4 class="alert-heading">Поздравляем!</h4>' +
                '<p>Вы освоили основные команды языка «Запросик»</p>' +
                '<hr>' +
                '<p class="mb-0">Артур поздравляет вас, вы ответили на все вопросы!<br/>Вы супер-Молодец.<br/>Можно переходить к следующему блоку.</p>' +
            '</div>'
        );
    }

    function loadQuestion() {
        // Загрузка вопроса
        if (currentQuestionIndex < 5) {
            var currentQuestion = questions[currentQuestionIndex];
            $('#question-area').html(currentQuestion.text);
            updateProgressBar();
            }
        else {
            // Иначе все вопросы уже отвечены, скрываем форму и бейджи вопросов
            EndTest();
            $('#nexttask').fadeIn().prop('disabled', false).addClass('btn-pulse');
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
            var startButton = document.getElementById("submit-answer-btn");
            startButton.disabled = true;
            startButton.innerHTML = '<span class="spinner-grow" style="width: 1.5rem; height: 1.5rem;" role="status" aria-hidden="true"></span> Проверяем...';
            var answer = editor.getValue();
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
                    startButton.disabled = false;
                    startButton.innerHTML = 'Проверить';
                    $('#feedback').html(
                        '<div id ="question_alert" class="alert alert-' + alertClass + ' alert-dismissible fade show" role="alert">' +
                            alertMessage +
                            '<button type="button" class="close" data-dismiss="alert" aria-label="Close">' +
                                '<span aria-hidden="true">&times;</span>' +
                            '</button>' +
                        '</div>'
                    );
                    if (response.correct) {
                        $("#responseTable_student_answer").remove(); // Удалить таблицу с ответами
                        $("#responseTable_reference_answer").remove();
                        currentQuestionIndex++; // Переходим к следующему вопросу

                        // Закрыть уведомление через 2 секунды
                        window.setTimeout(function() {
                            $("#question_alert").fadeTo(500, 0).slideUp(500, function(){
                                $(this).remove();
                            });
                        }, 2000);

                        loadQuestion();
                    }
                    else {
                        // Создать таблицу с данными
                        $("#responseTable_student_answer").remove(); // Сначала удалить пердыдущую
                        $("#responseTable_reference_answer").remove(); // Сначала удалить пердыдущую

                        var tableHtml_reference_answer = '<table id="responseTable_reference_answer" class="table table-bordered table-striped table-sm"><caption>Результат эталонного запроса:</caption>';
                        tableHtml_reference_answer += '<tbody>';
                        for (var i = 0; i < response.reference_answer.length; i++) {
                            var item = response.reference_answer[i];
                            tableHtml_reference_answer += '<tr>';
                            for (var j = 0; j < item.length; j++) {
                                tableHtml_reference_answer += '<td>' + item[j] + '</td>';
                            }
                            tableHtml_reference_answer += '</tr>';
                        }
                        tableHtml_reference_answer += '</tbody></table>';

                        var tableHtml_student_answer = '<table id="responseTable_student_answer" class="table table-bordered table-striped table-sm"><caption>Результат Вашего запроса:</caption>';
                        tableHtml_student_answer += '<tbody>';
                        for (var i = 0; i < response.student_answer.length; i++) {
                            var item = response.student_answer[i];
                            tableHtml_student_answer += '<tr>';
                            for (var j = 0; j < item.length; j++) {
                                tableHtml_student_answer += '<td>' + item[j] + '</td>';
                            }
                            tableHtml_student_answer += '</tr>';
                        }
                        tableHtml_student_answer += '</tbody></table>';

                        // Вставить таблицу после кнопки Сообщения "Фидбек"
                        $('#feedback').after(tableHtml_student_answer);
                        $('#reference').after(tableHtml_reference_answer);


                        // Закрыть уведомление через 2 секунды
                        window.setTimeout(function() {
                            $("#question_alert").fadeTo(500, 0).slideUp(500, function(){
                                $(this).remove();
                            });
                        }, 2000);
                    }
                }
            });
        });
        $('#reset_db').click(function(e) {
            e.preventDefault(); // Предотвратить стандартное поведение кнопки/формы
            var startButton = document.getElementById("reset_db");
            startButton.disabled = true;
            startButton.innerHTML = '<span class="spinner-grow" style="width: 1.5rem; height: 1.5rem;" role="status" aria-hidden="true"></span> Обновляем...';
            $.ajax({
                url: '{{ url_for('reset_database') }}',
                type: 'POST',
                success: function(response) {
                    startButton.disabled = false;
                    startButton.innerHTML = 'Обновить значения Базы данных';
                    var alertClass = response.dbupdate ? 'warning' : 'info';
                    var alertMessage = response.dbupdate ? 'База данных обновлена!' : 'Что-то пошло не так. Возможно даже сломалось. Попробуйте еще раз!';
                    var alertMessage = 'База данных обновлена!';
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
            var answers = [response.a1, response.a2, response.a3, response.a4, response.a5];
            currentQuestionIndex = answers.findIndex(function(a) {
                return a === false;
            });

            if (currentQuestionIndex !== -1) {
                loadQuestion();
            } else {
               // Иначе все вопросы уже отвечены, скрываем форму и бейджи вопросов
                EndTest();
                $('#nexttask').fadeIn().prop('disabled', false).addClass('btn-pulse');
            }
        }
    });
        submitAnswer();
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