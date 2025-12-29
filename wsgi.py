import sys
import os

# 添加项目目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# 导入Flask应用
from server import app as application

# 设置环境变量
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_SECRET_KEY'] = 'your-secret-key-here-change-in-production'