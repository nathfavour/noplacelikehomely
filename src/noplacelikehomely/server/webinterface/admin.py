from flask import Blueprint, render_template_string, jsonify, request
from noplacelikehomely.config import load_config, update_config
import os

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("/")
def admin_panel():
    config = load_config()
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>noplacelike Admin</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                /* Modern Admin UI Styles */
                :root {
                    --primary: #4444ff;
                    --bg-dark: #1a1a1a;
                    --text-light: #ffffff;
                }
                
                * { margin: 0; padding: 0; box-sizing: border-box; }
                
                body {
                    font-family: system-ui, -apple-system, sans-serif;
                    background: #f5f5f5;
                    color: #333;
                }

                .admin-header {
                    background: var(--bg-dark);
                    color: var(--text-light);
                    padding: 1rem;
                    position: fixed;
                    width: 100%;
                    top: 0;
                    z-index: 100;
                }

                .main-content {
                    margin-top: 60px;
                    padding: 2rem;
                }

                .section {
                    background: white;
                    border-radius: 8px;
                    padding: 1.5rem;
                    margin-bottom: 1.5rem;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }

                .scroll-container {
                    max-height: 300px;
                    overflow-y: auto;
                    border: 1px solid #eee;
                    border-radius: 4px;
                    padding: 1rem;
                    margin: 1rem 0;
                }

                .dir-table {
                    width: 100%;
                    border-collapse: collapse;
                }

                .dir-table th, .dir-table td {
                    padding: 0.75rem;
                    text-align: left;
                    border-bottom: 1px solid #eee;
                }

                .button {
                    background: var(--primary);
                    color: white;
                    border: none;
                    padding: 0.5rem 1rem;
                    border-radius: 4px;
                    cursor: pointer;
                }

                .button:hover { opacity: 0.9; }

                .input-group {
                    display: flex;
                    gap: 0.5rem;
                    margin: 1rem 0;
                }

                input[type="text"] {
                    flex: 1;
                    padding: 0.5rem;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                }
            </style>
        </head>
        <body>
            <header class="admin-header">
                <h1>noplacelike Server Administration</h1>
            </header>

            <main class="main-content">
                <section class="section">
                    <h2>Audio Streaming Directories</h2>
                    <div class="input-group">
                        <input type="text" id="newDir" placeholder="Enter directory path">
                        <button class="button" onclick="addDirectory()">Add Directory</button>
                    </div>
                    
                    <div class="scroll-container">
                        <table class="dir-table">
                            <thead>
                                <tr>
                                    <th>Directory Path</th>
                                    <th>Status</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody id="dirList">
                                <!-- Directories will be listed here -->
                            </tbody>
                        </table>
                    </div>
                </section>

                <section class="section">
                    <h2>Current Audio Files</h2>
                    <div class="scroll-container" id="audioFilesList">
                        <!-- Audio files will be listed here -->
                    </div>
                </section>
            </main>

            <script>
                async function loadDirectories() {
                    try {
                        const res = await fetch('/admin/dirs');
                        const data = await res.json();
                        const tbody = document.getElementById('dirList');
                        tbody.innerHTML = data.dirs.map(dir => `
                            <tr>
                                <td>${dir}</td>
                                <td>${checkDirStatus(dir)}</td>
                                <td>
                                    <button class="button" onclick="removeDirectory('${dir}')">Remove</button>
                                </td>
                            </tr>
                        `).join('');
                    } catch (error) {
                        console.error('Error loading directories:', error);
                    }
                }

                function checkDirStatus(dir) {
                    return 'Active'; // You can implement actual status checking
                }

                async function addDirectory() {
                    const input = document.getElementById('newDir');
                    const dir = input.value.trim();
                    if (!dir) return;

                    try {
                        const res = await fetch('/admin/dirs', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({dir})
                        });
                        const data = await res.json();
                        if (data.status === 'success') {
                            input.value = '';
                            loadDirectories();
                        } else {
                            alert(data.error || 'Failed to add directory');
                        }
                    } catch (error) {
                        alert('Error adding directory: ' + error.message);
                    }
                }

                async function removeDirectory(dir) {
                    try {
                        const res = await fetch('/admin/dirs', {
                            method: 'DELETE',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({dir})
                        });
                        const data = await res.json();
                        if (data.status === 'success') {
                            loadDirectories();
                        } else {
                            alert(data.error || 'Failed to remove directory');
                        }
                    } catch (error) {
                        alert('Error removing directory: ' + error.message);
                    }
                }

                // Initialize
                loadDirectories();
            </script>
        </body>
        </html>
    ''')

@admin_bp.route("/dirs", methods=["GET", "POST", "DELETE"])
def manage_dirs():
    config = load_config()
    
    if request.method == "GET":
        return jsonify({"dirs": config.get("audio_folders", [])})
    
    elif request.method == "POST":
        data = request.get_json()
        dir_path = os.path.expanduser(data.get("dir", ""))
        if not dir_path:
            return jsonify({"error": "No directory specified"}), 400

        current_dirs = config.get("audio_folders", [])
        if dir_path not in current_dirs:
            current_dirs.append(dir_path)
            update_config(audio_folders=current_dirs)
        return jsonify({"status": "success"})
    
    elif request.method == "DELETE":
        data = request.get_json()
        dir_path = data.get("dir")
        if not dir_path:
            return jsonify({"error": "No directory specified"}), 400

        current_dirs = config.get("audio_folders", [])
        if dir_path in current_dirs:
            current_dirs.remove(dir_path)
            update_config(audio_folders=current_dirs)
        return jsonify({"status": "success"})
