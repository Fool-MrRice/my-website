from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import sqlite3
import re
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'


@app.template_filter('nl2br')
def nl2br_filter(s):
    if not s:
        return ''
    # 把单个换行替换成 <br>，连续两个换行保留段落
    s = str(s)
    s = re.sub(r'(\r\n|\r|\n)', '<br>', s)
    return s


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
    
    # 创建用户表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 检查是否有默认用户，如果没有则创建一个
    cursor.execute('SELECT COUNT(*) FROM users WHERE username = ?', ('admin',))
    if cursor.fetchone()[0] == 0:
        hashed_password = generate_password_hash('admin123')
        cursor.execute('''
            INSERT INTO users (username, password_hash)
            VALUES (?, ?)
        ''', ('admin', hashed_password))
        print("默认管理员用户创建成功！用户名: admin, 密码: admin123")
    
    conn.commit()
    conn.close()

# 首页 - 内容列表
@app.route('/')
def index():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, author, created_at FROM contents ORDER BY created_at DESC')
    contents = cursor.fetchall()
    conn.close()
    return render_template('index.html', contents=contents)

# 内容详情页
@app.route('/content/<int:content_id>')
def content_detail(content_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM contents WHERE id = ?', (content_id,))
    content = cursor.fetchone()
    conn.close()
    
    if content is None:
        return "内容不存在", 404
    
    return render_template('content.html', content=content)

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
    conn.commit()
    conn.close()
    
    return jsonify({'message': '内容创建成功'}), 201

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

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)


