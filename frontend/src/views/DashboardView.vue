<!-- src/views/DashboardView.vue -->
<template>
  <div class="landing">

    <!-- ── HERO ── -->
    <section class="hero">
      <div class="hero-inner">
        <p class="hero-eyebrow"> Web-based annotation tool</p>

        <h1 class="hero-heading">
          Annotate any <span class="hl-yellow">image or video</span> —<br>
          quickly and easily
        </h1>

        <p class="hero-sub">
          Simple web-based annotation tool. Draw, label, and export your data without complexity.
        </p>

        <p class="hero-note">Works on any browser. No installation required.</p>

        <div class="hero-actions">
          <button class="cta-btn" @click="$router.push('/media/upload')">
             Start Annotating Now
          </button>
          <button class="sec-btn" @click="$router.push('/media/library')">
            📂 View Library
          </button>
        </div>
      </div>

      <div class="doodle doodle-1">✦</div>
      <div class="doodle doodle-2">◎</div>
      <div class="doodle doodle-3">✧</div>
    </section>

    <!-- ── FEATURES ── -->
    <section class="features">
      <div class="cards-grid">

        <div class="feat-card" style="transform: rotate(-1.2deg)">
          <div class="feat-icon">📤</div>
          <h3>Upload Media</h3>
          <p>Upload screenshots, images, or videos directly from your device.</p>
          <button class="card-btn" @click="$router.push('/media/upload')">Upload →</button>
        </div>

        <div class="feat-card" style="transform: rotate(0.8deg)">
          <div class="feat-icon">🖼️</div>
          <h3>Annotate Images</h3>
          <p>Draw bounding boxes, label objects, zoom, pan, and edit easily.</p>
          <button class="card-btn" @click="$router.push('/media/library')">Open Library →</button>
        </div>

        <div class="feat-card" style="transform: rotate(-0.6deg)">
          <div class="feat-icon">🎬</div>
          <h3>Annotate Videos</h3>
          <p>Frame-by-frame annotation with smooth navigation.</p>
          <button class="card-btn" @click="$router.push('/media/library')">Browse Videos →</button>
        </div>

        <div class="feat-card" style="transform: rotate(1.1deg)">
          <div class="feat-icon">📦</div>
          <h3>Export Dataset</h3>
          <p>Download annotations in YOLO format with images and labels.</p>
          <button class="card-btn" @click="$router.push('/media/library')">Export →</button>
        </div>

      </div>
    </section>

    <!-- ── TOOL LIST ── -->
    <section class="tool-strip">
      <h2 class="strip-title">Everything you need in one tool</h2>
      <div class="badge-row">
        <span class="ai-badge"> Rectangle</span>
        <span class="ai-badge"> Labels</span>
        <span class="ai-badge"> Zoom &amp; Pan</span>
        <span class="ai-badge">Undo / Redo</span>
        <span class="ai-badge"> Auto Annotate (AI)</span>
      </div>
      <p class="strip-note">Draw bounding boxes, label objects, and let AI do the heavy lifting.</p>
    </section>

    <!-- ── HOW IT WORKS ── -->
    <section class="how-section">
      <h2 class="section-heading">How it works</h2>
      <div class="steps-grid">
        <div class="step-card">
          <div class="step-num">1</div>
          <h3>Upload</h3>
          <p>Upload your images or videos from your device.</p>
        </div>
        <div class="step-arrow">→</div>
        <div class="step-card">
          <div class="step-num">2</div>
          <h3>Annotate</h3>
          <p>Draw bounding boxes and label objects on each frame.</p>
        </div>
        <div class="step-arrow">→</div>
        <div class="step-card">
          <div class="step-num">3</div>
          <h3>Export</h3>
          <p>Download your dataset in YOLO format, ready to train.</p>
        </div>
      </div>
    </section>

    <!-- ── WHY USE THIS ── -->
    <section class="why-section">
      <h2 class="section-heading">Why use this tool</h2>
      <div class="why-grid">
        <div class="why-item">
          <span class="why-icon">✅</span>
          <span>Simple and easy to use</span>
        </div>
        <div class="why-item">
          <span class="why-icon">✅</span>
          <span>No complex setup</span>
        </div>
        <div class="why-item">
          <span class="why-icon">✅</span>
          <span>Fast annotation workflow</span>
        </div>
        <div class="why-item">
          <span class="why-icon">✅</span>
          <span>AI-assisted labeling with YOLOv8</span>
        </div>
        <div class="why-item">
          <span class="why-icon">✅</span>
          <span>Works on any modern browser</span>
        </div>
        <div class="why-item">
          <span class="why-icon">✅</span>
          <span>Export in YOLO format instantly</span>
        </div>
      </div>
    </section>

    <!-- ── FINAL CTA ── -->
    <section class="final-cta">
      <h2 class="final-cta-heading">Ready to start annotating?</h2>
      <p class="final-cta-sub">Create an account and begin your workflow.</p>
      <button class="cta-btn" @click="$router.push('/media/upload')">
        ✏️ Start Annotating Now
      </button>
    </section>

  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '../stores/authStore'

