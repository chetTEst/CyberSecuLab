# -*- coding: utf-8 -*-
"""
Минифицирует:
  • static/css/*.css      → static/css/*.min.css
  • static/js/*.js        → static/js/*.min.js   (+ срезает console.*)
  • templates/**/*.j2     → build/templates/*.html (готовый HTML)
Запускать из корня проекта:  python tools/minify_assets.py
"""
from pathlib import Path
import re

from rcssmin import cssmin
from rjsmin  import jsmin
from htmlmin import minify
import uuid

# ------------------  общие директории  ------------------
CSS_SRC  = Path("../flask_app/app/static/css")
JS_SRC   = Path("../flask_app/app/static/js")
TPL_SRC  = Path("../flask_app/app/templates")
TPL_OUT  = Path("../flask_app/app/templates")

TPL_OUT.mkdir(parents=True, exist_ok=True)

SCRIPT_RE = re.compile(
    r"(<script[^>]*>)(.*?)(</script>)",
    re.IGNORECASE | re.DOTALL)

JINJA_RE = re.compile(r"({[{%].*?[}%]})", re.DOTALL)

# ------------------  JS: режем console.*  ------------------
_CONSOLE_RE = re.compile(
    r'^\s*console\.(?:log|debug|info|warn|error)\s*\([^)]*\);\s*$',
    re.MULTILINE
)

def strip_console(js_code: str) -> str:
    return _CONSOLE_RE.sub("", js_code)

# ------------------  CSS / JS  ------------------
def process_static():
    for css in CSS_SRC.glob("*.css"):
        tgt = css.with_suffix(".css")
        tgt.write_text(cssmin(css.read_text(encoding="utf-8")), encoding="utf-8")

    for js in JS_SRC.glob("*.js"):
        tgt = js.with_suffix(".js")
        raw = js.read_text(encoding="utf-8")
        tgt.write_text(jsmin(strip_console(raw)), encoding="utf-8")

# ------------------  Jinja2 → min-HTML  ------------------
def _tokenize_jinja(code: str):
    mapping = {}
    def _sub(m):
        token = f"__JINJA_{uuid.uuid4().hex}__"
        mapping[token] = m.group(1)
        return token
    tokenized = JINJA_RE.sub(_sub, code)
    return tokenized, mapping

def _untokenize(code: str, mapping: dict):
    for token, jinja in mapping.items():
        code = code.replace(token, jinja)
    return code

def minify_inline_js(html: str) -> str:
    def _replacer(m):
        open_tag, code, close_tag = m.groups()

        # 1) прячем Jinja-директивы под уникальные токены
        tokenized, mapping = _tokenize_jinja(code)

        # 2) минифицируем JS
        minified = jsmin(tokenized)

        # 3) восстанавливаем Jinja
        minified = _untokenize(minified, mapping)

        return f"{open_tag}{minified}{close_tag}"

    return SCRIPT_RE.sub(_replacer, html)

# ---------- main ----------
def process_templates():
    for tpl in TPL_SRC.rglob("*.html"):
        raw_html = tpl.read_text("utf-8")

        # 1. убираем HTML-комментарии / пробелы
        html = minify(raw_html,
                      remove_comments=True,
                      remove_empty_space=True)

        # 2. минифицируем inline-JS
        html = minify_inline_js(html)

        target = TPL_OUT / tpl.relative_to(TPL_SRC)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(html, "utf-8")
        print("✔︎", target)

if __name__ == "__main__":
    process_static()
    process_templates()
    print("✅ Минификация завершена")
