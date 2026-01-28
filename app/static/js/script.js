// Tab switching
document.querySelectorAll('.tab-button').forEach(button => {
    button.addEventListener('click', () => {
        // Clear active state
        document.querySelectorAll('.tab-button').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelectorAll('.tab-pane').forEach(pane => {
            pane.classList.remove('active');
        });
        
        // Activate current tab
        button.classList.add('active');
        const tabId = button.getAttribute('data-tab');
        document.getElementById(tabId).classList.add('active');
    });
});

// Speed slider updates
document.getElementById('design-speed').addEventListener('input', function() {
    document.getElementById('design-speed-value').textContent = this.value;
});

document.getElementById('clone-speed').addEventListener('input', function() {
    document.getElementById('clone-speed-value').textContent = this.value;
});

// Voice design
document.getElementById('design-btn').addEventListener('click', async function() {
    const button = this;
    const originalText = button.textContent;
    
    try {
        button.textContent = 'Generating...';
        button.disabled = true;
        
        const text = document.getElementById('design-text').value;
        const language = document.getElementById('design-language').value;
        const instruct = document.getElementById('design-instruct').value;
        const output = document.getElementById('design-output').value;
        const speed = parseFloat(document.getElementById('design-speed').value);
        
        if (!text || !language || !instruct) {
            alert('Please fill in all required fields.');
            return;
        }
        
        const response = await fetch('/voice_design', {
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
        
        if (response.ok) {
        // Handle audio stream
            const blob = await response.blob();
            const audioUrl = URL.createObjectURL(blob);
            
            // Show results
            document.getElementById('design-result').style.display = 'block';
            document.getElementById('design-audio').src = audioUrl;
            document.getElementById('design-download').href = audioUrl;
            document.getElementById('design-download').download = output || 'output_voice_design.wav';
            document.getElementById('design-download').style.display = 'inline-block';
        } else {
            // Try parsing error response
            try {
                const errorResult = await response.json();
                alert('Error: ' + errorResult.error);
            } catch (e) {
                alert('Request failed: ' + response.statusText);
            }
        }
    } catch (error) {
        alert('Request failed: ' + error.message);
    } finally {
        button.textContent = originalText;
        button.disabled = false;
    }
});

// Voice cloning
document.getElementById('clone-btn').addEventListener('click', async function() {
    const button = this;
    const originalText = button.textContent;
    
    try {
        button.textContent = 'Generating...';
        button.disabled = true;
        
        const text = document.getElementById('clone-text').value;
        const speakers = document.getElementById('clone-speakers').value;
        const output = document.getElementById('clone-output').value;
        const speed = parseFloat(document.getElementById('clone-speed').value);
        
        if (!text || !speakers) {
            alert('Please fill in all required fields.');
            return;
        }
        
        let speakerConfigs;
        try {
            speakerConfigs = JSON.parse(speakers);
        } catch (e) {
            alert('Speaker config JSON is invalid.');
            return;
        }
        
        const response = await fetch('/voice_clone', {
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
        
        if (response.ok) {
        // Handle audio stream
            const blob = await response.blob();
            const audioUrl = URL.createObjectURL(blob);
            
            // Show results
            document.getElementById('clone-result').style.display = 'block';
            document.getElementById('clone-audio').src = audioUrl;
            document.getElementById('clone-download').href = audioUrl;
            document.getElementById('clone-download').download = output || 'output_voice_clone.wav';
            document.getElementById('clone-download').style.display = 'inline-block';
        } else {
            // Try parsing error response
            try {
                const errorResult = await response.json();
                alert('Error: ' + errorResult.error);
            } catch (e) {
                alert('Request failed: ' + response.statusText);
            }
        }
    } catch (error) {
        alert('Request failed: ' + error.message);
    } finally {
        button.textContent = originalText;
        button.disabled = false;
    }
});