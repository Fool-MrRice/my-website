from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import sqlite3
import re
import os
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import uuid
import time

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'default-secret-key-change-in-production')
app.debug = False

# 限流配置
SINGLE_IP_LIMIT = 3  # 单IP每秒最多访问次数
SINGLE_IP_COOLDOWN = 2  # 单IP冷却时间（秒）
GLOBAL_IP_LIMIT = 20  # 每秒最大不同IP访问次数
GLOBAL_IP_COOLDOWN = 1  # 全局超过IP冷却时间（秒）
TIME_WINDOW = 1  # 时间窗口（秒）

# 存储IP访问记录 {ip: [timestamp1, timestamp2, ...]}
ip_access_records = {}

# 存储冷却中的IP {ip: end_time}
cooldown_ips = {}

# 存储全局IP访问记录 [{ip: str, timestamp: float}, ...]
global_access_records = []

# 中间件：限流
def rate_limit_middleware():
    def decorator(f):
        def wrapped(*args, **kwargs):
            # 获取客户端IP
            client_ip = request.remote_addr
            current_time = time.time()
            
            # 检查IP是否在冷却中
            if client_ip in cooldown_ips:
                if current_time < cooldown_ips[client_ip]:
                    return "访问过于频繁，3秒后再试", 429
                else:
                    # 冷却时间已过，移除冷却
                    del cooldown_ips[client_ip]
            
            # 清理单IP过期的访问记录
            if client_ip in ip_access_records:
                ip_access_records[client_ip] = [t for t in ip_access_records[client_ip] if current_time - t < TIME_WINDOW]
            else:
                ip_access_records[client_ip] = []
            
            # 清理全局过期的访问记录
            global global_access_records
            global_access_records = [t for t in global_access_records if current_time - t < TIME_WINDOW]
            
            # 检查单IP访问频率
            if len(ip_access_records[client_ip]) >= SINGLE_IP_LIMIT:
                # 单IP超过限制，加入冷却
                cooldown_ips[client_ip] = current_time + SINGLE_IP_COOLDOWN
                return "访问过于频繁，3秒后再试", 429
            
            # 检查全局IP访问频率（不同IP数量）
            unique_ips = set()
            for t in global_access_records:
                # 这里简化处理，实际应该记录每个时间戳对应的IP
                # 为了准确，我们需要重构global_access_records为[{ip, timestamp}]格式
                unique_ips.add(client_ip)
            
            if len(unique_ips) >= GLOBAL_IP_LIMIT:
                # 全局超过限制，加入冷却
                cooldown_ips[client_ip] = current_time + GLOBAL_IP_COOLDOWN
                return "网络繁忙，2秒后再试", 429
            
            # 记录访问
            ip_access_records[client_ip].append(current_time)
            global_access_records.append(current_time)
            
            return f(*args, **kwargs)
        return wrapped
    return decorator

# 应用中间件到所有路由
@app.before_request
def before_request():
    # 排除静态文件路由
    if request.path.startswith('/static/'):
        return
    
    # 获取客户端IP
    client_ip = request.remote_addr
    current_time = time.time()
    
    # 检查IP是否在冷却中
    if client_ip in cooldown_ips:
        if current_time < cooldown_ips[client_ip]:
            return "访问过于频繁，3秒后再试", 429
        else:
            # 冷却时间已过，移除冷却
            del cooldown_ips[client_ip]
    
    # 清理单IP过期的访问记录
    if client_ip in ip_access_records:
        ip_access_records[client_ip] = [t for t in ip_access_records[client_ip] if current_time - t < TIME_WINDOW]
    else:
        ip_access_records[client_ip] = []
    
    # 检查单IP访问频率
    if len(ip_access_records[client_ip]) >= SINGLE_IP_LIMIT:
        # 单IP超过限制，加入冷却
        cooldown_ips[client_ip] = current_time + SINGLE_IP_COOLDOWN
        return "访问过于频繁，3秒后再试", 429
    
    # 清理全局访问记录并统计唯一IP数
    global global_access_records
    global_access_records = [rec for rec in global_access_records if current_time - rec['timestamp'] < TIME_WINDOW]
    
    # 统计当前时间窗口内的唯一IP数
    unique_ips = set(rec['ip'] for rec in global_access_records)
    
    # 检查全局IP访问频率
    if len(unique_ips) >= GLOBAL_IP_LIMIT:
        # 全局超过限制，加入冷却
        cooldown_ips[client_ip] = current_time + GLOBAL_IP_COOLDOWN
        return "网络繁忙，2秒后再试", 429
    
    # 记录访问
    ip_access_records[client_ip].append(current_time)
    global_access_records.append({'ip': client_ip, 'timestamp': current_time})


