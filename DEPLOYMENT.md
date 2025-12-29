# mrrice的二手交易系统 - 部署指南

## 技术栈
- Python 3.x
- Flask 2.3.3
- SQLite 数据库
- Werkzeug 2.3.7

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
- 在PythonAnywhere控制台中，选择 "Files" 标签
- 点击 "Upload a file" 上传项目文件，或者使用Git克隆代码

### 4. 创建虚拟环境
- 选择 "Consoles" 标签，打开 "Bash" 控制台
- 运行以下命令：
  ```bash
  # 创建虚拟环境
  python3 -m venv venv
  # 激活虚拟环境
  source venv/bin/activate
  # 安装依赖
  pip install -r requirements.txt
  ```

### 5. 配置WSGI应用
- 选择 "Web" 标签
- 点击 "Add a new web app"
- 选择 "Flask"，然后选择Python版本（推荐3.9或更高）
- 在 "Path to your source code" 中输入项目路径
- 在 "Path to your WSGI configuration file" 中配置wsgi.py路径

### 6. 配置环境变量
- 在 "Web" 标签中，找到 "Virtualenv" 部分，输入虚拟环境路径：`/home/your-username/venv`
- 在 "Environment variables" 部分，添加：
  ```
  FLASK_ENV=production
  FLASK_SECRET_KEY=your-secret-key-here-change-in-production
  ```

### 7. 配置静态文件服务
- 在 "Web" 标签中，找到 "Static files" 部分
- 添加静态文件映射：
  - URL: `/static/`
  - Directory: `/home/your-username/your-project/static/`

### 8. 初始化数据库
- 在Bash控制台中运行：
  ```bash
  python -c "from server import init_db; init_db()"
  ```

### 9. 启动应用
- 在 "Web" 标签中，点击 "Reload your-username.pythonanywhere.com"
- 访问 `http://your-username.pythonanywhere.com` 测试应用

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