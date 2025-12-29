# 全栈内容管理系统

一个基于 Flask + SQLite 的轻量级内容管理系统，支持内容编辑和浏览功能。

## 🌟 功能特性

- **内容管理**：创建、编辑、删除内容
- **用户认证**：管理员登录系统
- **内容展示**：前端内容列表和详情页
- **响应式设计**：支持移动端和桌面端
- **RESTful API**：前后端分离的API设计

## 🛠 技术栈

- **后端**：Python Flask
- **数据库**：SQLite
- **前端**：HTML5 + CSS3 + JavaScript
- **样式**：CSS Grid + Flexbox

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行应用

```bash
python server.py
```

### 3. 访问网站

- **前端首页**：http://localhost:5000
- **管理后台**：http://localhost:5000/admin
- **登录页面**：http://localhost:5000/login

### 4. 默认账号

- **用户名**：`admin`
- **密码**：`admin123`

> ⚠️ **重要提示**：首次登录后请立即修改默认密码！

## 📁 项目结构

```
my-website/
├── server.py          # Flask后端主文件
├── database.db        # SQLite数据库
├── requirements.txt   # Python依赖包
├── README.md         # 项目说明文档
├── static/           # 静态文件目录
│   ├── css/
│   │   └── style.css # 样式文件
│   └── js/
│       └── main.js   # JavaScript交互逻辑
└── templates/        # HTML模板
    ├── index.html    # 首页（内容列表）
    ├── content.html  # 内容详情页
    ├── admin.html    # 管理后台
    └── login.html    # 登录页面
```

## 🔧 API 接口

### 内容管理

- `GET /api/contents/<id>` - 获取单个内容
- `POST /api/contents` - 创建内容
- `PUT /api/contents/<id>` - 更新内容
- `DELETE /api/contents/<id>` - 删除内容

### 页面路由

- `GET /` - 首页（内容列表）
- `GET /content/<id>` - 内容详情页
- `GET /admin` - 管理后台
- `GET|POST /login` - 登录页面
- `GET /logout` - 退出登录

## 🎨 功能说明

### 管理员功能

1. **登录系统**：使用管理员账号登录后台
2. **创建内容**：点击"新建内容"按钮，填写标题和内容
3. **编辑内容**：点击内容列表中的"编辑"按钮
4. **删除内容**：点击"删除"按钮，确认后删除内容

### 访客功能

1. **浏览内容列表**：首页展示所有已发布的内容
2. **查看内容详情**：点击标题或"阅读全文"查看完整内容

## 🔒 安全建议

1. **修改默认密码**：首次登录后立即修改管理员密码
2. **更换密钥**：修改 `server.py` 中的 `app.secret_key`
3. **使用HTTPS**：生产环境请配置SSL证书
4. **限制访问**：可以配置IP白名单限制后台访问
5. **定期备份**：定期备份 `database.db` 文件

## 🚀 生产部署

### 使用 Gunicorn 部署

```bash
# 安装 Gunicorn
pip install gunicorn

# 启动应用
gunicorn -w 4 -b 0.0.0.0:5000 server:app
```

### 使用 Nginx 反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### Docker 部署

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "server.py"]
```

## 📝 自定义配置

### 修改网站标题

编辑所有 `templates/*.html` 文件中的 `<title>` 标签和 `.logo` 文本。

### 修改样式

编辑 `static/css/style.css` 文件，自定义颜色、字体、布局等。

### 添加新功能

1. **用户注册**：在 `server.py` 中添加注册路由
2. **内容分类**：在数据库中添加分类字段
3. **文件上传**：集成文件上传功能
4. **搜索功能**：添加内容搜索API

## 🐛 常见问题

### Q: 数据库文件不存在？
A: 首次运行时会自动创建数据库和默认用户。

### Q: 忘记管理员密码？
A: 删除 `database.db` 文件后重新运行应用，会自动创建默认用户。

### Q: 如何修改端口？
A: 修改 `server.py` 最后一行的 `port` 参数。

### Q: 如何启用调试模式？
A: 开发时 `app.run(debug=True)` 已启用调试模式。

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**开发时间**：2025年
**作者**：全栈开发者
**版本**：1.0.0