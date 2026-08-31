"""Text tokenization and Markdown-aware protection.

The tokenizer never *removes* protected ranges: it replaces every protected
character with a space (newlines are preserved) so that offsets in the
masked text are identical to offsets in the raw text. Rules therefore report
line/column positions that map straight back to the user's document, even
when code spans or fenced blocks are present.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_WORD_RE = re.compile(r"[A-Za-z][A-Za-z'’\-]*")
_SENTENCE_END = ".!?"
# Abbreviations after which a period does NOT terminate a sentence.
_ABBREVIATIONS = frozenset({
    "mr", "mrs", "ms", "dr", "prof", "sr", "jr", "st", "vs", "etc", "e.g",
    "i.e", "fig", "no", "vol", "pp", "inc", "ltd", "co", "corp", "approx",
    "a.k.a", "u.s", "ph.d", "b.c", "a.d",
})


@dataclass
class Word:
    text: str
    start: int
    end: int

    @property
    def lower(self) -> str:
        return self.text.lower().replace("’", "'")


@dataclass
class Sentence:
    text: str
    start: int
    end: int
    words: list[Word]

    @property
    def first_word(self) -> Word | None:
        return self.words[0] if self.words else None


def mask_protected(text: str) -> str:
    """Mask fenced code, inline code, URLs and HTML comments with spaces.

    Newlines inside protected ranges are preserved so line numbers remain
    stable. Non-protected characters stay untouched.
    """
    chars = list(text)
    n = len(chars)

    def blank(a: int, b: int) -> None:
        for i in range(a, min(b, n)):
            if chars[i] != "\n":
                chars[i] = " "

    # 1. Fenced code blocks: ``` or ~~~ (optionally with an info string).
    i = 0
    while i < n:
        if (text.startswith("```", i) or text.startswith("~~~", i)):
            fence = text[i:i + 3]
            line_end = text.find("\n", i)
            if line_end == -1:
                blank(i, n)
                break
            close = text.find(fence, line_end + 1)
            if close == -1:
                blank(i, n)
                break
            stop = text.find("\n", close)
            blank(i, n if stop == -1 else stop)
            i = n if stop == -1 else stop
        else:
            i += 1

    masked = "".join(chars)

    # 2. Inline code spans (`...` or ``...``).
    def blank_inline(pattern: str, src: str) -> str:
        out = list(src)
        for m in re.finditer(pattern, src, re.S):
            for j in range(m.start(), m.end()):
                if out[j] != "\n":
                    out[j] = " "
        return "".join(out)

    masked = blank_inline(r"``.+?``", masked)
    masked = blank_inline(r"`[^`\n]+?`", masked)

    # 3. URLs and email addresses.
    masked = blank_inline(r"https?://[^\s)>\]]+", masked)
    masked = blank_inline(r"www\.[^\s)>\]]+", masked)
    masked = blank_inline(r"[\w.+-]+@[\w-]+\.[\w.-]+", masked)

    # 4. HTML comments.
    masked = blank_inline(r"<!--.*?-->", masked)

    # 5. Markdown image/link destinations: [text](DEST) – mask the URL part.
    def blank_link_dest(src: str) -> str:
        out = list(src)
        for m in re.finditer(r"\]\(([^()]*)\)", src):
            a, b = m.start(1), m.end(1)
            for j in range(a, b):
                if out[j] != "\n":
                    out[j] = " "
        return "".join(out)

    masked = blank_link_dest(masked)
    return masked


def word_spans(text: str, start: int = 0, end: int | None = None) -> list[Word]:
    if end is None:
        end = len(text)
    segment = text[start:end]
    words: list[Word] = []
    for m in _WORD_RE.finditer(segment):
        token = m.group(0).strip("'-’")
        if not token:
            continue
        offset_a = start + m.start() + (m.group(0).find(token))
        words.append(Word(token, offset_a, offset_a + len(token)))
    return words


def _is_abbreviation_before(text: str, dot_idx: int) -> bool:
    # Walk backwards collecting the current token.
    j = dot_idx - 1
    chars: list[str] = []
    while j >= 0 and (text[j].isalpha() or text[j] == "."):
        chars.append(text[j].lower())
        j -= 1
    token = "".join(reversed(chars)).strip(".")
    return token in _ABBREVIATIONS


def sentence_spans(text: str) -> list[Sentence]:
    """Split masked text into sentences while keeping absolute offsets.

    A sentence ends at (a) sentence punctuation (. ! ?) followed by
    whitespace and a new sentence, or (b) a paragraph break (a blank line).
    Common abbreviations do not terminate sentences.
    """
    sentences: list[Sentence] = []
    n = len(text)
    start = 0

    def emit(end_exclusive: int, next_start: int) -> None:
        nonlocal start
        segment = text[start:end_exclusive]
        stripped = segment.strip()
        if stripped:
            lead = len(segment) - len(segment.lstrip())
            trail = len(segment) - len(segment.rstrip())
            s_start = start + lead
            s_end = start + len(segment) - trail
            words = word_spans(text, s_start, s_end)
            sentences.append(Sentence(text[s_start:s_end], s_start, s_end, words))
        start = next_start

    i = 0
    while i < n:
        ch = text[i]
        if ch in _SENTENCE_END:
            j = i
            while j < n and text[j] in _SENTENCE_END:
                j += 1
            k = j
            while k < n and text[k] in "\"')”’]":
                k += 1
            m = k
            while m < n and text[m] in " \t\r\n":
                m += 1
            boundary = m >= n or (
                m < n and (text[m].isupper() or text[m] in "\"'“")
            )
            if boundary and not _is_abbreviation_before(text, i):
                emit(k, m if m < n else n)
                i = m if m < n else n
                continue
            i = j
        elif ch == "\n":
            para = re.match(r"\n[ \t]*(?:\r?\n)", text[i:])
            if para:
                emit(i, i + para.end())
                i += para.end()
                continue
            i += 1
        else:
            i += 1
    if start < n:
        emit(n, n)
    return sentences


def line_col(text: str, offset: int) -> tuple[int, int]:
    """Return 1-based (line, column) for an absolute offset."""
    offset = max(0, min(offset, len(text)))
    line = text.count("\n", 0, offset) + 1
    last_nl = text.rfind("\n", 0, offset)
    col = offset - last_nl if last_nl >= 0 else offset + 1
    return line, col
