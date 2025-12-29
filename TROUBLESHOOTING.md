# 常见问题解决指南

## 问题1：SQLite3-Win 安装失败

**错误信息：**
```
ERROR: Could not find a version that satisfies the requirement SQLite3-Win==0.0.1
```

**原因：**
SQLite3-Win 是一个不存在的包。SQLite3 是 Python 的内置模块，不需要额外安装。

**解决方案：**

### 方法1：手动安装依赖（推荐）
```bash
pip install Flask Werkzeug
```

### 方法2：修改 requirements.txt
1. 打开 requirements.txt 文件
2. 删除或注释掉 `SQLite3-Win==0.0.1` 这一行
3. 只保留：
```
Flask==2.3.3
Werkzeug==2.3.7
```
4. 然后运行：
```bash
pip install -r requirements.txt
```

### 方法3：使用 setup.py（最简单）
```bash
python setup.py
```
这个脚本会自动安装正确的依赖并初始化数据库。

---

## 问题2：ModuleNotFoundError: No module named 'flask'

**错误信息：**
```
ModuleNotFoundError: No module named 'flask'
```

**原因：**
Flask 没有安装或安装在错误的 Python 环境中。

**解决方案：**

### 方法1：确认 Python 环境
```bash
# 查看当前 Python 路径
where python
# 或 (Linux/Mac)
which python

# 查看 pip 路径
where pip
# 或 (Linux/Mac)
which pip
```

### 方法2：使用正确的 Python 版本安装
```bash
# 使用 Python 3
python3 -m pip install Flask Werkzeug

# 或使用 python 命令
python -m pip install Flask Werkzeug
```

### 方法3：在 PyCharm 中安装
1. 打开 PyCharm 的设置 (File → Settings)
2. 找到 Project: my-website → Python Interpreter
3. 点击 + 按钮添加包
4. 搜索并安装 Flask 和 Werkzeug

---

## 问题3：数据库文件无法创建

**错误信息：**
```
sqlite3.OperationalError: unable to open database file
```

**原因：**
没有写入权限或目录不存在。

**解决方案：**

### 方法1：检查文件权限
```bash
# Windows：确保有写入权限
# Linux/Mac：
chmod 755 .
```

### 方法2：手动创建数据库
```python
# 在 Python 交互式环境中运行
import sqlite3
conn = sqlite3.connect('database.db')
conn.close()
```

### 方法3：使用 setup.py
```bash
python setup.py
```

---

## 问题4：端口已被占用

**错误信息：**
```
OSError: [Errno 48] Address already in use
```

**原因：**
5000 端口已被其他程序占用。

**解决方案：**

### 方法1：修改端口号
编辑 server.py，修改最后一行：
```python
app.run(debug=True, host='0.0.0.0', port=8000)  # 改为8000或其他端口
```

### 方法2：查找并关闭占用端口的程序

**Windows：**
```bash
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

**Linux/Mac：**
```bash
lsof -i :5000
kill -9 <PID>
```

---

## 问题5：CSS 或 JS 文件加载失败

**现象：**
页面没有样式，或功能无法正常使用。

**原因：**
静态文件路径错误或 Flask 配置问题。

**解决方案：**

### 方法1：检查文件结构
确保项目结构如下：
```
my-website/
├── server.py
├── templates/
│   ├── index.html
│   ├── content.html
│   ├── admin.html
│   └── login.html
└── static/
    ├── css/
    │   └── style.css
    └── js/
        └── main.js
```

### 方法2：检查 Flask 静态文件配置
在 server.py 中确认：
```python
app = Flask(__name__)
```
不需要额外配置，Flask 会自动处理 static 目录。

### 方法3：清除浏览器缓存
按 Ctrl+F5 强制刷新页面。

---

## 问题6：登录失败或 Session 问题

**现象：**
无法登录，或登录后无法保持会话。

**原因：**
secret_key 配置问题或浏览器 Cookie 被禁用。

**解决方案：**

### 方法1：修改 secret_key
编辑 server.py：
```python
app.secret_key = 'your-very-secret-key-here-change-it'  # 改为复杂的密钥
```

### 方法2：检查浏览器设置
确保浏览器启用了 Cookie。

### 方法3：使用隐私模式
打开浏览器的隐私模式（无痕模式）再试。

---

## 问题7：中文乱码

**现象：**
中文内容显示为问号或乱码。

**原因：**
文件编码或数据库编码问题。

**解决方案：**

### 方法1：确保文件为 UTF-8 编码
在 PyCharm 中：
1. 右下角点击编码
2. 选择 UTF-8
3. 重新保存文件

### 方法2：检查数据库编码
SQLite 默认使用 UTF-8，一般没问题。如果问题依然存在，可以重建数据库：
```bash
# 删除旧数据库
rm database.db

# 重新运行应用
python server.py
```

---

## 问题8：PyCharm 中运行报错

**现象：**
在 PyCharm 中运行时报各种错误。

**解决方案：**

### 方法1：配置正确的 Python 解释器
1. File → Settings
2. Project: my-website → Python Interpreter
3. 选择合适的解释器或创建虚拟环境

### 方法2：设置环境变量
在 PyCharm 的运行配置中添加环境变量：
1. Run → Edit Configurations
2. 选择 server.py
3. 在 Environment variables 中添加：
   ```
   FLASK_ENV=development
   FLASK_DEBUG=1
   ```

### 方法3：以管理员身份运行
在 Windows 上，右键 PyCharm → 以管理员身份运行。

---

## 问题9：ModuleNotFoundError: No module named 'werkzeug'

**错误信息：**
```
ModuleNotFoundError: No module named 'werkzeug'
```

**解决方案：**
```bash
pip install Werkzeug==2.3.7
```

或
```bash
pip install -r requirements.txt
```

---

## 问题10：权限错误 (Permission Denied)

**错误信息：**
```
PermissionError: [Errno 13] Permission denied
```

**原因：**
没有足够权限。

**解决方案：**

### Windows：
以管理员身份运行命令提示符或 PowerShell。

### Linux/Mac：
```bash
sudo python server.py
```

或修改文件权限：
```bash
chmod 755 server.py
```

---

## 获取更多帮助

如果以上方法都无法解决问题，请：

1. 查看完整的错误日志
2. 确认 Python 版本（推荐 3.8+）
3. 检查操作系统兼容性
4. 在 GitHub 或相关社区寻求帮助

**提供信息时请包含：**
- 操作系统版本
- Python 版本
- 完整的错误信息
- 已尝试的解决方法