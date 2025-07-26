import re
from .models import Question, Option
from . import db
# Предполагается, что модели Question и Option уже определены, как в вашем запросе
QUESTION_NUMBER_RE = re.compile(r"//\s*QuestionNumber:\s*(\d+)", re.IGNORECASE)
QUESTION_RE = re.compile(r"(?P<text>.*)\{(?P<body>.*)\}", re.DOTALL)
DESCRIPTION_RE = re.compile(r"^(?!//)(?P<text>.+)$", re.DOTALL)


def import_gift(file_path):
    """
    Парсит GIFT-файл и сохраняет вопросы в базу данных.
    Args:
        file_path (str): Путь к GIFT-файлу.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
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
        block_text = '\n'.join(lines).strip()

        # Проверка на описание (без {})
        desc_match = DESCRIPTION_RE.match(block_text)
        if desc_match:
            q = Question(text=desc_match.group('text').strip(), qtype='description', pool=pool)
            db.session.add(q)
            continue

        # Обработка вопросов с {}
        question_match = QUESTION_RE.search(block_text)
        if not question_match:
            continue
        text = question_match.group('text').strip()
        body = question_match.group('body').strip()
        parse_question(text, body, pool)

    db.session.commit()

def parse_question(text, body, pool):
    """
    Парсит тело вопроса и сохраняет его и варианты ответа в базу данных.
    Args:
        text (str): Текст вопроса.
        body (str): Содержимое внутри {}.
        pool (int): Номер пула.
    """
    # Определение типа вопроса
    if not body:  # Эссе
        qtype = 'essay'
        q = Question(text=text, qtype=qtype, pool=pool)
        db.session.add(q)
        return
    elif body in ['T', 'F']:  # Правда/Ложь
        qtype = 'truefalse'
        q = Question(text=text, qtype=qtype, pool=pool)
        db.session.add(q)
        db.session.flush()
        db.session.add(Option(
            question_id=q.id,
            text='True' if body == 'T' else 'False',
            is_correct=True,
            order_pos=1
        ))
        db.session.add(Option(
            question_id=q.id,
            text='False' if body == 'T' else 'True',
            is_correct=False,
            order_pos=2
        ))
        return
    elif body.startswith('#'):  # Числовой
        qtype = 'numerical'
        num_value = body[1:].strip()
        q = Question(text=text, qtype=qtype, pool=pool)
        db.session.add(q)
        db.session.flush()
        db.session.add(Option(
            question_id=q.id,
            text=num_value,
            is_correct=True,
            order_pos=1
        ))
        return
    elif '->' in body and '=' in body:  # Соответствие
        qtype = 'matching'
        q = Question(text=text, qtype=qtype, pool=pool)
        db.session.add(q)
        db.session.flush()
        pairs = re.findall(r'=(.+?)->(.+?)(?=\s*=\s*|$)', body)
        for order_pos, (key, value) in enumerate(pairs, 1):
            db.session.add(Option(
                question_id=q.id,
                text=value.strip(),
                is_correct=True,
                match_key=key.strip(),
                order_pos=order_pos
            ))
        return
    elif '{' in text:  # Пропущенные слова
        qtype = 'missingword'
    else:
        # Проверка на короткий ответ или множественный выбор
        correct_count = body.count('=')
        if correct_count == 1 and body.count('~') == 0:
            qtype = 'shortanswer'
        else:
            qtype = 'multichoice'

    # Сохранение вопроса
    q = Question(text=text, qtype=qtype, pool=pool)
    db.session.add(q)
    db.session.flush()

    # Обработка вариантов ответа
    if qtype in ('multichoice', 'missingword', 'shortanswer'):
        parts = re.split(r'(?<!\\)([~|=])', body)
        options = []
        i = 0
        while i < len(parts):
            if parts[i] in ['~', '=']:
                prefix = parts[i]
                i += 1
                if i < len(parts):
                    text = parts[i].strip()
                    if text:
                        options.append((text, prefix == '='))
            i += 1
        for order_pos, (opt_text, is_correct) in enumerate(options, 1):
            db.session.add(Option(
                question_id=q.id,
                text=opt_text,
                is_correct=is_correct,
                order_pos=order_pos
            ))



