"""Style rules (PG400–PG409)."""

from __future__ import annotations

import re

from ..dictionaries import (
    WEASEL_WORDS, WEAK_ADVERBS, BE_FORMS, COMMON_PAST_PARTICIPLES,
    WORDY_PHRASES,
)
from .base import Document, RuleConfig, Finding, Rule

# Pre-compile the wordy-phrase matcher once at import time.
_WORDY_SORTED = sorted(WORDY_PHRASES, key=len, reverse=True)
_WORDY_RE = re.compile(
    r"\b(" + "|".join(re.escape(p) for p in _WORDY_SORTED) + r")\b",
    re.IGNORECASE,
)


def check_weasel_words(doc: Document, cfg: RuleConfig):
    for sentence in doc.sentences:
        for word in sentence.words:
            if word.lower in WEASEL_WORDS:
                yield Finding(
                    rule_id="", severity="", category="",
                    message=f"“{word.text}” is a hedge/weasel word; consider "
                            f"removing it or stating a precise claim.",
                    start=word.start, end=word.end,
                )


def check_weak_adverbs(doc: Document, cfg: RuleConfig):
    for sentence in doc.sentences:
        for word in sentence.words:
            if word.lower in WEAK_ADVERBS:
                yield Finding(
                    rule_id="", severity="", category="",
                    message=f"Weak intensifier “{word.text}”; prefer a strong "
                            f"verb or adjective.",
                    start=word.start, end=word.end,
                )


def check_passive_voice(doc: Document, cfg: RuleConfig):
    for sentence in doc.sentences:
        words = sentence.words
        for i, word in enumerate(words):
            if word.lower not in BE_FORMS:
                continue
            for nxt in words[i + 1:i + 4]:
                if nxt.lower in COMMON_PAST_PARTICIPLES:
                    yield Finding(
                        rule_id="", severity="", category="",
                        message=f"Possible passive voice “{word.text} "
                                f"{nxt.text}”. Prefer an active subject when "
                                f"possible.",
                        start=word.start, end=nxt.end,
                    )
                    break


def check_wordy_phrases(doc: Document, cfg: RuleConfig):
    for m in _WORDY_RE.finditer(doc.text):
        key = m.group(1).lower()
        replacement = WORDY_PHRASES[key]
        matched = m.group(1)
        if matched[:1].isupper():
            replacement = replacement[:1].upper() + replacement[1:]
        yield Finding(
            rule_id="", severity="", category="",
            message=f"Wordy phrase “{matched}”; consider “{replacement}”.",
            start=m.start(), end=m.end(), replacement=replacement,
        )


def check_long_sentences(doc: Document, cfg: RuleConfig):
    for sentence in doc.sentences:
        count = len(sentence.words)
        if count <= cfg.max_sentence_words:
            continue
        severity_note = (
            f"Sentence has {count} words; hard limit is "
            f"{cfg.long_sentence_hard}."
            if count > cfg.long_sentence_hard
            else f"Sentence has {count} words; aim for "
                 f"≤{cfg.max_sentence_words}."
        )
        yield Finding(
            rule_id="", severity="", category="",
            message=severity_note,
            start=sentence.start, end=sentence.end,
        )


def check_repeated_openers(doc: Document, cfg: RuleConfig):
    sentences = [s for s in doc.sentences if s.first_word]
    for i in range(2, len(sentences)):
        trio = sentences[i - 2:i + 1]
        openers = [s.first_word.lower for s in trio]
        if openers[0] == openers[1] == openers[2]:
            target = trio[2].first_word
            yield Finding(
                rule_id="", severity="", category="",
                message=f"Three consecutive sentences start with "
                        f"“{target.text}”; vary sentence openings.",
                start=target.start, end=target.end,
            )


RULES = [
    Rule("PG400", "suggestion", "style", "Weasel / hedge words",
         "Highlights vague qualifiers that weaken claims.",
         check_weasel_words),
    Rule("PG401", "suggestion", "style", "Weak intensifier",
         "Flags filler intensifiers such as “very” and “really”.",
         check_weak_adverbs),
    Rule("PG402", "suggestion", "style", "Possible passive voice",
         "Detects “be + past participle” constructions and suggests active "
         "voice.", check_passive_voice),
    Rule("PG403", "suggestion", "style", "Wordy phrase",
         "Replaces circumlocutions (“in order to”) with concise forms "
         "(“to”).", check_wordy_phrases, autofixable=True),
    Rule("PG404", "suggestion", "style", "Overlong sentence",
         "Warns when a sentence exceeds the configured word budget "
         "(default 25, hard 40).", check_long_sentences),
    Rule("PG405", "suggestion", "style", "Repeated sentence opener",
         "Warns when three sentences in a row begin with the same word.",
         check_repeated_openers),
]
