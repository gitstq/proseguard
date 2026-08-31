<div align="center">

# 🛡️ ProseGuard · 英文寫作零相依檢查器

**離線執行 · 零第三方相依 · 拼字 / 文法 / 標點 / 文風 / 可讀性 五位一體**

[简体中文](README.md) ｜ [繁體中文](README.zh-TW.md) ｜ [English](README.en.md)

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Dependencies](https://img.shields.io/badge/runtime%20dependencies-0-success)
![License](https://img.shields.io/badge/license-MIT-green)
![Rules](https://img.shields.io/badge/built--in%20rules-20-orange)
![Tests](https://img.shields.io/badge/tests-73%20passed-brightgreen)

</div>

---

## 🎉 專案介紹

**ProseGuard** 是一款面向開發者與寫作者的**離線英文寫作檢查工具**：一條指令即可掃描 Markdown、純文字、reStructuredText 與 LaTeX 文件，定位拼字錯誤、文法問題、標點排版、冗贅文風與可讀性瓶頸，並輸出終端機、JSON、Markdown、自包含 HTML 四種報告。

- 😩 **解決的痛點**：線上文法助手需要上傳文稿，有隱私外洩風險；傳統本機工具依賴龐大的語言模型或系統級元件；CI 管線裡缺少一個**可腳本化、結束碼語意明確、零網路相依**的英文品質把關工具。
- 🧩 **核心價值**：僅使用 Python 標準函式庫，Clone 即可跑、安裝就能用；規則可插拔、門檻可設定；同時提供 CLI 與可匯入的 Python 函式庫兩種型態。
- ✨ **自研差異化亮點**：
  - **Markdown 感知**：圍籬程式碼區塊、行內程式碼、URL、電子郵件、HTML 註解自動豁免，`--fix` 絕不會誤刪程式碼（具回歸測試把關）。
  - **確定性安全修復**：所有自動修復都基於明確取代、由後向前套用、重疊自動消弭，可重複執行且具備冪等性。
  - **可讀性量化**：內建 Flesch Reading Ease、Flesch–Kincaid 年級分、Gunning Fog 指數與音節估算器。
  - **工程友善**：`0/1/2` 語意化結束碼、JSON 機器可讀輸出、目錄遞迴掃描、個人詞典、GitHub Actions 隨插即用。
- 💡 **靈感來源**：GitHub Trending 榜上的離線文法檢查器 [Harper](https://github.com/Automattic/harper)（Rust 實作）。ProseGuard 僅參考其「本機優先、隱私優先」的產品理念，**全部程式碼皆為獨立自研**，以純 Python 標準函式庫實作，並在 Markdown 處理、自動修復、CI 整合方向做出差異化。

![demo](docs/demo.svg)

---

## ✨ 核心特性

### 🔤 拼字（Spelling）
- **PG100 常見拼字錯誤**：內建 **400+** 高頻易錯詞詞典（`definately → definitely`），自動保留大小寫。
- **PG101 詞語重複**：捕捉「詞彙錯覺」式重複（`the the`），同時放行 `had had` 等合法重複。

### 📐 文法（Grammar）
- **PG200 冠詞一致**：`a/an` 依**發音**判定，涵蓋 `an hour`、`a university` 等特例。
- **PG201 情態動詞誤用**：`should of → should have`。
- **PG202 雙重比較級**：`more easier → easier`。
- **PG203 人稱代名詞**：句中小寫 `i → I`。
- **PG204 第三人稱單數**：`he don't → he doesn't`。
- **PG205 句首大寫**：辨識 `iPhone / eBay / macOS` 等小寫品牌詞，避免誤報。

### ✒️ 標點與排版（Punctuation）
- **PG300** 多餘連續空格、**PG301** 標點前空格、**PG302** 標點後缺空格（自動豁免 `1,000`、`12:30`）、**PG303** 重複標點（豁免刪節號 `...`）、**PG304** 行尾空白。

### 🎩 文風（Style）
- **PG400 模糊詞／對沖詞**、**PG401 弱化副詞**（very / really / literally…）。
- **PG402 被動語態**：辨識 `be + 過去分詞` 型態，建議改寫為主動句。
- **PG403 冗贅片語**：內建 70+ 條精簡對照（`in order to → to`、`due to the fact that → because`）。
- **PG404 過長句**、**PG405 連續三句相同開頭詞**。

### 📊 可讀性（Readability）
- **PG500 高密度長句**：逐句估算 Flesch–Kincaid 風格年級分，超過門檻即提示拆分。
- `--stats` 輸出詞數、句數、複雜詞、音節數、平均句長、FRE、FK 年級分、Gunning Fog。

### 🧰 平台與工程能力
- ✅ **零執行期相依**：Python ≥ 3.9 標準函式庫即可，Windows / macOS / Linux 行為一致。
- ✅ **四種報告**：彩色終端機文字、JSON、Markdown、單檔 HTML（無外部連結，可直接夾帶寄送）。
- ✅ **安全自動修復** `--fix`：修復後自動複檢，只改可證明安全的問題。
- ✅ **設定檔** `.proseguard.json`：開關規則、個人詞典、長度門檻、副檔名與排除目錄，自動向上遞迴尋找。
- ✅ **函式庫型態 API**：`from proseguard import Linter`，便於嵌入編輯器外掛、寫作管線與 Agent。

---

## 🚀 快速開始

### 環境需求

| 項目 | 需求 |
| --- | --- |
| Python | **3.9 / 3.10 / 3.11 / 3.12 / 3.13**（純標準函式庫，無第三方執行期相依） |
| 作業系統 | Windows、macOS、Linux 任一終端機 |
| 磁碟 | 安裝後未滿 50 KB |

### 安裝

```bash
# 方式一：直接從 GitHub 安裝（推薦，本機需有 git）
pip install "git+https://github.com/gitstq/proseguard.git"

# 方式二：Clone 後可編輯安裝（適合二次開發）
git clone https://github.com/gitstq/proseguard.git
cd proseguard
pip install -e .

# 方式三：免安裝直接執行（零相依，設定 PYTHONPATH 即可）
PYTHONPATH=src python -m proseguard --version
```

> Windows PowerShell 設定環境變數：`$env:PYTHONPATH="src"; python -m proseguard --version`

### 30 秒上手

```bash
# 1. 檢視全部 20 條內建規則
proseguard --list-rules

# 2. 檢查單一檔案（結束碼：0 乾淨 / 1 有問題 / 2 執行錯誤）
proseguard docs/intro.md

# 3. 檢查整個目錄（遞迴，自動略過 .git、node_modules、venv 等）
proseguard .

# 4. 安全自動修復，並附上可讀性統計
proseguard --fix --stats README.md

# 5. 管線輸入
echo "This is definately wrong." | proseguard -

# 6. 匯出 HTML 報告
proseguard -f html docs/ -o report.html
```

### 作為 Python 函式庫使用

```python
from proseguard import Linter

linter = Linter()                       # 亦可傳入 Config(disable={"PG400"})
result = linter.lint_text("This is definately wrong.")

for finding in result.findings:
    line, col = finding.position(result.source)[:2]
    print(line, col, finding.rule_id, finding.message, finding.replacement)

print(result.stats.to_dict())           # 可讀性指標
```

---

## 📖 詳細使用指南

### 命令列參數一覽

| 參數 | 說明 |
| --- | --- |
| `paths...` | 檔案或目錄；目錄會依副檔名遞迴掃描；`-` 代表標準輸入 |
| `-c, --config` | 指定 `.proseguard.json`（預設從目標目錄向上自動尋找） |
| `-f, --format` | `text`（預設）/ `json` / `md` / `html` |
| `-o, --output` | 將報告寫入檔案而非標準輸出 |
| `--fix` | 原地套用安全自動修復，隨後自動複檢 |
| `--stats` | 文字報告中附上可讀性統計 |
| `--enable` | 僅啟用指定規則（逗號分隔，可重複），如 `--enable PG100,PG200` |
| `--disable` | 關閉指定規則，如 `--disable PG400,PG401` |
| `--ext` | 目錄掃描的副檔名，預設 `.md,.markdown,.txt,.rst,.tex` |
| `--exclude` | 掃描時排除的目錄名稱 / glob，可重複 |
| `--max-sentence-words` | 覆寫 PG404 軟上限（預設 25） |
| `--color` | `auto`（預設）/ `always` / `never` |
| `--encoding` | 來源檔案編碼，預設 `utf-8` |
| `--stdin-filename` | 為標準輸入內容指定展示用檔名 |
| `--list-rules` | 輸出規則目錄後退出 |
| `-V, --version` | 輸出版本號 |

### 內建規則目錄

| 規則 ID | 層級 | 分類 | 含義 | 可自動修復 |
| --- | --- | --- | --- | --- |
| PG100 | error | spelling | 常見拼字錯誤 | ✅ |
| PG101 | error | spelling | 詞語意外重複 | ✅ |
| PG200 | error | grammar | a/an 冠詞一致 | ✅ |
| PG201 | error | grammar | 情態動詞後接 of 誤用 | ✅ |
| PG202 | error | grammar | 雙重比較級 | ✅ |
| PG203 | error | grammar | 小寫人稱代名詞 i | ✅ |
| PG204 | error | grammar | 第三人稱單數 don't | ✅ |
| PG205 | suggestion | grammar | 句首未大寫 | ✅ |
| PG300 | warning | punctuation | 連續多空格 | ✅ |
| PG301 | warning | punctuation | 標點前多餘空格 | ✅ |
| PG302 | warning | punctuation | 標點後缺空格 | ✅ |
| PG303 | suggestion | punctuation | 重複標點 | ✅ |
| PG304 | warning | punctuation | 行尾空白 | ✅ |
| PG400 | suggestion | style | 模糊／對沖詞 | ❌ |
| PG401 | suggestion | style | 弱化副詞 | ❌ |
| PG402 | suggestion | style | 可能的被動語態 | ❌ |
| PG403 | suggestion | style | 冗贅片語 | ✅ |
| PG404 | suggestion | style | 過長句 | ❌ |
| PG405 | suggestion | style | 連續相同句首 | ❌ |
| PG500 | suggestion | readability | 高密度難讀句 | ❌ |

### 設定檔 `.proseguard.json`

設定會從被檢查檔案所在目錄開始**逐層向上**尋找；命令列參數優先級高於設定檔。

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

- `personal_dictionary`：專案專有名詞／自造詞，統一以小寫登錄，PG100 將永久豁免。
- `enable` 非空時進入**白名單模式**：僅列出的規則生效。

### 典型使用情境

**情境一：Pull Request 英文文件把關**

```bash
proseguard -f json docs/ > proseguard-report.json
# 存在 error 層級問題時結束碼為 1，可直接阻擋合併
```

**情境二：只做拼字與文法硬檢查，忽略風格建議**

```bash
proseguard --enable PG100,PG101,PG200,PG201,PG202,PG203,PG204,PG205 .
```

**情境三：批量安全修復後再人工潤稿**

```bash
proseguard --fix .          # 確定性問題一鍵修復
proseguard --stats .        # 剩餘風格建議與可讀性指標人工處理
```

### 輸出範例（JSON 片段）

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

### 執行截圖／展示

- 終端機展示圖：見專案頂部 [`docs/demo.svg`](docs/demo.svg)。
- 可直接用專案自帶範例體驗：`proseguard --stats examples/bad_writing.md`。
- 動圖佔位：後續版本將於 `docs/demo.gif` 補上真實終端機錄影。

---

## 💡 設計思路與迭代規劃

### 架構設計

```
proseguard/
├── src/proseguard/
│   ├── tokenizer.py     # 句子／詞語切分 + Markdown 等長遮罩（行列號零漂移）
│   ├── dictionaries.py  # 拼字、冗贅片語、被動分詞、發音特例等內建語料
│   ├── rules/           # 五類規則：spelling/grammar/punctuation/style/readability
│   ├── engine.py        # 規則編排、保護區間過濾、結果排序、可讀性統計
│   ├── autofix.py       # 確定性修復：重疊消弭 + 由後向前取代（冪等）
│   ├── report.py        # text / json / markdown / html 四種格式化器
│   ├── config.py        # .proseguard.json 尋找、合併與校驗
│   └── cli.py           # argparse 命令列入口
└── tests/               # 73 個 unittest 案例，零第三方測試相依
```

### 為何這樣选型？

1. **純標準函式庫**：寫作檢查器的價值在規則與語料，而非相依鏈。零相依代表任何 CI Runner、離線伺服器、受限內網都能秒級安裝執行。
2. **等長遮罩而非刪除**：先把程式碼／URL 取代成等長空格再跑規則，行列座標與原文嚴格對齊，並從機制上杜絕自動修復誤傷程式碼。
3. **規則即資料**：每條規則宣告 ID／層級／分類／可修復性，規則目錄、設定開關、報告渲染共用同一份詮釋資料。
4. **保守優先，寧可少報**：涉及語意判斷的規則（there/their、its/it's）預設不做高誤報猜測，維持輸出可信度。

### 迭代路線圖（Roadmap）

- [ ] v1.1：`--watch` 監聽模式與 LSP 最小實作（編輯器即時診斷）。
- [ ] v1.2：可擴充的自訂規則外掛入口（Python entry point）。
- [ ] v1.3：英式／美式拼字詞典切換與 CSV 個人詞典匯入。
- [ ] v1.4：SARIF 輸出，原生對接 GitHub Code Scanning 面板。
- [ ] v2.0：可選的輕量語言模型後端（離線、可關閉），用於語境級文法判斷。

### 社群貢獻方向

新增高頻易錯詞、補充冗贅片語對照、改進音節估算、增加輸出語系、補充各語種文件，都非常歡迎。

---

## 📦 打包與部署指南

ProseGuard 屬於**工具函式庫／CLI 類型專案**（純 Python、跨平台直譯執行），無需下載平台專屬執行檔。

### 從原始碼構建分發包

```bash
python -m pip install build
python -m build           # 產出 dist/*.tar.gz 與 dist/*.whl（py3-none-any）
pip install dist/proseguard-1.0.0-py3-none-any.whl
```

### GitHub Actions 整合

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

### 相容環境與邊界

- 支援 UTF-8 文字；其他編碼可以 `--encoding` 指定。
- 檢查對象聚焦**英文**；中文等 CJK 文字不會被誤判為拼字錯誤（分詞器只辨識拉丁字母詞元）。
- 不發起任何網路請求；HTML 報告為單一檔案，無外部資源參照。

---

## 🤝 貢獻指南

歡迎 Issue、PR 與詞典補充！詳細規範見 [CONTRIBUTING.md](CONTRIBUTING.md)，核心約定如下：

1. **Fork → 特性分支**：分支命名建議 `feat/xxx`、`fix/xxx`、`docs/xxx`。
2. **提交訊息遵循 Angular 規範**：`feat:` / `fix:` / `docs:` / `refactor:` / `test:` / `chore:`。
3. **測試同步**：新增規則必須附上正例＋反例 unittest；本機執行：
   ```bash
   make test          # 等同 PYTHONPATH=src python -m unittest discover -s tests -v
   ```
4. **零相依紅線**：執行期不允許引入任何第三方套件；確有需要請先開 Issue 討論。
5. **Issue 範本**：誤報請附上原文片段、預期行為與 `proseguard --version` 輸出。

---

## ❓ 常見問題（FAQ）

**Q：會把我的文件上傳到雲端嗎？**
A：不會。程式完全離線執行，不發起任何網路請求，原始碼可審計。

**Q：為什麼不檢查 there/their 這類錯誤？**
A：這類判斷高度依賴上下文，誤報代價高。ProseGuard 選擇保守策略，計畫在可選的模型後端中提供。

**Q：`--fix` 會不會改壞我的程式碼區塊？**
A：不會。圍籬程式碼區塊、行內程式碼、連連結網址在檢查前就受到等長遮罩保護，並有專屬回歸測試 `test_fix_never_erases_protected_code_or_links` 把關。

**Q：如何只在 CI 攔截 error、忽略建議？**
A：使用 `--enable` 白名單，或解析 JSON 輸出後依 `severity` 自行決策。

---

## 📄 開源授權

本專案以 **[MIT License](LICENSE)** 開源，可自由用於個人與商業用途，保留版權聲明即可。

<div align="center">

⭐ 如果 ProseGuard 幫你守住了文稿品質，歡迎點 Star 支持持續迭代！

</div>
