# Contributing to ProseGuard / 贡献指南

首先感谢你愿意改进 ProseGuard！本文档同时提供中英文说明。

Thanks for taking the time to improve ProseGuard! This guide is bilingual.

---

## 开发环境 / Development Setup

```bash
git clone https://github.com/gitstq/proseguard.git
cd proseguard
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .[dev]
make test     # == PYTHONPATH=src python -m unittest discover -s tests -v
```

ProseGuard has **zero runtime third-party dependencies**. New code must keep
that promise; the standard library is preferred for everything.

ProseGuard **运行时零第三方依赖**，这是硬性红线，所有新功能请优先使用标准库实现。

## 提交规范 / Commit Convention

We follow the [Angular commit convention](https://www.conventionalcommits.org/):

- `feat:` a new rule or capability / 新规则或新能力
- `fix:` a bug fix / 缺陷修复
- `docs:` documentation only / 仅文档
- `refactor:` internal restructuring without behavior change / 重构
- `test:` tests only / 仅测试
- `chore:` tooling, packaging, CI / 工程化杂项

## 新增一条规则 / Adding a New Rule

1. Pick the next free rule id in its category:
   `PG1xx` spelling, `PG2xx` grammar, `PG3xx` punctuation,
   `PG4xx` style, `PG5xx` readability.
2. Implement `check(doc, cfg)` in the matching module under
   `src/proseguard/rules/` and register a `Rule(...)` in its `RULES` list.
3. If the rule is deterministic and safe, provide `replacement` and mark it
   `autofixable=True`; never auto-fix anything ambiguous.
4. Add positive **and** negative unittest cases in `tests/`.
5. Update the rule catalog in all three READMEs (`README.md`,
   `README.zh-TW.md`, `README.en.md`) and `CHANGELOG.md`.

中文：规则 ID 按分类号段分配；可确定、零歧义的问题才允许自动修复，并必须补齐
正反两类测试与三语文档中的规则表。

## 扩充词典 / Extending Dictionaries

- Misspellings live in `src/proseguard/dictionaries.py` as
  `wrong -> correct` lower-case pairs; never add a self-mapping.
- Add regression cases that exercise every new entry when practical.
- Wordy phrases need a concise, meaning-preserving replacement.

## Pull Request 流程 / Pull Request Workflow

1. Fork and create a topic branch (`feat/rule-pg206`, `fix/passive-edge`).
2. Make sure `make test` is green and `python -m compileall src tests` passes.
3. Keep PRs focused; one logical change per PR.
4. Describe what changed, why, and how you tested it.
5. A maintainer will review with the checklist: zero new runtime deps,
   tests added, docs updated, no false-positive regressions.

## Issue 反馈 / Filing Issues

- 误报（false positive）请附上：原文片段、期望结果、`proseguard --version`。
- For false positives, include the source snippet, expected result and version.
- Feature requests should explain the writing problem and an example text.

## 行为准则 / Code of Conduct

Be kind and constructive. We keep discussions focused on the prose, not the
person. 保持友善与就事论事。
