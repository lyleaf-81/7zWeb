import os
import re
import time
import uuid
import logging
import subprocess
from pathlib import Path
from threading import Thread, Lock
from collections import defaultdict
from flask import Flask, jsonify, request
from werkzeug.utils import secure_filename
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:8080", "allowed_headers": ["Content-Type"]}})
app.config['UPLOAD_FOLDER'] = '/mnt'
tasks = {}
tasks_lock = Lock()
progress_re = re.compile(r'(\d+)%')
volume_re = re.compile(r'\.(part\d+|z\d{2}|7z\.\d{3}|r\d{2}|001)$', re.IGNORECASE)

def build_7z_command(file_path, is_volume, password):
    """构造7z解压命令"""
    cmd = ['7z', 'x', '-bsp1', '-bb1', '-y']

    if is_volume:
        # 分卷包处理（例如：filename.7z.001）
        if file_path.suffix.lower() == '.001':
            base_name = file_path.stem
            cmd.append(f'{base_name}.*')
        else:
            raise ValueError("分卷包必须以.001结尾")
    else:
        cmd.append(str(file_path))

    cmd += [
        f'-p{password}',
        f'-o{file_path.parent}',
        '-bse2',  # 错误输出到stderr
        '-scsUTF-8'  # 强制使用UTF-8编码
    ]
    return cmd

class ExtractionTask:
    def __init__(self, task_id, filename):
        self.task_id = task_id
        self.filename = filename
        self.status = 'waiting'
        self.progress = 0
        self.output = []
        self.start_time = time.time()


def validate_directory(path_param):
    """安全目录验证"""
    # 路径标准化处理
    base_dir = Path(app.config['UPLOAD_FOLDER']).resolve()
    
    requested_path = (base_dir / path_param).resolve()
    
    # 路径越界检查和类型验证
    if not requested_path.is_relative_to(base_dir) or re.search(r'\.\.|//', str(requested_path)):
        raise ValueError("非法路径访问")
    if not requested_path.exists() or not requested_path.is_dir():
        raise ValueError("请求的不是有效目录")

    # 检查符号链接
    if any(p.is_symlink() for p in requested_path.parents):
        raise ValueError("路径包含不安全符号链接")

    return requested_path

def extract_worker(task_id, file_path, password):
    try:
        with tasks_lock:
            tasks[task_id].status = 'running'

        # 检测是否为分卷包
        is_volume = False
        if volume_re.search(file_path.name):
            is_volume = True
            if not file_path.exists():
                raise FileNotFoundError("主分卷文件不存在")

        cmd = build_7z_command(file_path, is_volume, password)

        # 添加调试日志
        with tasks_lock:
            tasks[task_id].output.append(f'执行命令: {" ".join(cmd)}')

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            cwd=str(file_path.parent),  # 设置工作目录
            errors='replace'  # 处理编码错误
        )

        # 实时读取输出
        while True:
            line = process.stdout.readline()
            err_line = process.stderr.readline()
            if not line and not err_line and process.poll() is not None:
                break

            # 处理标准输出
            if line:
                with tasks_lock:
                    tasks[task_id].output.append(line.strip())
                if match := progress_re.search(line):
                    with tasks_lock:
                        tasks[task_id].progress = int(match.group(1))

            # 处理错误输出
            if err_line:
                with tasks_lock:
                    tasks[task_id].output.append(f"[ERROR] {err_line.strip()}")

        exit_code = process.poll()
        with tasks_lock:
            if exit_code == 0:
                tasks[task_id].status = 'success'
                tasks[task_id].progress = 100
            else:
                tasks[task_id].status = 'error'

    except Exception as e:
        with tasks_lock:
            tasks[task_id].status = 'error'
            tasks[task_id].output.append(f"系统错误: {str(e)}")

def process_volume_files(target_dir):
    """处理目标目录内的分卷压缩文件分组"""
    vol_files = defaultdict(list)
    extensions = ('.7z', '.zip', '.rar', '.001', '.002', '.z01', '.z02', '.r00')

    for f in target_dir.iterdir():
        if f.suffix.lower() not in extensions or not f.is_file():
            continue

        base_name = volume_re.sub('', f.name)
        if base_name != f.name:
            vol_files[base_name].append(f)

    return [
        {
            'name': f"{base_name}（分卷包）",
            'size': sum(p.stat().st_size for p in sorted_parts),
            'mtime': max(p.stat().st_mtime for p in sorted_parts),
            'is_volume': True,
            'base_name': base_name,
            'part_count': len(sorted_parts),
            'part_files': [p.name for p in sorted(sorted_parts, key=lambda x: x.name)]
        }
        for base_name, parts in vol_files.items()
        if len(sorted_parts := sorted(parts, key=lambda x: x.name)) > 1
    ]

