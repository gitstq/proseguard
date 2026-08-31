"""ProseGuard – a zero-dependency, offline English writing linter.

Public API
----------
>>> from proseguard import Linter, load_config
>>> linter = Linter()
>>> result = linter.lint_text("This is definately wrong.")
>>> [(f.rule_id, f.replacement) for f in result.findings]
[('PG100', 'definitely')]
"""

from __future__ import annotations

from .config import Config, load_config
from .engine import Linter, LintResult
from .rules.base import Finding
from .rules.readability import compute_stats, count_syllables
from .autofix import autofix_text, apply_fixes, plan_fixes

__version__ = "1.0.0"

__all__ = [
    "Linter", "LintResult", "Finding", "Config", "load_config",
    "compute_stats", "count_syllables",
    "autofix_text", "apply_fixes", "plan_fixes", "__version__",
]
