# Worked Example：Python Harness（import-linter）

示範把 `SKILL.md` 的六步流程套到 Python 專案。依賴方向／分層用 **import-linter**
（contract 宣告）；命名、裝飾器等結構慣例用自訂 AST 檢查 + pytest 補。

## 步驟 1–2：盤點與歸納（DERIVE，不發明）

讀套件結構與既有 import，歸納「現存且一致」的慣例，例如：

- 分層：`myapp.api → myapp.services → myapp.domain`，`domain` 為最底層。
- `domain` 不可 import 任何 web 框架（django/flask/fastapi）。
- 子套件獨立：`myapp.plugins.*` 之間不可互相依賴。

不一致處 → 標「歷史基線」，用 `ignore_imports` 暫時豁免，不在導入時強制掉。

## 步驟 5：機械化強制（.importlinter / setup.cfg）

**先跑 `lint-imports` 確認通過現狀**（既有違規先 `ignore_imports` 豁免），再納入 CI：

```ini
# setup.cfg（或獨立 .importlinter）
[importlinter]
root_package = myapp

[importlinter:contract:layers]
name = 分層架構：api → services → domain
type = layers
layers =
    myapp.api
    myapp.services
    myapp.domain

[importlinter:contract:domain-pure]
name = domain 不可依賴 web 框架
type = forbidden
source_modules =
    myapp.domain
forbidden_modules =
    django
    flask
    fastapi

[importlinter:contract:plugin-independence]
name = plugins 彼此獨立
type = independence
modules =
    myapp.plugins.billing
    myapp.plugins.reporting
    myapp.plugins.auth
```

安裝與執行（接 CI，contract 破壞時 exit 非 0）：

```bash
pip install import-linter
lint-imports        # CI step
```

## 命名等其他不變量（自訂 AST + pytest 補）

import-linter 管依賴；結構慣例（如「所有 service 類名以 Service 結尾」）用 AST 測試：

```python
# tests/test_architecture.py
import ast, pathlib

def test_service_classes_naming():
    for path in pathlib.Path("myapp/services").rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and not node.name.endswith("Service"):
                raise AssertionError(f"{path}:{node.lineno} {node.name} 應以 Service 結尾")
```

跟著既有 pytest 一起在 CI 跑即可。

## 步驟 4 & 6：地圖與漂移掃描

- **AGENTS.md**：~100 行地圖，標明分層約定、`lint-imports` 與 `pytest` 位置，細節指回各套件 docstring／README。
- **漂移掃描**：可重複指令（`lint-imports` + 上面的 AST 測試 + grep）對照約定，輸出「現況 vs 約定 vs 建議」並區分基線與新漂移。

## 對照 Java 版

流程與紀律完全相同，只換工具：ArchUnit → import-linter + AST/pytest。規則一樣先通過現狀、舊漂移標基線、AGENTS.md 維持地圖。
