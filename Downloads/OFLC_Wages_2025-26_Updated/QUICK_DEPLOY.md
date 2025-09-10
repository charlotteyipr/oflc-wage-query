# 🚀 快速部署指南

## 立即开始部署

### 最简单的方法：使用 Railway（推荐）

1. **访问 [Railway.app](https://railway.app)**
2. **注册账号并登录**
3. **点击 "New Project"**
4. **选择 "Deploy from GitHub repo"**
5. **连接你的GitHub仓库**
6. **Railway会自动检测并部署**

### 或者使用 Heroku

1. **安装 Heroku CLI**
```bash
# macOS
brew install heroku/brew/heroku
```

2. **运行部署脚本**
```bash
./deploy.sh
```

3. **选择选项1（Heroku）**
4. **输入应用名称**
5. **等待部署完成**

## 📋 部署前检查清单

- ✅ `app.py` - 主应用文件
- ✅ `requirements.txt` - Python依赖
- ✅ `templates/index.html` - 前端模板
- ✅ `ALC_Export.csv` - 薪资数据
- ✅ `Geography.csv` - 地理数据
- ✅ `oes_soc_occs.csv` - 职业数据
- ✅ `Procfile` - Heroku配置
- ✅ `railway.json` - Railway配置
- ✅ `render.yaml` - Render配置

## 🌐 部署后访问

部署完成后，你会得到一个公开的URL，例如：
- `https://your-app-name.railway.app`
- `https://your-app-name.herokuapp.com`
- `https://your-app-name.onrender.com`

## 🔧 环境变量

应用会自动使用以下环境变量：
- `PORT` - 端口号（自动设置）
- `FLASK_ENV` - 环境模式（生产环境）

## 📊 首次启动

首次部署时，应用会自动：
1. 创建SQLite数据库
2. 导入CSV数据
3. 建立索引
4. 启动Web服务

这个过程可能需要2-5分钟，请耐心等待。

## 🎯 推荐部署平台

| 平台 | 免费额度 | 部署难度 | 推荐度 |
|------|----------|----------|--------|
| Railway | 500小时/月 | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| Render | 750小时/月 | ⭐⭐ | ⭐⭐⭐⭐ |
| Heroku | 550小时/月 | ⭐⭐⭐ | ⭐⭐⭐ |

## 🆘 遇到问题？

1. **查看详细部署指南**: `deploy_guide.md`
2. **检查应用日志**: 在平台控制台查看
3. **运行本地测试**: `python3 app.py`
4. **检查依赖**: `pip3 install -r requirements.txt`

## 🎉 部署成功！

部署成功后，你的OFLC薪资查询系统就可以被全世界的用户访问了！

### 功能特性
- ✅ 三种查询模式
- ✅ 中英文双语支持
- ✅ 模糊搜索和自动完成
- ✅ 响应式设计
- ✅ 年薪显示
- ✅ 优化的地区查询

### 使用方式
用户可以通过以下方式使用：
1. 根据职位名称查询薪资
2. 根据薪资范围查询职位
3. 根据地区查询薪资水平
4. 支持县/镇级别搜索
5. 中英文界面切换
