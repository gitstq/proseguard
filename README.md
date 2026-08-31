<div align="center">

# 🛡️ ProseGuard · 英文写作零依赖检查器

**离线运行 · 零第三方依赖 · 拼写 / 语法 / 标点 / 文风 / 可读性 五维一体**

[简体中文](README.md) ｜ [繁體中文](README.zh-TW.md) ｜ [English](README.en.md)

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Dependencies](https://img.shields.io/badge/runtime%20dependencies-0-success)
![License](https://img.shields.io/badge/license-MIT-green)
![Rules](https://img.shields.io/badge/built--in%20rules-20-orange)
![Tests](https://img.shields.io/badge/tests-73%20passed-brightgreen)

</div>

---

## 🎉 项目介绍

**ProseGuard** 是一款面向开发者与写作者的**离线英文写作检查工具**：一条命令即可扫描 Markdown / 纯文本 / reStructuredText / LaTeX 文档，定位拼写错误、语法问题、标点排版、冗余文风与可读性瓶颈，并输出终端、JSON、Markdown、自包含 HTML 四种报告。

- 😩 **解决的痛点**：在线语法助手需要上传文稿、存在隐私泄露风险；传统本地工具依赖庞大的语言模型或系统级组件；CI 流水线里缺少一个**可脚本化、退出码语义明确、零网络依赖**的英文质量门禁。
- 🧩 **核心价值**：仅使用 Python 标准库，克隆即可跑、装上就能用；规则可插拔、阈值可配置；提供 CLI 与可导入的 Python 库两种形态。
- ✨ **自研差异化亮点**：
  - **Markdown 感知**：围栏代码块、行内代码、URL、邮箱、HTML 注释自动豁免，`--fix` 绝不会误删代码（有回归测试守护）。
  - **确定性安全修复**：所有自动修复都基于显式替换、从后向前应用、重叠自动消解，可重复执行且幂等。
  - **可读性量化**：内置 Flesch Reading Ease、Flesch–Kincaid 年级、Gunning Fog 指数与音节估算器。
  - **工程友好**：`0/1/2` 语义化退出码、JSON 机器可读输出、目录递归扫描、个人词典、GitHub Actions 即插即用。
- 💡 **灵感来源**：GitHub Trending 榜上的离线语法检查器 [Harper](https://github.com/Automattic/harper)（Rust 实现）。ProseGuard 仅参考其「本地优先、隐私优先」的产品理念，**全部代码为独立自研**，以纯 Python 标准库实现并在 Markdown 处理、自动修复、CI 集成方向做了差异化设计。

![demo](docs/demo.svg)

---

## ✨ 核心特性

### 🔤 拼写（Spelling）
- **PG100 常见拼写错误**：内置 **400+** 高频易错词词典（`definately → definitely`），自动保留大小写。
- **PG101 词语重复**：捕获「词汇错觉」式重复（`the the`），同时放行 `had had` 等合法重复。

### 📐 语法（Grammar）
- **PG200 冠词一致**：`a/an` 按**发音**判定，覆盖 `an hour`、`a university` 等特例。
- **PG201 情态动词误用**：`should of → should have`。
- **PG202 双重比较级**：`more easier → easier`。
- **PG203 人称代词**：句中小写 `i → I`。
- **PG204 第三人称单数**：`he don't → he doesn't`。
- **PG205 句首大写**：识别 `iPhone / eBay / macOS` 等小写品牌词，避免误报。

### ✒️ 标点与排版（Punctuation）
- **PG300** 多余连续空格、**PG301** 标点前空格、**PG302** 标点后缺空格（自动豁免 `1,000`、`12:30`）、**PG303** 重复标点（豁免省略号 `...`）、**PG304** 行尾空白。

### 🎩 文风（Style）
- **PG400 模糊词 / 对冲词**、**PG401 弱化副词**（very / really / literally…）。
- **PG402 被动语态**：`be + 过去分词` 模式识别，建议改写为主动句。
- **PG403 冗长短语**：内置 70+ 条精简映射（`in order to → to`、`due to the fact that → because`）。
- **PG404 超长句**、**PG405 连续三句相同开头词**。

### 📊 可读性（Readability）
- **PG500 高密度长句**：逐句估算 Flesch–Kincaid 风格年级分，超阈值即提示拆分。
- `--stats` 输出词数、句数、复杂词、音节数、平均句长、FRE、FK 年级、Gunning Fog。

### 🧰 平台与工程能力
- ✅ **零运行时依赖**：Python ≥ 3.9 标准库即可，Windows / macOS / Linux 全平台一致。
- ✅ **四种报告**：彩色终端文本、JSON、Markdown、单文件 HTML（无外链、可直接发邮件）。
- ✅ **安全自动修复** `--fix`：修复后自动复检，只改可证明安全的问题。
- ✅ **配置文件** `.proseguard.json`：开关规则、个人词典、长度阈值、扩展名与排除目录，自动向上递归发现。
- ✅ **库形态 API**：`from proseguard import Linter`，方便嵌入编辑器插件、写作流水线与 Agent。

---

## 🚀 快速开始

### 环境要求

| 项目 | 要求 |
| --- | --- |
| Python | **3.9 / 3.10 / 3.11 / 3.12 / 3.13**（纯标准库，无第三方运行时依赖） |
| 操作系统 | Windows、macOS、Linux 任意终端 |
| 磁盘 | 安装包 < 50 KB |

### 安装

```bash
# 方式一：从 GitHub 直接安装（推荐，需要本机有 git）
pip install "git+https://github.com/gitstq/proseguard.git"

# 方式二：克隆后可编辑安装（便于二次开发）
git clone https://github.com/gitstq/proseguard.git
cd proseguard
pip install -e .

# 方式三：免安装直接运行（零依赖，设置 PYTHONPATH 即可）
PYTHONPATH=src python -m proseguard --version
```

> Windows PowerShell 下设置环境变量：`$env:PYTHONPATH="src"; python -m proseguard --version`

### 30 秒上手

```bash
# 1. 查看全部 20 条内置规则
proseguard --list-rules

# 2. 检查单个文件（退出码：0 干净 / 1 有问题 / 2 运行错误）
proseguard docs/intro.md

# 3. 检查整个目录（递归，自动跳过 .git、node_modules、venv 等）
proseguard .

# 4. 安全自动修复，并附带可读性统计
proseguard --fix --stats README.md

# 5. 管道输入
echo "This is definately wrong." | proseguard -

# 6. 导出 HTML 报告
proseguard -f html docs/ -o report.html
```

### 作为 Python 库使用

```python
from proseguard import Linter

linter = Linter()                       # 也可传入 Config(disable={"PG400"})
result = linter.lint_text("This is definately wrong.")

for finding in result.findings:
    line, col = finding.position(result.source)[:2]
    print(line, col, finding.rule_id, finding.message, finding.replacement)

print(result.stats.to_dict())           # 可读性指标
```

---

## 📖 详细使用指南

### 命令行参数全览

| 参数 | 说明 |
| --- | --- |
| `paths...` | 文件或目录；目录会按扩展名递归扫描；`-` 表示标准输入 |
| `-c, --config` | 指定 `.proseguard.json`（默认从目标目录向上自动查找） |
| `-f, --format` | `text`（默认）/ `json` / `md` / `html` |
| `-o, --output` | 将报告写入文件而非标准输出 |
| `--fix` | 原地应用安全自动修复，随后自动复检 |
| `--stats` | 文本报告中附带可读性统计 |
| `--enable` | 仅启用指定规则（逗号分隔，可重复），如 `--enable PG100,PG200` |
| `--disable` | 关闭指定规则，如 `--disable PG400,PG401` |
| `--ext` | 目录扫描的扩展名，默认 `.md,.markdown,.txt,.rst,.tex` |
| `--exclude` | 扫描时排除的目录名 / glob，可重复 |
| `--max-sentence-words` | 覆盖 PG404 的软上限（默认 25） |
| `--color` | `auto`（默认）/ `always` / `never` |
| `--encoding` | 源文件编码，默认 `utf-8` |
| `--stdin-filename` | 为标准输入内容指定展示用文件名 |
| `--list-rules` | 输出规则目录后退出 |
| `-V, --version` | 输出版本号 |

### 内置规则目录

| 规则 ID | 级别 | 分类 | 含义 | 可自动修复 |
| --- | --- | --- | --- | --- |
| PG100 | error | spelling | 常见拼写错误 | ✅ |
| PG101 | error | spelling | 词语意外重复 | ✅ |
| PG200 | error | grammar | a/an 冠词一致 | ✅ |
| PG201 | error | grammar | 情态动词后接 of 误用 | ✅ |
| PG202 | error | grammar | 双重比较级 | ✅ |
| PG203 | error | grammar | 小写人称代词 i | ✅ |
| PG204 | error | grammar | 第三人称单数 don't | ✅ |
| PG205 | suggestion | grammar | 句首未大写 | ✅ |
| PG300 | warning | punctuation | 连续多空格 | ✅ |
| PG301 | warning | punctuation | 标点前多余空格 | ✅ |
| PG302 | warning | punctuation | 标点后缺空格 | ✅ |
| PG303 | suggestion | punctuation | 重复标点 | ✅ |
| PG304 | warning | punctuation | 行尾空白 | ✅ |
| PG400 | suggestion | style | 模糊 / 对冲词 | ❌ |
| PG401 | suggestion | style | 弱化副词 | ❌ |
| PG402 | suggestion | style | 可能的被动语态 | ❌ |
| PG403 | suggestion | style | 冗长短语 | ✅ |
| PG404 | suggestion | style | 超长句 | ❌ |
| PG405 | suggestion | style | 连续相同句首 | ❌ |
| PG500 | suggestion | readability | 高密度难读句 | ❌ |

### 配置文件 `.proseguard.json`

配置会从被检查文件所在目录开始**逐级向上**查找；命令行参数优先级高于配置文件。

```json
{
  "disable": ["PG400", "PG401"],
  "enable": [],
  "max_sentence_words": 28,
  "long_sentence_hard": 40,
  "readability_grade": 12,
  "personal_dictionary": ["proseguard", "pythonic"],
  "extensions": [".md", ".txt", ".rst"],
  "excludes": ["draft", "vendor"]
}
```

- `personal_dictionary`：项目专有名词 / 造词，统一小写录入，PG100 将永久豁免。
- `enable` 非空时进入**白名单模式**：仅列出的规则生效。

### 典型使用场景

**场景一：Pull Request 英文文档门禁**

```bash
proseguard -f json docs/ > proseguard-report.json
# 存在 error 级别问题时退出码为 1，可直接阻断合并
```

**场景二：只做拼写与语法硬检查，忽略风格建议**

```bash
proseguard --enable PG100,PG101,PG200,PG201,PG202,PG203,PG204,PG205 .
```

**场景三：批量安全修复后再人工润色**

```bash
proseguard --fix .          # 确定性问题一键修复
proseguard --stats .        # 剩余风格建议与可读性指标人工处理
```

### 输出示例（JSON 片段）

```json
{
  "files": [{
    "path": "intro.md",
    "findings": [{
      "rule_id": "PG100",
      "severity": "error",
      "category": "spelling",
      "start_line": 3, "start_column": 9,
      "message": "Possible misspelling “definately”. Did you mean “definitely”?",
      "replacement": "definitely",
      "autofixable": true
    }],
    "stats": { "words": 100, "sentences": 5, "flesch_kincaid_grade": 9.3 }
  }],
  "summary": { "error": 1, "warning": 0, "suggestion": 3 }
}
```

### 运行截图 / 演示

- 终端演示图：见仓库顶部 [`docs/demo.svg`](docs/demo.svg)。
- 可直接用仓库自带样例体验：`proseguard --stats examples/bad_writing.md`。
- 动图占位：后续版本将在 `docs/demo.gif` 补充真实终端录屏。

---

## 💡 设计思路与迭代规划

### 架构设计

```
proseguard/
├── src/proseguard/
│   ├── tokenizer.py     # 句子/词语切分 + Markdown 等长掩码（行列号零漂移）
│   ├── dictionaries.py  # 拼写、冗长短语、被动分词、发音特例等内置语料
│   ├── rules/           # 五类规则：spelling/grammar/punctuation/style/readability
│   ├── engine.py        # 规则编排、保护区间过滤、结果排序、可读性统计
│   ├── autofix.py       # 确定性修复：重叠消解 + 从后向前替换（幂等）
│   ├── report.py        # text / json / markdown / html 四种格式化器
│   ├── config.py        # .proseguard.json 发现、合并与校验
│   └── cli.py           # argparse 命令行入口
└── tests/               # 73 个 unittest 用例，零第三方测试依赖
```

### 为什么这样选型？

1. **纯标准库**：写作检查器的价值在规则与语料，不在依赖链。零依赖意味着任何 CI Runner、离线服务器、受限内网都能秒级安装运行。
2. **等长掩码而非删除**：先把代码 / URL 替换成等长空格再跑规则，行列坐标与原文严格对齐，同时从机制上杜绝自动修复误伤代码。
3. **规则即数据**：每条规则声明 ID / 级别 / 分类 / 可修复性，规则目录、配置开关、报告渲染共用同一份元数据。
4. **保守优先，宁可少报**：涉及语义判断的规则（there/their、its/it's）默认不做高误报猜测，保持输出可信度。

### 迭代路线图（Roadmap）

- [ ] v1.1：`--watch` 监听模式与 LSP 最小实现（编辑器实时诊断）。
- [ ] v1.2：可扩展的自定义规则插件入口（Python entry point）。
- [ ] v1.3：英式 / 美式拼写词典切换与 CSV 个人词典导入。
- [ ] v1.4：SARIF 输出，原生对接 GitHub Code Scanning 面板。
- [ ] v2.0：可选的轻量语言模型后端（离线、可关闭），用于语境级语法判断。

### 社区贡献方向

新增高频易错词、补充冗长短语映射、改进音节估算、增加输出语言、补充各语种文档，都是非常受欢迎的贡献。

---

## 📦 打包与部署指南

ProseGuard 属于**工具库 / CLI 类项目**（纯 Python、跨平台解释执行），无需下载平台二进制。

### 从源码构建分发包

```bash
python -m pip install build
python -m build           # 产出 dist/*.tar.gz 与 dist/*.whl（py3-none-any）
pip install dist/proseguard-1.0.0-py3-none-any.whl
```

### GitHub Actions 集成

```yaml
name: Docs prose check
on: [pull_request]
jobs:
  proseguard:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install "git+https://github.com/gitstq/proseguard.git"
      - run: proseguard --format json docs/ -o proseguard.json
      - uses: actions/upload-artifact@v4
        with: { name: proseguard-report, path: proseguard.json }
```

### 兼容环境与边界

- 支持 UTF-8 文本；其他编码可用 `--encoding` 指定。
- 检查对象聚焦**英文**；中文等 CJK 文本不会被误判为拼写错误（分词器仅识别拉丁字母词元）。
- 不做任何网络请求；HTML 报告为单文件、无外部资源引用。

---

## 🤝 贡献指南

欢迎 Issue、PR 与词典补充！详细规范见 [CONTRIBUTING.md](CONTRIBUTING.md)，核心约定如下：

1. **Fork → 特性分支**：分支命名建议 `feat/xxx`、`fix/xxx`、`docs/xxx`。
2. **提交信息遵循 Angular 规范**：`feat:` / `fix:` / `docs:` / `refactor:` / `test:` / `chore:`。
3. **测试同步**：新增规则必须附带正例 + 反例 unittest；本地执行：
   ```bash
   make test          # 等价于 PYTHONPATH=src python -m unittest discover -s tests -v
   ```
4. **零依赖红线**：运行时不允许引入任何第三方包；确有需要请先开 Issue 讨论。
5. **Issue 模板**：误报请附上原文片段、期望行为与 `proseguard --version` 输出。

---

## ❓ 常见问题（FAQ）

**Q：会把我的文档上传到云端吗？**
A：不会。程序完全离线运行，不发起任何网络请求，源码可审计。

**Q：为什么不检查 there/their 这类错误？**
A：这类判断高度依赖上下文，误报代价大。ProseGuard 选择保守策略，计划在可选的模型后端中提供。

**Q：`--fix` 会不会改坏我的代码块？**
A：不会。围栏代码块、行内代码、链接地址在检查前就被等长掩码保护，并有专门回归测试 `test_fix_never_erases_protected_code_or_links` 守护。

**Q：如何只在 CI 里拦截 error，忽略建议？**
A：用 `--enable` 白名单，或解析 JSON 输出后按 `severity` 自行决策。

---

## 📄 开源协议

本项目基于 **[MIT License](LICENSE)** 开源，可自由用于个人与商业用途，保留版权声明即可。

<div align="center">

⭐ 如果 ProseGuard 帮你守住了文稿质量，欢迎点 Star 支持持续迭代！

</div>
