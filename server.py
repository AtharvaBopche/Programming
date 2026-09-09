import http.server
import socketserver
import json
import os
import datetime
import sys
import sqlite3

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

PORT = 8000
DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'progress.json')
DB_FILE = r"C:\Users\athar\Downloads\c_recovery_with_advanced_dsa.db"
PUBLIC_DIR = os.path.join(os.path.dirname(__file__), 'public')

RANKS = [
    {"name": "🥚 C Beginner", "minXP": 0, "maxXP": 499},
    {"name": "🌱 C Learner", "minXP": 500, "maxXP": 1499},
    {"name": "⚔️ C Problem Solver", "minXP": 1500, "maxXP": 2999},
    {"name": "🔥 C Programmer", "minXP": 3000, "maxXP": 4999},
    {"name": "💻 C Developer", "minXP": 5000, "maxXP": 7499},
    {"name": "👑 C Master", "minXP": 7500, "maxXP": 11999},
    {"name": "🌳 DSA Specialist", "minXP": 12000, "maxXP": 17999},
    {"name": "⚡ Algorithm Architect", "minXP": 18000, "maxXP": 24999},
    {"name": "🚀 DSA Grandmaster", "minXP": 25000, "maxXP": 999999}
]

XP_TABLE = {
    "basic": 100,
    "medium": 200,
    "hard": 300,
    "boss": 500
}

LEVEL_ORDER = ["basic", "medium", "hard", "boss"]

def get_next_level(day, level):
    idx = LEVEL_ORDER.index(level)
    if idx < len(LEVEL_ORDER) - 1:
        return day, LEVEL_ORDER[idx + 1]
    else:
        if day < 50:
            return day + 1, "basic"
        return None, None

def calculate_rank(xp):
    for r in RANKS:
        if r["minXP"] <= xp <= r["maxXP"]:
            return r["name"]
    return "🚀 DSA Grandmaster"

def read_progress():
    if not os.path.exists(DATA_FILE):
        initial = {
            "totalXP": 0,
            "rank": "🥚 C Beginner",
            "currentDay": 1,
            "currentLevel": "basic",
            "completedLevels": [],
            "unlockedLevels": ["day1_basic"],
            "badges": [],
            "streak": 0,
            "longestStreak": 0,
            "lastCompletedDate": None,
            "activityHistory": [
                {
                    "id": "init",
                    "title": "Course Initialized",
                    "description": "Began C Programming Recovery Roadmap!",
                    "xp": 0,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "type": "info"
                }
            ],
            "perfectLevels": []
        }
        write_progress(initial)
        return initial
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

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
        
        # Update Profile
        cursor.execute("UPDATE profile SET total_xp = ?, current_day = ?, current_level = ?, current_streak = ?, longest_streak = ? WHERE id = 1;",
                       (data["totalXP"], data["currentDay"], data["currentLevel"], data.get("streak", 0), data.get("longestStreak", 0)))
        
        conn.commit()
        conn.close()
    except Exception as e:
        print("SQLite sync notice:", e)

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
    if any(int(lvl.split('_')[0].replace('day', '')) > 30 for lvl in completed if '_' in lvl and lvl.split('_')[0].replace('day','').isdigit()):
        earned.add("dsa_explorer")
    if "day50_boss" in completed or total_xp >= 25000:
        earned.add("dsa_grandmaster")

    data["badges"] = list(earned)

def process_level_completion(day, level, is_perfect=False):
    data = read_progress()
    key = f"day{day}_{level}"

    if key in data["completedLevels"]:
        return {
            "success": False,
            "message": f"Level Day {day} {level.upper()} has already been completed! No duplicate XP awarded.",
            "data": data
        }

    if key not in data["unlockedLevels"]:
        return {
            "success": False,
            "message": f"Level Day {day} {level.upper()} is currently locked!",
            "data": data
        }

    base_xp = XP_TABLE.get(level, 100)
    bonus_xp = 100 if is_perfect else 0
    earned_xp = base_xp + bonus_xp

    data["totalXP"] += earned_xp
    old_rank = data["rank"]
    data["rank"] = calculate_rank(data["totalXP"])

    data["completedLevels"].append(key)
    if is_perfect:
        data["perfectLevels"].append(key)

    next_day, next_level = get_next_level(day, level)
    newly_unlocked = None
    if next_day is not None and next_level is not None:
        next_key = f"day{next_day}_{next_level}"
        if next_key not in data["unlockedLevels"]:
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
        "id": f"act_{len(data['activityHistory']) + 1}",
        "title": f"Day {day} — {level.upper()} Completed",
        "description": f"Earned +{earned_xp} XP" + (" (Includes 💯 Perfect Bonus!)" if is_perfect else ""),
        "xp": earned_xp,
        "day": day,
        "level": level,
        "perfect": is_perfect,
        "timestamp": datetime.datetime.now().isoformat(),
        "type": "completion"
    }
    data["activityHistory"].insert(0, activity_item)

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

class RequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PUBLIC_DIR, **kwargs)

    def do_GET(self):
        if self.path == '/api/progress':
            data = read_progress()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(data).encode('utf-8'))
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
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))
            return

        elif self.path == '/api/save':
            write_progress(payload)
            sync_to_sqlite(payload)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"success": True, "message": "Saved!"}).encode('utf-8'))
            return

        elif self.path == '/api/reset':
            initial = {
                "totalXP": 0,
                "rank": "🥚 C Beginner",
                "currentDay": 1,
                "currentLevel": "basic",
                "completedLevels": [],
                "unlockedLevels": ["day1_basic"],
                "badges": [],
                "streak": 0,
                "longestStreak": 0,
                "lastCompletedDate": None,
                "activityHistory": [
                    {
                        "id": "reset",
                        "title": "Progress Reset",
                        "description": "Progress was reset to Day 1 Basic.",
                        "xp": 0,
                        "timestamp": datetime.datetime.now().isoformat(),
                        "type": "warning"
                    }
                ],
                "perfectLevels": []
            }
            write_progress(initial)
            sync_to_sqlite(initial)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"success": True, "data": initial}).encode('utf-8'))
            return

        self.send_error(404, "Endpoint not found")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

if __name__ == '__main__':
    os.makedirs(PUBLIC_DIR, exist_ok=True)
    print(f"Starting C Recovery Tracker Server on http://localhost:{PORT}")
    with socketserver.TCPServer(("", PORT), RequestHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
