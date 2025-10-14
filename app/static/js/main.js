/**
 * Python学习平台 - 主JavaScript文件
 * 包含全局功能和通用工具函数
 */

// 全局配置
window.PythonLearningPlatform = {
    config: {
        apiTimeout: 30000,
        codeExecutionTimeout: 15000,
        maxCodeLength: 10000,
        animationDuration: 300
    },
    
    // 执行历史
    executionHistory: [],
    
    // 当前主题
    currentTheme: 'light'
};

/**
 * 文档加载完成后的初始化
 */
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

/**
 * 初始化应用
 */
function initializeApp() {
    console.log('🐍 Python学习平台初始化中...');
    
    // 初始化代码高亮
    initializeCodeHighlighting();
    
    // 初始化工具提示
    initializeTooltips();
    
    // 初始化平滑滚动
    initializeSmoothScrolling();
    
    // 初始化键盘快捷键
    initializeKeyboardShortcuts();
    
    // 初始化页面动画
    initializePageAnimations();
    
    // 初始化代码执行功能
    initializeCodeExecution();
    
    console.log('✅ Python学习平台初始化完成');
}

/**
 * 初始化代码高亮
 */
function initializeCodeHighlighting() {
    // Prism.js 会自动处理代码高亮
    if (typeof Prism !== 'undefined') {
        Prism.highlightAll();
        console.log('📝 代码高亮已启用');
    }
}

/**
 * 初始化工具提示
 */
function initializeTooltips() {
    // 初始化 Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // 为代码块添加复制按钮和工具提示
    addCopyButtonsToCodeBlocks();
}

/**
 * 为代码块添加复制按钮
 */
function addCopyButtonsToCodeBlocks() {
    const codeBlocks = document.querySelectorAll('pre code');
    
    codeBlocks.forEach(function(codeBlock) {
        const pre = codeBlock.parentElement;
        
        // 避免重复添加
        if (pre.querySelector('.copy-btn')) return;
        
        // 创建复制按钮
        const copyBtn = document.createElement('button');
        copyBtn.className = 'btn btn-sm btn-outline-secondary copy-btn position-absolute';
        copyBtn.style.cssText = 'top: 0.5rem; right: 0.5rem; z-index: 10;';
        copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
        copyBtn.title = '复制代码';
        
        // 设置相对定位
        pre.style.position = 'relative';
        
        // 添加点击事件
        copyBtn.addEventListener('click', function() {
            copyToClipboard(codeBlock.textContent, copyBtn);
        });
        
        pre.appendChild(copyBtn);
    });
}

/**
 * 复制文本到剪贴板
 */
function copyToClipboard(text, button) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(function() {
            showCopySuccess(button);
        }, function(err) {
            console.error('复制失败:', err);
            fallbackCopyTextToClipboard(text, button);
        });
    } else {
        fallbackCopyTextToClipboard(text, button);
    }
}

/**
 * 备用复制方法
 */
function fallbackCopyTextToClipboard(text, button) {
    const textArea = document.createElement("textarea");
    textArea.value = text;
    textArea.style.position = "fixed";
    textArea.style.left = "-999999px";
    textArea.style.top = "-999999px";
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        const successful = document.execCommand('copy');
        if (successful) {
            showCopySuccess(button);
        } else {
            showCopyError(button);
        }
    } catch (err) {
        console.error('备用复制方法失败:', err);
        showCopyError(button);
    }
    
    document.body.removeChild(textArea);
}

/**
 * 显示复制成功
 */
function showCopySuccess(button) {
    const originalHTML = button.innerHTML;
    button.innerHTML = '<i class="fas fa-check text-success"></i>';
    button.classList.add('btn-success');
    button.classList.remove('btn-outline-secondary');
    
    setTimeout(function() {
        button.innerHTML = originalHTML;
        button.classList.remove('btn-success');
        button.classList.add('btn-outline-secondary');
    }, 2000);
}

/**
 * 显示复制错误
 */
function showCopyError(button) {
    const originalHTML = button.innerHTML;
    button.innerHTML = '<i class="fas fa-times text-danger"></i>';
    
    setTimeout(function() {
        button.innerHTML = originalHTML;
    }, 2000);
}

/**
 * 初始化平滑滚动
 */
