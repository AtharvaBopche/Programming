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
3. Enter the exact **Performance XP** score awarded by your AI Teacher (or use quick preset buttons ⭐ 100%, 🟢 90%, 🟡 80%, 🟠 60%, 🔴 40%).
4. (Optional) Check **"💯 Mark as Perfect Solution"** if your solution had clean style and optimal logic to earn **+100 Bonus XP**.
5. Click **"🏆 Record & Award XP"**.

### Method B: Programmatically via Terminal CLI
Record progress directly from the command line with custom performance XP:

```bash
python evaluate.py --day 1 --level basic --xp 84
```

---

## 🔄 4. How to Backup & Restore Progress

- **Export**: Click **"💾 Backup & Export"** in the top header -> **"Download progress.json"**.
- **Restore**: Click **"💾 Backup & Export"** -> Choose Backup File or paste raw JSON -> Click **"Restore Progress Data"**.
- **Reset Safety**: To reset progress back to Day 1 Basic, click **"Reset Progress..."** and type `RESET` to confirm.

---

## 🎮 5. Gamification & Performance XP System

XP is awarded dynamically based on how well you solved the problem (Correctness, Complexity, Code Quality, Edge Cases):

| Level Tier | Max XP Allowed | Performance Evaluation Range |
| :--- | :---: | :--- |
| 🟢 Basic Level | **100 XP** | Any score between 0 and 100 XP (e.g., 84/100) |
| 🟡 Medium Level | **200 XP** | Any score between 0 and 200 XP (e.g., 174/200) |
| 🔴 Hard Level | **300 XP** | Any score between 0 and 300 XP (e.g., 265/300) |
| ⚫ Boss Challenge | **500 XP** | Any score between 0 and 500 XP (e.g., 480/500) |
| 💯 Perfect Bonus | **+100 XP** | Bonus for clean style & optimal time complexity |

### 🏆 Ranks Pipeline
- **🥚 C Beginner**: 0 – 499 XP
- **🌱 C Learner**: 500 – 1,499 XP
- **⚔️ C Problem Solver**: 1,500 – 2,999 XP
- **🔥 C Programmer**: 3,000 – 4,999 XP
- **💻 C Developer**: 5,000 – 7,499 XP
- **👑 C Master**: 7,500 – 11,999 XP
- **🌳 DSA Specialist**: 12,000 – 17,999 XP
- **⚡ Algorithm Architect**: 18,000 – 24,999 XP
- **🚀 DSA Grandmaster**: 25,000+ XP

---

## 🗺️ 6. 50-Day Course & DSA Structure

Every single day features 4 difficulty levels:
- **🟢 Basic**: 5 questions
- **🟡 Medium**: 5 questions
- **🔴 Hard**: 3–5 questions
- **⚫ Boss**: 1–2 real-world challenges

### 📘 Phase 1: Core C Fundamentals (Days 1–30)
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
| **Day 30** | 👑 Phase 1 Boss — Student Management System |

### 🚀 Phase 2: Advanced Data Structures & Algorithms (Days 31–50)
| Day | Topic |
| :--- | :--- |
| **Day 31** | Arrays & Complexity |
| **Day 32** | Searching Algorithms |
| **Day 33** | Sorting Algorithms |
| **Day 34** | Recursion |
| **Day 35** | Linked Lists Basics |
| **Day 36** | Advanced Linked Lists |
| **Day 37** | Doubly & Circular Linked Lists |
| **Day 38** | Stacks |
| **Day 39** | Queues |
| **Day 40** | Hashing |
| **Day 41** | Trees Basics |
| **Day 42** | Binary Search Trees |
| **Day 43** | Heaps & Priority Queues |
| **Day 44** | Graphs Basics |
| **Day 45** | Shortest Paths & MST |
| **Day 46** | Greedy Algorithms |
| **Day 47** | Dynamic Programming |
| **Day 48** | Backtracking |
| **Day 49** | Integrated DSA |
| **Day 50** | 🚀 FINAL BOSS — DSA Capstone Challenge |

---

## 🤖 7. Recommended Workflow with AI Teacher / ChatGPT

1. Open the app and check your **Current Mission**.
2. Click **"📖 View Assignment Questions"** and click **"📋 Copy Prompt for AI Teacher"**.
3. Paste the prompt to ChatGPT to receive your C programming assignment.
4. Write your C solution code in your IDE/editor and test compile it.
5. Provide your C code to ChatGPT for evaluation.
6. When ChatGPT confirms you passed, open the **"🎓 Teacher Panel"** (or run `python evaluate.py ...`), enter the level, check Perfect if applicable, and submit to update your progress and unlock the next level!
