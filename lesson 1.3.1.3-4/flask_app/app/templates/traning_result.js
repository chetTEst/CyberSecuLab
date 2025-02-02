function updateBadges() {
    $.ajax({
        url: "/update_badges?session_id={{ session_link }}",
        method: "GET",
        success: function(data) {
            for (var login in data) {
                if (data[login]['a1']) {
                    $("#" + login + "_q1").removeClass("bg-secondary").addClass("bg-success");
                }
                if (data[login]['a2']) {
                    $("#" + login + "_q2").removeClass("bg-secondary").addClass("bg-success");
                }
                if (data[login]['a3']) {
                    $("#" + login + "_q3").removeClass("bg-secondary").addClass("bg-success");
                }
                if (data[login]['a4']) {
                    $("#" + login + "_q4").removeClass("bg-secondary").addClass("bg-success");
                }
            }
        }
    });
}

$(document).on('click', '.remove-user-btn', function () {
    const username = $(this).data('username');
    const sessionId = "{{ session_link }}";

    $(`#user-${username}`).remove();

    const userListItems = document.querySelectorAll('.list-group-item');
    userListItems.forEach((item, index) => {
        const userNameElement = item.querySelector('.user-name');
        const nameParts = userNameElement.textContent.split(')');
        if (nameParts.length > 1) {
            userNameElement.textContent = `${index + 1})${nameParts[1]}`;
        }
    });


    socket.emit('remove_user', {
        session_id: sessionId,
        username: username
    });
});




// Запуск функции сразу после загрузки страницы и каждые 10 секунд
$(document).ready(function() {
    updateBadges();
    setInterval(updateBadges, 10000);
});

const socket = io();
const sessionId = "{{ session_link }}";
socket.on('connect', () => {
    socket.emit('join_session', { session_id: sessionId });
});


socket.on('user_joined', (data) => {
    const userList = document.querySelector('.list-group');
    const nextIndex = userList.children.length + 1;
    const newItem = document.createElement('li');
    newItem.id = `user-${data.username}`;
    if(data.username != 'teacher') {
        newItem.className = 'list-group-item d-flex align-items-center';
        newItem.innerHTML = `<span class="user-name flex-grow-1">${nextIndex}). ${data.first_last_name}</span>
            <div class="badges d-flex gap-2">
                <span id="${data.username}_q1" class="badge bg-secondary">q1</span>
                <span id="${data.username}_q2" class="badge bg-secondary">q2</span>
                <span id="${data.username}_q3" class="badge bg-secondary">q3</span>
                <span id="${data.username}_q4" class="badge bg-secondary">q4</span>
            </div>
            <button class="btn btn-danger btn-sm float-end remove-user-btn" data-username="${data.username}">Удалить</button>`;
        userList.appendChild(newItem);
        }
});