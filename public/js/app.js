let progressState = null;

// INIT ON DOM LOADED
document.addEventListener('DOMContentLoaded', async () => {
  setupEventListeners();
  await loadProgressData();
  renderAll();
});

// FETCH PROGRESS DATA FROM SERVER OR LOCAL STORAGE
async function loadProgressData() {
  try {
    const res = await fetch('/api/progress');
    if (res.ok) {
      progressState = await res.json();
      saveToLocalStorage(progressState);
      return;
    }
  } catch (e) {
    console.warn("Backend server not reachable, loading from LocalStorage...");
  }

  // Fallback to localStorage
  const local = localStorage.getItem('c_recovery_progress');
  if (local) {
    try {
      progressState = JSON.parse(local);
      return;
    } catch (err) {}
  }

  // Default initial state
  progressState = {
    totalXP: 0,
    rank: "🥚 C Beginner",
    currentDay: 1,
    currentLevel: "basic",
    completedLevels: [],
    unlockedLevels: ["day1_basic"],
    badges: [],
    streak: 0,
    longestStreak: 0,
    lastCompletedDate: null,
    activityHistory: [
      {
        id: "init",
        title: "Course Initialized",
        description: "Began C Programming Recovery Roadmap!",
        xp: 0,
        timestamp: new Date().toISOString(),
        type: "info"
      }
    ],
    perfectLevels: []
  };
  saveToLocalStorage(progressState);
}

function saveToLocalStorage(data) {
  localStorage.setItem('c_recovery_progress', JSON.stringify(data));
}

