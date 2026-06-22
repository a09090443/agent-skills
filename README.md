# Agent Skills

這是一個自製的 Agent Skills 專案，用來擴充並管理 AI 助手的各項自訂技能。每個技能都存放在獨立的資料夾中，並包含對應的腳本與 `SKILL.md` 說明。

## 目前可用的 Skills

### 1. [Photo Sorter (相片分類工具)](photo-sorter/README.md)
- **目錄**：`photo-sorter/`
- **描述**：幫助使用者將含有 EXIF GPS 座標資訊的相片，依照地理位置及日期進行自動分類與重新命名。
- **詳細說明**：請參考 [`photo-sorter/README.md`](photo-sorter/README.md) 了解完整功能介紹。

### 2. [Docusaurus (網站管理工具)](docusaurus/SKILL.md)
- **目錄**：`docusaurus/`
- **描述**：協助管理 Docusaurus 說明文件網站，支援建立新專案、啟動與停止開發伺服器，以及進行常見的編譯與部署操作。
- **詳細說明**：請參考 [`docusaurus/SKILL.md`](docusaurus/SKILL.md) 了解完整功能介紹與腳本使用方式。

### 3. [Engineering a Harness (專案 Agent Harness 建構)](engineering-a-harness/SKILL.md)
- **目錄**：`engineering-a-harness/`
- **描述**：跨語言／技術棧的方法論，依 Harness Engineering 六原則把任一 repo 改造成 AI agent 可靠協作的環境——建立 `AGENTS.md` 導覽地圖、機械化強制慣例、漂移掃描。流程通用、規則逐專案歸納。
- **詳細說明**：請參考 [`engineering-a-harness/SKILL.md`](engineering-a-harness/SKILL.md)。各語言落地範例（同一流程、不同工具）：[Java/ArchUnit](engineering-a-harness/java-archunit-example.md)、[TypeScript/dependency-cruiser](engineering-a-harness/ts-dependency-cruiser-example.md)、[Python/import-linter](engineering-a-harness/python-import-linter-example.md)。

## 如何在各 CLI 或 IDE 中使用

這些技能（Skills）的設計理念是透過標準化的 `SKILL.md` 檔案，讓不同環境下的 AI Agent 都能閱讀並執行裡面定義好的步驟。

### Antigravity (Gemini Code Assist)
1. **全域使用 (Global)**：將技能資料夾放入使用者目錄下的 `~/.gemini/antigravity/skills/`。如此一來，不管在哪個工作區，都可以直接告訴它：「請使用 `<技能名稱>` 技能來幫我執行 <任務需求>」，它就能全域跨專案存取。
2. **專案使用 (Project)**：將技能資料夾放進專案的 `.agents/skills/`（或 `.agent/skills/`）目錄下。在對話中指示：「請查看 `.agents/skills/<技能名稱>/SKILL.md` 的步驟並執行 <任務需求>」。
3. Antigravity 收到指示後，會主動讀取該技能說明，並利用其內建的工具來運行對應的腳本。

### Claude Code
1. **全域使用 (Global)**：將技能說明檔放置於 `~/.claude/skills/<技能名稱>/SKILL.md` 或 `~/.claude/commands/`，即可在任何目錄下透過 `/user:<技能名稱>` 呼叫該技能。
2. **專案使用 (Project)**：將技能資料夾放入專案的 `.claude/skills/` 中。在終端機對話時提示：「參考 `.claude/skills/<技能名稱>/SKILL.md` 來幫我執行 <任務需求>」，Agent 便會解析步驟並自動執行。

### Cursor / 其它 AI IDE
1. **全域使用 (Global)**：Cursor 的全域規則設定於應用程式內的 Settings (`Cmd/Ctrl + ,` > General > Rules for AI)，你可以將通用的技能內容直接貼於此處。
2. **專案使用 (Project) (推薦)**：Cursor 官方推薦將專案規則放置於 `.cursor/rules/` 並使用 `.mdc` 格式。若維持使用本專案的 markdown 檔，請將其放入 Workspace 後，在 Chat 或是 Prompt 框中利用 `@` 提及對應的檔案（例如：輸入 `@<技能資料夾>/SKILL.md`）。
3. 給予指令：「請依照這個技能說明的步驟，幫我執行 <任務需求>」。IDE 的 AI 就會遵循指示，為你執行定義好的動作。

## 版本控管規範

- 專案根目錄的 [`.gitignore`](.gitignore) 用來排除不需納入版控的檔案。
- 目前已忽略 JetBrains 系列 IDE（IntelliJ IDEA、PyCharm 等）自動產生的 `.idea/` 設定目錄，避免個人化的 IDE 設定污染版本庫。
- 若日後加入其他工具或語言，請於 `.gitignore` 補上對應的忽略規則（例如 `node_modules/`、`__pycache__/`、`*.log` 等）。

---
*(若有新增其他技能，請在此補充)*
