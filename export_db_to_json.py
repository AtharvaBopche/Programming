import sqlite3
import json
import os
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

db_path = r"C:\Users\athar\Downloads\c_recovery_with_advanced_dsa.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get days
cursor.execute("SELECT day_id, day_number, title, topic FROM course_days ORDER BY day_number ASC;")
days_rows = cursor.fetchall()

course_data = []

for day_row in days_rows:
    day_id, day_num, title, topic = day_row
    
    # Get levels for this day
    cursor.execute("SELECT level_id, level_order, name, xp FROM levels WHERE day_id = ? ORDER BY level_order ASC;", (day_id,))
    level_rows = cursor.fetchall()
    
    levels_dict = {}
    
    for lvl_row in level_rows:
        level_id, lvl_order, lvl_name, xp = lvl_row
        lvl_key = lvl_name.lower()
        
        # Get questions for this level
        cursor.execute("SELECT question_id, question_number, question_text FROM questions WHERE level_id = ? ORDER BY question_number ASC;", (level_id,))
        q_rows = cursor.fetchall()
        
        questions_list = [q[2].strip() for q in q_rows]
        
        levels_dict[lvl_key] = {
            "levelId": level_id,
            "name": lvl_name,
            "xp": xp,
            "questionsCount": len(questions_list),
            "summary": f"{lvl_name} level challenge for {topic} with {len(questions_list)} problem(s).",
            "questions": questions_list
        }
        
    course_data.append({
        "day": day_num,
        "title": topic if topic else title,
        "rawTitle": title,
        "topics": [t.strip() for t in topic.replace('+', ',').split(',') if t.strip()],
        "levels": levels_dict
    })

conn.close()

# Save to JS file
js_content = "const COURSE_DATA = " + json.dumps(course_data, indent=2, ensure_ascii=False) + ";\n"

js_path = os.path.join(os.path.dirname(__file__), 'public', 'js', 'courseData.js')
with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js_content)

print(f"Successfully exported {len(course_data)} days and all questions to {js_path}")