async function saveProgressData(data) {
  progressState = data;
  saveToLocalStorage(data);
  try {
    await fetch('/api/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
  } catch (e) {}
}

// RENDER ENTIRE DASHBOARD
function renderAll() {
  if (!progressState) return;

  renderHeader();
  renderXPHero();
  renderCurrentMission();
  renderLevelMap();
  renderTopicList();
  renderBadgesGrid();
  renderStatsGrid();
  renderActivityFeed();
  populateTeacherDayDropdown();
}

// HEADER
function renderHeader() {
  const rankInfo = GAMIFICATION.getRankInfo(progressState.totalXP);
  document.getElementById('headerRankName').textContent = rankInfo.currentRank;
  document.getElementById('headerRankIcon').textContent = rankInfo.currentRank.split(' ')[0] || '🥚';
}

// XP HERO SECTION
function renderXPHero() {
  const xp = progressState.totalXP || 0;
  const rankInfo = GAMIFICATION.getRankInfo(xp);

  document.getElementById('dashTotalXP').textContent = xp.toLocaleString();
  document.getElementById('dashRankTitle').textContent = rankInfo.currentRank;

  if (rankInfo.isMax) {
    document.getElementById('dashNextRankText').textContent = "Maximum Rank Achieved! 👑";
  } else {
    document.getElementById('dashNextRankText').textContent = `${rankInfo.xpNeeded.toLocaleString()} XP needed for ${rankInfo.nextRank}`;
  }

  document.getElementById('dashXPBarFill').style.width = `${rankInfo.percentage}%`;
  document.getElementById('dashXPProgressText').textContent = rankInfo.isMax 
    ? `${xp.toLocaleString()} XP`
    : `${xp.toLocaleString()} / ${rankInfo.nextRankMinXP.toLocaleString()} XP`;
  document.getElementById('dashXPPercentage').textContent = `${rankInfo.percentage}%`;

  document.getElementById('dashStreak').textContent = `${progressState.streak || 0} Days`;
  
  const completedCount = (progressState.completedLevels || []).length;
  document.getElementById('dashCompletedCount').textContent = `${completedCount} / 120`;
  
  const badgesCount = (progressState.badges || []).length;
  document.getElementById('dashBadgesCount').textContent = `${badgesCount} / ${GAMIFICATION.BADGES.length}`;
  
  const overallPercent = Math.min(100, Math.floor((completedCount / 120) * 100));
  document.getElementById('dashOverallPercent').textContent = `${overallPercent}%`;
}

// CURRENT MISSION CARD
function renderCurrentMission() {
  const dayNum = progressState.currentDay || 1;
  const levelType = progressState.currentLevel || "basic";
  const courseDay = COURSE_DATA.find(d => d.day === dayNum) || COURSE_DATA[0];
  const levelDetails = courseDay.levels[levelType] || { questionsCount: 5, summary: "Level challenge", questions: [] };

  document.getElementById('missionDayBadge').textContent = `DAY ${dayNum}`;
  document.getElementById('missionTopicTitle').textContent = courseDay.title;

  const lvlBadge = document.getElementById('missionLevelBadge');
  lvlBadge.className = `mission-level-badge level-${levelType}`;
  
  const dotIcon = levelType === 'basic' ? '🟢' : levelType === 'medium' ? '🟡' : levelType === 'hard' ? '🔴' : '⚫';
  const xpVal = GAMIFICATION.XP_TABLE[levelType];
  
  lvlBadge.innerHTML = `<span class="dot">${dotIcon}</span> ${levelType.toUpperCase()} • ${levelDetails.questionsCount || (levelDetails.questions ? levelDetails.questions.length : 0)} Questions • +${xpVal} XP`;
  document.getElementById('missionSummaryText').textContent = levelDetails.summary;
}

// LEVEL MAP SKILL TREE
function renderLevelMap() {
  const container = document.getElementById('levelMapContainer');
  container.innerHTML = '';

  const completed = new Set(progressState.completedLevels || []);
  const unlocked = new Set(progressState.unlockedLevels || []);
  const curKey = `day${progressState.currentDay}_${progressState.currentLevel}`;

  COURSE_DATA.forEach(day => {
    const isCurrentDay = day.day === progressState.currentDay;
    const row = document.createElement('div');
    row.className = `map-day-row ${isCurrentDay ? 'active-day-row' : ''}`;

    const header = document.createElement('div');
    header.className = 'map-day-header';
    header.innerHTML = `
      <h4>Day ${day.day} — ${day.title}</h4>
      <p>${(day.topics || []).slice(0, 3).join(', ')}...</p>
    `;

    const nodesGrid = document.createElement('div');
    nodesGrid.className = 'map-nodes-grid';

    ['basic', 'medium', 'hard', 'boss'].forEach(lvl => {
      const key = `day${day.day}_${lvl}`;
      const isComp = completed.has(key);
      const isUnlk = unlocked.has(key);
      const isCur = key === curKey;

      const nodeBtn = document.createElement('button');
      let statusClass = 'locked';
      let icon = '🔒';

      if (isComp) {
        statusClass = 'completed';
        icon = '✅';
      } else if (isCur) {
        statusClass = 'current';
        icon = '⚡';
      } else if (isUnlk) {
        statusClass = 'available';
        icon = '🔓';
      }

      nodeBtn.className = `node-btn ${statusClass}`;
      
      const levelLabel = lvl === 'basic' ? '🟢 Basic' : lvl === 'medium' ? '🟡 Medium' : lvl === 'hard' ? '🔴 Hard' : '⚫ Boss';
      nodeBtn.innerHTML = `
        <span class="node-title">${levelLabel}</span>
        <span class="node-status-icon">${icon}</span>
      `;

      if (isUnlk || isComp) {
        nodeBtn.onclick = () => openAssignmentModal(day.day, lvl);
      }

      nodesGrid.appendChild(nodeBtn);
    });

    row.appendChild(header);
    row.appendChild(nodesGrid);
    container.appendChild(row);
  });
}

// TOPIC PROGRESS BREAKDOWN
function renderTopicList() {
  const container = document.getElementById('topicListContainer');
  container.innerHTML = '';

  const completed = new Set(progressState.completedLevels || []);

  COURSE_DATA.forEach(day => {
    let dayCompCount = 0;
    ['basic', 'medium', 'hard', 'boss'].forEach(lvl => {
      if (completed.has(`day${day.day}_${lvl}`)) dayCompCount++;
    });

    const percent = Math.floor((dayCompCount / 4) * 100);

    const item = document.createElement('div');
    item.className = 'topic-item';
    item.innerHTML = `
      <div class="topic-item-header">
        <span class="topic-name">${String(day.day).padStart(2, '0')} ${day.title}</span>
        <span class="topic-percent">${percent}%</span>
      </div>
      <div class="topic-bar-bg">
        <div class="topic-bar-fill" style="width: ${percent}%;"></div>
      </div>
    `;
    container.appendChild(item);
  });
}

// BADGES GALLERY
function renderBadgesGrid() {
  const container = document.getElementById('badgesGridContainer');
  container.innerHTML = '';

  const earnedBadges = new Set(progressState.badges || []);

  GAMIFICATION.BADGES.forEach(b => {
    const isUnlocked = earnedBadges.has(b.id);
    const card = document.createElement('div');
    card.className = `badge-card-item ${isUnlocked ? 'unlocked' : 'locked'}`;

    card.innerHTML = `
      <div class="badge-icon-wrap">${b.icon}</div>
      <div class="badge-title-text">${b.title}</div>
      <div class="badge-desc-text">${b.description}</div>
    `;
    container.appendChild(card);
  });
}

// STATS GRID
function renderStatsGrid() {
  const container = document.getElementById('statsGridContainer');
  container.innerHTML = '';

  const completed = progressState.completedLevels || [];
  const basicCount = completed.filter(k => k.includes('_basic')).length;
  const mediumCount = completed.filter(k => k.includes('_medium')).length;
  const hardCount = completed.filter(k => k.includes('_hard')).length;
  const bossCount = completed.filter(k => k.includes('_boss')).length;

  let topicCompCount = 0;
  COURSE_DATA.forEach(day => {
    if (['basic', 'medium', 'hard', 'boss'].every(l => completed.includes(`day${day.day}_${l}`))) {
      topicCompCount++;
    }
  });

  const stats = [
    { label: "Total XP", value: (progressState.totalXP || 0).toLocaleString() },
    { label: "Current Rank", value: (progressState.rank || "🥚 C Beginner").split(' ')[1] || "Beginner" },
    { label: "Levels Completed", value: `${completed.length} / 120` },
    { label: "Topics Completed", value: `${topicCompCount} / 30` },
    { label: "🟢 Basic Done", value: `${basicCount} / 30` },
    { label: "🟡 Medium Done", value: `${mediumCount} / 30` },
    { label: "🔴 Hard Done", value: `${hardCount} / 30` },
    { label: "⚫ Bosses Defeated", value: `${bossCount} / 30` },
    { label: "Current Streak", value: `${progressState.streak || 0} Days` },
    { label: "Longest Streak", value: `${progressState.longestStreak || 0} Days` }
  ];

  stats.forEach(s => {
    const box = document.createElement('div');
    box.className = 'stat-card-box';
    box.innerHTML = `
      <div class="stat-box-num">${s.value}</div>
      <div class="stat-box-lbl">${s.label}</div>
    `;
    container.appendChild(box);
  });
}

// ACTIVITY FEED
function renderActivityFeed() {
  const container = document.getElementById('activityFeedContainer');
  container.innerHTML = '';

  const history = progressState.activityHistory || [];
  if (history.length === 0) {
    container.innerHTML = '<p class="text-muted">No activities recorded yet.</p>';
    return;
  }

  history.slice(0, 20).forEach(act => {
    const item = document.createElement('div');
    item.className = 'activity-item';
    
    let formattedTime = act.timestamp ? new Date(act.timestamp).toLocaleDateString() + ' ' + new Date(act.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) : 'Recently';
    
    item.innerHTML = `
      <div class="activity-title">${act.title}</div>
      <div class="activity-desc">${act.description}</div>
      <div class="activity-time">${formattedTime}</div>
    `;
    container.appendChild(item);
  });
}

// POPULATE TEACHER DAY DROPDOWN
function populateTeacherDayDropdown() {
  const select = document.getElementById('evalDaySelect');
  if (!select) return;
  select.innerHTML = '';

  COURSE_DATA.forEach(day => {
    const opt = document.createElement('option');
    opt.value = day.day;
    opt.textContent = `Day ${day.day}: ${day.title}`;
    if (day.day === progressState.currentDay) {
      opt.selected = true;
    }
    select.appendChild(opt);
  });
}

// ASSIGNMENT MODAL VIEWER
function openAssignmentModal(dayNum, levelType) {
  audioFX.playClickSound();
  const day = COURSE_DATA.find(d => d.day === dayNum) || COURSE_DATA[0];
  const levelDetails = day.levels[levelType] || { questions: [], summary: "" };

  document.getElementById('assignModalTag').textContent = `DAY ${dayNum} • ${levelType.toUpperCase()}`;
  document.getElementById('assignModalTitle').textContent = `${day.title}`;
  document.getElementById('assignModalTopics').textContent = (day.topics || []).join(', ');
  
  const xpVal = GAMIFICATION.XP_TABLE[levelType];
  document.getElementById('assignModalXPReward').textContent = `+${xpVal} XP`;

  const qContainer = document.getElementById('assignQuestionsList');
  qContainer.innerHTML = '';

  const questions = levelDetails.questions || [];

  if (questions.length === 0) {
    qContainer.innerHTML = '<div class="question-box">No questions listed for this section.</div>';
  } else {
    questions.forEach((q, idx) => {
      const box = document.createElement('div');
      box.className = 'question-box';
      const qNum = idx + 1;
      const formattedQ = q.startsWith(`${qNum}.`) ? q : `${qNum}. ${q}`;
      box.textContent = formattedQ;
      qContainer.appendChild(box);
    });
  }

  const btnRecord = document.getElementById('btnModalRecordComplete');
  btnRecord.onclick = () => {
    closeModal('assignmentModal');
    openTeacherPanel(dayNum, levelType);
  };

  document.getElementById('btnCopyAssignment').onclick = () => {
    const promptText = `I am taking the C Programming Recovery Course.\nDay ${dayNum}: ${day.title}\nDifficulty Level: ${levelType.toUpperCase()}\n\nPlease review/give assignments covering these topics: ${(day.topics || []).join(', ')}.\nHere are the target questions from my recovery database:\n${questions.map((q, i) => `${i+1}. ${q}`).join('\n')}`;
    navigator.clipboard.writeText(promptText).then(() => {
      alert("Assignment questions copied to clipboard! Paste into ChatGPT for feedback or evaluation.");
    });
  };

  openModal('assignmentModal');
}

// TEACHER EVALUATION PANEL
function openTeacherPanel(dayNum = null, levelType = null) {
  audioFX.playClickSound();
  if (dayNum) {
    document.getElementById('evalDaySelect').value = dayNum;
  } else {
    document.getElementById('evalDaySelect').value = progressState.currentDay || 1;
  }
  if (levelType) {
    document.getElementById('evalLevelSelect').value = levelType;
  } else {
    document.getElementById('evalLevelSelect').value = progressState.currentLevel || 'basic';
  }

  document.getElementById('evalPerfectCheck').checked = false;
  openModal('teacherModal');
}

async function submitEvaluation() {
  const day = parseInt(document.getElementById('evalDaySelect').value);
  const level = document.getElementById('evalLevelSelect').value;
  const perfect = document.getElementById('evalPerfectCheck').checked;

  try {
    const res = await fetch('/api/evaluate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ day, level, perfect })
    });

    if (res.ok) {
      const result = await res.json();
      if (result.success) {
        progressState = result.data;
        saveToLocalStorage(progressState);
        closeModal('teacherModal');
        renderAll();
        showCelebration(day, level, result);
        return;
      } else {
        alert(result.message);
        return;
      }
    }
  } catch (e) {
    console.warn("Server unavailable, processing locally...");
  }

  // Fallback client-side logic if backend offline
  const result = processClientEvaluation(day, level, perfect);
  if (result.success) {
    saveProgressData(progressState);
    closeModal('teacherModal');
    renderAll();
    showCelebration(day, level, result);
  } else {
    alert(result.message);
  }
}

