"""Output formatters: stylish terminal text, JSON, Markdown and HTML."""

from __future__ import annotations

import html as html_mod
import json
from datetime import datetime, timezone

from .engine import LintResult

_ANSI = {
    "reset": "\033[0m", "bold": "\033[1m", "dim": "\033[2m",
    "red": "\033[31m", "yellow": "\033[33m", "cyan": "\033[36m",
    "green": "\033[32m", "magenta": "\033[35m",
}
_SEV_COLOR = {"error": "red", "warning": "yellow", "suggestion": "cyan"}
_SEV_LABEL = {"error": "error", "warning": "warn ", "suggestion": "hint "}


def _c(text: str, color: str, enabled: bool) -> str:
    if not enabled:
        return text
    return f"{_ANSI[color]}{text}{_ANSI['reset']}"


def _line_preview(source: str, line: int) -> str:
    lines = source.splitlines()
    if 1 <= line <= len(lines):
        return lines[line - 1].strip()
    return ""


def format_text(results: list[LintResult], color: bool = True,
                show_stats: bool = False) -> str:
    out: list[str] = []
    totals = {"error": 0, "warning": 0, "suggestion": 0}
    for result in results:
        if not result.findings and not show_stats:
            continue
        header = result.path or "<stdin>"
        out.append(_c(header, "bold", color))
        if show_stats and result.stats:
            s = result.stats
            out.append(
                "  " + _c("stats", "magenta", color) +
                f"  {s.words} words / {s.sentences} sentences · "
                f"FK grade {s.flesch_kincaid_grade:.1f} · "
                f"Fog {s.gunning_fog:.1f} · FRE {s.flesch_reading_ease:.1f}"
            )
        for finding in result.findings:
            sl, sc, _, _ = finding.position(result.source)
            color_name = _SEV_COLOR[finding.severity]
            tag = _c(f"{_SEV_LABEL[finding.severity]}", color_name, color)
            rid = _c(finding.rule_id, "dim", color)
            line = f"  {_c(f'{sl}:{sc}', 'green', color)}  {tag}  " \
                   f"{finding.message}  {rid}"
            out.append(line)
            if finding.replacement is not None:
                out.append("        " + _c(
                    f"→ {finding.replacement!r}", "dim", color))
            preview = _line_preview(result.source, sl)
            if preview:
                out.append("        " + _c(preview, "dim", color))
            totals[finding.severity] += 1
        out.append("")
    summary = (f"{totals['error']} error(s), {totals['warning']} warning(s), "
               f"{totals['suggestion']} suggestion(s)")
    if totals["error"] == 0 and totals["warning"] == 0 and totals["suggestion"] == 0:
        out.append(_c("✔ No problems found. Clean prose.", "green", color))
    else:
        color_name = "red" if totals["error"] else "yellow"
        out.append(_c("✖ " + summary, color_name, color))
    return "\n".join(out)


def format_json(results: list[LintResult]) -> str:
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "files": [],
    }
    totals = {"error": 0, "warning": 0, "suggestion": 0}
    for result in results:
        item = {
            "path": result.path,
            "findings": [f.to_dict(result.source, result.path)
                         for f in result.findings],
            "stats": result.stats.to_dict() if result.stats else None,
        }
        payload["files"].append(item)
        for f in result.findings:
            totals[f.severity] += 1
    payload["summary"] = totals
    return json.dumps(payload, ensure_ascii=False, indent=2)


def format_markdown(results: list[LintResult]) -> str:
    lines = ["# ProseGuard Report", "",
             f"_Generated: {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC_", ""]
    totals = {"error": 0, "warning": 0, "suggestion": 0}
    for result in results:
        title = result.path or "stdin"
        lines += [f"## `{title}`", ""]
        if not result.findings:
            lines += ["_No problems found._", ""]
            continue
        lines += ["| Position | Severity | Rule | Message | Fix |",
                  "| --- | --- | --- | --- | --- |"]
        for f in result.findings:
            sl, sc, _, _ = f.position(result.source)
            totals[f.severity] += 1
            fix = f.replacement or ""
            msg = f.message.replace("|", "\\|")
            lines.append(
                f"| {sl}:{sc} | {f.severity} | {f.rule_id} | {msg} | {fix} |"
            )
        lines.append("")
    lines += ["---", "",
              f"**Summary:** {totals['error']} errors · "
              f"{totals['warning']} warnings · {totals['suggestion']} suggestions"]
    return "\n".join(lines)


