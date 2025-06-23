from collections import defaultdict
from . import app
from .gift_importer import import_gift
from .models import db, Session, User, Question, Option, Assignment
from config import GIFT_FILE, PROD_STATE

from icecream import ic

ic.enable() if not PROD_STATE else ic.disable()

db.init_app(app)

with app.app_context():
    def pool_to_rom():
        pool_map = defaultdict(list)
        for q_id, pool in db.session.query(Question.id, Question.pool):
            pool_map[pool].append(q_id)

        # dict(...) — чтобы превратить defaultdict в обычный словарь и
        # случайно не изменить его позже
        app.config["QUESTIONS_BY_POOL"] = dict(pool_map)
        app.config['POOL_SIZE'] = len(pool_map)
        coorect_answers = defaultdict(list)
        for opt in Option.query.filter_by(is_correct=True).all():
            coorect_answers[opt.question_id].append(opt.plain_values.lower().strip())
        app.config['CORRECT_ANSWERS'] = dict(coorect_answers)
        return pool_map
    db.create_all()
# -------------------- импорт вопросов --------------------
    # Если таблица ещё пуста — заливаем GIFT
    if Question.query.count() == 0 and GIFT_FILE:
        try:
            importer = import_gift(GIFT_FILE, return_importer=True)
            app.logger.info(f"БД вопросов. ГОТОВО! Загружено {importer[1]} вопросов")
            # Сохраняем список пулов в конфиге для последующего использования
            # ----- кэшируем id вопросов по pool -----
            pool_to_rom()
            app.logger.info(f"Из которых всего различных вариантов вопросов: {app.config['POOL_SIZE']}")
            app.logger.info("Вопросы в кешэ. ГОТОВО!")
        except FileNotFoundError:
            # нет файла — молча пропускаем или логируем
            app.logger.warning("GIFT-файл %s не найден", GIFT_FILE)
    else:
        pool_to_rom()
        app.logger.info("Вопросы в кешэ из БД. ГОТОВО!")

