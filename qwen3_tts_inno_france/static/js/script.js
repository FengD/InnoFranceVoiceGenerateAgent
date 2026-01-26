// Tab切换功能
document.querySelectorAll('.tab-button').forEach(button => {
    button.addEventListener('click', () => {
        // 移除所有活动状态
        document.querySelectorAll('.tab-button').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelectorAll('.tab-pane').forEach(pane => {
            pane.classList.remove('active');
        });
        
        // 添加当前活动状态
        button.classList.add('active');
        const tabId = button.getAttribute('data-tab');
        document.getElementById(tabId).classList.add('active');
    });
});

// 速度滑块值显示
document.getElementById('design-speed').addEventListener('input', function() {
    document.getElementById('design-speed-value').textContent = this.value;
});

document.getElementById('clone-speed').addEventListener('input', function() {
    document.getElementById('clone-speed-value').textContent = this.value;
});

// 声音设计功能
document.getElementById('design-btn').addEventListener('click', async function() {
    const button = this;
    const originalText = button.textContent;
    
    try {
        button.textContent = '生成中...';
        button.disabled = true;
        
        const text = document.getElementById('design-text').value;
        const language = document.getElementById('design-language').value;
        const instruct = document.getElementById('design-instruct').value;
        const output = document.getElementById('design-output').value;
        const speed = parseFloat(document.getElementById('design-speed').value);
        
        if (!text || !language || !instruct) {
            alert('请填写所有必填字段');
            return;
        }
        
        const response = await fetch('/voice-design', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text: text,
                language: language,
                instruct: instruct,
                output_path: output,
                speed: speed
            })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            // 显示结果
            document.getElementById('design-result').style.display = 'block';
            // 修改为相对路径，让浏览器能正确访问生成的文件
            document.getElementById('design-audio').src = output + '?' + new Date().getTime();  // 添加时间戳避免缓存
            document.getElementById('design-download').href = output;
            document.getElementById('design-download').style.display = 'inline-block';
        } else {
            alert('错误: ' + result.error);
        }
    } catch (error) {
        alert('请求失败: ' + error.message);
    } finally {
        button.textContent = originalText;
        button.disabled = false;
    }
});

// 声音克隆功能
document.getElementById('clone-btn').addEventListener('click', async function() {
    const button = this;
    const originalText = button.textContent;
    
    try {
        button.textContent = '生成中...';
        button.disabled = true;
        
        const text = document.getElementById('clone-text').value;
        const speakers = document.getElementById('clone-speakers').value;
        const output = document.getElementById('clone-output').value;
        const speed = parseFloat(document.getElementById('clone-speed').value);
        
        if (!text || !speakers) {
            alert('请填写所有必填字段');
            return;
        }
        
        let speakerConfigs;
        try {
            speakerConfigs = JSON.parse(speakers);
        } catch (e) {
            alert('说话人配置格式错误，请检查JSON格式');
            return;
        }
        
        const response = await fetch('/voice-clone', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text: text,
                speaker_configs: speakerConfigs,
                output_path: output,
                speed: speed
            })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            // 显示结果
            document.getElementById('clone-result').style.display = 'block';
            // 修改为相对路径，让浏览器能正确访问生成的文件
            document.getElementById('clone-audio').src = output + '?' + new Date().getTime();  // 添加时间戳避免缓存
            document.getElementById('clone-download').href = output;
            document.getElementById('clone-download').style.display = 'inline-block';
        } else {
            alert('错误: ' + result.error);
        }
    } catch (error) {
        alert('请求失败: ' + error.message);
    } finally {
        button.textContent = originalText;
        button.disabled = false;
    }
});