"""
C Programming Recovery Tracker - Desktop Application
Runs the exact same web UI inside a native window using pywebview.
Includes a local HTTP server for API + static file serving.
Features export functionality to share progress with the website.
"""

import os
import sys
import json
import threading
import datetime
import http.server
import socketserver
import sqlite3
import webbrowser
import time

try:
    import webview
except ImportError:
    print("ERROR: pywebview is required. Install with: pip install pywebview")
    sys.exit(1)

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# --------------- PATH CONFIGURATION ---------------

PORT = 0  # Will auto-assign a free port
_assigned_port = [0]

# Base directory for PyInstaller frozen app
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PUBLIC_DIR = os.path.join(BASE_DIR, 'public')

# User data directory for persistent progress outside frozen EXE
USER_DATA_DIR = os.path.join(os.path.expanduser('~'), '.c_recovery_tracker')
os.makedirs(USER_DATA_DIR, exist_ok=True)

DATA_FILE = os.path.join(USER_DATA_DIR, 'progress.json')
DB_FILE = r"C:\Users\athar\Downloads\c_recovery_questions.db"

# --------------- GAME LOGIC CONSTANTS ---------------

RANKS = [
    {"name": "\U0001f95a C Beginner", "minXP": 0, "maxXP": 499},
    {"name": "\U0001f331 C Learner", "minXP": 500, "maxXP": 1499},
    {"name": "\u2694\ufe0f C Problem Solver", "minXP": 1500, "maxXP": 2999},
    {"name": "\U0001f525 C Programmer", "minXP": 3000, "maxXP": 4999},
    {"name": "\U0001f4bb C Developer", "minXP": 5000, "maxXP": 7499},
    {"name": "\U0001f451 C Master", "minXP": 7500, "maxXP": 999999}
]

XP_TABLE = {"basic": 100, "medium": 200, "hard": 300, "boss": 500}
LEVEL_ORDER = ["basic", "medium", "hard", "boss"]

# --------------- PROGRESS DATA MANAGEMENT ---------------

def read_progress():
    if not os.path.exists(DATA_FILE):
        initial = {
            "totalXP": 0,
            "rank": "\U0001f95a C Beginner",
            "currentDay": 1,
            "currentLevel": "basic",
            "completedLevels": [],
            "unlockedLevels": ["day1_basic"],
            "badges": [],
            "streak": 0,
            "longestStreak": 0,
            "lastCompletedDate": None,
            "activityHistory": [{
                "id": "init",
                "title": "Course Initialized",
                "description": "Began C Programming Recovery Roadmap!",
                "xp": 0,
                "timestamp": datetime.datetime.now().isoformat(),
                "type": "info"
            }],
            "perfectLevels": []
        }
        write_progress(initial)
        return initial
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def write_progress(data):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def sync_to_sqlite(data):
    if not os.path.exists(DB_FILE):
        return
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE profile SET total_xp = ?, current_day = ?, current_level = ?, current_streak = ?, longest_streak = ? WHERE id = 1;",
            (data.get("totalXP", 0), data.get("currentDay", 1), data.get("currentLevel", "basic"),
             data.get("streak", 0), data.get("longestStreak", 0))
        )
        conn.commit()
        conn.close()
    except Exception:
        pass

def calculate_rank(xp):
    for r in RANKS:
        if r["minXP"] <= xp <= r["maxXP"]:
            return r["name"]
    return "\U0001f451 C Master"

def get_next_level(day, level):
    idx = LEVEL_ORDER.index(level)
    if idx < len(LEVEL_ORDER) - 1:
        return day, LEVEL_ORDER[idx + 1]
    else:
        if day < 30:
            return day + 1, "basic"
        return None, None

def check_badges(data):
    earned = set(data.get("badges", []))
    completed = data.get("completedLevels", [])
    perfect = data.get("perfectLevels", [])
    total_xp = data.get("totalXP", 0)

    if any("_basic" in lvl for lvl in completed):
        earned.add("first_steps")
    if any("_medium" in lvl for lvl in completed):
        earned.add("logic_builder")
    if any("_hard" in lvl for lvl in completed):
        earned.add("problem_solver")
    if any("_boss" in lvl for lvl in completed):
        earned.add("boss_slayer")
    if len(perfect) > 0:
        earned.add("perfectionist")
    if len(completed) >= 3:
        earned.add("speed_runner")
    if len(completed) >= 20 or total_xp >= 3000:
        earned.add("c_programmer")
    if "day30_boss" in completed or total_xp >= 7500:
        earned.add("c_master")

    data["badges"] = list(earned)

