---
name: zipe-starters
description: >
  根據使用者需求，從 zipe-spring-boot-starters（https://a09090443.github.io/zipe-spring-boot-starters/）
  自動選取合適的 Starter 模組，並產生可立即使用的 Spring Boot 專案壓縮包（含 pom.xml、
  application.yml、設定檔與範例程式碼）。
  當使用者提到以下任一情境時，請務必使用此 Skill：
  - 想建立 Spring Boot 專案並需要郵件、加解密、資料庫、排程、登入認證、WebService、前端視圖等功能
  - 提到 zipe、zipe-starters、zipe-spring-boot-starters
  - 想整合 Quartz 排程、多資料來源、LDAP 認證、SOAP WebService、Thymeleaf/JSP 視圖
  - 詢問如何引入 base/db/job/logon/iam/web-service/web starter
  - 想要快速搭建具備認證、排程、資料庫的企業級 Spring Boot 骨架
---

# Zipe Spring Boot Starters 專案產生器

根據使用者需求，從官方文件自動選取 Starter 並產生完整可運行的專案壓縮包。

---

## 可用模組總覽

| 模組 key | artifactId | 主要功能 |
|---|---|---|
| `base` | base-spring-boot-starter | 郵件、AES/3DES 加解密、Excel、HTTP (OkHttp)、字串日期工具 |
| `db` | db-spring-boot-starter | 多資料來源動態切換 (`@DS`)、JDBC 封裝、SQL 外部化、P6Spy |
| `job` | job-spring-boot-starter | Quartz 排程（記憶體/JDBC）、REST API 管理排程 |
| `logon` | logon-spring-boot-starter | Spring Security 登入、LDAP、JWT |
| `iam` | iam-spring-boot-starter | 帳號/群組/權限管理（需搭配 logon） |
| `web-service` | web-service-spring-boot-starter | Apache CXF SOAP WebService |
| `web` | web-spring-boot-starter | Thymeleaf/JSP 視圖、統一 REST 回應格式 (`@ResponseResultBody`) |

> **基礎依賴**：`db`、`logon`、`web`、`job` 皆間接依賴 `base`，建議一律引入 `base`。

---

## 執行流程

### Step 1：抓取最新文件

每次執行前先從官方 llms.txt 取得最新模組清單：

```
GET https://a09090443.github.io/zipe-spring-boot-starters/llms.txt
```

若使用者選用特定模組，再抓取該模組的 index 與 quickstart 頁面：

```
GET https://a09090443.github.io/zipe-spring-boot-starters/docs/{module}-starter/index.md
GET https://a09090443.github.io/zipe-spring-boot-starters/docs/{module}-starter/quickstart.md
```

module 對應關係：`base` → `base-starter`、`db` → `db-starter`、`job` → `job-starter`、
`logon` → `logon-starter`、`iam` → `iam-starter`、`web-service` → `web-service-starter`、`web` → `web-starter`

---

### Step 2：需求訪談

詢問使用者以下資訊（可從對話中直接推斷，不須重複問已知的答案）：

1. **功能需求**：需要哪些功能？（RESTful API / 視圖頁面 / 資料庫 / 排程 / 認證 / WebService）
2. **資料庫**：使用哪種資料庫？（PostgreSQL / MySQL / MariaDB / SQL Server / 其他）
3. **建構工具**：Maven 或 Gradle？（目前 Starter 僅官方支援 Maven）
4. **套件名稱**：`groupId` 與根 package（預設 `com.example`）

---

### Step 3：Starter 模組對應規則

根據使用者需求自動對應：

| 使用者需求 | 必須引入的 Starter |
|---|---|
| RESTful API 統一回應格式 | `base` + `web` |
| 資料庫存取（任意種類） | `base` + `db` |
| Quartz 排程 | `base` + `job` |
| 登入認證（表單/LDAP/JWT） | `base` + `logon` |
| 帳號權限管理 | `base` + `db` + `logon` + `iam` |
| SOAP WebService | `base` + `web-service` |
| Thymeleaf/JSP 視圖頁面 | `base` + `web` |
| 純 RESTful（無視圖） | `base` + `web`（只啟用 `@ResponseResultBody`，關閉視圖引擎） |

---

### Step 4：產生專案檔案

依選用模組產生對應檔案，詳細規格見下方各節。

---

## 檔案產生規格

### pom.xml

- Spring Boot parent 版本：`4.0.0`
- Java 版本：`17`
- Zipe Starter 版本屬性：`<zipe.version>4.0.0.1</zipe.version>`
- `groupId`：`io.github.a09090443`
- **必須加入** `maven-compiler-plugin` 的 `annotationProcessorPaths`（含 Lombok），否則 `@RequiredArgsConstructor` 等 annotation 無法正確運作：

