class SoundEffects {
  constructor() {
    this.ctx = null;
  }

  init() {
    if (!this.ctx) {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (AudioCtx) {
        this.ctx = new AudioCtx();
      }
    }
    if (this.ctx && this.ctx.state === 'suspended') {
      this.ctx.resume();
    }
  }

  playNote(freq, type, duration, delay = 0, gainVal = 0.15) {
    this.init();
    if (!this.ctx) return;

    setTimeout(() => {
      try {
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = type;
        osc.frequency.setValueAtTime(freq, this.ctx.currentTime);

        gain.gain.setValueAtTime(gainVal, this.ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.0001, this.ctx.currentTime + duration);

        osc.connect(gain);
        gain.connect(this.ctx.destination);

        osc.start();
        osc.stop(this.ctx.currentTime + duration);
      } catch (e) {
        console.warn("Audio playback exception:", e);
      }
    }, delay * 1000);
  }

  playLevelCompleteSound() {
    // Ascending victory arpeggio (C5 -> E5 -> G5 -> C6)
    this.playNote(523.25, 'triangle', 0.2, 0.0, 0.2);
    this.playNote(659.25, 'triangle', 0.2, 0.12, 0.2);
    this.playNote(783.99, 'triangle', 0.2, 0.24, 0.2);
    this.playNote(1046.50, 'sine', 0.4, 0.36, 0.3);
  }

  playBadgeUnlockSound() {
    // Fanfare burst
    this.playNote(587.33, 'sine', 0.15, 0.0, 0.2);
    this.playNote(880.00, 'sine', 0.15, 0.1, 0.2);
    this.playNote(1174.66, 'sine', 0.35, 0.2, 0.3);
  }

  playRankUpSound() {
    // Triumph fanfare
    this.playNote(440.00, 'square', 0.15, 0.0, 0.1);
    this.playNote(554.37, 'square', 0.15, 0.1, 0.1);
    this.playNote(659.25, 'square', 0.15, 0.2, 0.1);
    this.playNote(880.00, 'square', 0.4, 0.3, 0.15);
  }

  playClickSound() {
    this.playNote(800, 'sine', 0.04, 0.0, 0.05);
  }
}

const audioFX = new SoundEffects();
