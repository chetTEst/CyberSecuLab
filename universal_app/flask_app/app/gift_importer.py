from __future__ import annotations

import re
from pathlib import Path
from typing import List, Optional
from argon2 import PasswordHasher

from .models import db, Question, Option


__all__ = ["GiftImporter", "import_gift"]


class GiftImporter:
    """Parse a GIFT file and persist all recognised questions.

    Parameters
    ----------
    file_path : str | Path
        Absolute or relative path to the GIFT file.

    Notes
    -----
    After calling :py:meth:`parse`, the attribute :pyattr:`pools` contains the
    *pool* (``int``) value for every parsed question in order of appearance.
    """

    # ------------------------------------------------------------------
    # Pre‑compiled regexes (class‑level, shared between instances)
    # ------------------------------------------------------------------
    _QUESTION_NUMBER_RE = re.compile(r"//\s*QuestionNumber:\s*(\d+)", re.IGNORECASE)
    _QUESTION_RE = re.compile(r"(?P<text>.*)\{(?P<body>.*)\}", re.DOTALL)
    _DESCRIPTION_RE = re.compile(r"^(?!//)(?P<text>.+)$", re.DOTALL)

    # Инициализируем PasswordHasher с заданными параметрами
    _ph = PasswordHasher(time_cost=3, memory_cost=64*1024, parallelism=3, hash_len=64, salt_len=64)


    def __init__(self, file_path: str | Path) -> None:
        self.file_path: Path = Path(file_path)
        self.pools: List[int] = []  # хранит pool каждого вопроса в порядке появления

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------
    def get_pools(self) -> List[int]:
        """Return the list of *pools* captured during :py:meth:`parse`."""
        return self.pools

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------
    def parse(self) -> int:
        """Read *file_path*, insert questions into the DB and commit.

        Returns
        -------
        int
            Number of questions/descriptions successfully inserted.
        """
        if not self.file_path.exists():
            raise FileNotFoundError(self.file_path)

        with self.file_path.open("r", encoding="utf-8") as fp:
            content = fp.read()

        inserted = 0
        for block in content.split("\n\n"):
            block = block.strip()
            if not block:
                # Skip consecutive empty blocks
                continue

            lines = block.splitlines()
            pool = 1  # default pool size

            # Optional header line that may specify pool/variants
            if lines and lines[0].startswith("//"):
                m = self._QUESTION_NUMBER_RE.search(lines[0])
                if m:
                    pool = int(m.group(1))
                lines = lines[1:]  # remove header from further processing

            self.pools.append(pool)

            # Re‑join the remaining lines for easier processing
            block_text = "\n".join(lines).strip()

            # ------------------------------------------------------------------
            # Description – a text block without braces "{}"
            # ------------------------------------------------------------------
            desc_match = self._DESCRIPTION_RE.match(block_text)
            if desc_match and "{" not in block_text:
                db.session.add(
                    Question(text=desc_match.group("text").strip(), qtype="description", pool=pool)
                )
                inserted += 1
                continue

            # ------------------------------------------------------------------
            # Question with "{}" delimiters
            # ------------------------------------------------------------------
            qmatch = self._QUESTION_RE.search(block_text)
            if qmatch is None:
                # Unsupported / malformed block; skip
                continue

            qtext = qmatch.group("text").strip()
            body = qmatch.group("body").strip()

            if self._persist_question(qtext, body, pool):
                inserted += 1

        # One commit at the very end of the import – more efficient and ensures
        # atomicity within the app context where this importer is used.
        db.session.commit()
        return inserted

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _persist_question(self, text: str, body: str, pool: int) -> bool:
        """Insert a single question + options. Return *True* if inserted."""
        # 1. Determine question type --------------------------------------------
        if not body:  # Essay question
            qtype = "essay"
            q = Question(text=text, qtype=qtype, pool=pool)
            db.session.add(q)
            return True

        if body in {"T", "F"}:  # True / False
            qtype = "truefalse"
            q = Question(text=text, qtype=qtype, pool=pool)
            db.session.add(q)
            db.session.flush()  # obtain q.id
            options_data = [("Правда", body == "T"), ("Ложь", body == "F")]
            options_to_add = []
            order_pos = 1
            for  opt_text, is_correct in options_data:
                if is_correct:
                    # Хешируем текст правильного ответа
                    hashed_text = self._ph.hash(opt_text)
                    options_to_add.append(Option(question_id=q.id, text=hashed_text, is_correct=is_correct, order_pos=order_pos, plain_values=opt_text))
                    order_pos += 1
                    options_to_add.append(Option(question_id=q.id, text=opt_text, is_correct=not(is_correct), order_pos=order_pos))
                else:
                    # Неправильные ответы сохраняем как есть
                    options_to_add.append(Option(question_id=q.id, text=opt_text, is_correct=is_correct, order_pos=order_pos))
                order_pos += 1
            db.session.add_all(options_to_add)
            return True

        if body.startswith("#"):  # Numerical question
            qtype = "numerical"
            num_value = body[1:].strip()
            q = Question(text=text, qtype=qtype, pool=pool)
            db.session.add(q)
            db.session.flush()
            opt_text = "{:.2f}".format(float(num_value))
            hashed_value = self._ph.hash(opt_text) # Хешируем значение числового ответа
            db.session.add(Option(question_id=q.id, text=hashed_value, is_correct=True, order_pos=1, plain_values=opt_text))
            return True

        if "->" in body and "=" in body:  # Matching question
            qtype = "matching"
            q = Question(text=text, qtype=qtype, pool=pool)
            db.session.add(q)
            db.session.flush()
            pairs = re.findall(r"=(.+?)->(.+?)(?=\s*=\s*|$)", body)
            options_to_add = []
            order_pos = 1
            for left, right in pairs:
                # Хешируем правую часть (текст правильного соответствия)
                hashed_right = self._ph.hash(right.strip())
                hashed_left = self._ph.hash(left.strip())
                options_to_add.append(
                    Option(
                        question_id=q.id,
                        text=hashed_left, # Храним хеш в поле text
                        is_correct=True,
                        match_key=hashed_right,  # Сохраняем хеш в поле match_key
                        order_pos=order_pos,
                        plain_values=right.strip()
                    )
                )
                order_pos += 1
                options_to_add.append(
                    Option(
                        question_id=q.id,
                        text=left,  # Храним хеш в поле text
                        is_correct=False,
                        match_key=right,  # Сохраняем хеш в поле match_key
                        order_pos=order_pos,
                    )
                )
                order_pos += 1
            db.session.add_all(options_to_add)
            return True

        # If braces appear inside *question text*, treat as fill‑in‑the‑blank
        if "{" in text:
            qtype = "missingword"
        else:
            # Decide between shortanswer vs multichoice
            correct_cnt = body.count("=")
            if correct_cnt == 1 and body.count("~") == 0:
                qtype = "shortanswer"
            else:
                qtype = "multichoice"

        # Persist question & answers -------------------------------------------\
        q = Question(text=text, qtype=qtype, pool=pool)
        db.session.add(q)
        db.session.flush()

        if qtype in {"multichoice", "missingword", "shortanswer"}:
            parts = re.split(r"(?<!\\)([~=])", body)
            i, opts = 0, []
            while i < len(parts):
                if parts[i] in {"~", "="}:
                    is_correct = parts[i] == "="
                    i += 1
                    if i < len(parts):
                        opt_text = parts[i].strip()
                        if opt_text:
                            # Сохраняем пары (текст, правильность) сначала
                            opts.append((opt_text, is_correct))
                i += 1

            options_to_add = []
            order_pos = 1
            for opt_text, is_correct in opts:
                if is_correct:
                    # Хешируем текст правильного варианта
                    hashed_opt_text = self._ph.hash(opt_text.strip().lower())
                    options_to_add.append(
                        Option(question_id=q.id, text=hashed_opt_text, is_correct=is_correct, order_pos=order_pos, plain_values=opt_text)
                    )
                    order_pos += 1
                    options_to_add.append(
                        Option(question_id=q.id, text=opt_text, is_correct=not(is_correct), order_pos=order_pos)
                    )
                else:
                     # Неправильные варианты сохраняем как есть
                    options_to_add.append(
                        Option(question_id=q.id, text=opt_text, is_correct=is_correct, order_pos=order_pos)
                    )
                order_pos += 1
            db.session.add_all(options_to_add)

        # Возвращаем True, если вопрос успешно обработан
        return True


# ---------------------------------------------------------------------------\
# Backward‑compatibility façade
# ---------------------------------------------------------------------------\

def import_gift(file_path: str | Path, *, return_importer: bool = False) -> Optional[tuple | int]:
    """Simple wrapper kept for existing code paths.

    Examples
    --------
    >>> import_gift("questions.gift")              # returns None
    >>> imp = import_gift("questions.gift", return_importer=True)
    >>> imp.get_pools()
    [1, 3, 2, ...]\
    """
    importer = GiftImporter(file_path)
    numer_of_questions = importer.parse()
    return (importer, numer_of_questions) if return_importer else numer_of_questions