# Zipe Starters 模組快速參考

> 本檔案為 SKILL.md 的補充，列出各模組引入時的完整設定與注意事項。
> 當使用者選用某模組時，讀取對應章節即可。

---

## base-spring-boot-starter

所有 Starter 的共同基礎，**無論選用哪些模組都必須引入**。

**依賴**：
```xml
<dependency>
    <groupId>io.github.a09090443</groupId>
    <artifactId>base-spring-boot-starter</artifactId>
    <version>${zipe.version}</version>
</dependency>
```

**主要工具類別**：
- `MailService`：郵件發送（純文字 / HTML / 附件 / Velocity 模板）
- `AesUtil`：AES-128/CBC/PKCS5Padding 加解密
- `OkHttpUtil`：OkHttp 封裝（GET / POST）
- `ExcelUtil`：POI Excel 匯入匯出
- `DateTimeUtils`：Java 8 日期工具（含台灣民國年互轉）
- `BeanUtil`：Bean 複製、JSON 序列化（Gson + Jackson）

---

## db-spring-boot-starter

**已內建驅動（無需額外加入）**：PostgreSQL、MySQL、MariaDB、SQL Server、AS400

**需要自行加入驅動**：Oracle、DB2

**@DS 切換規則**：
- 透過 AOP 攔截，僅對「跨 Bean 的外部呼叫」有效
- 同類別內 `this.method()` 呼叫無效
- 類別層級 `@DS` 優先於方法層級 `@DS`

---

## job-spring-boot-starter

**JDBC 持久化模式建表 SQL（PostgreSQL）**：
```sql
-- Quartz 官方資料表（需在啟用 jdbc 模式前建立）
-- 完整 SQL：https://github.com/quartz-scheduler/quartz/blob/main/quartz/src/main/resources/org/quartz/impl/jdbcjobstore/tables_postgres.sql
```

**REST API 端點**：

| Method | Path | 說明 |
|---|---|---|
| POST | `/quartz/register` | 新增或更新排程 |
| POST | `/quartz/delete` | 刪除排程 |
| POST | `/quartz/pause` | 暫停排程 |
| POST | `/quartz/resume` | 恢復排程 |
| POST | `/quartz/run` | 立即執行一次 |

**啟用 REST API**（預設關閉）：
```yaml
quartz:
  controller:
    enabled: true
  allowed-job-classes:
    - com.example.job.YourJob   # 白名單，防止任意類別被執行
```

**Cron 格式**：秒 分 時 日 月 週 [年]（6~7 欄位，與 Linux crontab 5 欄位不同）
- `0 * * * * ?` → 每分鐘整點
- `0 0 2 * * ?` → 每天凌晨 2 點
- `0 0 9 ? * MON-FRI` → 週一到週五早上 9 點

---

## logon-spring-boot-starter

**主要設定**（`application.yml`，前綴 `security.*`）：
```yaml
security:
  permit-all-patterns:
    - /public/**
    - /api/health
  login-page: /login
  default-success-url: /dashboard
```

**LDAP 設定**（前綴 `security.ldap.*`）：
```yaml
security:
  ldap:
    enabled: true
    url: ldap://localhost:389
    base: dc=example,dc=com
    user-dn-pattern: uid={0},ou=users
```

---

## iam-spring-boot-starter

**必須搭配** `logon-spring-boot-starter` 一起使用。

**主要設定**（前綴 `iam.*`）：
```yaml
iam:
  enabled: true
  base-packages: com.example
```

**內建 API**（可透過設定關閉）：提供帳號、群組、權限的 CRUD 端點。

---

## web-service-spring-boot-starter（Apache CXF SOAP）

**設定**（前綴 `web.service.*`）：
```yaml
web:
  service:
    path: /ws
    service-map:
      helloService: helloServiceBean
```

---

## web-spring-boot-starter

**統一 REST 回應格式**：

在 Controller 或方法標注 `@ResponseResultBody`，回傳值自動包裝：
```json
{ "code": 200, "message": "OK", "data": { ... } }
```

**自訂錯誤碼**（實作 `IResultStatus`）：
```java
public enum MyStatus implements IResultStatus {
    NOT_FOUND(404, "資源不存在"),
    FORBIDDEN(403, "無權限");

    private final int code;
    private final String message;
    // ... 建構子與 getter
}
```

**拋出業務例外**：
```java
throw new ResultException(MyStatus.NOT_FOUND);
```

**視圖路徑規則**：
- 回傳 `"th/index"` → `/WEB-INF/th/index.html`（prefix=`/WEB-INF/` + viewName + suffix=`.html`）
- JSP：回傳 `"jsp/index"` → `/WEB-INF/jsp/index.jsp`
