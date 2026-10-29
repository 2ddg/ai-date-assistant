# 🚂 Railway 部署指南（最快，全程浏览器操作，无需本地 Docker）

> 仓库根目录已配 `Dockerfile`，Railway 导入 GitHub 后自动构建前端 + 后端。
> 需要科学上网（梯子）操作 Railway；部署完的网址国内可直接打开（速度一般，能开）。

## 步骤

### 1. 注册并登录
- 打开 https://railway.com
- 用 Google / GitHub 账号注册登录（邮箱也行；不要用刚被拦截的方式，用 Google 最稳）

### 2. 从 GitHub 拉取项目
- 首页点 **New Project** → **Deploy from GitHub repo** → 授权 GitHub → 选 **`2ddg/i-date-assistant`**
- Railway 自动识别 `Dockerfile` 开始构建（首次 3-5 分钟）

### 3. 创建 MySQL 并配数据库环境变量
- 服务列表右上角 **+ New** → **Database** → 选 **MySQL**（免费模板）
- 等 MySQL Ready，打开它的 **Variables** 面板，复制连接信息
- 回到**后端服务**（显示构建日志那个）→ **Variables** 填入：

| 变量 | 值 |
|---|---|
| `MYSQL_HOST` | MySQL 服务内部域名（如 `mysql.railway.internal`，从 MySQL Variables 面板里拿） |
| `MYSQL_PORT` | `3306` |
| `MYSQL_USER` | `root` |
| `MYSQL_PASSWORD` | MySQL 面板里的密码 |
| `MYSQL_DATABASE` | Railway MySQL 变量里的 `MYSQLDATABASE` 值（形如 `railway`） |
| `JWT_SECRET_KEY` | 随便一串长随机字符（登录加密，必填） |
| `ZHIPU_API_KEY` | 智谱 `K-xxx`（AI 对话用，去 open.bigmodel.cn 免费注册拿） |

> 填完 Variables，Railway 会自动重新部署一次。

### 4. 生成网址
- 后端服务 → **Settings** → **Networking** → **Generate Domain**
- 得到一个 `https://xxx.up.railway.app`，打开它：能注册/登录、AI 对话、穿搭评价、约会地点 = 成功

### 5. 发给 HR
```
大三在读；在线演示：https://xxx.up.railway.app；代码仓库：https://github.com/2ddg/i-date-assistant
自己从 0 做的 Web 全栈项目（Vue3 前端 + FastAPI 后端 + MySQL），含登录鉴权、AI 对话、图片上传、地图 POI，可在线直接体验。
```

## ⚠️ 常见问题
- **登录 500**：MySQL 变量没配对（尤其 `MYSQL_HOST` 要填 Railway MySQL 的内部域名）
- **AI 对话没反应**：`ZHIPU_API_KEY` 未填/失效
- **重启后数据没丢**：数据在 Railway MySQL 服务里，后端服务重启不丢数据
- **免费额度**：新用户有 $5 试用额度（够本项目跑很久），到期前记得看用量、也可随时取消服务避免超费