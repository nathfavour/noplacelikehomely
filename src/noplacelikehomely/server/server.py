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
    """Get all valid IPv4 addresses including local network IPs."""
    ips = set()
    
    try:
        # Get hostname-based IP
        hostname_ip = socket.gethostbyname(socket.gethostname())
        if not hostname_ip.startswith('127.'):
            ips.add(hostname_ip)
            
        # Try to get additional IPs by creating a temporary socket
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            # We don't actually connect, just use this to get local IP
            s.connect(('8.8.8.8', 80))
            local_ip = s.getsockname()[0]
            if not local_ip.startswith('127.'):
                ips.add(local_ip)
    except Exception as e:
        logging.warning(f"Error getting IP addresses: {e}")
    
    # Always include localhost
    ips.add('127.0.0.1')
    
    # Sort IPs to prioritize local network addresses
    return sorted(list(ips), key=lambda x: (
        (0 if x.startswith('192.168.') else
         1 if x.startswith('10.') else
         2 if x.startswith('172.') else 3,
         x)
    ))

def run_server(host='0.0.0.0', port=8000):
    """Run the server and display QR codes for all valid interfaces."""
    ips = get_all_ips()
    urls = [f"http://{ip}:{port}" for ip in ips]
    
    print("\nServer accessible at:")
    for url in urls:
        if '192.168.' in url or '10.' in url:
            print("\n=== Local Network Access (preferred) ===")
        elif '127.0.0.1' in url:
            print("\n=== Localhost Access ===")
        else:
            print("\n=== Other Network Access ===")
            
        print(f"URL: {url}")
        qrcode_terminal.draw(url)
        print("-" * 50)

    try:
        app.run(host=host, port=port)
    except Exception as e:
        logging.exception("Server encountered an error:")
        raise
