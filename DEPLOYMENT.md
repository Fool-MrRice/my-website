# mrrice的二手交易系统 - 部署指南

## 技术栈
- **后端框架**: Flask 2.3.3 (轻量级Python Web框架)
- **数据库**: SQLite (嵌入式关系型数据库，适合小型应用)
- **Python版本**: 3.9+ (推荐使用3.10或3.11)
- **核心依赖**: 
  - Werkzeug 2.3.7 (WSGI工具库)
  - 标准Python库 (os, re, time, datetime, uuid等)
- **前端技术**: HTML5, CSS3, JavaScript (原生)
- **模板引擎**: Jinja2 (Flask内置)

## 部署平台选择
推荐使用 **PythonAnywhere** 作为免费部署平台，原因如下：
- 专门为Python应用设计，支持Flask
- 提供稳定的免费计划
- 支持SQLite数据库
- 操作简单，适合快速部署

## 部署步骤

### 1. 准备代码
- 确保已创建wsgi.py文件
- 更新requirements.txt文件
- 修改server.py文件适应生产环境

### 2. 注册PythonAnywhere账号
- 访问 https://www.pythonanywhere.com/ 注册免费账号
- 选择 "Beginner" 计划（免费）

### 3. 上传代码
#### 方法一：使用Git克隆（推荐）
- 登录PythonAnywhere后，在顶部导航栏选择 "Consoles" 标签
- 在 "New console" 区域，点击 "Bash" 按钮打开Bash控制台
- 在Bash控制台中，逐行运行以下命令克隆GitHub仓库的online分支：
  ```bash
  # 进入mrrice账户的主目录（默认位置）
  cd /home/mrrice
  
  # 克隆GitHub仓库的online分支到/home/mrrice/my-website目录
  git clone -b online https://github.com/Fool-MrRice/my-website.git
  
  # 检查克隆是否成功，应该能看到项目文件列表
  ls -la /home/mrrice/my-website
  ```

#### 方法二：手动上传文件
- 在顶部导航栏选择 "Files" 标签
- 在文件浏览器中，点击 "New directory" 创建 `/home/mrrice/my-website/` 目录（如果不存在）
- 导航到 `/home/mrrice/my-website/` 目录
- 点击 "Upload a file" 按钮，逐个上传项目文件
- 确保上传所有必要文件：server.py、wsgi.py、requirements.txt、templates/目录下所有文件、static/目录下所有文件等

### 4. 创建虚拟环境
- 在顶部导航栏选择 "Consoles" 标签，打开 "Bash" 控制台
- 在Bash控制台中，逐行运行以下命令：
  ```bash
  # 进入项目目录
  cd /home/mrrice/my-website
  
  # 在项目目录内创建名为venv的虚拟环境
  python3 -m venv venv
  
  # 激活虚拟环境（激活后命令行提示符会显示(venv)前缀）
  source venv/bin/activate
  
  # 升级pip到最新版本
  pip install --upgrade pip
  
  # 安装项目依赖（从requirements.txt文件）
  pip install -r requirements.txt
  
  # 验证依赖是否正确安装
  pip list
  ```

### 5. 配置WSGI应用
- 在顶部导航栏选择 "Web" 标签
- 点击 "Add a new web app" 按钮（如果是首次创建，可能需要确认域名）
- 在弹出的对话框中，选择 "Manual Configuration"（手动配置）
- 选择Python版本（推荐3.9或更高版本，例如Python 3.10）
- 点击 "Next" 按钮完成创建

#### 配置Source code和Working directory
- 在 "Web" 标签的 "Code" 部分，找到以下配置项：
  - **Source code**: 输入项目的根目录路径：`/home/mrrice/my-website`
  - **Working directory**: 输入与Source code相同的路径：`/home/mrrice/my-website`
  - 点击 "Save" 按钮保存配置

#### 编辑WSGI配置文件
- 在 "Web" 标签的 "Code" 部分，找到 "WSGI configuration file" 链接
- 点击该链接，打开WSGI配置文件（路径：`/var/www/mrrice_pythonanywhere_com_wsgi.py`）
- 删除文件中的所有默认内容，替换为以下代码：
  ```python
  import sys
  import os
  
  # 将项目目录添加到Python模块搜索路径
  sys.path.insert(0, '/home/mrrice/my-website')
  
  # 设置生产环境变量
  os.environ['FLASK_ENV'] = 'production'
  # FLASK_SECRET_KEY用于加密会话cookie、生成CSRF令牌等安全功能
  # 必须修改为安全的随机字符串，以下是生成方法：
  # 方法1：在Python控制台运行：python -c "import secrets; print(secrets.token_hex(16))"
  # 方法2：在Bash控制台运行：openssl rand -hex 16
  os.environ['FLASK_SECRET_KEY'] = 'your-secret-key-here-change-in-production'  # 请替换为生成的随机密钥58d58f6bde68abb84bf26eb11f02773b
  
  # 从server.py文件中导入Flask应用实例
  from server import app as application
  ```
