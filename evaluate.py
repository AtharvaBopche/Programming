import argparse
import sys
import os

# Fix Windows console UTF-8 output encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Import evaluation logic from server.py
sys.path.append(os.path.dirname(__file__))
from server import process_level_completion, read_progress

def main():
    parser = argparse.ArgumentParser(description="Evaluate & record C Recovery Tracker level completion.")
    parser.add_argument("--day", type=int, required=True, help="Day number (1-50)")
    parser.add_argument("--level", type=str, required=True, choices=["basic", "medium", "hard", "boss"], help="Level difficulty")
    parser.add_argument("--xp", type=int, default=None, help="Performance XP awarded by AI Teacher (0 to level max XP)")
    parser.add_argument("--perfect", action="store_true", help="Mark as perfect solution to award bonus +100 XP")

    args = parser.parse_args()

    result = process_level_completion(args.day, args.level.lower(), args.perfect, args.xp)

    if result["success"]:
        print("\n==========================================")
        print("🎉 LEVEL COMPLETED SUCCESSFULLY!")
        print("==========================================")
        print(f"Day: {args.day} | Level: {args.level.upper()}")
        print(f"XP Earned: +{result['earnedXP']} XP (Base: {result['baseXP']} | Bonus: {result['bonusXP']})")
        print(f"Total XP: {result['totalXP']}")
        print(f"Rank: {result['rank']}" + (" 🏆 RANK UP!" if result['rankUp'] else ""))
        if result["newBadges"]:
            print(f"🏅 New Badges Earned: {', '.join(result['newBadges'])}")
        if result["nextUnlocked"]:
            print(f"🔓 Next Level Unlocked: {result['nextUnlocked']}")
        print("==========================================\n")
    else:
        print("\n❌ UPDATE FAILED:")
        print(result["message"])

if __name__ == '__main__':
    main()
