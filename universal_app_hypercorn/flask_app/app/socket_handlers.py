from flask import current_app, request
from flask_socketio import emit, join_room, leave_room
from . import db
from app.models import User, Assignment, Question, EssayAnswer, Session
from urllib.parse import unquote
import time

active_sessions = {}
connection_timestamps = {}

socketio = None

def init_socketio(sio):
    global socketio
    socketio = sio
    def socket_get_real_ip(request):

        """
        Получение реального IP клиента через цепочку прокси
        Порядок проверки заголовков важен!
        """

        # Проверяем заголовки в порядке приоритета
        headers_to_check = [
            'X-Forwarded-For',      # Основной заголовок для прокси
            'X-Real-IP',            # Nginx Proxy Manager может использовать этот
            'X-Original-Forwarded-For',  # Дополнительный заголовок
            'CF-Connecting-IP',     # Cloudflare
            'True-Client-IP',       # Другие CDN
        ]

        for header in headers_to_check:
            ip = request.headers.get(header)
            if ip:
                # X-Forwarded-For может содержать несколько IP через запятую
                # Берем первый (самый левый) - это оригинальный клиент
                if ',' in ip:
                    ip = ip.split(',')[0].strip()
                
                # Проверяем, что это не внутренний IP
                if not ip.startswith(('127.', '10.', '172.', '192.168.')):
                    return ip
                
                # Если это внутренний IP, но он не наш прокси - возвращаем его
                if ip != '192.168.100.81':
                    return ip

        # Если ничего не найдено, возвращаем remote_addr
        return request.remote_addr or 'unknown'

    @socketio.on('connect')
    def handle_connect():
        current_app.logger.debug(' ============== handle_connect ================ WebSocket соединение установлено')
        try:
            sid = request.sid
            connection_timestamps[sid] = time.time()
            
            # Логируем информацию о подключении
            real_ip = socket_get_real_ip(request)
            user_agent = request.headers.get('User-Agent', 'Unknown')
            
            current_app.logger.debug(f'Подключение - SID: {sid}, IP: {real_ip}, UA: {user_agent[:50]}...')
            return

        except Exception as e:
            current_app.logger.error(f"Ошибка при подключении WebSocket: {e}")
            return


    @socketio.on('join_session')
    def handle_join(data):
        current_app.logger.debug(' ============== handle_join ================')
        try:
            current_app.logger.debug('Произошел join_session socketio')
            session_identifier = data.get('session_id')
            username = data.get('username')
            first_last_name = unquote(data.get('first_last_name', 'teacher maybe'))
            current_app.logger.debug(f'Данные подключения: session={session_identifier}, user={username}, name={first_last_name}')       
            # Определяем, является ли идентификатор UUID или числом

            if not session_identifier or not username:
                current_app.logger.error('Недостаточно данных для подключения')
                return

            if session_identifier == '0':
                session_obj = Session.query.filter_by(number=0).first()
                room_id = '0'  # Для сессии 0 используем '0' как идентификатор комнаты
                current_app.logger.debug('Попытка подключения к сессии 0')
                return
            else:
                # Ищем сессию по UUID
                session_obj = Session.query.filter_by(uuid=session_identifier).first()
                if not session_obj:
                    current_app.logger.error(f"Сессия {session_identifier} не найдена")
                    return
                room_id = session_identifier  # Используем UUID как идентификатор комнаты

            user = User.query.filter_by(username=username).first()
            current_app.logger.debug(f"Текущий пользователь {user} ")

            if session_identifier not in active_sessions:
                active_sessions[session_identifier] = {}

            if user and user.session == session_obj:

                # если пользователь уже есть в сессии и не было дисконекта, обновляем его SID  в комнате
                if username in active_sessions[session_identifier]:
                    current_app.logger.debug(f'Пользователь {username} переподкючен')
                    join_room(room_id)
                    return
                # Добавляем пользователя в словарь активных сессий
                active_sessions[session_identifier][username] = request.sid

                assignments = (Assignment.query
                            .filter_by(user_id=user.id)  # фильтруем по логину
                            .join(Question)  # если требуется доступ к вопросам
                            .all())
                questions = []
                for a in assignments:
                    question_data = {
                        'id': a.question_id,
                        'qtype': a.question.qtype,
                        'correct': a.correct,
                        'user_correct': a.client_correct
                    }

                    # Добавляем текст эссе, если это эссе
                    if a.question.qtype == 'essay':
                        essay_answer = EssayAnswer.query.filter_by(
                            user_id=user.id,
                            question_id=a.question_id,
                            session_id=session_obj.id
                        ).first()
                        question_data['essay_text'] = essay_answer.text if essay_answer else ''
                        question_data['essay_question'] = a.question.text if a.question else ''
                    questions.append(question_data)
                data = {
                    'username': username,
                    'first_last_name': first_last_name,
                    'questions': questions
                }
                current_app.logger.debug(f"Подключение ученика {username} к сокету")
                current_app.logger.debug(f"active_sessions {active_sessions}" )
                join_room(room_id)
                emit('user_joined', data, room=room_id)
            else:
                current_app.logger.debug(f"Подключение учителя к комнате {room_id}")
                # Добавляем пользователя в словарь активных сессий
                active_sessions[session_identifier]['teacher'] = request.sid
                current_app.logger.debug(f"active_sessions {active_sessions}" )
                join_room(room_id)
                emit('user_joined', {'username': 'teacher'}, room=room_id)  
        except Exception as e:
            current_app.logger.error(f"Error in join_session handler: {e}")


    @socketio.on('remove_user')
    def handle_remove_user(data):
        current_app.logger.debug(' ============== handle_remove_user ================')
        try:
            session_identifier = data.get('session_id')
            current_app.logger.debug(f"session_identifier {session_identifier}")
            username = data.get('username')
            current_app.logger.debug(f"username {username}")
            # Определяем, является ли идентификатор UUID или числом
            if session_identifier == '0':
                session_obj = Session.query.filter_by(number=0).first()
            else:
                # Ищем сессию по UUID
                session_obj = Session.query.filter_by(uuid=session_identifier).first()
                if not session_obj:
                    return

            # Удаление пользователя из иктивных пользователей сессии
            user = User.query.filter_by(username=username, session_id=session_obj.id).first()
            if user:
                user.active = False
                current_app.logger.debug(f'delete {user}, {user.username}')
                db.session.commit()
                emit('remove_user', {'username': user.username}, room=session_identifier)
        except Exception as e:
            current_app.logger.error(f"Error in remove_user handler: {e}")


    @socketio.on('disconnect')
    def handle_disconnect():
        current_app.logger.debug(' ============== handle_disconnect ================ WebSocket соединение разорвано')
        try:
            sid = request.sid
            current_app.logger.debug(f'Отключение SID: {sid}')
            
            # Удаляем из временных меток
            if sid in connection_timestamps:
                connection_time = time.time() - connection_timestamps[sid]
                current_app.logger.debug(f'Время соединения: {connection_time:.2f} секунд')
                del connection_timestamps[sid]
            
            # Очищаем активные сессии
            sessions_to_clean = []
            for session_id, users in active_sessions.items():
                users_to_remove = []
                for username, user_sid in users.items():
                    if user_sid == sid:
                        users_to_remove.append(username)
                
                for username in users_to_remove:
                    del users[username]
                    current_app.logger.debug(f'Удален пользователь {username} из сессии {session_id}')
                
                # Если сессия пуста, помечаем для удаления
                if not users:
                    sessions_to_clean.append(session_id)
            
            # Удаляем пустые сессии
            for session_id in sessions_to_clean:
                del active_sessions[session_id]
                current_app.logger.debug(f'Удалена пустая сессия {session_id}')
                
        except Exception as e:
            current_app.logger.error(f"Ошибка при отключении WebSocket: {e}")

    @socketio.on('ping')
    def handle_ping():
        """Обработка ping от клиента"""
        emit('pong', {'timestamp': time.time()})