- 点击 "Save" 按钮保存配置文件

### 6. 配置环境变量
#### 配置虚拟环境路径
- 在 "Web" 标签中，找到 "Virtualenv" 部分
- 在输入框中输入虚拟环境路径：`/home/mrrice/my-website/venv`
- 点击 "Save" 按钮保存虚拟环境配置

#### 添加系统环境变量（方法一）
- 如果在 "Web" 标签中能找到 "Environment variables" 部分：
  - 点击 "Add or modify environment variables" 按钮
  - 在弹出的对话框中，添加以下环境变量：
    | 变量名 | 变量值 | 说明 |
    |--------|--------|------|
    | FLASK_ENV | production | 应用运行环境（生产环境） |
    | FLASK_SECRET_KEY | your-secret-key-here-change-in-production | 应用密钥，用于加密会话和CSRF令牌。必须修改为安全的随机字符串。生成方法：1) Python控制台运行 `python -c "import secrets; print(secrets.token_hex(16))"`；2) Bash控制台运行 `openssl rand -hex 16` |
  - 点击 "Save" 按钮保存环境变量配置

#### 添加系统环境变量（方法二：如果找不到Environment variables部分）
- 如果在PythonAnywhere界面中找不到 "Environment variables" 部分，您可以直接在wsgi.py文件中配置环境变量：
  - 在 "Web" 标签的 "Code" 部分，点击 "WSGI configuration file" 链接
  - 在wsgi.py文件中，找到以下行并修改：
    ```python
    # 设置环境变量
    os.environ['FLASK_ENV'] = 'production'
    os.environ['FLASK_SECRET_KEY'] = 'your-secret-key-here-change-in-production'  # 替换为生成的随机密钥
    ```
  - 点击 "Save" 按钮保存wsgi.py文件

#### 注意事项
- 这两种方法效果相同，都能让应用正确读取环境变量
- 如果两种方法都配置了，wsgi.py中的配置会优先生效
- 即使找不到 "Environment variables" 部分，也不会影响网站部署，只要您在wsgi.py中正确配置了环境变量

### 7. 配置静态文件服务
- 在 "Web" 标签中，找到 "Static files" 部分
- 点击 "Enter URL" 输入框，输入：`/static/`
- 点击 "Enter path" 输入框，输入：`/home/mrrice/my-website/static/`
- 点击 "Add" 按钮保存静态文件映射
- （可选）如果有其他静态文件目录需要配置，可以重复上述步骤添加

### 8. 初始化数据库
- 在顶部导航栏选择 "Consoles" 标签，打开 "Bash" 控制台
- 在Bash控制台中，逐行运行以下命令：
  ```bash
  # 进入项目目录
  cd /home/mrrice/my-website
  
  # 激活虚拟环境（如果尚未激活）
  source venv/bin/activate
  
  # 执行数据库初始化命令
  python -c "from server import init_db; init_db()"
  
  # 验证数据库是否创建成功（应该能看到database.db文件）
  ls -la /home/mrrice/my-website/database.db
  ```

### 9. 启动应用
- 在顶部导航栏选择 "Web" 标签
- 在页面顶部找到 "Reload mrrice.pythonanywhere.com" 按钮
- 点击该按钮重新加载应用
- 等待3-5秒钟，确保应用重启完成

#### 测试应用
- 打开浏览器，在地址栏输入：`http://mrrice.pythonanywhere.com`
- 检查首页是否正常加载
- 尝试访问管理后台：`http://mrrice.pythonanywhere.com/admin`
- 登录测试：用户名 `admin`，密码 `admin`（首次登录后请立即修改密码）
- 测试网站的各种功能，确保一切正常运行

## 数据库配置
本项目使用SQLite数据库，无需额外配置。数据库文件将自动创建在项目根目录下的 `database.db`。

## 静态文件服务
- 所有静态文件（CSS、JavaScript、图片）都存储在 `static/` 目录下
- 在PythonAnywhere上配置静态文件映射后，Flask会自动处理静态文件请求

## 维护和更新
### 更新代码
1. 上传新的代码文件
2. 在Bash控制台中重新安装依赖（如果有变化）
3. 点击 "Reload" 按钮重新启动应用

### 备份数据库
- 定期下载 `database.db` 文件到本地备份
- 在PythonAnywhere的 "Files" 标签中可以直接下载

## 注意事项
1. 免费计划有流量限制，适合小型应用
2. 确保修改默认的管理员密码
3. 定期备份数据库
4. 不要在代码中硬编码敏感信息

## 域名和HTTPS（可选）
- PythonAnywhere免费计划提供 `your-username.pythonanywhere.com` 域名
- 如果需要自定义域名，可以升级到付费计划
- HTTPS支持需要付费计划