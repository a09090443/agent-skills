# Worked Example：Java / Spring Boot 多模組 Harness

本範例取自一個真實的 Spring Boot Starter 集合（多模組 Maven reactor，發佈 Maven Central）。
示範如何把 `SKILL.md` 的六步流程與「建規則配方」套到實際 repo。

## 診斷結果（六原則）

- 原則 1（真相來源）、4（agent-readable）、5（發套件維持把關）：已符合。
- 缺口集中在 **2（缺 AGENTS.md）、3（只有格式 lint，無結構測試）、6（無漂移掃描）**。

## 步驟 1–2：盤點與歸納（DERIVE，不發明）

從現有 7 個模組 grep 出真實慣例：

- 自動配置類在 `com.zipe.autoconfiguration`、類名以 `AutoConfiguration` 結尾、標 `@AutoConfiguration`。
- 以 `META-INF/spring/...AutoConfiguration.imports` 註冊（非舊式 `spring.factories`）。
- `@ConfigurationProperties` 類為 `public`。

**同時發現漂移**（標為「歷史基線」，不在導入時強制掉）：
- logon 的 `SecurityConfiguration` 未循 `*AutoConfiguration` 命名。
- job 用 `com.zipe.quartz.autoconfiguration` 子套件。

## 步驟 5：機械化強制（ArchUnit）

**先驗證全專案無踩雷類別**（規則必須通過現狀），再寫規則。規則刻意設計成能容納既有基線：
規則只要求「套件含 `autoconfiguration`」與「`*AutoConfiguration` 結尾者才需註解」，故上述漂移仍合法通過，無需改動已發佈類名。

```java
package com.zipe.architecture;

import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.classes;
import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.noClasses;

import com.tngtech.archunit.core.importer.ImportOption;
import com.tngtech.archunit.junit.AnalyzeClasses;
import com.tngtech.archunit.junit.ArchTest;
import com.tngtech.archunit.lang.ArchRule;
import org.springframework.boot.autoconfigure.AutoConfiguration;
import org.springframework.boot.context.properties.ConfigurationProperties;

@AnalyzeClasses(packages = "com.zipe", importOptions = ImportOption.DoNotIncludeTests.class)
class StarterArchitectureTest {

    // 規則 1：@AutoConfiguration 的類必須在 autoconfiguration 套件
    @ArchTest
    static final ArchRule autoConfigInPackage = classes()
            .that().areAnnotatedWith(AutoConfiguration.class)
            .should().resideInAPackage("..autoconfiguration..")
            .allowEmptyShould(true);

    // 規則 2：命名 *AutoConfiguration 者必須真的帶 @AutoConfiguration（避免假的自動配置類）
    @ArchTest
    static final ArchRule suffixImpliesAnnotation = classes()
            .that().resideInAPackage("..autoconfiguration..")
            .and().haveSimpleNameEndingWith("AutoConfiguration")
            .should().beAnnotatedWith(AutoConfiguration.class)
            .allowEmptyShould(true);

    // 規則 3：@ConfigurationProperties 類必須 public（否則綁定失敗）
    @ArchTest
    static final ArchRule propsArePublic = classes()
            .that().areAnnotatedWith(ConfigurationProperties.class)
            .should().bePublic()
            .allowEmptyShould(true);

    // 規則 4：正式碼不可依賴測試套件
    @ArchTest
    static final ArchRule mainNotDependOnTest = noClasses()
            .that().resideInAPackage("com.zipe..")
            .should().dependOnClassesThat().resideInAPackage("..test..")
            .allowEmptyShould(true);
}
```

相依（test scope，版本由根 pom 統一管理）：

```xml
<dependency>
    <groupId>com.tngtech.archunit</groupId>
    <artifactId>archunit-junit5</artifactId>
    <scope>test</scope>
</dependency>
```

`mvn verify` 即執行；違規於 CI 階段擋下，而非靠人工 review。

## 步驟 4 & 6：地圖與漂移掃描

- **AGENTS.md**：~100 行導覽地圖，含模組表、必讀工作流程、機械化強制位置、不可違反的規範；細節一律指回 `.claude/rules/` 與 skill，不複製內容。
- **漂移掃描**：可重複執行的 grep 程序，逐項對照黃金規範（註冊方式、命名、套件、可覆寫性、格式、結構測試覆蓋），輸出「現況 vs 規範 vs 建議」表，並區分「歷史基線」與「本次新漂移」。

## 可遷移的要點（換到別的 stack 時）

1. **流程不變**：盤點 → 診斷 → 歸納 → 地圖 → 強制 → 掃描。
2. **只換工具**：ArchUnit → dependency-cruiser／import-linter／depguard（見 SKILL.md 對照表）。
3. **紀律不變**：規則先通過現狀、舊漂移標基線、AGENTS.md 維持地圖、慣例先驗證再寫。
