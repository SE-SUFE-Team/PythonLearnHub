# 使用官方 Python 镜像作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 将依赖文件复制到工作目录
COPY requirements.txt .

# 安装项目依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件到工作目录
COPY . .

# 暴露端口
EXPOSE 5000

# 运行 Gunicorn 服务器
CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:5000", "app:app"]

