#!/usr/bin/env python3
"""
全栈内容管理系统 - 安装和初始化脚本
"""

import sys
import subprocess
import os

def install_dependencies():
    """安装项目依赖"""
    print("正在安装项目依赖...")
    try:
        # 安装 Flask 和 Werkzeug
        subprocess.check_call([sys.executable, "-m", "pip", "install", "Flask==2.3.3", "Werkzeug==2.3.7"])
        print("✓ 依赖安装成功！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ 依赖安装失败: {e}")
        return False

def init_database():
    """初始化数据库"""
    print("正在初始化数据库...")
    try:
        # 导入并运行数据库初始化
        from server import init_db
        init_db()
        print("✓ 数据库初始化成功！")
        return True
    except Exception as e:
        print(f"✗ 数据库初始化失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("全栈内容管理系统 - 安装向导")
    print("=" * 50)
    
    # 1. 安装依赖
    if not install_dependencies():
        sys.exit(1)
    
    # 2. 初始化数据库
    if not init_database():
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("安装完成！")
    print("=" * 50)
    print("\n使用方法：")
    print("1. 运行: python server.py")
    print("2. 访问: http://localhost:5000")
    print("3. 后台: http://localhost:5000/admin")
    print("4. 账号: admin / admin123")
    print("\n注意：首次登录后请立即修改默认密码！")

if __name__ == "__main__":
    main()