function initializeSmoothScrolling() {
    // 为锚点链接添加平滑滚动
    document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href === '#') return;
            
            const target = document.querySelector(href);
            if (target) {
                e.preventDefault();
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

/**
 * 初始化键盘快捷键
 */
function initializeKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl + / 显示快捷键帮助
        if (e.ctrlKey && e.key === '/') {
            e.preventDefault();
            showKeyboardShortcuts();
        }
        
        // Ctrl + K 聚焦搜索框
        if (e.ctrlKey && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('input[name="q"]');
            if (searchInput) {
                searchInput.focus();
                searchInput.select();
            }
        }
        
        // ESC 键关闭模态框
        if (e.key === 'Escape') {
            const openModals = document.querySelectorAll('.modal.show');
            openModals.forEach(modal => {
                const modalInstance = bootstrap.Modal.getInstance(modal);
                if (modalInstance) {
                    modalInstance.hide();
                }
            });
        }
    });
}

/**
 * 显示键盘快捷键帮助
 */
function showKeyboardShortcuts() {
    const shortcuts = [
        { key: 'Ctrl + /', desc: '显示快捷键帮助' },
        { key: 'Ctrl + K', desc: '聚焦搜索框' },
        { key: 'Ctrl + Enter', desc: '运行代码 (在代码编辑器中)' },
        { key: 'ESC', desc: '关闭模态框' }
    ];
    
    let shortcutsHTML = '<div class="modal fade" id="shortcutsModal" tabindex="-1">';
    shortcutsHTML += '<div class="modal-dialog"><div class="modal-content">';
    shortcutsHTML += '<div class="modal-header">';
    shortcutsHTML += '<h5 class="modal-title"><i class="fas fa-keyboard"></i> 键盘快捷键</h5>';
    shortcutsHTML += '<button type="button" class="btn-close" data-bs-dismiss="modal"></button>';
    shortcutsHTML += '</div><div class="modal-body">';
    shortcutsHTML += '<div class="row">';
    
    shortcuts.forEach(shortcut => {
        shortcutsHTML += '<div class="col-12 mb-2">';
        shortcutsHTML += '<div class="d-flex justify-content-between align-items-center">';
        shortcutsHTML += `<span>${shortcut.desc}</span>`;
        shortcutsHTML += `<kbd class="ms-2">${shortcut.key}</kbd>`;
        shortcutsHTML += '</div></div>';
    });
    
    shortcutsHTML += '</div></div></div></div></div>';
    
    // 移除已存在的模态框
    const existingModal = document.getElementById('shortcutsModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // 添加新模态框
    document.body.insertAdjacentHTML('beforeend', shortcutsHTML);
    
    // 显示模态框
    const modal = new bootstrap.Modal(document.getElementById('shortcutsModal'));
    modal.show();
    
    // 模态框隐藏后移除元素
    document.getElementById('shortcutsModal').addEventListener('hidden.bs.modal', function() {
        this.remove();
    });
}

/**
 * 初始化页面动画
 */
function initializePageAnimations() {
    // 创建 Intersection Observer
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // 观察需要动画的元素
    const animatedElements = document.querySelectorAll('.card, .example-item, .feature-card');
    animatedElements.forEach(el => {
        observer.observe(el);
    });
}

/**
 * 初始化代码执行功能
 */
function initializeCodeExecution() {
    // 统一处理代码执行按钮
    document.addEventListener('click', function(e) {
        if (e.target.closest('.run-code-btn') || e.target.closest('[data-action="run-code"]')) {
            const button = e.target.closest('button');
            const code = button.getAttribute('data-code') || getCodeFromElement(button);
            
            if (code) {
                executeCode(code, button);
            }
        }
    });
}

/**
 * 从元素获取代码
 */
function getCodeFromElement(button) {
    // 尝试从同级元素获取代码
    const codeContainer = button.closest('.example-item')?.querySelector('code');
    if (codeContainer) {
        return codeContainer.textContent;
    }
    
    // 尝试从数据属性获取
    return button.getAttribute('data-code') || '';
}

/**
 * 执行用户输入的代码
 */
function executeUserCode() {
    console.log('🚀 executeUserCode 函数被调用');
    
    const codeInput = document.getElementById('codeInput');
    const output = document.getElementById('output');
    
    console.log('📝 找到的元素:', {
        codeInput: codeInput ? '存在' : '不存在',
        output: output ? '存在' : '不存在'
    });
    
    if (!codeInput) {
        console.error('❌ 找不到代码输入框');
        showNotification('找不到代码输入框', 'error');
        return;
    }
    
    const code = codeInput.value.trim();
    console.log('📄 用户输入的代码:', code);
    
    if (!code) {
        console.warn('⚠️ 代码为空');
        showNotification('请输入要执行的代码', 'warning');
        return;
    }
    
    // 更新输出区域显示执行中状态
    if (output) {
        output.textContent = '执行中...';
        output.style.color = '#6c757d';
        console.log('🔄 更新输出区域显示执行中状态');
    }
    
    // 创建临时按钮用于执行
    const tempButton = document.createElement('button');
    tempButton.style.display = 'none';
    document.body.appendChild(tempButton);
    
    console.log('🎯 调用 executeCode 函数');
    // 使用现有的executeCode函数
    executeCode(code, tempButton, output);
    
    // 清理临时按钮
    setTimeout(() => {
        if (tempButton.parentNode) {
            tempButton.parentNode.removeChild(tempButton);
        }
    }, 100);
}

/**
 * 执行Python代码
 */
function executeCode(code, button, outputElement) {
    console.log('🎯 executeCode 函数被调用', { code: code.substring(0, 50) + '...', button, outputElement });
    
    if (!code || !code.trim()) {
        console.warn('⚠️ executeCode: 代码为空');
        showNotification('请输入要执行的代码', 'warning');
        return;
    }
    
    if (code.length > window.PythonLearningPlatform.config.maxCodeLength) {
        showNotification('代码长度超出限制', 'error');
        return;
    }
    
    // 更新按钮状态
    const originalHTML = button.innerHTML;
    button.innerHTML = '<span class="loading-spinner"></span> 执行中...';
    button.disabled = true;
    
    // 确定输出元素
    let output = outputElement;
    if (!output) {
        output = findOrCreateOutputElement(button);
    }
    
    // 显示执行中状态
    if (output) {
        if (output.querySelector('.output-content')) {
            output.querySelector('.output-content').textContent = '执行中...';
            output.style.display = 'block';
        } else {
            // 处理简单的输出元素（如用户代码执行区域）
            output.textContent = '执行中...';
            output.style.color = '#6c757d';
        }
    }
    
    const startTime = Date.now();
    
    // 发送执行请求
    fetch('/api/execute', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ code: code }),
        signal: AbortSignal.timeout(window.PythonLearningPlatform.config.codeExecutionTimeout)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return response.json();
    })
    .then(data => {
        const executionTime = ((Date.now() - startTime) / 1000).toFixed(3);
        displayExecutionResult(data, output, executionTime);
        
        // 添加到执行历史
        window.PythonLearningPlatform.executionHistory.push({
            code: code,
            result: data,
            timestamp: new Date().toISOString(),
            executionTime: executionTime
        });
        
        // 限制历史记录长度
        if (window.PythonLearningPlatform.executionHistory.length > 50) {
            window.PythonLearningPlatform.executionHistory.shift();
        }
    })
    .catch(error => {
        console.error('代码执行错误:', error);
        const errorMessage = error.name === 'AbortError' ? '执行超时' : `网络错误: ${error.message}`;
        displayExecutionError(errorMessage, output);
    })
    .finally(() => {
        // 恢复按钮状态
        button.innerHTML = originalHTML;
        button.disabled = false;
    });
}

