from flask import Blueprint, render_template_string

ui_bp = Blueprint("ui", __name__, url_prefix="/ui")

@ui_bp.route("/")
def home():
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>noplacelike</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                /* Reset and base styles */
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body {
                    font-family: system-ui, -apple-system, sans-serif;
                    background: #f5f5f5;
                    color: #333;
                    line-height: 1.5;
                }

                /* Layout */
                .navbar {
                    background: white;
                    padding: 1rem;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                }

                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 1rem;
                }

                .grid {
                    display: grid;
                    gap: 1rem;
                    margin: 1rem 0;
                }

                @media (min-width: 768px) {
                    .grid { grid-template-columns: 1fr 1fr; }
                }

                /* Cards */
                .card {
                    background: white;
                    border-radius: 8px;
                    padding: 1.5rem;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                }

                /* Form elements */
                .textarea, .upload-area input { width: 100%; }
                .textarea {
                    height: 8rem;
                    padding: 0.5rem;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    margin: 0.5rem 0;
                    font-family: inherit;
                }

                .button {
                    background: #4444ff;
                    color: white;
                    border: none;
                    padding: 0.5rem 1rem;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 1rem;
                }

                .button:hover {
                    background: #3333dd;
                }

                /* File upload area */
                .upload-area {
                    border: 2px dashed #ddd;
                    border-radius: 4px;
                    padding: 2rem;
                    text-align: center;
                }

                /* File list */
                .file-list {
                    margin-top: 1rem;
                }

                .file-item {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 0.75rem 0;
                    border-bottom: 1px solid #eee;
                }

                .file-item:last-child {
                    border-bottom: none;
                }

                .link-button {
                    color: #4444ff;
                    text-decoration: none;
                    cursor: pointer;
                }

                .link-button:hover {
                    text-decoration: underline;
                }
            </style>
        </head>
        <body>
            <nav class="navbar">
                <div class="container">
                    <h1 style="font-size: 1.5rem; font-weight: 600;">noplacelike</h1>
                </div>
            </nav>

            <main class="container">
                <div class="grid">
                    <!-- Clipboard Card -->
                    <div class="card">
                        <h3 style="font-size: 1.2rem; margin-bottom: 1rem;">Clipboard Sharing</h3>
                        <textarea id="clipboard" class="textarea" 
                                placeholder="Paste text here to share..."></textarea>
                        <button onclick="shareClipboard()" class="button">
                            Share Clipboard
                        </button>
                    </div>

                    <!-- File Sharing Card -->
                    <div class="card">
                        <h3 style="font-size: 1.2rem; margin-bottom: 1rem;">File Sharing</h3>
                        <div class="upload-area">
                            <input type="file" id="fileInput" style="display: none;" multiple onchange="uploadFiles()">
                            <button onclick="document.getElementById('fileInput').click()" 
                                    class="button">
                                Select Files
                            </button>
                            <p style="margin-top: 0.5rem; color: #666;">
                                or drag and drop files here
                            </p>
                        </div>
                    </div>
                </div>

                <!-- File List -->
                <div class="card">
                    <h3 style="font-size: 1.2rem; margin-bottom: 1rem;">Shared Files</h3>
                    <div id="fileList" class="file-list">
                        <!-- Files will be listed here dynamically -->
                    </div>
                </div>
            </main>

            <script>
                // Fetch and display files
                async function updateFileList() {
                    try {
                        const response = await fetch('/api/files');
                        const data = await response.json();
                        const fileList = document.getElementById('fileList');
                        fileList.innerHTML = data.files.map(file => `
                            <div class="file-item">
                                <span>${file}</span>
                                <button onclick="downloadFile('${file}')" 
                                        class="link-button">Download</button>
                            </div>
                        `).join('');
                    } catch (error) {
                        console.error('Error updating file list:', error);
                    }
                }

                // Share clipboard content
                async function shareClipboard() {
                    const text = document.getElementById('clipboard').value;
                    try {
                        await fetch('/api/clipboard', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({text})
                        });
                        alert('Clipboard shared successfully!');
                    } catch (error) {
                        alert('Failed to share clipboard: ' + error.message);
                    }
                }

                async function uploadFiles() {
                    const input = document.getElementById('fileInput');
                    const files = input.files;
                    if (!files.length) return;
                    for (let file of files) {
                        const formData = new FormData();
                        formData.append('file', file);
                        try {
                            const res = await fetch('/api/files', {
                                method: 'POST',
                                body: formData
                            });
                            const result = await res.json();
                            if (res.ok) {
                                console.log('Uploaded:', result.filename);
                            } else {
                                alert(result.error || 'Upload failed');
                            }
                        } catch (error) {
                            console.error('Upload error:', error);
                        }
                    }
                    input.value = '';
                    updateFileList();
                }

                function downloadFile(filename) {
                    window.open('/api/files/' + filename, '_blank');
                }

                // Initialize
                updateFileList();
            </script>
        </body>
        </html>
    ''')
