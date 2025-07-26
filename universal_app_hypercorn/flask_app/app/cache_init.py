# app/cache_init.py

from collections import defaultdict
from .models import Question, Option

def build_questions_by_pool(db):
    pool_map = defaultdict(list)
    for q_id, pool in db.session.query(Question.id, Question.pool):
        pool_map[pool].append(q_id)
    return dict(pool_map)

def build_correct_answers(db):
    correct_answers = defaultdict(list)
    for opt in Option.query.filter_by(is_correct=True).all():
        correct_answers[opt.question_id].append(opt.plain_values.lower().strip())
    return dict(correct_answers)
