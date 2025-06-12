import re
from .models import db, Question, Option

QUESTION_NUMBER_RE = re.compile(r"//\s*QuestionNumber:\s*(\d+)", re.IGNORECASE)

QUESTION_RE = re.compile(r"(?P<text>.*)\{(?P<body>.*)\}", re.DOTALL)

def import_gift(file_path):
    with open(file_path, encoding='utf-8') as f:
        content = f.read()

    for block in content.split('\n\n'):
        block = block.strip()
        if not block:
            continue
        lines = block.splitlines()
        pool = 1
        if lines and lines[0].startswith('//'):
            mnum = QUESTION_NUMBER_RE.search(lines[0])
            if mnum:
                pool = int(mnum.group(1))
            lines = lines[1:]
        block_text = '\n'.join(lines)
        m = QUESTION_RE.search(block_text)
        if not m:
            continue
        text = m.group('text').strip()
        body = m.group('body').strip()
        parse_question(text, body, pool)
    db.session.commit()

def parse_question(text, body, pool):
    if '->' in body and '=' in body:
        qtype = 'matching'
        pairs = [p.strip() for p in body.split('=') if p.strip()]
        q = Question(text=text, qtype=qtype, pool=pool)
        db.session.add(q)
        db.session.flush()
        for pair in pairs:
            left, right = pair.split('->')
            opt = Option(question_id=q.id, text=left.strip(), is_correct=True, match_key=right.strip())
            db.session.add(opt)
        return

    correct_count = body.count('=')
    if correct_count > 1:
        qtype = 'multi'
    elif correct_count == 1 or '~' in body:
        qtype = 'single'
    else:
        qtype = 'text'

    q = Question(text=text, qtype=qtype, pool=pool)
    db.session.add(q)
    db.session.flush()

    if qtype in ('single', 'multi'):
        parts = re.split(r'[=~]', body)
        signs = [c for c in body if c in '=~']
        for sign, part in zip(signs, parts[1:]):
            opt = Option(question_id=q.id, text=part.strip(), is_correct=(sign=='='))
            db.session.add(opt)
    elif qtype == 'text':
        opt = Option(question_id=q.id, text=body.strip(), is_correct=True)
        db.session.add(opt)