_HTML_CSS = """
:root{--bg:#0f1420;--card:#171d2c;--fg:#e6eaf2;--muted:#93a0b8;--line:#283149;
--error:#ff6b6b;--warning:#ffd166;--hint:#5cc8ff;--ok:#51cf66}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);
font:14px/1.6 -apple-system,Segoe UI,Roboto,'PingFang SC','Microsoft YaHei',sans-serif}
.wrap{max-width:980px;margin:0 auto;padding:32px 20px 64px}
h1{font-size:24px;margin:0 0 4px}.sub{color:var(--muted);margin-bottom:24px}
.cards{display:flex;gap:12px;margin:16px 0 28px}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;
padding:14px 18px;flex:1}.card b{font-size:22px;display:block}
.file{background:var(--card);border:1px solid var(--line);border-radius:12px;
margin:16px 0;overflow:hidden}.file h2{font-size:14px;margin:0;padding:12px 16px;
border-bottom:1px solid var(--line);font-family:ui-monospace,Menlo,monospace}
table{width:100%;border-collapse:collapse}td,th{padding:9px 12px;text-align:left;
border-bottom:1px solid var(--line);vertical-align:top;font-size:13px}
th{color:var(--muted);font-weight:600}.sev{font-weight:700;font-size:12px;
padding:2px 8px;border-radius:999px;white-space:nowrap}
.sev-error{background:rgba(255,107,107,.14);color:var(--error)}
.sev-warning{background:rgba(255,209,102,.14);color:var(--warning)}
.sev-suggestion{background:rgba(92,200,255,.14);color:var(--hint)}
.rid{font-family:ui-monospace,Menlo,monospace;color:var(--muted)}
.fix{color:var(--ok);font-family:ui-monospace,Menlo,monospace}
.clean{color:var(--ok);padding:12px 16px}
"""


def format_html(results: list[LintResult]) -> str:
    totals = {"error": 0, "warning": 0, "suggestion": 0}
    body: list[str] = []
    for result in results:
        title = html_mod.escape(result.path or "stdin")
        body.append(f'<section class="file"><h2>{title}</h2>')
        if not result.findings:
            body.append('<div class="clean">✔ No problems found.</div></section>')
            continue
        body.append("<table><thead><tr><th>Pos</th><th>Severity</th><th>Rule</th>"
                    "<th>Message</th><th>Suggested fix</th></tr></thead><tbody>")
        for f in result.findings:
            sl, sc, _, _ = f.position(result.source)
            totals[f.severity] += 1
            fix = f'<span class="fix">{html_mod.escape(f.replacement)}</span>' \
                if f.replacement is not None else "—"
            body.append(
                f"<tr><td>{sl}:{sc}</td>"
                f'<td><span class="sev sev-{f.severity}">{f.severity}</span></td>'
                f'<td class="rid">{f.rule_id}</td>'
                f"<td>{html_mod.escape(f.message)}</td><td>{fix}</td></tr>"
            )
        body.append("</tbody></table></section>")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ProseGuard Report</title>
<style>{_HTML_CSS}</style>
</head>
<body>
<div class="wrap">
<h1>ProseGuard Report</h1>
<div class="sub">Generated {html_mod.escape(now)} · offline, zero-dependency writing linter</div>
<div class="cards">
  <div class="card"><b style="color:var(--error)">{totals['error']}</b>errors</div>
  <div class="card"><b style="color:var(--warning)">{totals['warning']}</b>warnings</div>
  <div class="card"><b style="color:var(--hint)">{totals['suggestion']}</b>suggestions</div>
</div>
{''.join(body)}
</div>
</body>
</html>
"""


FORMATTERS = {
    "text": None,  # bound in CLI due to color flags
    "json": format_json,
    "md": format_markdown,
    "markdown": format_markdown,
    "html": format_html,
}
