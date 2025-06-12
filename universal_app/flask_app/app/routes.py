from flask import request, jsonify
from . import app
from .models import db, User, Question, Option, Assignment
from .utils import import_gift
import random

@app.route('/webhook/import', methods=['POST'])
def webhook_import():
    file_path = request.json.get('file')
    if not file_path:
        return jsonify({'error': 'file field required'}), 400
    import_gift(file_path)
    return jsonify({'status': 'ok'})

@app.route('/webhook/create_user', methods=['POST'])
def create_user():
    username = request.json.get('username')
    if not username:
        return jsonify({'error': 'username required'}), 400
    user = User(username=username)
    db.session.add(user)
    db.session.commit()
    return jsonify({'id': user.id})

@app.route('/webhook/assign', methods=['POST'])
def assign_questions():
    user_id = request.json.get('user_id')
    count = request.json.get('count', 5)
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'user not found'}), 404
    q_ids = [q.id for q in Question.query.all()]
    random.shuffle(q_ids)
    for q_id in q_ids[:count]:
        assignment = Assignment(user_id=user.id, question_id=q_id)
        db.session.add(assignment)
    db.session.commit()
    return jsonify({'assigned': count})

@app.route('/webhook/submit', methods=['POST'])
def submit():
    data = request.json
    user_id = data.get('user_id')
    answers = data.get('answers', {})
    results = []
    for assign_id, ans in answers.items():
        assignment = Assignment.query.get(assign_id)
        if not assignment:
            continue
        question = Question.query.get(assignment.question_id)
        correct = check_answer(question, ans)
        assignment.answered = True
        assignment.correct = correct
        results.append({'id': assign_id, 'correct': correct})
    db.session.commit()
    return jsonify({'results': results})

def check_answer(question, ans):
    if question.qtype == 'text':
        option = Option.query.filter_by(question_id=question.id).first()
        return option.text.strip().lower() == str(ans).strip().lower()
    elif question.qtype == 'single':
        opt = Option.query.filter_by(question_id=question.id, is_correct=True).first()
        return str(ans) == str(opt.id)
    elif question.qtype == 'matching':
        pairs = Option.query.filter_by(question_id=question.id).all()
        for p in pairs:
            if p.text not in ans or ans[p.text] != p.match_key:
                return False
        return True
    return False

