// 全局变量
let currentEditingId = null;
let uploadedImages = [];

// 显示创建内容的模态框
function showCreateModal() {
    currentEditingId = null;
    uploadedImages = [];
    document.getElementById('modalTitle').textContent = '新建内容';
    document.getElementById('contentTitle').value = '';
    document.getElementById('contentBody').value = '';
    document.getElementById('contentModal').style.display = 'block';
    clearImagePreview();
    setupImageUpload();
}

// 编辑内容
function editContent(id) {
    currentEditingId = id;
    uploadedImages = [];
    
    // 获取内容数据
    fetch(`/api/contents/${id}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('modalTitle').textContent = '编辑内容';
            document.getElementById('contentTitle').value = data.title;
            document.getElementById('contentBody').value = data.content;
            
            // 获取已上传的图片
            return fetch(`/api/contents/${id}/images`);
        })
        .then(response => response.json())
        .then(data => {
            uploadedImages = data.images || [];
            updateImagePreview();
            document.getElementById('contentModal').style.display = 'block';
            setupImageUpload();
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
    uploadedImages = [];
    clearImagePreview();
}

// 设置图片上传
function setupImageUpload() {
    const imageUpload = document.getElementById('imageUpload');
    if (imageUpload) {
        imageUpload.addEventListener('change', handleImageSelection);
    }
}

// 处理图片选择
function handleImageSelection(e) {
    const files = Array.from(e.target.files);
    
    // 检查图片数量限制
    if (uploadedImages.length + files.length > 5) {
        alert('最多只能上传5张图片！');
        e.target.value = ''; // 清空选择
        return;
    }
    
    // 显示图片预览
    files.forEach(file => {
        if (file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = function(event) {
                const preview = {
                    id: null, // 新上传的图片没有ID
                    filename: file.name,
                    previewUrl: event.target.result,
                    file: file
                };
                uploadedImages.push(preview);
                updateImagePreview();
            };
            reader.readAsDataURL(file);
        }
    });
    
    e.target.value = ''; // 清空选择，允许重新选择相同文件
}

// 清除图片预览
function clearImagePreview() {
    const previewContainer = document.getElementById('imagePreviewContainer');
    if (previewContainer) {
        previewContainer.innerHTML = '';
    }
}

// 更新图片预览
function updateImagePreview() {
    const previewContainer = document.getElementById('imagePreviewContainer');
    if (!previewContainer) return;
    
    previewContainer.innerHTML = '';
    
    uploadedImages.forEach((image, index) => {
        const previewItem = document.createElement('div');
        previewItem.className = 'image-preview-item';
        
        const img = document.createElement('img');
        img.src = image.previewUrl || `/static/uploads/${image.filename}`;
        img.alt = `图片 ${index + 1}`;
        img.className = 'image-preview';
        
        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'image-delete-btn';
        deleteBtn.textContent = '×';
        deleteBtn.onclick = () => deleteImagePreview(index);
        
        previewItem.appendChild(img);
        previewItem.appendChild(deleteBtn);
        previewContainer.appendChild(previewItem);
    });
}

// 删除图片预览
function deleteImagePreview(index) {
    const image = uploadedImages[index];
    
    if (image.id) {
        // 如果是已上传的图片，需要调用API删除
        if (confirm('确定要删除这张图片吗？')) {
            fetch(`/api/images/${image.id}`, {
                method: 'DELETE'
            })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    uploadedImages.splice(index, 1);
                    updateImagePreview();
                }
            })
            .catch(error => {
                alert('删除图片失败：' + error.message);
            });
        }
    } else {
        // 如果是还未上传的图片，直接从预览中删除
        uploadedImages.splice(index, 1);
        updateImagePreview();
    }
}

// 表单提交处理
document.addEventListener('DOMContentLoaded', function() {
    const contentForm = document.getElementById('contentForm');
    if (contentForm) {
        contentForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const title = document.getElementById('contentTitle').value.trim();
            const content = document.getElementById('contentBody').value.trim();
            
            if (!title || !content) {
                alert('标题和内容不能为空！');
                return;
            }
            
            try {
                // 保存内容（标题和正文）
                const contentUrl = currentEditingId ? `/api/contents/${currentEditingId}` : '/api/contents';
                const contentMethod = currentEditingId ? 'PUT' : 'POST';
                
                const contentResponse = await fetch(contentUrl, {
                    method: contentMethod,
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        title: title,
                        content: content
                    })
                });
                
                const contentData = await contentResponse.json();
                if (contentData.error) {
                    throw new Error(contentData.error);
                }
                
                // 获取内容ID（新创建的或已存在的）
                const contentId = currentEditingId || (contentResponse.status === 201 ? 
                    // 从创建响应中直接获取新创建的ID
                    contentData.id : 
                    currentEditingId);
                
                // 上传新图片（只有file属性的才是新图片）
                const newImages = uploadedImages.filter(img => img.file);
                for (const image of newImages) {
                    const formData = new FormData();
                    formData.append('file', image.file);
                    
                    const imageResponse = await fetch(`/api/contents/${contentId}/images`, {
                        method: 'POST',
                        body: formData
                    });
                    
                    const imageData = await imageResponse.json();
                    if (imageData.error) {
                        throw new Error(imageData.error);
                    }
                }
                
                // 操作成功
                alert('内容保存成功！');
                closeModal();
                location.reload(); // 刷新页面
            } catch (error) {
                alert('操作失败：' + error.message);
            }
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