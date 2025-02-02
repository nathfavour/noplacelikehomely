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

def get_all_ips():
    """Return a list of all IPv4 addresses for the current host."""
    ips = set()
    try:
        hostname = socket.gethostname()
        for ip in socket.gethostbyname_ex(hostname)[2]:
            ips.add(ip)
    except Exception as e:
        logging.warning("Error getting host IPs: %s", e)
    # Always include localhost
    ips.add("127.0.0.1")
    return list(ips)

def run_server(host='0.0.0.0', port=8000):
    ips = get_all_ips()
    urls = [f"http://{ip}:{port}" for ip in ips]
    for url in urls:
        logging.info("Server interface available at %s", url)
        print("Scan this QR code for:", url)
        qrcode_terminal.draw(url)
    try:
        app.run(host=host, port=port)
    except Exception as e:
        logging.exception("Server encountered an error:")
        raise