```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-compiler-plugin</artifactId>
    <configuration>
        <annotationProcessorPaths>
            <path>
                <groupId>org.projectlombok</groupId>
                <artifactId>lombok</artifactId>
                <version>${lombok.version}</version>
            </path>
        </annotationProcessorPaths>
    </configuration>
</plugin>
```

- 選用模組對應的 `<dependency>`：

```xml
<!-- base（必引入） -->
<dependency>
    <groupId>io.github.a09090443</groupId>
    <artifactId>base-spring-boot-starter</artifactId>
    <version>${zipe.version}</version>
</dependency>

<!-- db（有資料庫需求時引入，已內建 PostgreSQL/MySQL/MariaDB/SQL Server 驅動） -->
<dependency>
    <groupId>io.github.a09090443</groupId>
    <artifactId>db-spring-boot-starter</artifactId>
    <version>${zipe.version}</version>
</dependency>

<!-- job（有排程需求時引入） -->
<dependency>
    <groupId>io.github.a09090443</groupId>
    <artifactId>job-spring-boot-starter</artifactId>
    <version>${zipe.version}</version>
</dependency>

<!-- logon（有登入認證需求時引入） -->
<dependency>
    <groupId>io.github.a09090443</groupId>
    <artifactId>logon-spring-boot-starter</artifactId>
    <version>${zipe.version}</version>
</dependency>

<!-- iam（有帳號/群組/權限管理時引入，必須搭配 logon） -->
<dependency>
    <groupId>io.github.a09090443</groupId>
    <artifactId>iam-spring-boot-starter</artifactId>
    <version>${zipe.version}</version>
</dependency>

<!-- web-service（有 SOAP WebService 需求時引入） -->
<dependency>
    <groupId>io.github.a09090443</groupId>
    <artifactId>web-service-spring-boot-starter</artifactId>
    <version>${zipe.version}</version>
</dependency>

<!-- web（有 REST 統一回應或視圖需求時引入） -->
<dependency>
    <groupId>io.github.a09090443</groupId>
    <artifactId>web-spring-boot-starter</artifactId>
    <version>${zipe.version}</version>
</dependency>
```

---

### application.yml

**⚠️ 必填項目**：

```yaml
spring:
  main:
    # web-starter 的 ViewResolverAutoConfiguration 會與 Spring Boot 內建的
    # WebMvcAutoConfiguration 產生 localeResolver Bean 名稱衝突，必須允許覆寫。
    allow-bean-definition-overriding: true
```

各模組對應的 yml 區塊：

**job-starter（引入排程時）**：
```yaml
spring:
  quartz:
    enable: true
    job-store-type: memory   # 或 jdbc（需建 QRTZ_* 資料表）
    auto-startup: true
    overwrite-existing-jobs: false
    scheduler-name: jobScheduler

quartz:
  controller:
    enabled: true   # 啟用 POST /quartz/register|delete|pause|resume|run
  allowed-job-classes:
    - com.example.job.DemoJob
```

**web-starter（純 RESTful，無視圖）**：
```yaml
web:
  thymeleaf:
    enable: false
  jsp:
    enable: false
```

**web-starter（含 Thymeleaf 視圖）**：
```yaml
web:
  thymeleaf:
    enable: true
    viewNames: "html/*,vue/*,templates/*,th/*"
    stuff: .html
    templateMode: HTML
  jsp:
    enable: false
```

---

### data-source.properties（引入 db-starter 時）

⚠️ **關鍵注意事項**（必須在檔案中以註解提醒使用者）：

1. 密碼欄位名稱是 **`pa55word`**（不是 `password`），這是刻意設計，填錯會導致密碼為空白
2. `dynamic.primary` 的值必須與 `dynamic.data-source-map` 中實際存在的 key 一致
3. 使用 P6Spy 監控時，URL 需加 `p6spy:` 前綴；不需要監控則使用原生驅動

PostgreSQL 範例：
```properties
dynamic.primary=master
dynamic.entity-scan=com.example
dynamic.is-encrypt=false

# P6Spy 監控版本
dynamic.data-source-map[master].url=jdbc:p6spy:postgresql://localhost:5432/demo_db?characterEncoding=UTF-8&serverTimezone=Asia/Taipei
dynamic.data-source-map[master].username=postgres
dynamic.data-source-map[master].pa55word=your_password
dynamic.data-source-map[master].driverClassName=com.p6spy.engine.spy.P6SpyDriver
```

