import socket
import logging
import qrcode_terminal
from flask import Flask, redirect

from noplacelikehomely.server.webinterface.webinterface import api_bp
from noplacelikehomely.server.webinterface.webui import ui_bp

app = Flask(__name__)
app.register_blueprint(api_bp)
app.register_blueprint(ui_bp)

@app.route("/")
def index():
    # Redirect root to the UI
    return redirect("/ui")

def run_server(host='0.0.0.0', port=8000):
    # Determine local IP address for the QR code
    local_ip = socket.gethostbyname(socket.gethostname())
    url = f"http://{local_ip}:{port}"
    logging.info("Starting server at %s", url)
    print("Scan this QR code to access the UI:")
    qrcode_terminal.draw(url)
    app.run(host=host, port=port)
