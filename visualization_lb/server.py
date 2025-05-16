#!/usr/bin/env python3
# server.py

from flask import Flask, request, jsonify, send_from_directory, abort
import os, json, glob

app = Flask(__name__, static_folder='static', static_url_path='/static')
VIDEOS_DIR = 'videos'

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:filename>')
def serve_html_file(filename):
    filepath = os.path.join(app.static_folder, filename)
    if os.path.isfile(filepath):
        return send_from_directory(app.static_folder, filename)
    else:
        abort(404, f"{filename} not found")

# —— 静态资源托管 ——
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

# —— 列出所有视频文件名 ——
@app.route('/videos/list', methods=['GET'])
def list_videos():
    names = []
    for fn in os.listdir(VIDEOS_DIR):
        if fn.endswith('.json') and fn != 'index.json':
            names.append(fn[:-5])
    return jsonify(names)

# —— 分页并过滤视频列表 ——
@app.route('/videos', methods=['GET'])
def list_videos_paginated():
    field = request.args.get('field')
    choice = request.args.get('choice')
    # 支持多选 checklist 过滤
    choices_param = request.args.get('choices')
    choices = choices_param.split(',') if choices_param else None
    try:
        page = int(request.args.get('page', 1))
        size = int(request.args.get('size', 9))
    except ValueError:
        abort(400, "Invalid page or size")

    entries = []
    for path in glob.glob(os.path.join(VIDEOS_DIR, '*.json')):
        fname = os.path.basename(path)
        if fname == 'index.json':
            continue
        with open(path, 'r', encoding='utf-8') as f:
            obj = json.load(f)
        ls = obj.get('lighting_setup', {})
        ok = False
        if choices:
            ok = all(ls.get(opt) is True for opt in choices)
        elif choice is not None:
            ok = (ls.get(field) == choice)
        else:
            ok = (ls.get(field) is True)
        if ok:
            entries.append(obj)

    total = len(entries)
    start = (page - 1) * size
    page_items = entries[start:start + size]

    return jsonify({
        'total': total,
        'page': page,
        'size': size,
        'videos': page_items
    })

# —— 获取单条视频 JSON ——
@app.route('/videos/<video_name>.json', methods=['GET'])
def get_video(video_name):
    filepath = os.path.join(VIDEOS_DIR, f"{video_name}.json")
    if not os.path.isfile(filepath):
        abort(404, f"{video_name}.json not found")
    return send_from_directory(VIDEOS_DIR, f"{video_name}.json")

# —— 更新单条视频 JSON ——
@app.route('/videos/<video_name>.json', methods=['PUT'])
def update_video(video_name):
    filepath = os.path.join(VIDEOS_DIR, f"{video_name}.json")
    if not os.path.isfile(filepath):
        abort(404, f"{video_name}.json not found")
    new_data = request.get_json(force=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(new_data, f, indent=4, ensure_ascii=False)
    return jsonify(status='ok', message=f"{video_name}.json updated"), 200

if __name__ == '__main__':
    os.makedirs(VIDEOS_DIR, exist_ok=True)
    app.run(port=8000, debug=True)