其他資料庫 URL 格式（P6Spy 版本）：
- MySQL：`jdbc:p6spy:mysql://localhost:3306/db?characterEncoding=UTF-8&serverTimezone=Asia/Taipei`，driver：`com.p6spy.engine.spy.P6SpyDriver`
- MariaDB：`jdbc:p6spy:mariadb://localhost:3306/db`，driver：`com.p6spy.engine.spy.P6SpyDriver`
- SQL Server：`jdbc:p6spy:sqlserver://localhost:1433;databaseName=db`，driver：`com.p6spy.engine.spy.P6SpyDriver`

---

### quartz-jobs.properties（引入 job-starter 時）

```properties
# 啟動時自動批次建立排程
quartz.job-map[DemoJob].name=DemoJob
quartz.job-map[DemoJob].description=每分鐘示範排程
quartz.job-map[DemoJob].group=demo
quartz.job-map[DemoJob].clazz=com.example.job.DemoJob
# Quartz Cron：秒 分 時 日 月 週 [年]（與 Linux crontab 5 欄位不同）
quartz.job-map[DemoJob].cronExpression=0 * * * * ?
```

---

### SQL 檔案（引入 db-starter 時）

BaseJDBC 不允許直接傳入 SQL 字串，所有 SQL 必須存於 `src/main/resources/sql/*.sql`：

```sql
-- DEMO_LIST.sql
SELECT id, name, description, created_at
FROM demo
WHERE 1 = 1
${CONDITIONS}
ORDER BY created_at DESC
```

---

### Java 範例程式碼

#### 排程 Job（引入 job-starter 時）

```java
// 繼承 QuartzJobFactory（不是 BaseJob），覆寫 executeJob()
@Slf4j
public class DemoJob extends QuartzJobFactory {
    @Override
    protected void executeJob(JobExecutionContext context) throws Exception {
        String param = context.getJobDetail().getJobDataMap().getString("param");
        log.info("DemoJob 執行，參數：{}", param);
    }
}
```

#### DAO（引入 db-starter 時）

```java
@Repository
public class DemoJdbc extends BaseJDBC {
    public List<Map<String, Object>> findAll() {
        return queryForList(ResourceEnum.SQL.getResource("DEMO_LIST"));
    }
    public List<Map<String, Object>> searchByName(String name) {
        Conditions conditions = new Conditions();
        conditions.like("d.name", name);
        return queryForList(ResourceEnum.SQL.getResource("DEMO_LIST"), new HashMap<>(), conditions);
    }
}
```

#### Service（@DS 多資料來源切換）

```java
@Slf4j
@Service
@RequiredArgsConstructor
public class DemoService {
    private final DemoJdbc demoJdbc;

    public List<Map<String, Object>> findAll() {
        return demoJdbc.findAll();
    }

    @DS("report")   // 切換至 report 資料來源
    public List<Map<String, Object>> findAllFromReport() {
        return demoJdbc.findAll();
    }
}
```

#### Controller（引入 web-starter 時）

```java
@Slf4j
@RestController
@ResponseResultBody   // 自動包裝為 { "code": 200, "message": "OK", "data": ... }
@RequestMapping("/api/demo")
@RequiredArgsConstructor
public class DemoController {
    private final DemoService demoService;

    @GetMapping
    public List<Map<String, Object>> findAll() {
        return demoService.findAll();
    }

    @GetMapping("/search")
    public List<Map<String, Object>> search(@RequestParam String name) {
        return demoService.searchByName(name);
    }

    @GetMapping("/health")
    public Map<String, String> health() {
        return Map.of("status", "UP");
    }
}
```

---

## 已知問題（必須主動處理，不能等使用者回報）

| 問題 | 原因 | 解法 |
|---|---|---|
| `localeResolver` bean 衝突，啟動失敗 | web-starter 與 Spring Boot 內建的 WebMvcAutoConfiguration 同名 bean | `application.yml` 加入 `spring.main.allow-bean-definition-overriding: true` |
| `@RequiredArgsConstructor` 產生的建構子找不到 | pom.xml 缺少 Lombok annotationProcessorPaths | `maven-compiler-plugin` 加入 `annotationProcessorPaths` |
| 密碼為空，資料庫連線失敗 | data-source.properties 誤用 `password` 而非 `pa55word` | 在設定檔中加上醒目註解提醒 |
| 目錄名稱出現 `{a,b,c}` 字元 | bash brace expansion 失效 | 使用獨立的 `mkdir` 指令建立各子目錄 |

---

## 專案產出規格

