#!/usr/bin/env python3
"""
Python学习平台性能监控脚本
监控应用状态、资源使用情况和服务健康状态
"""

import requests
import psutil
import time
import json
from datetime import datetime
import sys
import os

# 配置
APP_URL = "http://localhost:5555"
CHECK_INTERVAL = 30  # 检查间隔（秒）
LOG_FILE = "logs/monitor.log"

def log_message(message, level="INFO"):
    """记录日志消息"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] {message}"
    print(log_entry)
    
    # 确保日志目录存在
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry + "\n")

def check_app_health():
    """检查应用健康状态"""
    try:
        response = requests.get(APP_URL, timeout=10)
        if response.status_code == 200:
            return True, f"应用正常运行 (状态码: {response.status_code})"
        else:
            return False, f"应用响应异常 (状态码: {response.status_code})"
    except requests.exceptions.RequestException as e:
        return False, f"应用无法访问: {str(e)}"

def get_system_stats():
    """获取系统资源使用情况"""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        "cpu_percent": cpu_percent,
        "memory_percent": memory.percent,
        "memory_available": memory.available / (1024**3),  # GB
        "disk_percent": disk.percent,
        "disk_free": disk.free / (1024**3)  # GB
    }

def get_process_stats():
    """获取应用进程统计信息"""
    python_processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'cmdline']):
        try:
            if proc.info['name'] == 'python' or proc.info['name'] == 'python3':
                cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                if 'app.py' in cmdline or 'gunicorn' in cmdline:
                    python_processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cpu_percent': proc.info['cpu_percent'],
                        'memory_percent': proc.info['memory_percent'],
                        'cmdline': cmdline
                    })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    return python_processes

def check_log_files():
    """检查日志文件大小"""
    log_info = {}
    
    log_files = [
        "logs/access.log",
        "logs/error.log",
        "logs/monitor.log"
    ]
    
    for log_file in log_files:
        if os.path.exists(log_file):
            size = os.path.getsize(log_file) / (1024**2)  # MB
            log_info[log_file] = f"{size:.2f} MB"
        else:
            log_info[log_file] = "文件不存在"
    
    return log_info

def main():
    """主监控循环"""
    log_message("🚀 Python学习平台监控启动")
    
    try:
        while True:
            # 检查应用健康状态
            is_healthy, health_message = check_app_health()
            if is_healthy:
                log_message(f"✅ {health_message}")
            else:
                log_message(f"❌ {health_message}", "ERROR")
            
            # 获取系统统计信息
            system_stats = get_system_stats()
            log_message(f"📊 系统状态: CPU {system_stats['cpu_percent']:.1f}%, "
                       f"内存 {system_stats['memory_percent']:.1f}%, "
                       f"磁盘 {system_stats['disk_percent']:.1f}%")
            
            # 检查资源使用警告
            if system_stats['cpu_percent'] > 80:
                log_message(f"⚠️ CPU使用率过高: {system_stats['cpu_percent']:.1f}%", "WARNING")
            
            if system_stats['memory_percent'] > 80:
                log_message(f"⚠️ 内存使用率过高: {system_stats['memory_percent']:.1f}%", "WARNING")
            
            if system_stats['disk_percent'] > 90:
                log_message(f"⚠️ 磁盘空间不足: {system_stats['disk_percent']:.1f}%", "WARNING")
            
            # 获取进程信息
            processes = get_process_stats()
            if processes:
                log_message(f"🔍 发现 {len(processes)} 个相关Python进程")
                for proc in processes:
                    log_message(f"   PID {proc['pid']}: CPU {proc['cpu_percent']:.1f}%, "
                               f"内存 {proc['memory_percent']:.1f}%")
            else:
                log_message("⚠️ 未发现应用进程", "WARNING")
            
            # 检查日志文件
            log_info = check_log_files()
            for log_file, size_info in log_info.items():
                if "MB" in size_info:
                    size_mb = float(size_info.split()[0])
                    if size_mb > 100:  # 日志文件大于100MB时警告
                        log_message(f"⚠️ 日志文件过大: {log_file} ({size_info})", "WARNING")
            
            time.sleep(CHECK_INTERVAL)
            
    except KeyboardInterrupt:
        log_message("🛑 监控程序停止")
    except Exception as e:
        log_message(f"❌ 监控程序异常: {str(e)}", "ERROR")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--health":
            # 单次健康检查
            is_healthy, message = check_app_health()
            print(message)
            sys.exit(0 if is_healthy else 1)
        elif sys.argv[1] == "--stats":
            # 显示统计信息
            stats = get_system_stats()
            processes = get_process_stats()
            logs = check_log_files()
            
            print("=== 系统状态 ===")
            print(f"CPU: {stats['cpu_percent']:.1f}%")
            print(f"内存: {stats['memory_percent']:.1f}% (可用: {stats['memory_available']:.2f}GB)")
            print(f"磁盘: {stats['disk_percent']:.1f}% (可用: {stats['disk_free']:.2f}GB)")
            
            print("\n=== 进程信息 ===")
            for proc in processes:
                print(f"PID {proc['pid']}: {proc['cmdline']}")
            
            print("\n=== 日志文件 ===")
            for log_file, size in logs.items():
                print(f"{log_file}: {size}")
            
            sys.exit(0)
    
    main()