const authStore = useAuthStore()

const userName = computed(() => {
  const name = authStore.user?.name || authStore.user?.email || 'User'
  return name.split(' ')[0]
})

const recentProjects = [
  { id: 1, name: 'Medical Image Dataset', tasks: 245, members: 8, progress: 68, color: '#4F46E5' },
  { id: 2, name: 'Vehicle Detection AI', tasks: 189, members: 5, progress: 45, color: '#059669' },
  { id: 3, name: 'Facial Recognition', tasks: 324, members: 12, progress: 82, color: '#DC2626' },
  { id: 4, name: 'Text Classification', tasks: 156, members: 6, progress: 34, color: '#F59E0B' }
]

const activities = [
  { id: 1, type: 'success', text: 'Completed annotation batch #2847', time: '2 minutes ago' },
  { id: 2, type: 'info', text: 'New user Sarah joined the team', time: '1 hour ago' },
  { id: 3, type: 'warning', text: 'Quality check required for batch #2846', time: '3 hours ago' },
  { id: 4, type: 'success', text: 'Project "Medical Dataset" reached 50%', time: '5 hours ago' },
  { id: 5, type: 'info', text: 'Export completed for batch #2845', time: '1 day ago' }
]
</script>

<style scoped>
/* ── Page shell ── */
.landing {
  max-width: 960px;
  margin: 0 auto;
  padding: 40px 24px 80px;
  font-family: 'Patrick Hand', cursive;
}

/* ══════════════════════════════
   HERO
══════════════════════════════ */
.hero {
  position: relative;
  text-align: center;
  padding: 64px 24px 72px;
  margin-bottom: 64px;
  background: #fffef5;
  border: 2px solid #1a1a1a;
  border-radius: 12px;
  box-shadow: 6px 6px 0px #1a1a1a;
  overflow: hidden;
}

.hero-inner {
  position: relative;
  z-index: 1;
}

.hero-eyebrow {
  font-size: 14px;
  letter-spacing: 0.08em;
  color: #555;
  margin-bottom: 20px;
  text-transform: uppercase;
}

.hero-heading {
  font-size: clamp(2rem, 5vw, 3.2rem);
  font-weight: 700;
  line-height: 1.2;
  color: #1a1a1a;
  margin-bottom: 20px;
}

/* Yellow marker highlight — matches reference images */
.hl-yellow {
  background: linear-gradient(
    104deg,
    transparent 0.5%,
    #fff59d 2%,
    #fff59d 95%,
    transparent 99%
  );
  padding: 0 6px;
  border-radius: 3px;
}

.hero-sub {
  font-size: 1.1rem;
  color: #333;
  margin-bottom: 36px;
  line-height: 1.7;
}

/* Sketch underline on sub text */
.hl-underline {
  text-decoration: underline;
  text-decoration-style: wavy;
  text-decoration-color: #4f46e5;
  text-underline-offset: 4px;
}

