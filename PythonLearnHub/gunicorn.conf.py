# Gunicorn配置文件
bind = "0.0.0.0:8000"  # 绑定地址和端口
workers = 4  # 工作进程数
worker_class = "sync"  # 工作模式
worker_connections = 1000  # 每个worker的连接数
timeout = 30  # 超时时间
keepalive = 2  # 保持连接时间

# 日志配置
accesslog = "logs/access.log"  # 访问日志
errorlog = "logs/error.log"    # 错误日志
loglevel = "info"              # 日志级别

# 进程管理
max_requests = 1000           # 每个worker处理请求数上限
max_requests_jitter = 100     # 随机抖动
preload_app = True           # 预加载应用

# 安全配置
user = None                  # 运行用户（生产环境建议设置）
group = None                 # 运行组
tmp_upload_dir = None        # 临时上传目录

# 性能优化
worker_tmp_dir = "/dev/shm"  # worker临时目录（Linux）