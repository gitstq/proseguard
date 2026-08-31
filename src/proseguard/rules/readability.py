"""Readability metrics and rule (PG500)."""

from __future__ import annotations

from dataclasses import dataclass

from .base import Document, RuleConfig, Finding, Rule


def count_syllables(word: str) -> int:
    """Estimate spoken syllable count using the classic vowel-group heuristic."""
    w = word.lower().strip("'\"-.!?,:;()")
    if len(w) <= 3:
        return 1
    groups = 0
    prev_vowel = False
    for ch in w:
        is_vowel = ch in "aeiouy"
        if is_vowel and not prev_vowel:
            groups += 1
        prev_vowel = is_vowel
    # Silent final “e” (but keep “-ee”, “-ie”, “-ye”; the consonant+“-le”
    # case first loses its “e” here and wins a syllable back below).
    if w.endswith("e") and not w.endswith(("ee", "ie", "ye")) and groups > 1:
        groups -= 1
    # Consonant + “-le” adds a syllable (table, candle, puzzle).
    if w.endswith("le") and len(w) > 2 and w[-3] not in "aeiouy":
        groups += 1
    return max(1, groups)


@dataclass
class ReadabilityStats:
    sentences: int
    words: int
    complex_words: int
    syllables: int
    avg_sentence_length: float
    flesch_reading_ease: float
    flesch_kincaid_grade: float
    gunning_fog: float

    def to_dict(self) -> dict:
        return {
            "sentences": self.sentences,
            "words": self.words,
            "complex_words": self.complex_words,
            "syllables": self.syllables,
            "avg_sentence_length": round(self.avg_sentence_length, 2),
            "flesch_reading_ease": round(self.flesch_reading_ease, 2),
            "flesch_kincaid_grade": round(self.flesch_kincaid_grade, 2),
            "gunning_fog": round(self.gunning_fog, 2),
        }


def compute_stats(doc: Document) -> ReadabilityStats:
    n_sent = max(1, len(doc.sentences))
    words = [w for s in doc.sentences for w in s.words]
    n_words = max(1, len(words))
    syllables = 0
    complex_words = 0
    for w in words:
        syl = count_syllables(w.text)
        syllables += syl
        if syl >= 3 and not w.text.isupper():
            complex_words += 1
    asl = len(words) / n_sent
    phw = syllables / n_words * 100
    # Flesch Reading Ease
    fre = 206.835 - 1.015 * asl - 84.6 * (syllables / n_words)
    # Flesch–Kincaid Grade Level
    fk = 0.39 * asl + 11.8 * (syllables / n_words) - 15.59
    # Gunning Fog Index
    fog = 0.4 * (asl + 100 * complex_words / n_words)
    return ReadabilityStats(
        sentences=len(doc.sentences), words=len(words),
        complex_words=complex_words, syllables=syllables,
        avg_sentence_length=asl, flesch_reading_ease=fre,
        flesch_kincaid_grade=fk, gunning_fog=fog,
    )


def check_hard_sentence(doc: Document, cfg: RuleConfig):
    for sentence in doc.sentences:
        words = sentence.words
        if len(words) < 12:
            continue
        syllables = sum(count_syllables(w.text) for w in words)
        grade = (0.39 * len(words)
                 + 11.8 * (syllables / len(words)) - 15.59)
        if grade > cfg.readability_grade:
            yield Finding(
                rule_id="", severity="", category="",
                message=f"Dense sentence (estimated grade {grade:.1f}, "
                        f"{len(words)} words). Split or simplify it.",
                start=sentence.start, end=sentence.end,
            )


RULES = [
    Rule("PG500", "suggestion", "readability", "Hard-to-read sentence",
         "Estimates per-sentence reading grade (Flesch–Kincaid style) and "
         "flags sentences above the configured grade threshold.",
         check_hard_sentence),
]
