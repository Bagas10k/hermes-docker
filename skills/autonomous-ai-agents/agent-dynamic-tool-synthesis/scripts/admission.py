"""Bounded integer RPN DSL. Trusted host library, NOT a code sandbox."""
from dataclasses import dataclass
import hashlib
import json
import re

MAX_BYTES = 4096
MAX_TOKENS = 64
MAX_VALUE = 10**12
NAME = re.compile(r'[a-z][a-z0-9_]{0,31}\Z')
OPS = {'+', '-', '*', '//', 'min', 'max'}

class Rejected(ValueError):
    """Candidate, arguments or capability rejected."""

def _object(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise Rejected('duplicate key')
        out[key] = value
    return out

def _json(raw):
    if type(raw) is not bytes or len(raw) > MAX_BYTES:
        raise Rejected('bytes required; size limit')
    # Bound nesting before the stdlib recursive parser sees the input.
    depth = 0
    quoted = escaped = False
    for b in raw:
        if quoted:
            if escaped:
                escaped = False
            elif b == 92:
                escaped = True
            elif b == 34:
                quoted = False
        elif b == 34:
            quoted = True
        elif b in (91, 123):
            depth += 1
            if depth > 4:
                raise Rejected('JSON nesting limit')
        elif b in (93, 125):
            depth -= 1
    try:
        obj = json.loads(raw, object_pairs_hook=_object,
                         parse_constant=lambda _: (_ for _ in ()).throw(Rejected('nonfinite')))
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise Rejected('invalid JSON') from exc
    if type(obj) is not dict:
        raise Rejected('object required')
    return obj

def _integer(value):
    if type(value) is not int or abs(value) > MAX_VALUE:
        raise Rejected('bounded integer required')
    return value

@dataclass(frozen=True)
class Tool:
    name: str
    inputs: tuple
    code: tuple
    digest: str

def compile_tool(raw):
    obj = _json(raw)
    if set(obj) != {'name', 'inputs', 'program'}:
        raise Rejected('manifest keys')
    name, inputs, program = obj['name'], obj['inputs'], obj['program']
    if type(name) is not str or not NAME.fullmatch(name):
        raise Rejected('name')
    if type(inputs) is not list or not 1 <= len(inputs) <= 8:
        raise Rejected('inputs')
    if any(type(x) is not str or not NAME.fullmatch(x) for x in inputs):
        raise Rejected('input name')
    if len(set(inputs)) != len(inputs) or type(program) is not str:
        raise Rejected('duplicate input or program type')
    tokens = program.split()
    if not 1 <= len(tokens) <= MAX_TOKENS:
        raise Rejected('instruction budget')
    code, height = [], 0
    for token in tokens:
        if token.startswith('$') and token[1:] in inputs:
            code.append(('arg', token[1:]))
            height += 1
        elif re.fullmatch(r'-?(0|[1-9][0-9]{0,12})', token):
            code.append(('int', _integer(int(token))))
            height += 1
        elif token in OPS:
            if height < 2:
                raise Rejected('stack underflow')
            code.append(('op', token))
            height -= 1
        else:
            raise Rejected('unsupported token')
        if height > 16:
            raise Rejected('stack budget')
    if height != 1:
        raise Rejected('one result required')
    canonical = json.dumps({'policy': 'rpn-int-v1', 'name': name,
                            'inputs': inputs, 'code': code}, sort_keys=True, separators=(',', ':')).encode()
    return Tool(name, tuple(inputs), tuple(code), hashlib.sha256(canonical).hexdigest())

def evaluate(tool, raw_args):
    # Tool objects are trusted compiler output, not a deserialization API.
    args = _json(raw_args)
    if set(args) != set(tool.inputs):
        raise Rejected('argument keys')
    for value in args.values():
        _integer(value)
    stack = []
    for kind, value in tool.code:
        if kind == 'arg':
            stack.append(args[value])
        elif kind == 'int':
            stack.append(value)
        else:
            right, left = stack.pop(), stack.pop()
            if value == '+': result = left + right
            elif value == '-': result = left - right
            elif value == '*': result = left * right
            elif value == '//':
                if right == 0: raise Rejected('division by zero')
                result = left // right
            elif value == 'min': result = min(left, right)
            elif value == 'max': result = max(left, right)
            else: raise Rejected('invalid trusted tool')
            stack.append(_integer(result))
    return stack[0]


import math
import secrets
import threading
import time

class Registry:
    """Process-local capabilities. Caller/clock/host are trusted; bytes are not."""
    def __init__(self, *, clock=time.monotonic):
        self._clock = clock
        self._entries = {}
        self._lock = threading.RLock()
        self._closed = False

    def _now(self):
        now = self._clock()
        if type(now) not in (int, float) or not math.isfinite(now):
            raise Rejected('invalid trusted clock')
        return now

    def _purge(self, now):
        for h in list(self._entries):
            if now >= self._entries[h][2]:
                del self._entries[h]

    @staticmethod
    def _owner(owner):
        if type(owner) is not str or not NAME.fullmatch(owner):
            raise Rejected('owner identifier')

    def admit(self, raw, *, owner, ttl, calls):
        self._owner(owner)
        if type(ttl) not in (int, float) or not math.isfinite(ttl) or not 0 < ttl <= 300:
            raise Rejected('TTL policy')
        if type(calls) is not int or not 1 <= calls <= 100:
            raise Rejected('call policy')
        tool = compile_tool(raw)
        with self._lock:
            if self._closed:
                raise Rejected('closed')
            now = self._now()
            self._purge(now)
            if len(self._entries) >= 32:
                raise Rejected('registry full')
            handle = secrets.token_urlsafe(32)
            while handle in self._entries:
                handle = secrets.token_urlsafe(32)
            self._entries[handle] = [tool, owner, now + ttl, calls]
            return handle, tool.digest

    def _entry(self, handle, owner):
        self._owner(owner)
        if type(handle) is not str or len(handle) > 64:
            raise Rejected('invalid handle')
        self._purge(self._now())
        entry = self._entries.get(handle)
        if self._closed or entry is None or entry[1] != owner:
            raise Rejected('capability unavailable')
        return entry

    def call(self, handle, *, owner, arguments):
        with self._lock:
            entry = self._entry(handle, owner)
            entry[3] -= 1
            if entry[3] == 0:
                del self._entries[handle]
            # Count failed authorized attempts too; no quota refund.
            return evaluate(entry[0], arguments)

    def revoke(self, handle, *, owner):
        with self._lock:
            self._entry(handle, owner)
            del self._entries[handle]

    def size(self):
        with self._lock:
            self._purge(self._now())
            return len(self._entries)

    def close(self):
        with self._lock:
            self._entries.clear()
            self._closed = True
