# Changelog

All notable changes to ProseGuard are documented here. The project follows
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## v1.0.0 – 2026-08-31

Initial stable release.

### Added
- Zero-dependency, offline English writing linter (Python standard library
  only, Python >= 3.9).
- 20 built-in rules across five categories:
  - Spelling: common misspellings (PG100), repeated words (PG101).
  - Grammar: a/an agreement (PG200), modal + "of" (PG201), double
    comparatives (PG202), lowercase "i" (PG203), third-person "don't"
    (PG204), sentence capitalization (PG205).
  - Punctuation: multiple spaces (PG300), space before punctuation (PG301),
    missing space after punctuation (PG302), repeated punctuation (PG303),
    trailing whitespace (PG304).
  - Style: weasel words (PG400), weak intensifiers (PG401), passive voice
    (PG402), wordy phrases (PG403), overlong sentences (PG404), repeated
    sentence openers (PG405).
  - Readability: hard-to-read sentence detection (PG500) plus Flesch Reading
    Ease, Flesch–Kincaid Grade and Gunning Fog statistics.
- Markdown-aware protection: fenced blocks, inline code, URLs, emails and
  HTML comments are never linted.
- Safe deterministic auto-fixer (`--fix`) for all fixable rules.
- Four report formats: stylish terminal text, JSON, Markdown and a
  self-contained HTML report.
- `.proseguard.json` configuration with personal dictionaries, rule toggles
  and thresholds; CLI overrides; directory scanning with excludes.
- Importable library API (`proseguard.Linter`) and a `proseguard` console
  script.
- Full unittest suite with no third-party dependencies.
