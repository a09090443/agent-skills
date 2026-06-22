---
name: engineering-a-harness
description: Use when setting up or auditing a repository so AI agents can operate it reliably — establishing an agent navigation map (AGENTS.md), mechanical enforcement of conventions, and convention-drift detection. Applies to any language or stack.
---

# Engineering a Harness（為專案建立 Agent Harness）

## Overview

Harness（控制系統）是讓 AI agent 能**可靠操作一個 repo** 的環境：邊界、地圖、回饋迴路。
理念是 **humans steer, agents execute**——你定義約束，agent 寫碼，機器執行。你架設 agent 運作的環境，而不是逐步指揮它。

依據 OpenAI「Harness Engineering」六原則。本 skill 教**怎麼把任一專案改造成 agent-operable**，適用任何語言／技術棧。

> **核心鐵則：流程到處相同；規則必須逐專案從現有程式碼歸納，嚴禁憑空發明。**
> 「不管哪種專案都照相同模式」指的是**流程與建規則的配方**相同，不是規則內容相同。Python 專案沒有 `@AutoConfiguration`，硬套等於發明不存在的規範。

## When to use

- 接手一個 repo、想讓它能被 agent 穩定協作
- 想稽核現有 repo 是否符合 harness 規劃
- 多人／多 agent 高頻改動，需要防止慣例漂移
- **不要用於**：一次性腳本、無協作需求的個人小專案

## 六原則診斷（每個專案先跑這張表）

| # | 原則 | 檢查 |
|---|---|---|
| 1 | Repository as Source of Truth | 決策／規範／計畫是否入庫版控？沒寫下＝對 agent 不存在 |
| 2 | Maps Not Manuals | 有無 `AGENTS.md` 精簡導覽（~100 行索引），漸進式揭露而非百科？ |
| 3 | Mechanical Enforcement | 不變量是否由 lint／結構測試自動強制？錯誤訊息是否內含修復指引？ |
| 4 | Agent-Readable Code | 技術是否穩定、透明、好被 AI 推理？ |
| 5 | Throughput / Merge | 改動成本低＝快速迭代；高風險（如發佈套件）＝維持把關。依專案定 |
| 6 | Entropy Management | 有無金科玉律 + 定期掃描漂移的機制？agent 會複製好壞模式 |

## 建構流程（固定六步，每個專案一樣）

1. **盤點**：讀現有結構、命名、相依方向、CI、既有規範文件。用 grep／讀碼**取得事實**。
2. **診斷**：對照六原則，標出缺口（通常集中在 2、3、6）。
3. **歸納黃金規範**：把「現存且一致」的慣例寫成規範文件。**DERIVE，不發明**；不一致處標為「歷史漂移基線」。
4. **建 AGENTS.md**：精簡地圖，指回詳規與工作流程，**不複製內容**。
5. **接機械化強制**：依 stack 選工具（見下表），規則**先確保通過現狀**，再接進 CI。
6. **寫漂移掃描程序**：可重複執行的檢查，定期對照黃金規範掃描跨模組／目錄漂移。

## 機械化強制工具（依 stack 選，原則 3）

| Stack | 結構／依賴強制 | 格式／lint |
|---|---|---|
| Java / JVM | **ArchUnit** | Spotless、Checkstyle |
| TypeScript / JS | dependency-cruiser、ts-arch、ESLint 自訂規則 | ESLint、Prettier |
| Python | import-linter、自訂 AST 檢查 + pytest | ruff、black |
| Go | depguard、go-arch-lint、自訂 analyzer | golangci-lint |
| Rust | 自訂 clippy lint、cargo-deny | rustfmt、clippy |
| 任意 | CI 內 grep／script 斷言（最低保底） | editorconfig |

## 建規則的配方（這就是「相同模式」，每條規則都走這五步）

1. **找一條不變量**：依賴方向（A 不可依賴 B）／位置（X 類放 Y 目錄）／命名／可見性／禁用 API。
2. **依 stack 選工具**（見上表）。
3. **寫成規則**（讀起來像白話斷言）。
4. **先對現狀跑**：**必須通過**。既有違規 → 標為基線、不在導入時強制掉（避免為配合規則去改已發佈／高風險程式碼）。
5. **接進 CI**：讓違規在 build 階段就紅，而非靠人工 review 或 agent 自律。

## Common Mistakes（取自真實執行的失敗模式）

| 念頭 | 事實 |
|---|---|
| 「直接套一份通用規則就好」 | 規則必須源於該 repo；別的專案慣例可能相反。先盤點再歸納。 |
| 「把 Java 的 ArchUnit 搬到別的 stack」 | 換工具（見對照表），概念相同、工具不同。 |
| 「規則寫成理想狀態」 | 會在既有漂移上爆掉。**先通過現狀**，舊漂移標基線、另行計畫性清理。 |
| 「AGENTS.md 多寫點才完整」 | 它是地圖（~100 行），細節留在連結目標。長成百科＝違反原則 2。 |
| 「憑印象描述慣例」 | 先 grep／讀碼確認，再寫。發明出來的規範會誤導下一個 agent。 |
| 「導入時順手把舊漂移改掉」 | 改已發佈類名／介面是破壞性變更；分開評估，別混進 harness 導入。 |

## Red flags — 停下來

- 想直接複製規則，卻還沒讀過目標 repo 的程式碼
- 規則第一次跑就紅，而你想**改程式去配合規則**（應改放寬規則或標基線）
- AGENTS.md 開始長出教學／百科內容
- 寫下一條「慣例」前沒有用 grep／讀碼驗證它真的存在且一致

## Worked examples（同一流程、不同 stack）

挑你的 stack 對應的範例，三者**流程與紀律相同、只換工具**：

| Stack | 範例檔 | 強制工具 |
|---|---|---|
| Java / Spring | `java-archunit-example.md` | ArchUnit |
| TypeScript / JS | `ts-dependency-cruiser-example.md` | dependency-cruiser + ESLint |
| Python | `python-import-linter-example.md` | import-linter + AST/pytest |

每份都示範：先驗證／讓規則通過現狀 → 舊漂移標為基線而不強制 → 接進 CI。
其他語言照「建規則配方」+ 工具對照表自行套用同一流程。
