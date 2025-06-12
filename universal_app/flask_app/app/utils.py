import re
from .models import db, Question, Option

QUESTION_RE = re.compile(r"(?P<text>.*)\{(?P<body>.*)\}", re.DOTALL)

def import_gift(file_path):
    with open(file_path, encoding='utf-8') as f:
        content = f.read()

    for block in content.split('\n\n'):
        block = block.strip()
        if not block:
            continue
        m = QUESTION_RE.search(block)
        if not m:
            continue
        text = m.group('text').strip()
        body = m.group('body').strip()
        parse_question(text, body)
    db.session.commit()

def parse_question(text, body):
    if '->' in body and '=' in body:
        qtype = 'matching'
        pairs = [p.strip() for p in body.split('=') if p.strip()]
        q = Question(text=text, qtype=qtype)
        db.session.add(q)
        db.session.flush()
        for pair in pairs:
            left, right = pair.split('->')
            opt = Option(question_id=q.id, text=left.strip(), is_correct=True, match_key=right.strip())
            db.session.add(opt)
        return
    if body.count('=') > 1 or '~' in body:
        qtype = 'single'
        q = Question(text=text, qtype=qtype)
        db.session.add(q)
        db.session.flush()
        parts = re.split(r'[=~]', body)
        signs = [c for c in body if c in '=~']
        for sign, part in zip(signs, parts[1:]):
            opt = Option(question_id=q.id, text=part.strip(), is_correct=(sign=='='))
            db.session.add(opt)
        return
    qtype = 'text'
    q = Question(text=text, qtype=qtype)
    db.session.add(q)
    db.session.flush()
    opt = Option(question_id=q.id, text=body.strip(), is_correct=True)
    db.session.add(opt)