function processClientEvaluation(day, level, perfect) {
  const key = `day${day}_${level}`;
  if ((progressState.completedLevels || []).includes(key)) {
    return { success: false, message: `Level Day ${day} ${level.toUpperCase()} already completed!` };
  }

  const baseXP = GAMIFICATION.XP_TABLE[level] || 100;
  const bonusXP = perfect ? 100 : 0;
  const earned = baseXP + bonusXP;

  progressState.totalXP += earned;
  const oldRank = progressState.rank;
  progressState.rank = GAMIFICATION.getRankInfo(progressState.totalXP).currentRank;

  progressState.completedLevels.push(key);
  if (perfect) progressState.perfectLevels.push(key);

  // Unlock next
  const order = ['basic', 'medium', 'hard', 'boss'];
  const idx = order.indexOf(level);
  let nextKey = null;
  if (idx < order.length - 1) {
    nextKey = `day${day}_${order[idx + 1]}`;
    progressState.currentDay = day;
    progressState.currentLevel = order[idx + 1];
  } else if (day < 30) {
    nextKey = `day${day + 1}_basic`;
    progressState.currentDay = day + 1;
    progressState.currentLevel = 'basic';
  }

  if (nextKey && !progressState.unlockedLevels.includes(nextKey)) {
    progressState.unlockedLevels.push(nextKey);
  }

  // Activity log
  progressState.activityHistory.unshift({
    id: `act_${Date.now()}`,
    title: `Day ${day} — ${level.toUpperCase()} Completed`,
    description: `Earned +${earned} XP` + (perfect ? " (💯 Perfect Bonus!)" : ""),
    xp: earned,
    timestamp: new Date().toISOString(),
    type: "completion"
  });

  return {
    success: true,
    earnedXP: earned,
    rankUp: oldRank !== progressState.rank,
    nextUnlocked: nextKey,
    newBadges: []
  };
}