@app.template_filter('nl2br')
def nl2br_filter(s):
    if not s:
        return ''
    # 把单个换行替换成 <br>，连续两个换行保留段落
    s = str(s)
    s = re.sub(r'(\r\n|\r|\n)', '<br>', s)
    return s


# 数据库初始化确保上传目录存在
UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 允许上传的文件类型
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 数据库初始化
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # 创建内容表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            author TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建图片表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            order_index INTEGER DEFAULT 0,
            FOREIGN KEY (content_id) REFERENCES contents(id) ON DELETE CASCADE
        )
    ''')
    
    # 创建用户表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 更新或创建admin用户，密码为admin
    hashed_password_admin = generate_password_hash('admin')
    cursor.execute('SELECT id FROM users WHERE username = ?', ('admin',))
    admin_user = cursor.fetchone()
    if admin_user:
        # 更新admin用户密码
        cursor.execute('UPDATE users SET password_hash = ? WHERE username = ?', (hashed_password_admin, 'admin'))
        print("管理员用户密码已更新！用户名: admin, 密码: admin")
    else:
        # 创建admin用户
        cursor.execute('''
            INSERT INTO users (username, password_hash)
            VALUES (?, ?)
        ''', ('admin', hashed_password_admin))
        print("默认管理员用户创建成功！用户名: admin, 密码: admin")
    
    # 创建mrrice用户，密码为mrrice202
    cursor.execute('SELECT COUNT(*) FROM users WHERE username = ?', ('mrrice',))
    if cursor.fetchone()[0] == 0:
        hashed_password_mrrice = generate_password_hash('mrrice202')
        cursor.execute('''
            INSERT INTO users (username, password_hash)
            VALUES (?, ?)
        ''', ('mrrice', hashed_password_mrrice))
        print("用户mrrice创建成功！用户名: mrrice, 密码: mrrice202")
    
    conn.commit()
    conn.close()

# 首页 - 内容列表
@app.route('/')
def index():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # 获取所有内容及其首张图片
    cursor.execute('''
        SELECT c.id, c.title, c.author, c.created_at, 
               (SELECT i.filename FROM images i WHERE i.content_id = c.id ORDER BY i.order_index ASC LIMIT 1) as first_image
        FROM contents c
        ORDER BY c.created_at DESC
    ''')
    contents = cursor.fetchall()
    conn.close()
    return render_template('index.html', contents=contents)

# 内容详情页
@app.route('/content/<int:content_id>')
def content_detail(content_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # 获取内容详情
    cursor.execute('SELECT * FROM contents WHERE id = ?', (content_id,))
    content = cursor.fetchone()
    
    if content is None:
        conn.close()
        return "内容不存在", 404
    
    # 获取该内容的所有图片
    cursor.execute('SELECT filename FROM images WHERE content_id = ? ORDER BY order_index ASC', (content_id,))
    images = cursor.fetchall()
    conn.close()
    
    return render_template('content.html', content=content, images=images)

# 登录页面
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            return redirect(url_for('admin'))
        else:
            flash('用户名或密码错误！')
    
    return render_template('login.html')

# 退出登录
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# 管理后台
@app.route('/admin')
def admin():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM contents ORDER BY created_at DESC')
    contents = cursor.fetchall()
    conn.close()
    
    return render_template('admin.html', contents=contents, username=session['username'])

# API：创建内容
@app.route('/api/contents', methods=['POST'])
def create_content():
    if 'user_id' not in session:
        return jsonify({'error': '未授权访问'}), 401
    
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    
    if not title or not content:
        return jsonify({'error': '标题和内容不能为空'}), 400
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO contents (title, content, author)
        VALUES (?, ?, ?)
    ''', (title, content, session['username']))
    
    # 获取新创建的内容ID
    content_id = cursor.lastrowid
    
    conn.commit()
    conn.close()
    
    return jsonify({'message': '内容创建成功', 'id': content_id}), 201

