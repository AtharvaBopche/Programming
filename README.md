# ⚡ C Programming Recovery Tracker GUI

An RPG-style gamified progression dashboard designed to guide and track your C programming recovery course across a structured 30-day roadmap.

---

## 🚀 1. How to Run the Application

The application comes with an instant local HTTP & REST server built using Python's standard library. No `npm install` or third-party packages required!

### Launch the App:
Run the following command in the project directory:

```bash
python server.py
```

Then open your browser and navigate to:
👉 **[http://localhost:8000](http://localhost:8000)**

---

## 💾 2. Where Progress is Stored

Progress data is persisted dual-way:
1. **On Disk**: Stored in JSON format at [`data/progress.json`](file:///C:/Users/athar/.gemini/antigravity-ide/scratch/c-recovery-tracker/data/progress.json).
2. **In Browser**: Synchronized automatically with browser `localStorage`.

---

## 🎓 3. How to Update a Completed Level

Progress is **never** auto-awarded just by clicking around. It is recorded intentionally after your C programming solution is checked and approved by your AI Teacher (ChatGPT).

### Method A: Via GUI Teacher Panel (Recommended)
1. Click the **"🎓 Teacher Panel"** button in the header (or **"✅ Record Level Completion"** on your mission card).
2. Select the **Day/Topic** and **Difficulty Level** (🟢 Basic, 🟡 Medium, 🔴 Hard, ⚫ Boss).
3. (Optional) Check **"💯 Mark as Perfect Level"** if your solution had clean style and optimal logic to earn **+100 Bonus XP**.
4. Click **"🏆 Record & Award XP"**.
5. Enjoy the victory fanfare & celebration modal!

### Method B: Programmatically via Terminal CLI
Codex or your teacher can record progress directly from the command line:

```bash
python evaluate.py --day 1 --level basic --perfect
```

> **Note**: The system prevents double-awarding XP for already completed levels.

---

## 🔄 4. How to Backup & Restore Progress

- **Export**: Click **"💾 Backup & Export"** in the top header -> **"Download progress.json"**.
- **Restore**: Click **"💾 Backup & Export"** -> Choose Backup File or paste raw JSON -> Click **"Restore Progress Data"**.
- **Reset Safety**: To reset progress back to Day 1 Basic, click **"Reset Progress..."** and type `RESET` to confirm.

---

## 🎮 5. Gamification & XP System

| Achievement | XP Awarded |
| :--- | :---: |
| 🟢 Basic Level Completed | **+100 XP** |
| 🟡 Medium Level Completed | **+200 XP** |
| 🔴 Hard Level Completed | **+300 XP** |
| ⚫ Boss Level Defeated | **+500 XP** |
| 💯 Perfect Level Bonus | **+100 Bonus XP** |

### 🏆 Ranks Pipeline
- **🥚 C Beginner**: 0 – 499 XP
- **🌱 C Learner**: 500 – 1,499 XP
- **⚔️ C Problem Solver**: 1,500 – 2,999 XP
- **🔥 C Programmer**: 3,000 – 4,999 XP
- **💻 C Developer**: 5,000 – 7,499 XP
- **👑 C Master**: 7,500+ XP

---

## 🗺️ 6. 30-Day Course Structure

Every single day features 4 difficulty levels:
- **🟢 Basic**: 5 questions
- **🟡 Medium**: 5 questions
- **🔴 Hard**: 3–5 questions
- **⚫ Boss**: 1–2 real-world challenges (Day 30 is the 👑 Student Management System Final Boss)

| Day | Topic |
| :--- | :--- |
| **Day 1** | C Basics + Input/Output |
| **Day 2** | Variables + Data Types |
| **Day 3** | Operators |
| **Day 4** | if / else |
| **Day 5** | switch |
| **Day 6** | for Loop |
| **Day 7** | while / do-while |
| **Day 8** | Number Logic |
| **Day 9** | Pattern Programming |
| **Day 10** | Functions Basics |
| **Day 11** | Function Types |
| **Day 12** | Call by Value / Reference |
| **Day 13** | Arrays |
| **Day 14** | Array Problems |
| **Day 15** | Searching + Sorting |
| **Day 16** | 2D Arrays |
| **Day 17** | Matrix Operations |
| **Day 18** | Matrix Problems |
| **Day 19** | Strings |
| **Day 20** | String Functions |
| **Day 21** | String Problems |
| **Day 22** | Pointers Basics |
| **Day 23** | Pointers + Arrays |
| **Day 24** | Pointers + Functions |
| **Day 25** | Structures |
| **Day 26** | Structure Arrays |
| **Day 27** | Structure Problems |
| **Day 28** | File Handling |
| **Day 29** | Dynamic Memory |
| **Day 30** | 👑 FINAL BOSS — Student Management System |

---

## 🤖 7. Recommended Workflow with AI Teacher / ChatGPT

1. Open the app and check your **Current Mission**.
2. Click **"📖 View Assignment Questions"** and click **"📋 Copy Prompt for AI Teacher"**.
3. Paste the prompt to ChatGPT to receive your C programming assignment.
4. Write your C solution code in your IDE/editor and test compile it.
5. Provide your C code to ChatGPT for evaluation.
6. When ChatGPT confirms you passed, open the **"🎓 Teacher Panel"** (or run `python evaluate.py ...`), enter the level, check Perfect if applicable, and submit to update your progress and unlock the next level!
