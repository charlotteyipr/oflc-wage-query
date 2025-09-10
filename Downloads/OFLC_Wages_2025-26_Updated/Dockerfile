# 使用官方Python运行时作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 复制requirements文件并安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建非root用户
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# 暴露端口
EXPOSE 8080

# 设置环境变量
ENV FLASK_ENV=production
ENV PORT=8080

# 启动命令
CMD ["python3", "app.py"]
