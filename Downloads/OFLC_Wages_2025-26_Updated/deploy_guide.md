# OFLC薪资查询系统 - 部署指南

## 🌐 部署选项

### 方案1：免费云平台部署（推荐新手）

#### 1. Heroku 部署
**优点：** 简单易用，免费额度
**缺点：** 免费额度有限，应用会休眠

**步骤：**
1. 注册 [Heroku](https://heroku.com) 账号
2. 安装 Heroku CLI
3. 在项目目录运行：
```bash
heroku create your-app-name
git add .
git commit -m "Initial deployment"
git push heroku main
```

#### 2. Railway 部署
**优点：** 免费额度，简单部署
**缺点：** 免费额度有限

**步骤：**
1. 注册 [Railway](https://railway.app) 账号
2. 连接 GitHub 仓库
3. 选择项目，Railway 会自动检测并部署

#### 3. Render 部署
**优点：** 免费额度，自动部署
**缺点：** 免费额度有限

**步骤：**
1. 注册 [Render](https://render.com) 账号
2. 连接 GitHub 仓库
3. 选择 "Web Service"
4. 使用提供的 `render.yaml` 配置

### 方案2：VPS部署（推荐生产环境）

#### 1. DigitalOcean
**优点：** 稳定，性能好
**缺点：** 需要付费

**步骤：**
1. 注册 [DigitalOcean](https://digitalocean.com) 账号
2. 创建 Droplet（Ubuntu 20.04）
3. 按照 VPS 部署指南操作

#### 2. 其他VPS提供商
- Linode
- Vultr
- AWS EC2
- Google Cloud Platform

## 🚀 快速部署步骤

### 使用 Heroku（最简单）

1. **准备代码**
```bash
# 确保所有文件都在项目目录中
ls -la
# 应该看到：app.py, requirements.txt, Procfile, templates/, static/, *.csv
```

2. **安装 Heroku CLI**
```bash
# macOS
brew install heroku/brew/heroku

# 或下载安装包
# https://devcenter.heroku.com/articles/heroku-cli
```

3. **部署到 Heroku**
```bash
# 登录 Heroku
heroku login

# 创建应用
heroku create your-app-name

# 部署
git add .
git commit -m "Deploy OFLC Wage Query System"
git push heroku main

# 查看应用
heroku open
```

### 使用 Railway（推荐）

1. **准备代码**
   - 确保所有文件都在项目目录中
   - 确保有 `railway.json` 配置文件

2. **部署步骤**
   - 访问 [Railway](https://railway.app)
   - 点击 "New Project"
   - 选择 "Deploy from GitHub repo"
   - 选择你的仓库
   - Railway 会自动检测并部署

### 使用 Render

1. **准备代码**
   - 确保所有文件都在项目目录中
   - 确保有 `render.yaml` 配置文件

2. **部署步骤**
   - 访问 [Render](https://render.com)
   - 点击 "New +"
   - 选择 "Web Service"
   - 连接 GitHub 仓库
   - 选择项目
   - 点击 "Create Web Service"

## 🔧 环境配置

### 环境变量
```bash
FLASK_ENV=production
PORT=8080
```

### 数据库初始化
应用会自动创建 SQLite 数据库并导入数据，首次启动可能需要几分钟。

## 📊 性能优化

### 免费平台限制
- **Heroku**: 免费应用会休眠，首次访问较慢
- **Railway**: 免费额度有限，超出后需要付费
- **Render**: 免费额度有限，超出后需要付费

### 生产环境建议
1. 使用付费VPS获得更好性能
2. 考虑使用PostgreSQL替代SQLite
3. 添加缓存机制
4. 使用CDN加速静态资源

## 🔒 安全考虑

1. **环境变量**
   - 不要将敏感信息硬编码
   - 使用环境变量存储配置

2. **数据库安全**
   - 定期备份数据
   - 考虑使用更安全的数据库

3. **HTTPS**
   - 生产环境必须使用HTTPS
   - 大多数云平台自动提供SSL证书

## 🐛 故障排除

### 常见问题

1. **应用无法启动**
   - 检查 `requirements.txt` 是否完整
   - 检查 `Procfile` 或启动命令是否正确
   - 查看日志：`heroku logs --tail`

2. **数据库初始化失败**
   - 检查CSV文件是否存在
   - 检查文件权限
   - 查看应用日志

3. **静态文件无法加载**
   - 检查 `static/` 目录结构
   - 检查文件路径

### 日志查看
```bash
# Heroku
heroku logs --tail

# Railway
# 在 Railway 控制台查看日志

# Render
# 在 Render 控制台查看日志
```

## 📞 技术支持

如果遇到问题，可以：
1. 查看平台文档
2. 检查应用日志
3. 联系平台技术支持
4. 查看项目README.md

## 🎯 推荐部署方案

**新手推荐：** Railway 或 Render
**生产环境：** DigitalOcean VPS
**企业级：** AWS 或 Google Cloud Platform
