"""Command line interface for ProseGuard."""

from __future__ import annotations

import argparse
import fnmatch
import os
import sys
from pathlib import Path

from . import __version__
from .config import Config, load_config
from .engine import Linter, LintResult
from .autofix import autofix_text
from . import report as report_mod


def _split_csv(values: list[str] | None) -> set[str]:
    out: set[str] = set()
    for value in values or []:
        out.update(part.strip().upper() for part in value.split(",") if part.strip())
    return out


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="proseguard",
        description="Zero-dependency, offline English writing linter "
                    "(spelling · grammar · punctuation · style · readability).",
        epilog="Exit codes: 0 clean, 1 findings reported, 2 usage/runtime error.",
    )
    parser.add_argument("paths", nargs="*", default=["."],
                        help="Files or directories to lint (default: current "
                             "directory; use '-' to read standard input).")
    parser.add_argument("-c", "--config", help="Path to a .proseguard.json file")
    parser.add_argument("-f", "--format", dest="fmt",
                        choices=["text", "json", "md", "html"], default="text",
                        help="Output format (default: text)")
    parser.add_argument("-o", "--output", help="Write the report to a file")
    parser.add_argument("--fix", action="store_true",
                        help="Apply safe automatic fixes in place, then re-lint")
    parser.add_argument("--stats", action="store_true",
                        help="Include readability statistics (text format)")
    parser.add_argument("--enable", action="append",
                        help="Enable only these rule ids (comma-separated, repeatable)")
    parser.add_argument("--disable", action="append",
                        help="Disable these rule ids (comma-separated, repeatable)")
    parser.add_argument("--ext",
                        help="Comma-separated extensions when scanning folders "
                             "(default: .md,.markdown,.txt,.rst,.tex)")
    parser.add_argument("--exclude", action="append",
                        help="Directory/glob to exclude when scanning (repeatable)")
    parser.add_argument("--max-sentence-words", type=int,
                        help="Override the soft sentence-length limit")
    parser.add_argument("--color", choices=["auto", "always", "never"],
                        default="auto", help="Colorize text output (default: auto)")
    parser.add_argument("--encoding", default="utf-8",
                        help="Source file encoding (default: utf-8)")
    parser.add_argument("--stdin-filename", default="<stdin>",
                        help="File name to label stdin input with")
    parser.add_argument("--list-rules", action="store_true",
                        help="Print the built-in rule catalog and exit")
    parser.add_argument("-V", "--version", action="version",
                        version=f"ProseGuard {__version__}")
    return parser


def discover_files(paths: list[str], cfg: Config) -> list[Path]:
    found: list[Path] = []
    for raw in paths:
        if raw == "-":
            found.append(Path("-"))
            continue
        p = Path(raw)
        if p.is_file():
            found.append(p)
        elif p.is_dir():
            for root, dirs, files in os.walk(p):
                dirs[:] = sorted(
                    d for d in dirs
                    if d not in cfg.excludes
                    and not any(fnmatch.fnmatch(d, pat) for pat in cfg.excludes)
                )
                for name in sorted(files):
                    child = Path(root) / name
                    if child.suffix.lower() in cfg.extensions:
                        found.append(child)
        else:
            raise FileNotFoundError(f"path does not exist: {raw}")
    # De-duplicate while preserving order.
    seen: set[str] = set()
    unique: list[Path] = []
    for f in found:
        key = str(f)
        if key not in seen:
            seen.add(key)
            unique.append(f)
    return unique


def _print_rule_catalog() -> str:
    rows = Linter.catalog()
    width = max(len(r["id"]) for r in rows)
    lines = []
    for r in rows:
        fix = " [fixable]" if r["autofixable"] else ""
        lines.append(
            f"{r['id']:<{width}}  {r['severity']:<10} {r['category']:<11} "
            f"{r['title']}{fix}"
        )
    return "\n".join(lines)


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.list_rules:
        print(_print_rule_catalog())
        return 0

    try:
        cfg = load_config(args.config)
        cfg.enable |= _split_csv(args.enable)
        cfg.disable |= _split_csv(args.disable)
        if args.ext:
            cfg.extensions = {
                e.strip() if e.strip().startswith(".") else f".{e.strip()}"
                for e in args.ext.split(",") if e.strip()
            }
        if args.exclude:
            cfg.excludes |= set(args.exclude)
        if args.max_sentence_words:
            cfg.max_sentence_words = args.max_sentence_words
        files = discover_files(args.paths, cfg)
    except (ValueError, FileNotFoundError, OSError) as exc:
        print(f"proseguard: {exc}", file=sys.stderr)
        return 2

    try:
        linter = Linter(cfg)
    except ValueError as exc:
        print(f"proseguard: {exc}", file=sys.stderr)
        return 2

    use_color = args.color == "always" or (
        args.color == "auto" and sys.stdout.isatty()
    )

    results: list[LintResult] = []
    for path in files:
        if str(path) == "-":
            text = sys.stdin.read()
            result = linter.lint_text(text, path=args.stdin_filename)
            if args.fix:
                fixed, _ = autofix_text(result)
                sys.stdout.write(fixed)
                return 0
            results.append(result)
            continue
        try:
            text = path.read_text(encoding=args.encoding)
        except (UnicodeDecodeError, OSError) as exc:
            print(f"proseguard: cannot read {path}: {exc}", file=sys.stderr)
            return 2
        if args.fix:
            first = linter.lint_text(text, path=str(path))
            fixed, n_fixes = autofix_text(first)
            if n_fixes and fixed != text:
                path.write_text(fixed, encoding=args.encoding)
                text = fixed
        result = linter.lint_text(text, path=str(path))
        results.append(result)

    if args.fmt == "text":
        rendered = report_mod.format_text(results, color=use_color,
                                          show_stats=args.stats)
    else:
        formatter = report_mod.FORMATTERS[args.fmt]
        rendered = formatter(results)

    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        print(rendered)

    total = sum(len(r.findings) for r in results)
    return 1 if total else 0


def main() -> int:
    try:
        return run()
    except KeyboardInterrupt:
        return 2
