function startTraining() {
        var startButton = document.getElementById("start-training-btn");
        startButton.disabled = true;
        startButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Начинаем загрузку...';

        $.ajax({
            url: '{{ url_for('start_training_async') }}',
            type: 'POST',
            success: function(response) {
                window.location.href = response.redirect_url;
            },
            error: function() {
                alert('Возникла непредвиденная ошибка. Повторите попытку позже');
                startButton.disabled = false;
                startButton.innerHTML = 'Начать тренировку';
            }
        });
    }