.hero-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  flex-wrap: wrap;
}

.cta-btn {
  padding: 14px 32px;
  font-family: 'Patrick Hand', cursive;
  font-size: 1rem;
  font-weight: 700;
  background: #1a1a1a;
  color: #fffef5;
  border: 2px solid #1a1a1a;
  border-radius: 8px;
  box-shadow: 4px 4px 0px #4f46e5;
  cursor: pointer;
  transition: box-shadow 0.1s, transform 0.1s;
}

.cta-btn:hover {
  box-shadow: 6px 6px 0px #4f46e5;
  transform: translate(-1px, -1px);
}

.cta-btn:active {
  box-shadow: 2px 2px 0px #4f46e5;
  transform: translate(2px, 2px);
}

.sec-btn {
  padding: 14px 28px;
  font-family: 'Patrick Hand', cursive;
  font-size: 1rem;
  background: #fffef5;
  color: #1a1a1a;
  border: 2px solid #1a1a1a;
  border-radius: 8px;
  box-shadow: 4px 4px 0px #1a1a1a;
  cursor: pointer;
  transition: box-shadow 0.1s, transform 0.1s;
}

.sec-btn:hover {
  box-shadow: 6px 6px 0px #1a1a1a;
  transform: translate(-1px, -1px);
}

.sec-btn:active {
  box-shadow: 2px 2px 0px #1a1a1a;
  transform: translate(2px, 2px);
}

/* Decorative doodle characters */
.doodle {
  position: absolute;
  font-size: 2rem;
  color: rgba(79, 70, 229, 0.18);
  pointer-events: none;
  user-select: none;
}
.doodle-1 { top: 16px;  left: 24px;  font-size: 2.4rem; }
.doodle-2 { bottom: 20px; right: 32px; font-size: 2rem; }
.doodle-3 { top: 50%;  right: 20px; font-size: 1.6rem; }

/* ══════════════════════════════
   FEATURES
══════════════════════════════ */
.features {
  margin-bottom: 56px;
}

.features-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1a1a1a;
  margin-bottom: 32px;
  text-align: center;
  /* hand-drawn underline via border */
  display: inline-block;
  width: 100%;
  padding-bottom: 8px;
  border-bottom: 2px dashed #1a1a1a;
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 24px;
}

.feat-card {
  background: #fffef5;
  border: 2px solid #1a1a1a;
  border-radius: 10px;
  box-shadow: 4px 4px 0px #1a1a1a;
  padding: 28px 20px 22px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  transition: box-shadow 0.12s, transform 0.12s;
}

.feat-card:hover {
  box-shadow: 6px 6px 0px #1a1a1a;
  transform: translate(-1px, -1px) rotate(0deg) !important;
}

.feat-icon {
  font-size: 2rem;
  line-height: 1;
}

.feat-card h3 {
  font-size: 1.05rem;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0;
}

.feat-card p {
  font-size: 0.88rem;
  color: #444;
  line-height: 1.55;
  flex: 1;
}

.card-btn {
  align-self: flex-start;
  padding: 7px 16px;
  font-family: 'Patrick Hand', cursive;
  font-size: 0.82rem;
  font-weight: 700;
  background: #fffef5;
  color: #1a1a1a;
  border: 1.5px solid #1a1a1a;
  border-radius: 6px;
  box-shadow: 2px 2px 0px #1a1a1a;
  cursor: pointer;
  transition: box-shadow 0.1s, transform 0.1s;
  margin-top: 4px;
}

.card-btn:hover {
  box-shadow: 4px 4px 0px #1a1a1a;
  transform: translate(-1px, -1px);
}

.card-btn:active {
  box-shadow: 1px 1px 0px #1a1a1a;
  transform: translate(1px, 1px);
}

/* ══════════════════════════════
   AI STRIP
══════════════════════════════ */
.ai-strip {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 28px;
  background: #fffef5;
  border: 2px solid #1a1a1a;
  border-radius: 10px;
  box-shadow: 4px 4px 0px #1a1a1a;
  font-size: 0.95rem;
  color: #1a1a1a;
}

