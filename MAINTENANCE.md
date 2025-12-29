# mrrice的二手交易系统 - 维护和更新指南

## 目录
- [日常维护](#日常维护)
- [代码更新](#代码更新)
- [数据库管理](#数据库管理)
- [安全维护](#安全维护)
- [性能优化](#性能优化)
- [常见问题排查](#常见问题排查)

## 日常维护

### 1. 监控应用状态
- 定期访问网站，确保所有页面正常加载
- 检查控制台是否有错误日志
- 监控访问量和响应时间

### 2. 备份数据
- 定期备份数据库文件 `database.db`
- 备份上传的图片文件（`static/uploads/` 目录）
- 推荐使用云存储服务（如Google Drive、Dropbox）存储备份

### 3. 更新依赖
- 定期更新Python依赖包，确保安全性和稳定性
- 运行以下命令更新依赖：
  ```bash
  pip install --upgrade -r requirements.txt
  ```

## 代码更新

### 1. 本地开发
- 在本地创建分支进行开发
- 测试新功能和修复
- 确保所有测试通过

### 2. 部署更新
- 将更新后的代码上传到PythonAnywhere
- 重新安装依赖（如果有变化）
- 重启应用服务

```bash
# 在PythonAnywhere控制台中
cd /home/your-username/your-project
git pull  # 如果使用Git
pip install --upgrade -r requirements.txt
pythonanywhere webapp your-app-name reload
```

## 数据库管理

### 1. 备份数据库
```bash
# 方法1：直接下载文件
# 在PythonAnywhere的Files页面下载database.db

# 方法2：使用命令行
cp /home/your-username/your-project/database.db /home/your-username/backups/database-$(date +%Y%m%d).db
```

### 2. 恢复数据库
```bash
# 方法1：直接上传文件
# 在PythonAnywhere的Files页面上传备份的database.db

# 方法2：使用命令行
cp /home/your-username/backups/database-20250101.db /home/your-username/your-project/database.db
```

### 3. 数据库优化
- 定期运行SQLite优化命令
```bash
python -c "
import sqlite3
conn = sqlite3.connect('database.db')
conn.execute('VACUUM')
conn.close()
"
```

## 安全维护

### 1. 更改默认密码
- 首次登录后，立即修改管理员密码
- 定期更换密码
- 使用强密码（包含大小写字母、数字和特殊字符）

### 2. 更新密钥
- 定期更换Flask secret key
- 在PythonAnywhere的环境变量中更新 `FLASK_SECRET_KEY`
- 重启应用使更改生效

### 3. 防止SQL注入
- 项目已使用参数化查询，无需额外处理
- 避免直接拼接SQL语句

### 4. 防止XSS攻击
- 确保用户输入已正确转义
- 项目已使用Flask的模板自动转义功能

## 性能优化

### 1. 静态文件优化
- 压缩CSS和JavaScript文件
- 使用CDN服务（可选，需付费）
- 优化图片大小，减少加载时间

### 2. 数据库优化
- 为常用查询添加索引
- 定期清理过期数据
- 限制每页显示的内容数量

### 3. 缓存策略
- 考虑使用Flask-Cache扩展缓存频繁访问的页面
- 缓存数据库查询结果

## 常见问题排查

### 1. 应用无法访问
- 检查PythonAnywhere的Web应用状态
- 查看错误日志（在Web标签的"Error log"部分）
- 确保虚拟环境配置正确

### 2. 数据库连接错误
- 检查数据库文件路径是否正确
- 确保数据库文件有读写权限
- 尝试重新初始化数据库

### 3. 静态文件无法加载
- 检查静态文件映射配置
- 确保文件路径正确
- 检查文件权限

### 4. 登录失败
- 检查用户名和密码是否正确
- 确保session配置正确
- 检查浏览器cookie设置

## 联系方式
- 如有问题或需要技术支持，请联系mrrice

## 版本历史
- v1.0.0 (2025-12-30): 初始部署版本