# API：更新内容
@app.route('/api/contents/<int:content_id>', methods=['PUT'])
def update_content(content_id):
    if 'user_id' not in session:
        return jsonify({'error': '未授权访问'}), 401
    
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    
    if not title or not content:
        return jsonify({'error': '标题和内容不能为空'}), 400
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE contents 
        SET title = ?, content = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (title, content, content_id))
    conn.commit()
    conn.close()
    
    return jsonify({'message': '内容更新成功'})

# API：删除内容
@app.route('/api/contents/<int:content_id>', methods=['DELETE'])
def delete_content(content_id):
    if 'user_id' not in session:
        return jsonify({'error': '未授权访问'}), 401
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM contents WHERE id = ?', (content_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'message': '内容删除成功'})

# API：获取单个内容
@app.route('/api/contents/<int:content_id>', methods=['GET'])
def get_content(content_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM contents WHERE id = ?', (content_id,))
    content = cursor.fetchone()
    conn.close()
    
    if content is None:
        return jsonify({'error': '内容不存在'}), 404
    
    return jsonify({
        'id': content[0],
        'title': content[1],
        'content': content[2],
        'author': content[3],
        'created_at': content[4],
        'updated_at': content[5]
    })


# API：获取内容的图片列表
@app.route('/api/contents/<int:content_id>/images', methods=['GET'])
def get_content_images(content_id):
    if 'user_id' not in session:
        return jsonify({'error': '未授权访问'}), 401
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, filename FROM images WHERE content_id = ? ORDER BY order_index ASC', (content_id,))
    images = cursor.fetchall()
    conn.close()
    
    return jsonify({
        'images': [{'id': img[0], 'filename': img[1]} for img in images]
    })


# API：上传图片
@app.route('/api/contents/<int:content_id>/images', methods=['POST'])
def upload_image(content_id):
    if 'user_id' not in session:
        return jsonify({'error': '未授权访问'}), 401
    
    # 检查内容是否存在
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM contents WHERE id = ?', (content_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'error': '内容不存在'}), 404
    
    # 检查是否有图片文件上传
    if 'file' not in request.files:
        conn.close()
        return jsonify({'error': '未上传图片文件'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        conn.close()
        return jsonify({'error': '未选择图片文件'}), 400
    
    # 检查文件类型
    if not allowed_file(file.filename):
        conn.close()
        return jsonify({'error': '不允许的文件类型'}), 400
    
    # 检查图片数量限制（最多5张）
    cursor.execute('SELECT COUNT(*) FROM images WHERE content_id = ?', (content_id,))
    if cursor.fetchone()[0] >= 5:
        conn.close()
        return jsonify({'error': '图片数量已达上限（最多5张）'}), 400
    
    # 生成唯一文件名
    filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4()}_{filename}"
    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
    
    # 保存文件
    file.save(file_path)
    
    # 获取当前最大order_index
    cursor.execute('SELECT COALESCE(MAX(order_index), -1) FROM images WHERE content_id = ?', (content_id,))
    max_order = cursor.fetchone()[0]
    
    # 插入数据库
    cursor.execute('''
        INSERT INTO images (content_id, filename, order_index)
        VALUES (?, ?, ?)
    ''', (content_id, unique_filename, max_order + 1))
    conn.commit()
    conn.close()
    
    return jsonify({
        'message': '图片上传成功',
        'filename': unique_filename
    }), 201


# API：删除图片
@app.route('/api/images/<int:image_id>', methods=['DELETE'])
def delete_image(image_id):
    if 'user_id' not in session:
        return jsonify({'error': '未授权访问'}), 401
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # 获取图片信息
    cursor.execute('SELECT filename FROM images WHERE id = ?', (image_id,))
    image = cursor.fetchone()
    if not image:
        conn.close()
        return jsonify({'error': '图片不存在'}), 404
    
    # 删除文件
    file_path = os.path.join(UPLOAD_FOLDER, image[0])
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # 删除数据库记录
    cursor.execute('DELETE FROM images WHERE id = ?', (image_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'message': '图片删除成功'})

if __name__ == '__main__':
    init_db()
    # 仅在开发环境中运行开发服务器
    app.run(host='0.0.0.0', port=5000)


