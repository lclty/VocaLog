from flask import Blueprint, jsonify, request
from database import get_db
from services import parse_singers_txt, save_all_singers, open_local_folder
import json
from datetime import datetime

api = Blueprint('api', __name__)

# --- 歌手相关 ---
@api.route('/singers', methods=['GET'])
def get_singers():
    return jsonify(parse_singers_txt())

@api.route('/singers', methods=['POST'])
def save_singers():
    # 现在前端发送完整的歌手列表给我们，我们直接覆盖文件
    # 这样既支持添加，也支持修改
    try:
        save_all_singers(request.json)
        return jsonify({"message": "saved"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- 项目相关 ---
@api.route('/projects', methods=['GET'])
def get_projects():
    with get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM projects ORDER BY id DESC")
        rows = c.fetchall()
        results = []
        for r in rows:
            item = dict(r)
            # 解析 JSON 字段，如果解析失败或为空，返回默认值
            item['staff'] = json.loads(item['staff']) if item['staff'] else {}
            item['progress'] = json.loads(item['progress']) if item['progress'] else {}
            # singer 现在也是 JSON 列表
            try:
                item['singer'] = json.loads(item['singer']) if item['singer'] else []
            except:
                item['singer'] = [] # 兼容旧数据防止报错
            results.append(item)
        return jsonify(results)

@api.route('/projects', methods=['POST'])
def save_project():
    data = request.json
    
    # 序列化所有 JSON 字段
    staff_json = json.dumps(data.get('staff', {}))
    progress_json = json.dumps(data.get('progress', {}))
    # 将歌手列表序列化
    singer_json = json.dumps(data.get('singer', [])) 
    
    with get_db() as conn:
        c = conn.cursor()
        if 'id' in data and data['id']: # 更新
            c.execute("""UPDATE projects SET title=?, singer=?, path=?, staff=?, progress=? WHERE id=?""",
                      (data['title'], singer_json, data.get('path', ''), staff_json, progress_json, data['id']))
        else: # 新建
            # 新建时只填 Title，其他给默认空值
            c.execute("""INSERT INTO projects (title, singer, status, path, staff, progress) VALUES (?, ?, 'Doing', ?, ?, ?)""",
                      (data['title'], singer_json, '', staff_json, progress_json))
        conn.commit()
    return jsonify({"message": "success"}), 201

@api.route('/projects/<int:pid>', methods=['DELETE'])
def delete_project(pid):
    with get_db() as conn:
        conn.execute("DELETE FROM projects WHERE id=?", (pid,))
        conn.commit()
    return jsonify({"message": "deleted"}), 200

# --- 工具 ---
@api.route('/open-folder', methods=['POST'])
def open_folder():
    path = request.json.get('path')
    try:
        open_local_folder(path)
        return jsonify({"message": "opened"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400