const GAMIFICATION = {
  XP_TABLE: {
    basic: 100,
    medium: 200,
    hard: 300,
    boss: 500,
    perfectBonus: 100
  },

  RANKS: [
    { name: "🥚 C Beginner", minXP: 0, maxXP: 499, badge: "🥚", description: "Beginning the fundamental C journey." },
    { name: "🌱 C Learner", minXP: 500, maxXP: 1499, badge: "🌱", description: "Building core logic and variables mastery." },
    { name: "⚔️ C Problem Solver", minXP: 1500, maxXP: 2999, badge: "⚔️", description: "Tackling control flow, arrays, and functions." },
    { name: "🔥 C Programmer", minXP: 3000, maxXP: 4999, badge: "🔥", description: "Mastering pointers, strings, and matrix logic." },
    { name: "💻 C Developer", minXP: 5000, maxXP: 7499, badge: "💻", description: "Building complex structures and memory management." },
    { name: "👑 C Master", minXP: 7500, maxXP: 11999, badge: "👑", description: "Conquered the Core 30-Day C Recovery Course!" },
    { name: "🌳 DSA Specialist", minXP: 12000, maxXP: 17999, badge: "🌳", description: "Mastering Linked Lists, Stacks, Queues & Trees." },
    { name: "⚡ Algorithm Architect", minXP: 18000, maxXP: 24999, badge: "⚡", description: "Conquering Heaps, Graphs, Greedy & Dynamic Programming." },
    { name: "🚀 DSA Grandmaster", minXP: 25000, maxXP: 999999, badge: "🚀", description: "Conquered all 50 Days of Core C & Advanced DSA!" }
  ],

  BADGES: [
    {
      id: "first_steps",
      title: "🏅 First Steps",
      description: "Complete your first Basic level.",
      icon: "🏅",
      category: "Milestone"
    },
    {
      id: "logic_builder",
      title: "⚡ Logic Builder",
      description: "Complete your first Medium level.",
      icon: "⚡",
      category: "Skill"
    },
    {
      id: "problem_solver",
      title: "🔥 Problem Solver",
      description: "Complete your first Hard level.",
      icon: "🔥",
      category: "Mastery"
    },
    {
      id: "boss_slayer",
      title: "👑 Boss Slayer",
      description: "Defeat your first Boss level challenge.",
      icon: "👑",
      category: "Boss"
    },
    {
      id: "perfectionist",
      title: "💯 Perfectionist",
      description: "Earn a Perfect Level bonus reward.",
      icon: "💯",
      category: "Special"
    },
    {
      id: "speed_runner",
      title: "🚀 Speed Runner",
      description: "Complete 3 or more levels total.",
      icon: "🚀",
      category: "Streak"
    },
    {
      id: "c_programmer",
      title: "💻 C Programmer",
      description: "Reach 3,000 XP or complete 20 course topics.",
      icon: "💻",
      category: "Rank"
    },
    {
      id: "c_master",
      title: "👑 C Master",
      description: "Conquer the Day 30 Student Management System Final Boss!",
      icon: "👑",
      category: "Ultimate"
    },
    {
      id: "dsa_explorer",
      title: "🌳 DSA Explorer",
      description: "Unlock and complete your first Advanced DSA day (Days 31–50).",
      icon: "🌳",
      category: "Phase 2"
    },
    {
      id: "dsa_grandmaster",
      title: "🚀 DSA Grandmaster",
      description: "Conquer the Day 50 DSA Capstone Challenge!",
      icon: "🚀",
      category: "Legendary"
    }
  ],

  getRankInfo(xp) {
    for (let i = 0; i < this.RANKS.length; i++) {
      const r = this.RANKS[i];
      if (xp >= r.minXP && xp <= r.maxXP) {
        const nextRank = this.RANKS[i + 1] || null;
        const currentMin = r.minXP;
        const currentMax = nextRank ? nextRank.minXP : r.maxXP;
        const xpInCurrentRank = xp - currentMin;
        const xpRequiredForRank = currentMax - currentMin;
        const percentage = Math.min(100, Math.max(0, Math.floor((xpInCurrentRank / xpRequiredForRank) * 100)));

        return {
          currentRank: r.name,
          currentMin: r.minXP,
          currentMax: r.maxXP,
          nextRank: nextRank ? nextRank.name : "Maximum Rank Achieved",
          nextRankMinXP: nextRank ? nextRank.minXP : r.maxXP,
          xpNeeded: nextRank ? Math.max(0, nextRank.minXP - xp) : 0,
          percentage: percentage,
          isMax: !nextRank
        };
      }
    }
    return {
      currentRank: "🚀 DSA Grandmaster",
      currentMin: 25000,
      currentMax: 999999,
      nextRank: "Max Rank",
      nextRankMinXP: 25000,
      xpNeeded: 0,
      percentage: 100,
      isMax: true
    };
  }
};