/**
 * 查找或创建输出元素
 */
function findOrCreateOutputElement(button) {
    // 尝试在父级容器中找到输出元素
    const container = button.closest('.example-item') || button.closest('.card-body');
    let output = container?.querySelector('.code-output');
    
    if (!output) {
        // 创建输出元素
        output = document.createElement('div');
        output.className = 'code-output mt-3';
        output.style.display = 'none';
        output.innerHTML = `
            <div class="card border-success">
                <div class="card-header bg-light">
                    <small class="text-muted">
                        <i class="fas fa-terminal"></i> 执行结果
                    </small>
                </div>
                <div class="card-body">
                    <pre class="output-content mb-0"></pre>
                </div>
            </div>
        `;
        
        // 插入到适当位置
        if (container) {
            container.appendChild(output);
        } else {
            button.parentElement.insertAdjacentElement('afterend', output);
        }
    }
    
    return output;
}

/**
 * 显示执行结果
 */
function displayExecutionResult(data, outputElement, executionTime) {
    if (!outputElement) return;
    
    const outputContent = outputElement.querySelector('.output-content');
    const cardHeader = outputElement.querySelector('.card-header');
    
    if (data.success) {
        const result = data.output || '(无输出)';
        
        if (outputContent) {
            // 处理复杂的输出元素（有.output-content的）
            outputContent.textContent = result;
            outputContent.className = 'output-content mb-0 text-success';
        } else {
            // 处理简单的输出元素（如用户代码执行区域）
            outputElement.textContent = result;
            outputElement.style.color = '#28a745';
        }
        
        if (cardHeader) {
            cardHeader.innerHTML = `
                <small class="text-muted">
                    <i class="fas fa-check text-success"></i> 
                    执行成功 (耗时: ${data.execution_time || executionTime}s)
                </small>
            `;
        }
        
        // 显示变量信息
        if (data.variables && Object.keys(data.variables).length > 0) {
            const varsInfo = Object.keys(data.variables).join(', ');
            if (cardHeader) {
                cardHeader.innerHTML += `<br><small class="text-info">变量: ${varsInfo}</small>`;
            }
        }
        
        if (outputElement.querySelector('.card')) {
            outputElement.querySelector('.card').className = 'card border-success';
        }
    } else {
        const error = data.error || '执行出错';
        
        if (outputContent) {
            // 处理复杂的输出元素
            outputContent.textContent = error;
            outputContent.className = 'output-content mb-0 text-danger';
        } else {
            // 处理简单的输出元素
            outputElement.textContent = error;
            outputElement.style.color = '#dc3545';
        }
        
        if (cardHeader) {
            cardHeader.innerHTML = `
                <small class="text-muted">
                    <i class="fas fa-times text-danger"></i> 
                    执行失败 (耗时: ${data.execution_time || executionTime}s)
                </small>
            `;
        }
        
        if (outputElement.querySelector('.card')) {
            outputElement.querySelector('.card').className = 'card border-danger';
        }
    }
    
    outputElement.style.display = 'block';
    
    // 滚动到结果区域
    outputElement.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

/**
 * 显示执行错误
 */
function displayExecutionError(errorMessage, outputElement) {
    if (!outputElement) return;
    
    const outputContent = outputElement.querySelector('.output-content');
    const cardHeader = outputElement.querySelector('.card-header');
    
    if (outputContent) {
        // 处理复杂的输出元素
        outputContent.textContent = errorMessage;
        outputContent.className = 'output-content mb-0 text-danger';
    } else {
        // 处理简单的输出元素
        outputElement.textContent = errorMessage;
        outputElement.style.color = '#dc3545';
    }
    
    if (cardHeader) {
        cardHeader.innerHTML = `
            <small class="text-muted">
                <i class="fas fa-times text-danger"></i> 执行失败
            </small>
        `;
    }
    
    if (outputElement.querySelector('.card')) {
        outputElement.querySelector('.card').className = 'card border-danger';
    }
    outputElement.style.display = 'block';
}

/**
 * 显示通知消息
 */
function showNotification(message, type = 'info', duration = 3000) {
    const types = {
        'success': { icon: 'check', class: 'alert-success' },
        'error': { icon: 'times', class: 'alert-danger' },
        'warning': { icon: 'exclamation-triangle', class: 'alert-warning' },
        'info': { icon: 'info-circle', class: 'alert-info' }
    };
    
    const config = types[type] || types.info;
    
    const notification = document.createElement('div');
    notification.className = `alert ${config.class} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 100px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        <i class="fas fa-${config.icon} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // 自动移除
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, duration);
}

/**
 * 工具函数：格式化时间
 */
function formatTime(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString('zh-CN');
}

/**
 * 工具函数：转义HTML
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * 工具函数：解转义HTML
 */
function unescapeHtml(html) {
    const div = document.createElement('div');
    div.innerHTML = html;
    return div.textContent || div.innerText || '';
}

/**
 * 工具函数：防抖
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * 工具函数：节流
 */
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * 主题切换功能（预留）
 */
function toggleTheme() {
    const currentTheme = window.PythonLearningPlatform.currentTheme;
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    
    document.body.setAttribute('data-theme', newTheme);
    window.PythonLearningPlatform.currentTheme = newTheme;
    
    // 保存到本地存储
    localStorage.setItem('theme', newTheme);
    
    console.log(`主题已切换到: ${newTheme}`);
}

/**
 * 页面卸载时的清理
 */
window.addEventListener('beforeunload', function() {
    // 清理定时器、事件监听器等
    console.log('🧹 清理资源...');
});

// 导出到全局作用域
window.PythonLearningPlatform.utils = {
    executeCode,
    executeUserCode,
    showNotification,
    copyToClipboard,
    formatTime,
    escapeHtml,
    unescapeHtml,
    debounce,
    throttle,
    toggleTheme
};

// 测试函数
function testFunction() {
    console.log('🧪 测试函数被调用');
    alert('JavaScript 工作正常！');
    
    const codeInput = document.getElementById('codeInput');
    const output = document.getElementById('output');
    
    if (output) {
        output.textContent = '测试成功！JavaScript 正常工作。';
        output.style.color = '#28a745';
    }
}

// 直接导出到全局作用域以便模板调用
window.executeUserCode = executeUserCode;
window.executeCode = executeCode;
window.testFunction = testFunction;

console.log('📜 主JavaScript文件已加载');
console.log('🔧 测试函数是否可用:');
console.log('executeUserCode:', typeof window.executeUserCode);
console.log('executeCode:', typeof window.executeCode);