def process_level_completion(day, level, is_perfect=False):
    data = read_progress()
    key = f"day{day}_{level}"

    if key in data.get("completedLevels", []):
        return {
            "success": False,
            "message": f"Level Day {day} {level.upper()} has already been completed! No duplicate XP awarded.",
            "data": data
        }

    if key not in data.get("unlockedLevels", []):
        return {
            "success": False,
            "message": f"Level Day {day} {level.upper()} is currently locked!",
            "data": data
        }

    base_xp = XP_TABLE.get(level, 100)
    bonus_xp = 100 if is_perfect else 0
    earned_xp = base_xp + bonus_xp

    data["totalXP"] = data.get("totalXP", 0) + earned_xp
    old_rank = data.get("rank", "\U0001f95a C Beginner")
    data["rank"] = calculate_rank(data["totalXP"])

    data.setdefault("completedLevels", []).append(key)
    if is_perfect:
        data.setdefault("perfectLevels", []).append(key)

    next_day, next_level = get_next_level(day, level)
    newly_unlocked = None
    if next_day is not None and next_level is not None:
        next_key = f"day{next_day}_{next_level}"
        if next_key not in data.get("unlockedLevels", []):
            data["unlockedLevels"].append(next_key)
            newly_unlocked = next_key
        data["currentDay"] = next_day
        data["currentLevel"] = next_level

    today_str = datetime.date.today().isoformat()
    last_date = data.get("lastCompletedDate")
    if last_date == today_str:
        pass
    elif last_date == (datetime.date.today() - datetime.timedelta(days=1)).isoformat():
        data["streak"] = data.get("streak", 0) + 1
    else:
        data["streak"] = 1

    if data["streak"] > data.get("longestStreak", 0):
        data["longestStreak"] = data["streak"]

    data["lastCompletedDate"] = today_str

    old_badges = set(data.get("badges", []))
    check_badges(data)
    new_badges = list(set(data["badges"]) - old_badges)

    activity_item = {
        "id": f"act_{len(data.get('activityHistory', [])) + 1}",
        "title": f"Day {day} \u2014 {level.upper()} Completed",
        "description": f"Earned +{earned_xp} XP" + (" (Includes \U0001f4af Perfect Bonus!)" if is_perfect else ""),
        "xp": earned_xp,
        "day": day,
        "level": level,
        "perfect": is_perfect,
        "timestamp": datetime.datetime.now().isoformat(),
        "type": "completion"
    }
    data.setdefault("activityHistory", []).insert(0, activity_item)

    write_progress(data)
    sync_to_sqlite(data)

    return {
        "success": True,
        "message": f"Congratulations! Day {day} {level.upper()} marked as complete.",
        "earnedXP": earned_xp,
        "baseXP": base_xp,
        "bonusXP": bonus_xp,
        "totalXP": data["totalXP"],
        "rank": data["rank"],
        "rankUp": old_rank != data["rank"],
        "newBadges": new_badges,
        "nextUnlocked": newly_unlocked,
        "data": data
    }

# --------------- DESKTOP-SPECIFIC INJECTED JS ---------------