1. 建立完整目錄結構，**每個子目錄獨立 `mkdir`**（不使用 brace expansion）
2. 建立所有必要檔案
3. 用 `zip -r` 打包為 `{專案名稱}.zip`
4. 呼叫 `present_files` 讓使用者下載

### 啟動指引（在 README.md 中說明）

```bash
# 1. 安裝所需 Starters 至本地 Maven Repository
for module in base db job web; do
  (cd ${module}-spring-boot-starter && ./mvnw clean install -DskipTests)
done

# 2. 修改 data-source.properties（密碼欄位是 pa55word）

# 3. 啟動
./mvnw spring-boot:run
```

---

## 需求超出 Starters 範圍的處理規則

### 判斷方式

收到使用者需求後，先對照「可用模組總覽」逐項比對。若需求**完全無法對應到任何 Starter**，即為「超出範圍」。

### 回覆原則

**絕對不可以：**
- 捏造一個不存在的 Starter（如 `redis-spring-boot-starter`）放進 pom.xml
- 沉默地忽略該需求，假裝已實現
- 宣稱 Starter 支援它不支援的功能

**必須這樣做：**
1. **明確告知**哪個需求超出 zipe-starters 的範圍
2. **推薦對應的 Spring Boot 官方或常見第三方依賴**作為替代
3. **仍然產生專案**，把可對應的 Starter 用上，不支援的部分改用標準依賴補足
4. 在 `pom.xml` 中**加上清楚的區塊註解**區分 zipe Starter 與額外依賴

### 回覆範例語句

```
您需要的「Redis 快取」功能目前不在 zipe-spring-boot-starters 的範圍內。
我會使用 Spring Boot 官方的 spring-boot-starter-data-redis 來實現這個功能，
其餘部分（資料庫、排程）仍使用 zipe starters。
```

### 常見超出範圍的需求對應表

| 使用者需求 | zipe 是否支援 | 建議替代方案 |
|---|---|---|
| Redis 快取 / Session | ❌ | `spring-boot-starter-data-redis` |
| Kafka / RabbitMQ 訊息佇列 | ❌ | `spring-kafka` / `spring-boot-starter-amqp` |
| Elasticsearch | ❌ | `spring-boot-starter-data-elasticsearch` |
| OAuth2 / SSO（Keycloak 等） | ❌ | `spring-boot-starter-oauth2-client` |
| GraphQL API | ❌ | `spring-boot-starter-graphql` |
| WebSocket | ❌ | `spring-boot-starter-websocket` |
| MongoDB | ❌ | `spring-boot-starter-data-mongodb` |
| gRPC | ❌ | `grpc-spring-boot-starter`（第三方） |
| 檔案上傳至 S3/MinIO | ❌ | AWS SDK / `minio` 官方 SDK |
| 健康檢查 / Metrics | ❌ | `spring-boot-starter-actuator` |
| API 文件（Swagger） | ❌ | `springdoc-openapi-starter-webmvc-ui` |
| 郵件發送 | ✅ | 使用 `base-starter` 的 `MailService` |
| 加解密 | ✅ | 使用 `base-starter` 的 `AesUtil` 等 |
| 資料庫（PostgreSQL/MySQL 等） | ✅ | 使用 `db-starter` |
| Quartz 排程 | ✅ | 使用 `job-starter` |
| Spring Security 登入 | ✅ | 使用 `logon-starter` |
| SOAP WebService | ✅ | 使用 `web-service-starter` |

### pom.xml 區塊註解範例（混用時）

```xml
<!-- ===== Zipe Starters（核心功能） ===== -->
<dependency>
    <groupId>io.github.a09090443</groupId>
    <artifactId>db-spring-boot-starter</artifactId>
    <version>${zipe.version}</version>
</dependency>

<!-- ===== 額外依賴（超出 zipe-starters 範圍，以標準 Spring Boot 依賴補足） ===== -->
<!-- Redis 快取：zipe-starters 未提供，使用 Spring Boot 官方 Starter -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-redis</artifactId>
</dependency>
```

### 部分支援的情境

若使用者需求「部分涵蓋」，例如：

- **OAuth2 登入**：`logon-starter` 支援表單登入與 LDAP，但不支援 OAuth2。
  → 說明 logon-starter 能做的範圍，OAuth2 部分加入 `spring-boot-starter-oauth2-client`。

- **Oracle 資料庫**：`db-starter` 的 JDBC 機制相容 Oracle，但未內建 Oracle 驅動。
  → 引入 `db-starter` 並額外加入 Oracle JDBC 驅動依賴，並在 data-source.properties 中使用原生驅動（非 P6Spy）。
