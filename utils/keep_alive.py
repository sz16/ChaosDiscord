from threading import Thread
from flask import Flask, request, jsonify, Response, render_template_string
import os
import json
import base64
import random
from datetime import datetime
from hashlib import sha256

import logging
from . import database

logger = logging.getLogger(__name__)

app = Flask(__name__)
data_path = 'data.json'
log_path = 'bot.log'
debug_path = 'debug.log'

@app.route('/')
def index():
    # Get today's date
    today = datetime.now().strftime('%Y-%m-%d %H:%M')
    return f"Alive at {today}"

@app.route('/data')
def send_data():
    try:
        data = database.getDatabase()
        data = json.dumps(data, indent=4, ensure_ascii=False)
        return Response(data, mimetype='application/json')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/debug')
def send_debug():
    if os.path.exists(debug_path):
        with open(debug_path, 'r', encoding='utf-8') as f:
            data = f.read()
        return Response(data, mimetype='text/plain')
    else:
        return jsonify({"error": "Log file not found"}), 404

@app.route('/log')
def send_log():
    if os.path.exists(log_path):
        with open(log_path, 'r', encoding='utf-8') as f:
            data = f.read()
        return Response(data, mimetype='text/plain')
    else:
        return jsonify({"error": "Log file not found"}), 404

# Giao diện chỉnh sửa JSON
@app.route('/edit', methods=['GET'])
def edit_logs():
    data = database.getDatabase()
    data = json.dumps(data, indent=4, ensure_ascii=False)
    html = f"""
    <h2>Edit data.json</h2>
    <form action="/update_logs" method="post">
        <textarea name="json_data" rows="20" cols="80">{data}</textarea><br>
        <button type="submit">Save</button>
    </form>
    """
    return render_template_string(html)

def randomData():
    char = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return ''.join(random.choice(char) for i in range(36))
    
@app.route('/special', methods=['POST'])
def special():
    data = request.get_json().get('data',randomData())
    return sha256(base64.b64encode(json.dumps(data).encode('utf-8'))).hexdigest()

# Nhận dữ liệu POST và lưu vào file
@app.route('/update_logs', methods=['POST'])
def update_logs():
    logger.debug("Update data.json")
    data = request.form.get("json_data")
    if not data:
        return "No data received", 400
    try:
        parsed = json.loads(data)  # kiểm tra JSON hợp lệ
    except Exception as e:
        return f"Invalid JSON: {e}", 400
    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump(parsed, f, ensure_ascii=False, indent=4)
    database.setDatabase(parsed)
    return "Saved successfully! <a href='/edit'>Back</a>"

def run(): 
    app.run(host='0.0.0.0', port=8080) 
    
def keep_alive(): 
    t = Thread(target=run) 
    t.daemon = True 
    t.start()

if __name__ == "__main__": 
    keep_alive()
    while True:
        pass

