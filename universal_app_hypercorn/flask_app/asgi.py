#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ASGI приложение для Flask + Socket.IO с Uvicorn
"""

import os
import sys
import socketio

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, socketio as sio

def create_asgi_app():
    """Создает ASGI приложение"""
    
    # Создаем Flask приложение
    flask_app = create_app()
    flask_app.logger.error(f"SocketIO async_mode is {sio.async_mode}")
    
    # Для Flask-SocketIO с threading режимом используем WSGIMiddleware
    from uvicorn.middleware.wsgi import WSGIMiddleware
    
    # Оборачиваем Flask app в WSGI middleware для Uvicorn
    asgi_app = WSGIMiddleware(flask_app)
    
    return asgi_app

# Создаем приложение для Uvicorn
app = create_asgi_app()

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(
        "asgi:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        workers=1,
        log_level="debug",
        access_log=True
    )