.ai-badge {
  flex-shrink: 0;
  background: #fff59d;
  border: 1.5px solid #1a1a1a;
  border-radius: 6px;
  padding: 4px 10px;
  font-weight: 700;
  font-size: 0.82rem;
  box-shadow: 2px 2px 0px #1a1a1a;
}

/* ── Responsive ── */
@media (max-width: 600px) {
  .hero {
    padding: 40px 16px 48px;
  }
  .cards-grid {
    grid-template-columns: 1fr;
  }
  .ai-strip {
    flex-direction: column;
    text-align: center;
  }
}

/* ══════════════════════════════
   HERO NOTE
══════════════════════════════ */
.hero-note {
  font-size: 0.85rem;
  color: #777;
  margin-bottom: 28px;
  font-style: italic;
}

/* ══════════════════════════════
   TOOL STRIP
══════════════════════════════ */
.tool-strip {
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 24px 28px;
  margin-bottom: 40px;
  background: #fffef5;
  border: 2px solid #1a1a1a;
  border-radius: 10px;
  box-shadow: 4px 4px 0px #1a1a1a;
}

.strip-title {
  font-size: 1.1rem;
  font-weight: 700;
  margin: 0;
  color: #1a1a1a;
}

.badge-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.strip-note {
  margin: 0;
  font-size: 0.88rem;
  color: #555;
}

/* ══════════════════════════════
   SECTION HEADING (shared)
══════════════════════════════ */
.section-heading {
  font-size: 1.35rem;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0 0 28px 0;
  padding-bottom: 10px;
  border-bottom: 2px dashed #1a1a1a;
}

/* ══════════════════════════════
   HOW IT WORKS
══════════════════════════════ */
.how-section {
  margin-bottom: 48px;
}

.steps-grid {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.step-card {
  flex: 1;
  min-width: 160px;
  background: #fffef5;
  border: 2px solid #1a1a1a;
  border-radius: 10px;
  box-shadow: 4px 4px 0px #1a1a1a;
  padding: 24px 20px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.step-num {
  width: 32px;
  height: 32px;
  background: #fff59d;
  border: 2px solid #1a1a1a;
  border-radius: 50%;
  box-shadow: 2px 2px 0px #1a1a1a;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.95rem;
}

.step-card h3 {
  font-size: 1rem;
  font-weight: 700;
  margin: 0;
  color: #1a1a1a;
}

.step-card p {
  font-size: 0.87rem;
  color: #444;
  margin: 0;
  line-height: 1.5;
}

.step-arrow {
  font-size: 1.6rem;
  color: #aaa;
  flex-shrink: 0;
}

/* ══════════════════════════════
   WHY USE THIS
══════════════════════════════ */
.why-section {
  margin-bottom: 48px;
}

.why-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 14px;
}

.why-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 16px;
  background: #fffef5;
  border: 2px solid #1a1a1a;
  border-radius: 8px;
  box-shadow: 2px 2px 0px #1a1a1a;
  font-size: 0.9rem;
  color: #1a1a1a;
  font-weight: 500;
}

.why-icon {
  font-size: 1rem;
  flex-shrink: 0;
}

/* ══════════════════════════════
   FINAL CTA
══════════════════════════════ */
.final-cta {
  text-align: center;
  padding: 48px 24px 56px;
  background: #fffef5;
  border: 2px solid #1a1a1a;
  border-radius: 12px;
  box-shadow: 6px 6px 0px #1a1a1a;
  margin-bottom: 40px;
}

.final-cta-heading {
  font-size: 1.6rem;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0 0 12px 0;
}

.final-cta-sub {
  font-size: 1rem;
  color: #555;
  margin: 0 0 28px 0;
}

@media (max-width: 600px) {
  .steps-grid {
    flex-direction: column;
  }
  .step-arrow {
    transform: rotate(90deg);
  }
  .why-grid {
    grid-template-columns: 1fr;
  }
}
</style>
