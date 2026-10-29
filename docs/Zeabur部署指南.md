# 🌐 Zeabur 一键部署指南（约 10 分钟）

> 本仓库已配好 `Dockerfile`，Zeabur 导入后自动识别，一条龙构建前端 + 后端。

## 你需要提前准备的

1. **GitHub 账号**（已有，仓库 `2ddg/i-date-assistant`）
2. **一个 MySQL 连接信息**：部署时会用到 Zeabur 自带的 MySQL 服务，免费额度内有
3. **（可选但推荐）智谱 API Key**：AI 对话功能用它，注册 [智谱开放平台 bigmodel.cn](https://open.bigmodel.cn)（免费注册送额度，拿 K 开头的 key）

## 步骤

### 1. 注册并登录 Zeabur
- 打开 https://zeabur.com 用微信/GitHub 登录，完成实名（免费）

### 2. 新建项目并从 GitHub 导入
- 点「新建项目」→「部署新服务」→ 选 **GitHub** → 授权并选择 `i-date-assistant` 仓库
- Zeabur 会自动检测 Dockerfile → 自动开始构建
- 构建时间约 3-5 分钟（先装前端依赖再装 Python）

### 3. 创建 MySQL 并配环境变量
- 在项目里点「+」→ 创建 **MySQL** 服务（免费的 `zeabur-mysql` 即可）
- 等 MySQL 就绪，把它的连接信息填到后端服务的**环境变量**里：

| 环境变量 | 填什么 |
|---|---|
| `MYSQL_HOST` | MySQL 服务内部域名（如 `mysql:3306` 或 Zeabur 给的 host） |
| `MYSQL_PORT` | `3306` |
| `MYSQL_USER` | `root`（Zeabur 默认） |
| `MYSQL_PASSWORD` | MySQL 服务给出的密码 |
| `MYSQL_DATABASE` | 新建一个库名，如 `ai_date_assistant` |
| `JWT_SECRET_KEY` | 随便一串随机字符（登录加密用，必填） |
| `ZHIPU_API_KEY` | 智谱的 `K-xxx` key（AI 对话用） |
| `BAIDU_MAP_AUTH_TOKEN` | 可选：百度地图 token（约会地点 POI 用） |

### 4. 部署完成，拿网址
- 后端服务部署成功后，Zeabur 会给一个 `https://xxx.zeabur.app` 域名
- 打开网址：能注册、登录、用 AI 对话 / 穿搭评价 / 约会地点，就成功了

### 5. 把网址发给 HR
- 投递/打招呼时附上：年级 + 在线演示地址 + GitHub 仓库地址
- 示例：
  ```
  大三在读；在线演示：https://xxx.zeabur.app；代码仓库：https://github.com/2ddg/i-date-assistant
  这是我自己从 0 做的 Web 全栈项目（前端 Vue3 + 后端 Node/Python + MySQL），
  含登录鉴权、AI 对话、图片上传/评价、地图 POI 等功能，可在演示地址直接体验。
  ```

## ⚠️ 常见坑

- **登录 500**：多半是 MySQL 环境变量没配对（尤其 `MYSQL_HOST` 在 Zeabur 里通常是服务名而非 IP）或数据库还没建表成功
- **AI 对话失败**：`ZHIPU_API_KEY` 没填或 key 失效
- **照片上传失败**：上传目录 `uploads` 会自动创建，若报权限问题在环境变量加 `MAX_UPLOAD_BYTES`
- **HTTPS**：Zeabur 默认给 HTTPS 域名，无需自己配证书