@app.route('/api/delete', methods=['POST'])
def delete_item():
    """安全删除文件/目录接口"""
    try:
        data = request.json
        # 校验必要参数
        if 'path' not in data or 'item_type' not in data:
            return jsonify({"error": "缺少必要参数"}), 400

        target_path = validate_path(data['path'])
        item_type = data['item_type']

        # 执行删除操作
        if item_type == 'file':
            if not target_path.is_file():
                raise ValueError("目标不是文件")
            target_path.unlink()  # 删除文件
        elif item_type == 'directory':
            if not target_path.is_dir():
                raise ValueError("目标不是目录")
            if any(target_path.iterdir()):
                raise ValueError("目录非空无法删除")
            target_path.rmdir()  # 删除空目录
        else:
            raise ValueError("无效的操作类型")

        return jsonify({"success": True, "message": "删除成功"})

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        logging.error(f"删除操作错误: {str(e)}")
        return jsonify({"error": "删除失败"}), 500


def validate_path(relative_path):
    """增强型路径验证"""
    base_dir = Path(app.config['UPLOAD_FOLDER']).resolve()
    target_path = (base_dir / relative_path).resolve()

    # 防止路径穿越
    if not target_path.is_relative_to(base_dir):
        raise ValueError("非法路径访问")

    # 检查是否存在
    if not target_path.exists():
        raise ValueError("目标不存在")

    return target_path


@app.route('/api/files')
def list_files():
    """优化的文件列表接口（不递归子目录）"""
    try:
        req_path = request.args.get('path', '').lstrip('/')
        current_dir = validate_directory(req_path)

        directories = []
        normal_files = []

        for item in current_dir.iterdir():
            if item.is_dir():
                # 仅统计直接文件大小（不递归）
                dir_files = [f for f in item.iterdir() if f.is_file()]
                directories.append({
                    'name': item.name,
                    'size': sum(f.stat().st_size for f in dir_files),
                    'file_count': len(dir_files),
                    'mtime': item.stat().st_mtime,
                    'type': 'directory'
                })
            elif item.is_file():
                # 仅显示压缩文件
                if item.suffix.lower() in ('.zip', '.7z', '.rar'):
                    normal_files.append({
                        'name': item.name,
                        'size': item.stat().st_size,
                        'mtime': item.stat().st_mtime,
                        'type': 'file'
                    })

        return jsonify({
            'currentPath': str(current_dir.relative_to(app.config['UPLOAD_FOLDER'])),
            'directories': sorted(directories, key=lambda x: x['mtime'], reverse=True),
            'files': {
                'singleFiles': sorted(normal_files, key=lambda x: x['mtime'], reverse=True),
                'volumeGroups': process_volume_files(current_dir)
            }
        })

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        logging.error(f"文件列表错误: {str(e)}")
        return jsonify({"error": "服务器错误"}), 500



@app.route('/api/extract', methods=['POST'])
def start_extraction():
    """启动解压任务"""
    data = request.json
    base_dir = Path(app.config['UPLOAD_FOLDER']).resolve()
    file_path = (base_dir / data['filename']).resolve()
    print('base_dir',base_dir)
    print('requested_path',file_path)
    # try:
    #     file_path = validate_directory(data['filename'])
    # except ValueError:
    #     return jsonify({"error": "非法文件名"}), 400

    task_id = str(uuid.uuid4())
    password = data.get('password', '')

    with tasks_lock:
        tasks[task_id] = ExtractionTask(task_id, data['filename'])

    Thread(
        target=extract_worker,
        args=(task_id, file_path, password),
        daemon=True
    ).start()

    return jsonify({
        "task_id": task_id,
        "status_url": f"/api/tasks/{task_id}"
    }), 202


@app.route('/api/tasks')
def list_tasks():
    """列出所有解压任务"""
    with tasks_lock:
        return jsonify([
            {
                "id": t.task_id,
                "filename": t.filename,
                "status": t.status,
                "progress": t.progress,
                "start_time": int(t.start_time),
                "logs": t.output[-10:]  # 最近10条日志
            }
            for t in tasks.values()
        ])


@app.route('/api/tasks/<task_id>')
def get_task(task_id):
    """获取单个任务详情"""
    with tasks_lock:
        task = tasks.get(task_id)
        if not task:
            return jsonify({"error": "任务不存在"}), 404

        return jsonify({
            "id": task.task_id,
            "filename": task.filename,
            "status": task.status,
            "progress": task.progress,
            "logs": task.output[-10:]
        })

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(host='0.0.0.0', port=5000)
