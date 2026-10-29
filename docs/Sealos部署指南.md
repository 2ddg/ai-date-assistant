# 🐳 Sealos 部署指南（国内可访问，无需本地 Docker）

> 部署思路：GitHub Actions 已自动把本项目构建成镜像并推到 `ghcr.io/2ddg/i-date-assistant:latest`。
> Sealos（国内平台）只需拉取这个镜像即可，全程浏览器操作、国内打开快。

## 步骤

### 1. 注册 Sealos
- 打开 https://cloud.sealos.run → 手机号注册（免费，国内无需梯子）→ 实名认证

### 2. 创建 MySQL 数据库
- 桌面点「**数据库**」→ 创建 **MySQL**（免费额度的 `postgres`/`mongodb` 或 mysql，选 MySQL 相关模板）
- 数据库就绪后，记录它的**连接地址 / 用户名 / 密码 / 库名**

### 3. 创建应用（拉取镜像）
- 桌面点「**应用管理**」→ 新建应用
- 镜像填：`ghcr.io/2ddg/i-date-assistant:latest`
  - 如果拉取提示需要凭据，在应用的环境变量或 Sealos「我的密钥」里加 `GHCR_TOKEN`（用你在 GitHub 生成的 Personal Access Token，read:packages 权限）
- 端口填写：容器端口 `8080`，对外暴露
- **环境变量**（参考下方表格）

### 4. 配环境变量

| 变量 | 值 |
|---|---|
| `MYSQL_HOST` | 第 2 步 MySQL 的连接地址（Sealos 内网域名，如 `mysql-xxx.ns-xxx.svc.cluster.local`） |
| `MYSQL_PORT` | `3306` |
| `MYSQL_USER` | MySQL 用户名 |
| `MYSQL_PASSWORD` | MySQL 密码 |
| `MYSQL_DATABASE` | MySQL 库名 |
| `JWT_SECRET_KEY` | 一长串随机字符（必填） |
| `ZHIPU_API_KEY` | 智谱 `K-xxx`（AI 对话用，open.bigmodel.cn 免费注册） |

### 5. 部署 + 绑域名
- 保存部署，等状态变 Running
- 应用「绑定域名」→ 生成 `xxx.sealos.run` 或自定义域名 → 拿到在线网址
- 打开网址：能注册/登录、AI 对话、穿搭、地点 = 成功

### 6. 发给 HR
```
大三在读；在线演示：https://xxx；代码仓库：https://github.com/2ddg/i-date-assistant
自研 Web 全栈项目（Vue3 + FastAPI + MySQL，GitHub Actions 自动构建镜像），含登录鉴权、AI 对话、图片上传、地图 POI，可在线体验。
```

## ⚠️ 常见坑
- **登录 500** → 查 MySQL 变量，尤其 `MYSQL_HOST` 要用 Sealos 数据库服务给的内网域名
- **AI 对话失败** → `ZHIPU_API_KEY` 未填或错误
- **拉镜像慢/失败** → GHCR 在 Sealos 一般可访问；不行就换用 GitHub 的 `ghcr.io` 镜像或阿里云镜像加速
- **免费额度**：Sealos 每月送一定量的 CPU/内存/流量，本项目演示用量很小，足够用