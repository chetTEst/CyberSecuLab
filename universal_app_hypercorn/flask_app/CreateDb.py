
import sys
import os
# Импортируем Flask приложение для создания контекста
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from collections import defaultdict
from flask import current_app
from config import GIFT_FILE, db_host, db_port, db_user, db_pass, db_name
from sqlalchemy import inspect
# Заменяем относительные импорты на абсолютные
try:
    # Пробуем относительные импорты (если запускается из приложения)
    from .models import Session, User, Question, Option, Assignment
    from . import db, create_app_for_db
    from .gift_importer import import_gift
except ImportError:
    # Если не получается, используем абсолютные импорты
    from app.models import Session, User, Question, Option, Assignment
    from app import db, create_app_for_db
    from app.gift_importer import import_gift


def check_initialization_marker():
    """Проверяет маркер инициализации в таблице Session"""
    try:
        # Используем сессию 0 как маркер инициализации
        marker = Session.query.filter_by(number=-1).first()  # Специальный маркер
        return marker is not None
    except:
        return False

def create_initialization_marker():
    """Создает маркер инициализации"""
    try:
        marker = Session(number=-1, id=-1)  # Специальный маркер инициализации
        db.session.add(marker)
        db.session.commit()
        current_app.logger.info("Маркер инициализации создан")
        return False
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Ошибка при создании маркера: {e}")
        return True

def initialize_db():
    current_app.logger.debug("========== initialize_db ==========")
    
    # Проверяем маркер инициализации
    if check_initialization_marker():
        current_app.logger.info("База данных уже инициализирована, пропускаем...")
        return
    
    # Проверяем, существуют ли уже таблицы в базе данных
    inspector = inspect(db.engine)
    tables_exist = inspector.get_table_names()
    
    # Создаем таблицы только если их нет
    if not tables_exist:
        try:
            db.create_all()
            current_app.logger.info("Таблицы созданы в базе данных")
        except Exception as e:
            current_app.logger.error(f"Ошибка при создании таблиц: {e}")
            return
    else:
        current_app.logger.info("Таблицы уже существуют в базе данных")

    # Проверяем, существует ли сессия 0
    session_zero = Session.query.filter_by(number=0).first()
    if not session_zero:
        try:
            session = Session(number=0, id=0)
            db.session.add(session)
            db.session.commit()
            current_app.logger.info("Добавлена сессия 0!")
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Ошибка при добавлении сессии 0: {e}")

    # -------------------- импорт вопросов --------------------
    # Если таблица ещё пуста — заливаем GIFT
    if Question.query.count() == 0 and GIFT_FILE:
        try:
            importer = import_gift(GIFT_FILE, return_importer=True)
            current_app.logger.info(f"БД вопросов. ГОТОВО! Загружено {importer[1]} вопросов")
            current_app.logger.info("Импорт вопросов завершен!")
        except FileNotFoundError:
            current_app.logger.warning("GIFT-файл %s не найден", GIFT_FILE)
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Ошибка при импорте вопросов: {e}")
    else:
        current_app.logger.info("Вопросы уже загружены в БД")
    
# Создаем маркер успешной инициализации
if __name__ == "__main__":
    app = create_app_for_db()
    db.init_app(app)
    with app.app_context():
        db.create_all()
        initialize_db()
        if not check_initialization_marker():
            create_initialization_marker()
        current_app.logger.info("========== Инициализация БД завершена ==========")
