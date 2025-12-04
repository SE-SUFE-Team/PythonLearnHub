# Docker 部署指南

本文档详细介绍了如何使用 Docker 和 Docker Compose 在服务器上部署 PythonLearnHub 应用。

## 1. 概述

本项目使用 Docker 进行容器化部署，以确保开发、测试和生产环境的一致性。通过 `docker-compose`，我们可以轻松地管理应用服务、网络和数据卷。

## 2. 环境要求

-   **Docker**: [安装指南](https://docs.docker.com/engine/install/)
-   **Docker Compose**: [安装指南](https://docs.docker.com/compose/install/)

## 3. 部署文件详解

为了实现 Docker 部署，项目中添加了以下几个关键文件：

### 3.1 `Dockerfile`

该文件定义了如何构建应用的 Docker 镜像。主要步骤包括：

-   **基础镜像**: 使用官方的 `python:3.11-slim` 作为基础，这是一个轻量级的 Python 运行时环境。
-   **工作目录**: 在容器内创建 `/app` 目录作为应用的工作空间。
-   **安装依赖**: 复制 `requirements.txt` 文件并使用 `pip` 安装所有必需的 Python 包。
-   **复制源码**: 将项目的所有文件复制到容器的 `/app` 目录中。
-   **暴露端口**: 声明容器将监听 `5000` 端口。
-   **启动命令**: 使用 `gunicorn` 作为生产环境的 WSGI 服务器来启动 Flask 应用。它配置了 4 个工作进程，并监听所有网络接口的 `5000` 端口。

```dockerfile
# 使用官方 Python 镜像作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 将依赖文件复制到工作目录
COPY ../requirements.txt .

# 安装项目依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件到工作目录
COPY .. .

# 暴露端口
EXPOSE 5000

# 运行 Gunicorn 服务器
CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:5000", "app:app"]
```

### 3.2 `docker-compose.yml`

此文件用于定义和运行多容器 Docker 应用。在本项目中，我们只定义了一个服务 `web`：

-   **`build: .`**: 指示 Docker Compose 使用当前目录下的 `Dockerfile` 来构建镜像。
-   **`ports: - "5000:5000"`**: 将主机的 `5000` 端口映射到容器的 `5000` 端口。
-   **`volumes: - .:/app`**: 将当前目录挂载到容器的 `/app` 目录，这样您在主机上修改代码后，容器内的应用会自动更新（`gunicorn` 需要重启才能加载新代码）。

```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - .:/app
```

### 3.3 `.dockerignore`

这个文件的作用类似于 `.gitignore`，它告诉 Docker 在构建镜像时忽略哪些文件和目录。这有助于减小镜像体积并加快构建速度。

```
# 忽略 __pycache__ 目录
__pycache__/

# 忽略 .idea 目录
.idea/

# 忽略 .git 目录
.git/

# 忽略 .gitignore 文件
.gitignore

# 忽略 README.md 文件
README.md
```

### 3.4 `.env`

该文件用于存储环境变量，`docker-compose` 会自动加载它。将敏感信息或配置与代码分离是一种最佳实践。

```dotenv
SECRET_KEY=my-secret-key
DATABASE_URL=sqlite:///database.db
```

## 4. 应用配置 (`app.py`)

为了适应 Docker 部署，`app.py` 中的配置项已修改为从环境变量中读取，并提供了默认值：

```python
# 从环境变量获取密钥，如果未设置则使用默认值
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'python_learning_platform_2024')

# 从环境变量获取数据库连接，如果未设置则使用默认的 SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///database.db')
```

## 5. 部署步骤

请按照以下步骤在您的服务器上部署应用：

1.  **克隆或上传项目**: 将整个项目文件夹上传到您的服务器。

2.  **进入项目目录**:
    ```bash
    cd /path/to/your/PythonLearnHub
    ```

3.  **构建并启动容器**:
    运行以下命令，Docker Compose 将会读取 `docker-compose.yml` 文件，自动构建镜像并启动容器。
    `--build` 标志会强制重新构建镜像。
    `-d` 标志会让容器在后台运行。

    ```bash
    docker-compose up --build -d
    ```

4.  **查看容器状态**:
    您可以使用以下命令检查容器是否正在运行：
    ```bash
    docker-compose ps
    ```
    或者查看容器的实时日志：
    ```bash
    docker-compose logs -f
    ```

## 6. 访问应用

容器成功运行后，您可以通过浏览器访问它：

-   **URL**: `http://<服务器的公网IP地址或域名>:5000`

**重要提示**: 请确保您服务器的防火墙或云服务商的安全组规则已允许外部访问 `5000` 端口。

## 7. 停止应用

如果您需要停止应用，可以运行以下命令：

```bash
docker-compose down
```
该命令会停止并移除由 `docker-compose up` 创建的容器和网络。

## 8. 数据库

本项目使用 SQLite 数据库。数据库文件 `database.db` 位于 `instance` 目录下。由于我们在 `docker-compose.yml` 中配置了卷挂载 (`.:/app`)，数据库文件会持久化存储在您的主机上，即使容器被删除也不会丢失数据。