// CELEBRATION MODAL & SOUND FX
function showCelebration(day, level, result) {
  audioFX.playLevelCompleteSound();
  if (result.rankUp) {
    setTimeout(() => audioFX.playRankUpSound(), 600);
  }

  const dayObj = COURSE_DATA.find(d => d.day === day) || COURSE_DATA[0];
  document.getElementById('celebLevelInfo').innerHTML = `DAY ${day} — ${dayObj.title.toUpperCase()}<br>Level: ${level.toUpperCase()}`;
  document.getElementById('celebXPEarned').textContent = `+${result.earnedXP} XP`;

  const extras = document.getElementById('celebExtras');
  extras.innerHTML = '';

  if (result.rankUp) {
    const alertBox = document.createElement('div');
    alertBox.className = 'celeb-alert-box';
    alertBox.textContent = `🏆 RANK UP! You are now ${result.rank}!`;
    extras.appendChild(alertBox);
  }

  if (result.newBadges && result.newBadges.length > 0) {
    const badgeBox = document.createElement('div');
    badgeBox.className = 'celeb-alert-box';
    badgeBox.textContent = `🏅 NEW BADGE UNLOCKED: ${result.newBadges.join(', ')}`;
    extras.appendChild(badgeBox);
  }

  if (result.nextUnlocked) {
    document.getElementById('celebNextUnlocked').textContent = `🔓 NEXT LEVEL UNLOCKED: ${result.nextUnlocked.replace('_', ' ').toUpperCase()}`;
  } else {
    document.getElementById('celebNextUnlocked').textContent = `👑 COURSE COMPLETED! YOU ARE A C MASTER!`;
  }

  openModal('celebrationModal');
  launchConfetti();
}

