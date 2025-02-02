from flask import Blueprint, render_template_string

ui_bp = Blueprint("ui", __name__, url_prefix="/ui")

@ui_bp.route("/")
def home():
    # ...Implement rich UI rendering as needed...
    return render_template_string('''
        <html>
          <body>
            <h1>noplacelike Web UI</h1>
            <ul>
              <li><a href="/api/clipboard">Clipboard API</a></li>
              <li><a href="/api/files">Files API</a></li>
            </ul>
          </body>
        </html>
    ''')
