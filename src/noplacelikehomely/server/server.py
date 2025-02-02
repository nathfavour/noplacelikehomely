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

def get_local_ip():
    """Robustly determine the local IP address with a fallback."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Connect to an external host; doesn't actually send data.
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception as e:
        logging.warning("Could not determine local IP, defaulting to 127.0.0.1: %s", e)
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

def run_server(host='0.0.0.0', port=8000):
    # Use the robust local IP determination
    local_ip = get_local_ip()
    url = f"http://{local_ip}:{port}"
    logging.info("Starting server at %s", url)
    print("Scan this QR code to access the UI:")
    qrcode_terminal.draw(url)
    try:
        app.run(host=host, port=port)
    except Exception as e:
        logging.exception("Server encountered an error:")
        raise
