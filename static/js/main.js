// 全局变量
let currentEditingId = null;

// 显示创建内容的模态框
function showCreateModal() {
    currentEditingId = null;
    document.getElementById('modalTitle').textContent = '新建内容';
    document.getElementById('contentTitle').value = '';
    document.getElementById('contentBody').value = '';
    document.getElementById('contentModal').style.display = 'block';
}

// 编辑内容
function editContent(id) {
    currentEditingId = id;
    
    // 获取内容数据
    fetch(`/api/contents/${id}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('modalTitle').textContent = '编辑内容';
            document.getElementById('contentTitle').value = data.title;
            document.getElementById('contentBody').value = data.content;
            document.getElementById('contentModal').style.display = 'block';
        })
        .catch(error => {
            alert('获取内容失败：' + error.message);
        });
}

// 删除内容
function deleteContent(id) {
    if (confirm('确定要删除这条内容吗？此操作无法撤销。')) {
        fetch(`/api/contents/${id}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                alert(data.message);
                location.reload(); // 刷新页面
            }
        })
        .catch(error => {
            alert('删除失败：' + error.message);
        });
    }
}

// 关闭模态框
function closeModal() {
    document.getElementById('contentModal').style.display = 'none';
    currentEditingId = null;
}

// 表单提交处理
document.addEventListener('DOMContentLoaded', function() {
    const contentForm = document.getElementById('contentForm');
    if (contentForm) {
        contentForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const title = document.getElementById('contentTitle').value.trim();
            const content = document.getElementById('contentBody').value.trim();
            
            if (!title || !content) {
                alert('标题和内容不能为空！');
                return;
            }
            
            const url = currentEditingId ? `/api/contents/${currentEditingId}` : '/api/contents';
            const method = currentEditingId ? 'PUT' : 'POST';
            
            fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    title: title,
                    content: content
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    alert(data.message);
                    closeModal();
                    location.reload(); // 刷新页面
                } else if (data.error) {
                    alert('错误：' + data.error);
                }
            })
            .catch(error => {
                alert('操作失败：' + error.message);
            });
        });
    }
    
    // 点击模态框外部关闭模态框
    const modal = document.getElementById('contentModal');
    if (modal) {
        window.addEventListener('click', function(e) {
            if (e.target === modal) {
                closeModal();
            }
        });
    }
    
    // ESC键关闭模态框
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeModal();
        }
    });
});

// 工具函数：显示通知
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    // 添加样式
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        background: ${type === 'error' ? '#dc3545' : '#28a745'};
        color: white;
        border-radius: 4px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        z-index: 10000;
        animation: slideIn 0.3s ease-out;
    `;
    
    document.body.appendChild(notification);
    
    // 3秒后自动移除
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// 添加CSS动画
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);