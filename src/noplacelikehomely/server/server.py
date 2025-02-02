import socket
import logging
import qrcode_terminal
import netifaces
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
    
    # Get all network interfaces
    for interface in netifaces.interfaces():
        try:
            # Get IPv4 addresses for this interface
            ifaddresses = netifaces.ifaddresses(interface)
            if netifaces.AF_INET in ifaddresses:
                for addr in ifaddresses[netifaces.AF_INET]:
                    ip = addr['addr']
                    # Only add non-loopback IPs
                    if not ip.startswith('127.'):
                        ips.add(ip)
        except Exception as e:
            logging.warning(f"Error getting IP for interface {interface}: {e}")
    
    # Always include localhost last
    ips.add('127.0.0.1')
    
    # Sort IPs to prioritize local network addresses
    return sorted(list(ips), key=lambda x: (
        # Priority order: 192.168.x.x first, then 10.x.x.x, then others
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
