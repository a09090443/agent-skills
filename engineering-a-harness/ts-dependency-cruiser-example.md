# Worked Example：TypeScript / JS Harness（dependency-cruiser）

示範把 `SKILL.md` 的六步流程套到 TypeScript 專案。強制工具用 **dependency-cruiser**
（依賴方向／分層／循環）；命名等其他不變量可用 ESLint 自訂規則補。

## 步驟 1–2：盤點與歸納（DERIVE，不發明）

讀 `src/` 結構與既有 import，歸納「現存且一致」的慣例，例如：

- 分層：`api → services → domain`，`domain` 不可反向依賴上層或框架。
- feature 隔離：`src/features/<x>` 之間不可互相 import，只能經 `src/shared`。
- 全專案不可有循環依賴。

不一致處（例如某個 legacy 模組違反分層）→ 標為「歷史基線」，先用 `severity: 'warn'` 或範圍排除，不在導入時強制掉。

## 步驟 5：機械化強制（.dependency-cruiser.js）

**先對現狀跑一次**確認規則能通過（既有違規先降級或排除），再設 `error`：

```js
// .dependency-cruiser.js
module.exports = {
  forbidden: [
    {
      name: 'no-circular',
      comment: '不可循環依賴',
      severity: 'error',
      from: {},
      to: { circular: true },
    },
    {
      name: 'domain-not-depend-on-framework',
      comment: 'domain 為純邏輯，不可依賴上層或框架',
      severity: 'error',
      from: { path: '^src/domain' },
      to: { path: '^(src/(api|services)|node_modules/(react|express))' },
    },
    {
      name: 'no-cross-feature',
      comment: 'features 只能透過 src/shared 互通',
      severity: 'error',
      from: { path: '^src/features/([^/]+)/.+' },
      // 允許同一 feature 內部互相 import，禁止跨 feature
      to: { path: '^src/features/(?!\\1)[^/]+/.+' },
    },
  ],
  options: {
    doNotFollow: { path: 'node_modules' },
    tsConfig: { fileName: 'tsconfig.json' },
  },
};
```

安裝與執行（接 CI，違規時 exit code 非 0）：

```bash
npm i -D dependency-cruiser
npx depcruise src --config .dependency-cruiser.js   # CI step；--output-type err-long 可讀
```

`package.json`：

```json
{ "scripts": { "arch:check": "depcruise src --config .dependency-cruiser.js" } }
```

## 命名等其他不變量（ESLint 補）

dependency-cruiser 管依賴；命名／禁用 API 用 ESLint：

```js
// eslint.config.js（節錄）
rules: {
  // domain 層禁止直接 import 框架
  'no-restricted-imports': ['error', { patterns: ['react', 'next/*'] }],
}
// 或用 eslint-plugin-boundaries 做更完整的分層宣告
```

## 步驟 4 & 6：地圖與漂移掃描

- **AGENTS.md**：~100 行地圖，標明分層約定、feature 隔離規則、`npm run arch:check` 位置，細節指回各 package README。
- **漂移掃描**：可重複指令（`depcruise --output-type dot` 產依賴圖目視；或 grep 跨 feature import）對照約定，輸出「現況 vs 約定 vs 建議」。

## 對照 Java 版

流程與紀律完全相同，只換工具：ArchUnit → dependency-cruiser + ESLint。規則一樣先通過現狀、舊漂移標基線、AGENTS.md 維持地圖。
