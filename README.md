# File Extraction Service 📂

[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://python.org)
[![Flask](https://img.shields.io/badge/flask-2.0.3-green)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/license-MIT-orange)](LICENSE)

基于Flask的7z分卷解压服务，提供安全可靠的文件管理与解压操作REST API接口。

## 🌟 功能特性

- 🛡️ 安全路径验证与目录遍历保护
- 📦 支持7z/zip/rar格式解压（含分卷包）
- ⏳ 实时解压进度跟踪与日志查看
- 🌍 跨域资源共享支持（CORS）
- 📊 文件目录可视化浏览与安全删除
- 🧵 多线程任务处理队列
- 🔑 加密压缩包解压支持

## 🚀 快速开始

### 环境要求
- Python 3.8+
- p7zip工具包
- Linux / macOS 环境

### 安装步骤
1. 安装系统依赖：
2. python依赖 
3. python app.py
```bash
sudo apt-get install p7zip-full  # Debian/Ubuntu
brew install p7zip               # macOS
pip install flask werkzeug flask-cors
python app.py
```
## 📡 API文档
- GET /api/files
- 功能：获取当前目录文件列表
- 参数：
- GET /api/files?path=subdirectory
- 响应示例：
```
{
    "currentPath": "documents",
    "directories": [
        {
            "name": "images",
            "size": 1024000,
            "file_count": 18,
            "mtime": 1678923400,
            "type": "directory"
        }
    ],
    "files": {
        "singleFiles": [
            {
                "name": "archive.zip",
                "size": 5242880,
                "mtime": 1678923500,
                "type": "file"
            }
        ],
        "volumeGroups": [
            {
                "name": "bigfile.7z（分卷包）",
                "size": 104857600,
                "part_count": 5,
                "is_volume": true
            }
        ]
    }
}

```
- POST /api/extract
- 功能：启动解压任务
- 参数：
```
{
    "filename": "path/to/archive.7z.001",
    "password": "optional_password"
}

```
- 响应示例：
```
{
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "status_url": "/api/tasks/550e8400-e29b-41d4-a716-446655440000"
}


```
## 🛡️ 安全最佳实践
### 权限控制：
1. 安装系统依赖：
```bash
# 创建专用用户
sudo useradd extractor
sudo chown -R extractor:extractor $UPLOAD_FOLDER
```
### 运行服务：
```bash
sudo -u extractor python app.py
```
- 定期清理任务记录
- 使用HTTPS加密传输
- 配置防火墙规则限制访问IP