# This JavaScript is injected into the web page after load to add the
# Export Progress button (desktop-only feature) and make the Backup & Export
# modal show the desktop-specific export options.
DESKTOP_INJECT_JS = r"""
(function() {
  // Wait for DOM to be fully ready
  function injectDesktopFeatures() {
    // === 1. Add "Export to Website" button in the header ===
    var headerActions = document.querySelector('.header-actions');
    if (headerActions && !document.getElementById('btnDesktopExport')) {
      var exportBtn = document.createElement('button');
      exportBtn.id = 'btnDesktopExport';
      exportBtn.className = 'btn btn-primary';
      exportBtn.innerHTML = '<span class="btn-icon">📤</span> Export for Website';
      exportBtn.title = 'Export progress JSON to import in website';
      exportBtn.style.background = 'linear-gradient(135deg, #059669, #047857)';
      exportBtn.style.boxShadow = '0 4px 14px rgba(5, 150, 105, 0.3)';
      exportBtn.onclick = function() {
        exportProgressForWebsite();
      };
      // Insert before the audio toggle button
      var audioBtn = document.getElementById('btnAudioToggle');
      if (audioBtn) {
        headerActions.insertBefore(exportBtn, audioBtn);
      } else {
        headerActions.appendChild(exportBtn);
      }
    }

    // === 2. Modify the Data Modal to add desktop-specific export section ===
    var dataModalBody = document.querySelector('#dataModal .modal-body');
    if (dataModalBody && !document.getElementById('desktopExportSection')) {
      var exportSection = document.createElement('div');
      exportSection.id = 'desktopExportSection';
      exportSection.className = 'data-option-box';
      exportSection.style.background = 'linear-gradient(135deg, #ecfdf5, #d1fae5)';
      exportSection.style.border = '2px solid #059669';
      exportSection.innerHTML = `
        <h3>📤 Export Progress for Website Import</h3>
        <p style="margin-bottom: 12px; font-size: 13px; color: #065f46;">
          Download your progress as a JSON file that can be imported into the web version of the tracker.
          This syncs your desktop progress to the website.
        </p>
        <button class="btn btn-success" id="btnDesktopExportModal" style="width: 100%;">
          📤 Download Export File for Website
        </button>
      `;
      // Insert at the top of the modal body
      dataModalBody.insertBefore(exportSection, dataModalBody.firstChild);

      // Add divider after export section
      var divider = document.createElement('hr');
      divider.className = 'divider';
      dataModalBody.insertBefore(divider, exportSection.nextSibling);

      // Attach click handler
      document.getElementById('btnDesktopExportModal').onclick = function() {
        exportProgressForWebsite();
      };
    }

    // === 3. Add a subtle desktop indicator badge ===
    var brand = document.querySelector('.brand-section');
    if (brand && !document.getElementById('desktopBadge')) {
      var badge = document.createElement('span');
      badge.id = 'desktopBadge';
      badge.textContent = 'DESKTOP';
      badge.style.cssText = 'font-size: 9px; font-weight: 800; letter-spacing: 1.5px; background: linear-gradient(135deg, #4f46e5, #0284c7); color: #fff; padding: 3px 10px; border-radius: 20px; margin-left: 12px; vertical-align: middle;';
      var title = brand.querySelector('.app-title');
      if (title) {
        title.appendChild(document.createTextNode(' '));
        title.appendChild(badge);
      }
    }
  }

  // Export function
  function exportProgressForWebsite() {
    fetch('/api/export_to_file')
      .then(function(res) { return res.json(); })
      .then(function(resData) {
        if (resData.success) {
          alert('✅ Progress Exported Successfully!\n\n📁 File saved to your Downloads folder:\n' + resData.filePath + '\n\nYou can now go to the website and click "Import from Desktop" to import this file.');
          showDesktopToast('✅ Saved to Downloads: ' + resData.fileName);
        } else {
          alert('Export failed: ' + (resData.message || 'Unknown error'));
        }
      })
      .catch(function(err) {
        alert('Export failed: ' + err.message);
      });
  }

  // Toast notification helper
  function showDesktopToast(message) {
    var existing = document.getElementById('desktopToast');
    if (existing) existing.remove();

    var toast = document.createElement('div');
    toast.id = 'desktopToast';
    toast.textContent = message;
    toast.style.cssText = 'position: fixed; bottom: 24px; right: 24px; background: linear-gradient(135deg, #059669, #047857); color: white; padding: 14px 24px; border-radius: 12px; font-family: Outfit, sans-serif; font-size: 14px; font-weight: 600; box-shadow: 0 8px 30px rgba(5, 150, 105, 0.4); z-index: 10000; animation: slideInToast 0.4s ease; transition: opacity 0.4s ease;';
    
    var style = document.createElement('style');
    style.textContent = '@keyframes slideInToast { from { transform: translateY(40px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }';
    document.head.appendChild(style);
    
    document.body.appendChild(toast);

    setTimeout(function() {
      toast.style.opacity = '0';
      setTimeout(function() { toast.remove(); }, 500);
    }, 4500);
  }

  // Run injection after short delay to ensure DOM is ready
  if (document.readyState === 'complete' || document.readyState === 'interactive') {
    setTimeout(injectDesktopFeatures, 500);
  } else {
    document.addEventListener('DOMContentLoaded', function() {
      setTimeout(injectDesktopFeatures, 500);
    });
  }

  // Also inject when navigating (in case of SPA behavior)
  window.addEventListener('load', function() {
    setTimeout(injectDesktopFeatures, 800);
  });
})();
"""

# --------------- HTTP SERVER FOR DESKTOP APP ---------------

class DesktopRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Serves static files from PUBLIC_DIR and handles API endpoints."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PUBLIC_DIR, **kwargs)

    def log_message(self, format, *args):
        # Suppress console logging in desktop mode
        pass

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        if self.path == '/api/progress':
            data = read_progress()
            self._send_json(200, data)
            return

        if self.path == '/api/export':
            data = read_progress()
            export_payload = {
                "_exportMeta": {
                    "source": "desktop_app",
                    "exportedAt": datetime.datetime.now().isoformat(),
                    "version": "1.0"
                },
                "progress": data
            }
            self._send_json(200, export_payload)
            return

        if self.path == '/api/export_to_file':
            try:
                data = read_progress()
                export_payload = {
                    "_exportMeta": {
                        "source": "desktop_app",
                        "exportedAt": datetime.datetime.now().isoformat(),
                        "version": "1.0"
                    },
                    "progress": data
                }
                downloads_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
                os.makedirs(downloads_dir, exist_ok=True)
                filename = f"c_recovery_export_{datetime.date.today().isoformat()}.json"
                file_path = os.path.join(downloads_dir, filename)

                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(export_payload, f, indent=2, ensure_ascii=False)

                self._send_json(200, {
                    "success": True,
                    "filePath": file_path,
                    "fileName": filename,
                    "message": f"Exported successfully to {file_path}"
                })
            except Exception as e:
                self._send_json(500, {"success": False, "message": str(e)})
            return

        if self.path == '/api/health':
            self._send_json(200, {"status": "ok", "app": "desktop", "port": _assigned_port[0]})
            return

        # Serve the index.html with injected desktop JS
        if self.path == '/' or self.path == '/index.html':
            self._serve_index_with_injection()
            return

        return super().do_GET()

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        payload = json.loads(body.decode('utf-8')) if body else {}

        if self.path == '/api/evaluate':
            day = int(payload.get('day', 1))
            level = str(payload.get('level', 'basic')).lower()
            perfect = bool(payload.get('perfect', False))
            result = process_level_completion(day, level, perfect)
            self._send_json(200, result)
            return

        elif self.path == '/api/save':
            write_progress(payload)
            sync_to_sqlite(payload)
            self._send_json(200, {"success": True, "message": "Saved!"})
            return

        elif self.path == '/api/reset':
            initial = {
                "totalXP": 0,
                "rank": "\U0001f95a C Beginner",
                "currentDay": 1,
                "currentLevel": "basic",
                "completedLevels": [],
                "unlockedLevels": ["day1_basic"],
                "badges": [],
                "streak": 0,
                "longestStreak": 0,
                "lastCompletedDate": None,
                "activityHistory": [{
                    "id": "reset",
                    "title": "Progress Reset",
                    "description": "Progress was reset to Day 1 Basic.",
                    "xp": 0,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "type": "warning"
                }],
                "perfectLevels": []
            }
            write_progress(initial)
            sync_to_sqlite(initial)
            self._send_json(200, {"success": True, "data": initial})
            return

        elif self.path == '/api/import':
            # Import progress data (from website export or manual)
            if "progress" in payload:
                progress_data = payload["progress"]
            else:
                progress_data = payload

            if isinstance(progress_data, dict) and "totalXP" in progress_data:
                write_progress(progress_data)
                sync_to_sqlite(progress_data)
                self._send_json(200, {"success": True, "message": "Progress imported successfully!", "data": progress_data})
            else:
                self._send_json(400, {"success": False, "message": "Invalid progress data format."})
            return

        self.send_error(404, "Endpoint not found")

    def _send_json(self, status, data):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def _serve_index_with_injection(self):
        """Serve index.html with desktop-specific JS injected before </body>."""
        index_path = os.path.join(PUBLIC_DIR, 'index.html')
        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                html = f.read()

            # Inject the desktop JS before </body>
            injection = f"\n<script>\n{DESKTOP_INJECT_JS}\n</script>\n"
            html = html.replace('</body>', injection + '</body>')

            encoded = html.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)
        except Exception as e:
            self.send_error(500, f"Error serving index: {e}")


def find_free_port():
    """Find a free TCP port on localhost."""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]


def start_server(port):
    """Start the embedded HTTP server."""
    _assigned_port[0] = port
    try:
        # Allow address reuse to avoid "address already in use" errors
        socketserver.TCPServer.allow_reuse_address = True
        with socketserver.TCPServer(("127.0.0.1", port), DesktopRequestHandler) as httpd:
            httpd.serve_forever()
    except Exception as e:
        print(f"Server error: {e}")


def main():
    # Find a free port to avoid conflicts
    port = find_free_port()
    _assigned_port[0] = port

    # Start HTTP server in background thread
    srv_thread = threading.Thread(target=start_server, args=(port,), daemon=True)
    srv_thread.start()

    # Give server a moment to start
    time.sleep(0.3)

    # Create native WebView desktop application window
    window = webview.create_window(
        title="C Programming Recovery Tracker — Desktop",
        url=f"http://127.0.0.1:{port}",
        width=1400,
        height=900,
        resizable=True,
        min_size=(960, 640),
        text_select=True
    )

    # Start the webview GUI (blocking call)
    webview.start(debug=False)


if __name__ == '__main__':
    main()
