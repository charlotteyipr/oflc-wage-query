#!/bin/bash

# OFLC薪资查询系统 - 快速部署脚本

echo "🚀 OFLC薪资查询系统部署脚本"
echo "================================"

# 检查必要的文件
echo "📋 检查部署文件..."
required_files=("app.py" "requirements.txt" "templates/index.html" "ALC_Export.csv" "Geography.csv" "oes_soc_occs.csv")

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ 缺少必要文件: $file"
        exit 1
    fi
done

echo "✅ 所有必要文件检查完成"

# 选择部署平台
echo ""
echo "请选择部署平台："
echo "1) Heroku"
echo "2) Railway"
echo "3) Render"
echo "4) 本地测试"
echo "5) 退出"

read -p "请输入选择 (1-5): " choice

case $choice in
    1)
        echo "🔧 准备Heroku部署..."
        if ! command -v heroku &> /dev/null; then
            echo "❌ 请先安装Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli"
            exit 1
        fi
        
        read -p "请输入应用名称: " app_name
        if [ -z "$app_name" ]; then
            echo "❌ 应用名称不能为空"
            exit 1
        fi
        
        echo "🚀 部署到Heroku..."
        heroku create $app_name
        git add .
        git commit -m "Deploy OFLC Wage Query System"
        git push heroku main
        heroku open
        ;;
        
    2)
        echo "🔧 准备Railway部署..."
        echo "请访问 https://railway.app 并按照以下步骤："
        echo "1. 注册账号并登录"
        echo "2. 点击 'New Project'"
        echo "3. 选择 'Deploy from GitHub repo'"
        echo "4. 选择你的仓库"
        echo "5. Railway会自动检测并部署"
        echo ""
        echo "📁 确保你的代码已推送到GitHub仓库"
        ;;
        
    3)
        echo "🔧 准备Render部署..."
        echo "请访问 https://render.com 并按照以下步骤："
        echo "1. 注册账号并登录"
        echo "2. 点击 'New +'"
        echo "3. 选择 'Web Service'"
        echo "4. 连接GitHub仓库"
        echo "5. 选择项目并点击 'Create Web Service'"
        echo ""
        echo "📁 确保你的代码已推送到GitHub仓库"
        ;;
        
    4)
        echo "🔧 本地测试..."
        echo "安装依赖..."
        pip3 install -r requirements.txt
        
        echo "启动应用..."
        python3 app.py
        ;;
        
    5)
        echo "👋 退出部署脚本"
        exit 0
        ;;
        
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

echo ""
echo "✅ 部署完成！"
echo "📖 详细部署指南请查看: deploy_guide.md"
