<template>
  <div class="auth-shell">
    <section class="auth-story">
      <div class="story-glow" />
      <header class="story-brand">
        <span class="brand-mark">✳</span>
        <div>
          <strong>AI 约会助手</strong>
          <span>THE LOVE LAB</span>
        </div>
      </header>

      <div class="story-copy">
        <p class="page-kicker">{{ kicker }}</p>
        <h1>{{ heading }}</h1>
        <p class="story-lead">{{ lead }}</p>
      </div>

      <figure class="story-quote">
        <span class="quote-mark">“</span>
        <blockquote>好的关系不是找到完美的人，<br />而是学会看清自己。</blockquote>
        <figcaption>LOVE NOTE · 001</figcaption>
      </figure>

      <footer class="story-foot">
        <span>真实地点 · 穿搭建议 · 对话练习</span>
        <span>EST. 2026</span>
      </footer>
    </section>

    <section class="auth-panel">
      <div class="panel-inner">
        <div class="panel-top">
          <span class="panel-label">{{ label }}</span>
          <span class="panel-index">{{ index }}</span>
        </div>
        <slot />
        <p class="panel-foot">慢一点喜欢，认真一点相处。</p>
      </div>
    </section>
  </div>
</template>

<script setup>
defineProps({
  kicker: { type: String, default: 'BEFORE YOU MEET' },
  heading: { type: String, default: '先成为值得被爱的人，再遇见爱。' },
  lead: { type: String, default: '一个不替你谈恋爱的 AI 军师：帮你看清场合、穿对衣服、选对地点。' },
  label: { type: String, default: 'WELCOME' },
  index: { type: String, default: '01 / 02' },
})
</script>

<style scoped>
.auth-shell {
  position: relative;
  display: grid;
  grid-template-columns: minmax(0, 1.05fr) minmax(420px, 0.95fr);
  min-height: 100vh;
  background: var(--color-canvas);
  overflow: hidden;
}

.auth-story {
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 44px 56px 38px;
  background:
    radial-gradient(700px 500px at 12% 108%, rgba(255, 107, 157, 0.2), transparent 60%),
    radial-gradient(560px 460px at 100% 0%, rgba(154, 68, 98, 0.22), transparent 62%),
    linear-gradient(150deg, #1e1014 0%, #12090c 100%);
  overflow: hidden;
}

.story-glow {
  position: absolute;
  right: -160px;
  bottom: 10%;
  width: 460px;
  height: 460px;
  border: 1px solid rgba(255, 107, 157, 0.15);
  border-radius: 50%;
  pointer-events: none;
}

.story-glow::before,
.story-glow::after {
  content: "";
  position: absolute;
  border: 1px solid rgba(255, 107, 157, 0.08);
  border-radius: 50%;
}

.story-glow::before {
  inset: 54px;
}

.story-glow::after {
  inset: 118px;
}

.story-brand {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  gap: 13px;
}

.brand-mark {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--color-primary-line);
  border-radius: 50%;
  color: var(--color-primary);
  font-size: 16px;
  background: rgba(255, 107, 157, 0.06);
}

.story-brand div {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.story-brand strong {
  color: var(--color-ink);
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 0.2px;
}

.story-brand span:last-child {
  color: var(--color-muted-soft);
  font-size: 8px;
  letter-spacing: 2.2px;
}

.story-copy {
  position: relative;
  z-index: 1;
  max-width: 620px;
  margin: 56px 0 auto;
}

.story-copy h1 {
  margin: 0;
  font-family: var(--font-serif);
  font-size: clamp(36px, 4.2vw, 56px);
  font-weight: 500;
  line-height: 1.28;
  letter-spacing: -1.5px;
  color: var(--color-ink);
  white-space: pre-line;
}

.story-lead {
  max-width: 420px;
  margin: 22px 0 0;
  color: var(--color-muted);
  font-size: 14px;
  line-height: 1.9;
  white-space: pre-line;
}

.story-quote {
  position: relative;
  z-index: 1;
  width: min(380px, 88%);
  margin: 44px 0 36px;
  padding: 22px 24px 18px;
  border: 1px solid var(--color-hairline);
  border-radius: 3px 16px 16px 3px;
  background: rgba(255, 255, 255, 0.035);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.22);
  transform: rotate(-2deg);
}

.story-quote::before {
  content: "";
  position: absolute;
  top: 12px;
  bottom: 12px;
  left: 9px;
  width: 1px;
  background: rgba(255, 107, 157, 0.28);
}

.quote-mark {
  position: absolute;
  top: 2px;
  right: 16px;
  color: var(--color-primary);
  font-family: var(--font-serif);
  font-size: 40px;
  opacity: 0.45;
}

.story-quote blockquote {
  margin: 0 0 14px;
  color: var(--color-body);
  font-family: var(--font-serif);
  font-size: 17px;
  line-height: 1.8;
}

.story-quote figcaption {
  color: var(--color-muted-soft);
  font-size: 8px;
  letter-spacing: 1.8px;
}

.story-foot {
  position: relative;
  z-index: 1;
  display: flex;
  justify-content: space-between;
  gap: 20px;
  color: var(--color-muted-soft);
  font-size: 9px;
  letter-spacing: 1.2px;
  text-transform: uppercase;
}

.auth-panel {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 48px 40px;
  background:
    radial-gradient(500px 400px at 100% 0%, rgba(255, 107, 157, 0.08), transparent 65%),
    rgba(24, 14, 17, 0.72);
  border-left: 1px solid var(--color-hairline-soft);
}

.panel-inner {
  width: min(100%, 380px);
  animation: panel-in var(--dur-base) var(--ease-out) both;
}

@keyframes panel-in {
  from {
    opacity: 0;
    transform: translateY(12px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.panel-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 34px;
  color: var(--color-muted-soft);
  font-size: 9px;
  letter-spacing: 2px;
}

.panel-label {
  color: var(--color-primary);
}

.panel-foot {
  margin: 28px 0 0;
  color: var(--color-muted-soft);
  font-family: var(--font-serif);
  font-size: 12px;
  font-style: italic;
  text-align: center;
}

@media (max-width: 980px) {
  .auth-shell {
    grid-template-columns: minmax(0, 1fr);
  }

  .auth-story {
    min-height: 42vh;
    padding: 30px 28px 28px;
  }

  .story-copy {
    margin: 34px 0 10px;
  }

  .story-copy h1 {
    font-size: clamp(32px, 7vw, 48px);
  }

  .story-quote,
  .story-foot {
    display: none;
  }

  .auth-panel {
    min-height: auto;
    padding: 36px 24px 48px;
    border-left: 0;
    border-top: 1px solid var(--color-hairline-soft);
  }
}

@media (max-width: 520px) {
  .auth-story {
    min-height: 34vh;
  }

  .story-lead {
    display: none;
  }

  .auth-panel {
    padding: 28px 20px 40px;
  }
}
</style>