// CONFETTI ANIMATION ENGINE
function launchConfetti() {
  const canvas = document.getElementById('confettiCanvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  canvas.width = canvas.parentElement.clientWidth;
  canvas.height = canvas.parentElement.clientHeight;

  const particles = [];
  const colors = ['#4f46e5', '#059669', '#d97706', '#e11d48', '#7c3aed', '#0284c7'];

  for (let i = 0; i < 60; i++) {
    particles.push({
      x: canvas.width / 2,
      y: canvas.height / 2,
      vx: (Math.random() - 0.5) * 12,
      vy: (Math.random() - 0.7) * 12,
      size: Math.random() * 8 + 4,
      color: colors[Math.floor(Math.random() * colors.length)],
      alpha: 1
    });
  }

  function renderFrame() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    let active = false;

    particles.forEach(p => {
      p.x += p.vx;
      p.y += p.vy;
      p.vy += 0.25; // gravity
      p.alpha -= 0.015;

      if (p.alpha > 0) {
        active = true;
        ctx.globalAlpha = p.alpha;
        ctx.fillStyle = p.color;
        ctx.fillRect(p.x, p.y, p.size, p.size);
      }
    });

    if (active) {
      requestAnimationFrame(renderFrame);
    }
  }

  renderFrame();
}

// DATA EXPORT / IMPORT / RESET
function setupEventListeners() {
  // Navigation tabs
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.onclick = () => {
      audioFX.playClickSound();
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

      btn.classList.add('active');
      const target = btn.dataset.tab;
      document.getElementById(target).classList.add('active');
    };
  });

  // Modal open/close handlers
  document.getElementById('btnOpenTeacherPanel').onclick = () => openTeacherPanel();
  document.getElementById('btnCloseTeacherModal').onclick = () => closeModal('teacherModal');
  document.getElementById('btnCancelTeacherModal').onclick = () => closeModal('teacherModal');
  document.getElementById('btnSubmitTeacherEval').onclick = () => submitEvaluation();

  document.getElementById('btnRecordMissionComplete').onclick = () => {
    openTeacherPanel(progressState.currentDay, progressState.currentLevel);
  };
  document.getElementById('btnViewAssignment').onclick = () => {
    openAssignmentModal(progressState.currentDay, progressState.currentLevel);
  };

  document.getElementById('btnCloseAssignModal').onclick = () => closeModal('assignmentModal');
  document.getElementById('btnCloseCelebration').onclick = () => closeModal('celebrationModal');

  // Data Modal
  document.getElementById('btnOpenDataModal').onclick = () => openModal('dataModal');
  document.getElementById('btnCloseDataModal').onclick = () => closeModal('dataModal');

  // Export JSON
  document.getElementById('btnExportJSON').onclick = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(progressState, null, 2));
    const dlAnchor = document.createElement('a');
    dlAnchor.setAttribute("href", dataStr);
    dlAnchor.setAttribute("download", `c_recovery_progress_${new Date().toISOString().slice(0,10)}.json`);
    document.body.appendChild(dlAnchor);
    dlAnchor.click();
    dlAnchor.remove();
  };

  // Import JSON file chooser
  document.getElementById('btnChooseImportFile').onclick = () => {
    document.getElementById('importFileInput').click();
  };

  document.getElementById('importFileInput').onchange = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (evt) => {
      document.getElementById('importJsonTextarea').value = evt.target.result;
    };
    reader.readAsText(file);
  };

  // Desktop Import: header shortcut button
  document.getElementById('btnImportFromDesktop').onclick = () => {
    openModal('dataModal');
    // Scroll to the import section
    setTimeout(() => {
      const importSection = document.getElementById('desktopImportSection');
      if (importSection) importSection.scrollIntoView({ behavior: 'smooth' });
    }, 300);
  };

  // Desktop Import: file chooser button
  document.getElementById('btnChooseDesktopImport').onclick = () => {
    document.getElementById('desktopImportFileInput').click();
  };

  // Desktop Import: file selected
  document.getElementById('desktopImportFileInput').onchange = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const statusDiv = document.getElementById('desktopImportStatus');
    const reader = new FileReader();
    reader.onload = (evt) => {
      try {
        const parsed = JSON.parse(evt.target.result);
        let progressData = null;

        // Handle desktop export format (with _exportMeta wrapper)
        if (parsed._exportMeta && parsed.progress) {
          progressData = parsed.progress;
          statusDiv.style.display = 'block';
          statusDiv.style.background = '#ecfdf5';
          statusDiv.style.color = '#065f46';
          statusDiv.style.border = '1px solid #059669';
          statusDiv.innerHTML = `✅ Desktop export file detected!<br>
            <small>Exported from: <strong>${parsed._exportMeta.source || 'Desktop App'}</strong> on ${new Date(parsed._exportMeta.exportedAt).toLocaleString()}</small><br>
            <small>XP: <strong>${progressData.totalXP || 0}</strong> | Completed: <strong>${(progressData.completedLevels || []).length}</strong> levels</small><br><br>
            <button class="btn btn-success" id="btnConfirmDesktopImport" style="width: 100%;">✅ Apply Desktop Progress</button>`;
          
          document.getElementById('btnConfirmDesktopImport').onclick = () => {
            saveProgressData(progressData);
            renderAll();
            statusDiv.innerHTML = '✅ Progress imported successfully from Desktop App!';
            setTimeout(() => closeModal('dataModal'), 1500);
          };
        }
        // Handle raw progress JSON (no wrapper)
        else if (parsed.totalXP !== undefined && Array.isArray(parsed.completedLevels)) {
          progressData = parsed;
          statusDiv.style.display = 'block';
          statusDiv.style.background = '#fffbeb';
          statusDiv.style.color = '#92400e';
          statusDiv.style.border = '1px solid #d97706';
          statusDiv.innerHTML = `⚠️ Raw progress file detected (not a desktop export).<br>
            <small>XP: <strong>${progressData.totalXP || 0}</strong> | Completed: <strong>${(progressData.completedLevels || []).length}</strong> levels</small><br><br>
            <button class="btn btn-warning" id="btnConfirmDesktopImport" style="width: 100%;">Import Raw Progress</button>`;
          
          document.getElementById('btnConfirmDesktopImport').onclick = () => {
            saveProgressData(progressData);
            renderAll();
            statusDiv.innerHTML = '✅ Progress imported successfully!';
            statusDiv.style.background = '#ecfdf5';
            statusDiv.style.color = '#065f46';
            statusDiv.style.border = '1px solid #059669';
            setTimeout(() => closeModal('dataModal'), 1500);
          };
        } else {
          statusDiv.style.display = 'block';
          statusDiv.style.background = '#fff1f2';
          statusDiv.style.color = '#be123c';
          statusDiv.style.border = '1px solid #e11d48';
          statusDiv.textContent = '❌ Invalid file! This does not appear to be a valid progress export.';
        }
      } catch (err) {
        statusDiv.style.display = 'block';
        statusDiv.style.background = '#fff1f2';
        statusDiv.style.color = '#be123c';
        statusDiv.style.border = '1px solid #e11d48';
        statusDiv.textContent = '❌ JSON parsing error: ' + err.message;
      }
    };
    reader.readAsText(file);
    // Reset the input so the same file can be selected again
    e.target.value = '';
  };

  document.getElementById('btnApplyRestore').onclick = () => {
    const raw = document.getElementById('importJsonTextarea').value;
    if (!raw.trim()) {
      alert("Please select a valid JSON backup file or paste JSON code.");
      return;
    }
    try {
      const parsed = JSON.parse(raw);
      if (typeof parsed.totalXP === 'number' && Array.isArray(parsed.completedLevels)) {
        saveProgressData(parsed);
        renderAll();
        closeModal('dataModal');
        alert("Progress data restored successfully!");
      } else {
        alert("Invalid progress file format!");
      }
    } catch (err) {
      alert("JSON parsing error: " + err.message);
    }
  };

  // Reset Modal
  document.getElementById('btnOpenResetConfirm').onclick = () => {
    closeModal('dataModal');
    document.getElementById('resetConfirmInput').value = '';
    document.getElementById('btnConfirmReset').disabled = true;
    openModal('resetConfirmModal');
  };

  document.getElementById('btnCloseResetModal').onclick = () => closeModal('resetConfirmModal');
  document.getElementById('btnCancelReset').onclick = () => closeModal('resetConfirmModal');

  const confirmInput = document.getElementById('resetConfirmInput');
  confirmInput.oninput = () => {
    document.getElementById('btnConfirmReset').disabled = (confirmInput.value.trim() !== 'RESET');
  };

  document.getElementById('btnConfirmReset').onclick = async () => {
    try {
      const res = await fetch('/api/reset', { method: 'POST' });
      if (res.ok) {
        const result = await res.json();
        progressState = result.data;
        saveToLocalStorage(progressState);
        renderAll();
        closeModal('resetConfirmModal');
        alert("Progress reset to Day 1 Basic.");
        return;
      }
    } catch (e) {}

    // Local reset fallback
    progressState = {
      totalXP: 0,
      rank: "🥚 C Beginner",
      currentDay: 1,
      currentLevel: "basic",
      completedLevels: [],
      unlockedLevels: ["day1_basic"],
      badges: [],
      streak: 0,
      longestStreak: 0,
      lastCompletedDate: null,
      activityHistory: [{
        id: "reset",
        title: "Progress Reset",
        description: "Progress reset to Day 1 Basic.",
        xp: 0,
        timestamp: new Date().toISOString(),
        type: "warning"
      }],
      perfectLevels: []
    };
    saveProgressData(progressState);
    renderAll();
    closeModal('resetConfirmModal');
    alert("Progress reset to Day 1 Basic.");
  };
}

// MODAL UTILITY FUNCTIONS
function openModal(id) {
  document.getElementById(id).classList.add('active');
}

function closeModal(id) {
  document.getElementById(id).classList.remove('active');
}
