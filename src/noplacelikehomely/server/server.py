import socket
import logging
import qrcode_terminal
from flask import Flask, redirect

from noplacelikehomely.server.webinterface.webinterface import api_bp
from noplacelikehomely.server.webinterface.webui import ui_bp

app = Flask(__name__)
app.register_blueprint(api_bp)
app.register_blueprint(ui_bp)

# Apply secure settings for a localserver environment
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    REMEMBER_COOKIE_HTTPONLY=True,
    # Add any additional secure settings as needed
)

@app.route("/")
def index():
    # Redirect root to the UI
    return redirect("/ui")

def get_all_ips():
    """Return all IPv4 addresses (including local network ones) for this host."""
    ips = set()
    try:
        # Retrieve all addresses via getaddrinfo
        for info in socket.getaddrinfo(socket.gethostname(), None):
            if info[0] == socket.AF_INET:
                ip = info[4][0]
                # Exclude loopback if found; we'll add it manually later
                if not ip.startswith("127."):
                    ips.add(ip)
    except Exception as e:
        logging.warning("Error getting interface IPs: %s", e)
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
        # Running without SSL context for local server; secure settings are applied via app.config
        app.run(host=host, port=port)
    except Exception as e:
        logging.exception("Server encountered an error:")
        raise
