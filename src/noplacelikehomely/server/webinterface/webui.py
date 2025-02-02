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
            <script src="https://cdn.tailwindcss.com"></script>
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
        </head>
        <body class="bg-gray-50 font-[Inter]">
            <div class="min-h-screen">
                <!-- Navbar -->
                <nav class="bg-white shadow-sm">
                    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                        <div class="flex justify-between h-16">
                            <div class="flex-shrink-0 flex items-center">
                                <h1 class="text-2xl font-semibold text-gray-900">noplacelike</h1>
                            </div>
                        </div>
                    </div>
                </nav>

                <!-- Main Content -->
                <main class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
                    <!-- Feature Grid -->
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <!-- Clipboard Card -->
                        <div class="bg-white overflow-hidden shadow rounded-lg">
                            <div class="p-6">
                                <h3 class="text-lg font-medium text-gray-900">Clipboard Sharing</h3>
                                <div class="mt-4">
                                    <textarea id="clipboard" 
                                            class="w-full h-32 p-2 border rounded-md"
                                            placeholder="Paste text here to share..."></textarea>
                                    <button onclick="shareClipboard()"
                                            class="mt-3 bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 transition-colors">
                                        Share Clipboard
                                    </button>
                                </div>
                            </div>
                        </div>

                        <!-- File Sharing Card -->
                        <div class="bg-white overflow-hidden shadow rounded-lg">
                            <div class="p-6">
                                <h3 class="text-lg font-medium text-gray-900">File Sharing</h3>
                                <div class="mt-4">
                                    <div class="border-2 border-dashed border-gray-300 rounded-md p-6 text-center">
                                        <input type="file" id="fileInput" class="hidden" multiple>
                                        <button onclick="document.getElementById('fileInput').click()"
                                                class="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 transition-colors">
                                            Select Files
                                        </button>
                                        <p class="mt-2 text-sm text-gray-600">or drag and drop files here</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- File List -->
                    <div class="mt-6 bg-white shadow rounded-lg">
                        <div class="p-6">
                            <h3 class="text-lg font-medium text-gray-900">Shared Files</h3>
                            <div id="fileList" class="mt-4 divide-y divide-gray-200">
                                <!-- Files will be listed here dynamically -->
                            </div>
                        </div>
                    </div>
                </main>
            </div>

            <script>
                // Fetch and display files
                async function updateFileList() {
                    const response = await fetch('/api/files');
                    const data = await response.json();
                    const fileList = document.getElementById('fileList');
                    fileList.innerHTML = data.files.map(file => `
                        <div class="py-4 flex justify-between items-center">
                            <span class="text-gray-900">${file}</span>
                            <button onclick="downloadFile('${file}')"
                                    class="text-indigo-600 hover:text-indigo-900">
                                Download
                            </button>
                        </div>
                    `).join('');
                }

                // Share clipboard content
                async function shareClipboard() {
                    const text = document.getElementById('clipboard').value;
                    await fetch('/api/clipboard', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({text})
                    });
                    alert('Clipboard shared successfully!');
                }

                // Initialize
                updateFileList();
            </script>
        </body>
        </html>
    ''')
