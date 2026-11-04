"""Format generated JSON-compatible data as reviewable JS and read it back.

Generated payloads used to be written as one line of tens of thousands of characters, which
Git hosts refuse to diff. This writes the same value over many short lines in the style of
tools/build_animated_login_background.py: hex strings become 64-character chunks joined at load
time (so the evaluated value is still one string), integer lists wrap eight per line, and
records that fit in WIDTH columns stay on one line.
"""
import json
import re

WIDTH = 100
TAB = 4
CHUNK = 64
HEX_KEYS = ('hex',)


def _inline(value):
    return json.dumps(value, ensure_ascii=False)


def js_data(value, level=0, key=None):
    pad = '\t' * level
    inner = '\t' * (level + 1)
    if isinstance(value, str) and key in HEX_KEYS and len(value) > CHUNK:
        rows = ',\n'.join(inner + json.dumps(value[i:i + CHUNK]) for i in range(0, len(value), CHUNK))
        return '[\n' + rows + '\n' + pad + '].join("")'
    if isinstance(value, dict):
        if not value:
            return '{}'
        flat = _inline(value)
        if level * TAB + len(flat) <= WIDTH and not any(
                isinstance(v, str) and k in HEX_KEYS and len(v) > CHUNK for k, v in value.items()):
            return flat
        return '{\n' + ',\n'.join(inner + json.dumps(k, ensure_ascii=False) + ': ' + js_data(v, level + 1, k)
                                  for k, v in value.items()) + '\n' + pad + '}'
    if isinstance(value, list):
        if not value:
            return '[]'
        flat = _inline(value)
        if level * TAB + len(flat) <= WIDTH:
            return flat
        if all(isinstance(v, int) and not isinstance(v, bool) for v in value):
            return '[\n' + ',\n'.join(inner + ', '.join(map(str, value[i:i + 8]))
                                      for i in range(0, len(value), 8)) + '\n' + pad + ']'
        return '[\n' + ',\n'.join(inner + js_data(v, level + 1) for v in value) + '\n' + pad + ']'
    return _inline(value)


def js_statement(name, value):
    """`NAME = <data>;` as it appears in a patch file (LF newlines)."""
    return name + ' = ' + js_data(value) + ';'


_JOIN = re.compile(r'\[\s*((?:"[0-9a-fA-F]*"\s*,?\s*)+)\]\.join\(""\)')


def parse_js_data(text):
    """Inverse of js_data for text that is JSON apart from the hex `.join("")` arrays."""
    flat = _JOIN.sub(lambda m: json.dumps(''.join(re.findall(r'"([0-9a-fA-F]*)"', m.group(1)))), text)
    return json.loads(flat)


def load_assignment(source, name):
    """Value assigned to `name` in `source`, whether one line or many, JSON or the wrapped form."""
    m = re.search(r'^' + re.escape(name) + r'\s*=\s*', source, re.M)
    if not m:
        raise KeyError(name)
    start = m.end()
    end = source.index(';\n', start) if ';\n' in source[start:] else len(source.rstrip().rstrip(';'))
    return parse_js_data(source[start:end])
