import re

class JSParseError(Exception):
    pass


def _skip_ws(s, i):
    n = len(s)
    while i < n:
        c = s[i]
        if c in ' \t\r\n':
            i += 1
        elif c == '/' and i + 1 < n and s[i + 1] == '/':
            j = s.find('\n', i)
            i = n if j == -1 else j + 1
        elif c == '/' and i + 1 < n and s[i + 1] == '*':
            j = s.find('*/', i + 2)
            i = n if j == -1 else j + 2
        else:
            break
    return i


_ESC = {'n': '\n', 't': '\t', 'r': '\r', '"': '"', "'": "'", '\\': '\\',
        '/': '/', 'b': '\b', 'f': '\f', '0': '\0'}


def _parse_string(s, i):
    quote = s[i]
    i += 1
    out = []
    n = len(s)
    while i < n:
        c = s[i]
        if c == '\\':
            nc = s[i + 1]
            if nc == 'u':
                code = s[i + 2:i + 6]
                out.append(chr(int(code, 16)))
                i += 6
                continue
            if nc == '\n':
                i += 2
                continue
            out.append(_ESC.get(nc, nc))
            i += 2
            continue
        if c == quote:
            i += 1
            break
        out.append(c)
        i += 1
    return ''.join(out), i


_NUM_RE = re.compile(r'-?\d+(\.\d+)?([eE][-+]?\d+)?')
_IDENT_RE = re.compile(r'[A-Za-z_$][A-Za-z0-9_$]*')


def _parse_value(s, i):
    i = _skip_ws(s, i)
    c = s[i]
    if c in '"\'':
        return _parse_string(s, i)
    if c == '{':
        return _parse_object(s, i)
    if c == '[':
        return _parse_array(s, i)
    m = _NUM_RE.match(s, i)
    if m:
        txt = m.group(0)
        val = float(txt) if ('.' in txt or 'e' in txt or 'E' in txt) else int(txt)
        return val, m.end()
    m2 = _IDENT_RE.match(s, i)
    if m2:
        word = m2.group(0)
        j = m2.end()
        if word == 'true':
            return True, j
        if word == 'false':
            return False, j
        if word in ('null', 'undefined'):
            return None, j
        return word, j
    raise JSParseError(f'cannot parse value at {i}: ...{s[i:i + 40]!r}')


def _parse_key(s, i):
    i = _skip_ws(s, i)
    if s[i] in '"\'':
        return _parse_string(s, i)
    m = _IDENT_RE.match(s, i)
    if m:
        return m.group(0), m.end()
    m2 = _NUM_RE.match(s, i)
    if m2:
        return m2.group(0), m2.end()
    raise JSParseError(f'cannot parse key at {i}: ...{s[i:i + 40]!r}')


def _parse_object(s, i):
    assert s[i] == '{'
    i += 1
    obj = {}
    while True:
        i = _skip_ws(s, i)
        if s[i] == '}':
            return obj, i + 1
        if s[i] == ',':
            i += 1
            continue
        key, i = _parse_key(s, i)
        i = _skip_ws(s, i)
        if s[i] != ':':
            raise JSParseError(f'expected : at {i}: ...{s[i:i + 40]!r}')
        i += 1
        val, i = _parse_value(s, i)
        obj[key] = val
        i = _skip_ws(s, i)
        if s[i] == ',':
            i += 1
        elif s[i] == '}':
            return obj, i + 1


def _parse_array(s, i):
    assert s[i] == '['
    i += 1
    arr = []
    while True:
        i = _skip_ws(s, i)
        if s[i] == ']':
            return arr, i + 1
        if s[i] == ',':
            i += 1
            continue
        val, i = _parse_value(s, i)
        arr.append(val)
        i = _skip_ws(s, i)
        if s[i] == ',':
            i += 1
        elif s[i] == ']':
            return arr, i + 1


def find_js_object_assignment(html, varname):
    """Find `varname = { ... }` (const/let/var optional) and parse the object
    literal with a small JS-literal parser (handles unquoted keys, single or
    double quoted strings, nested objects/arrays, numbers, // comments)."""
    m = re.search(r'\b' + re.escape(varname) + r'\s*=\s*\{', html)
    if not m:
        return None
    i = m.end() - 1
    try:
        obj, _ = _parse_object(html, i)
    except (JSParseError, IndexError):
        return None
    return obj
