<template>
  <div class="chat-page fade-rise">
    <aside class="persona-panel">
      <div class="persona-head">
        <p class="page-kicker">CHOOSE YOUR ALLY</p>
        <h2>今天想听谁说话？</h2>
        <p>换一个人格，换一种看问题的方式。</p>
      </div>

      <div class="persona-list">
        <button
          v-for="p in personas"
          :key="p.id"
          type="button"
          class="persona-item"
          :class="{ active: selectedPersona === p.id }"
          @click="selectPersona(p.id)"
        >
          <span class="persona-avatar">{{ personaInitial(p.name) }}</span>
          <span class="persona-copy">
            <strong>{{ p.name }}</strong>
            <em>{{ p.speaking_style || '你的专属恋爱军师' }}</em>
          </span>
          <el-icon v-if="selectedPersona === p.id" class="persona-check"><Check /></el-icon>
        </button>
      </div>

      <div class="persona-note">
        <span>✳</span>
        <p>AI 不会替你做决定，<br />但会陪你把话想清楚。</p>
      </div>
    </aside>

    <section class="chat-stage">
      <header class="chat-head">
        <span class="stage-mark"><el-icon><ChatLineRound /></el-icon></span>
        <div class="chat-head-copy">
          <h2>{{ currentPersona?.name || 'AI 军师' }}</h2>
          <p>{{ currentPersona?.speaking_style || '正在等你开口' }}</p>
        </div>
        <span class="online-pill"><i />在线</span>
      </header>

      <div ref="chatBoxRef" class="chat-box">
        <div v-if="!messages.length && !streaming" class="chat-welcome">
          <span class="welcome-mark">✳</span>
          <h3>把没想明白的事，说出来。</h3>
          <p>这里没有标准答案。你可以从下面一句话开始，也可以直接说你现在的心情。</p>
          <div class="suggestions">
            <button
              v-for="suggestion in suggestions"
              :key="suggestion"
              type="button"
              @click="useSuggestion(suggestion)"
            >
              {{ suggestion }}
              <el-icon><Right /></el-icon>
            </button>
          </div>
        </div>

        <div
          v-for="(msg, idx) in messages"
          :key="idx"
          class="message"
          :class="msg.role"
        >
          <span v-if="msg.role === 'assistant'" class="message-avatar">
            {{ personaInitial(currentPersona?.name) }}
          </span>
          <div class="message-body">
            <span class="message-meta">
              {{ msg.role === 'user' ? '你' : currentPersona?.name || 'AI' }}
            </span>
            <div class="message-bubble">{{ msg.content }}</div>
          </div>
        </div>

        <div v-if="streaming" class="message assistant">
          <span class="message-avatar">{{ personaInitial(currentPersona?.name) }}</span>
          <div class="message-body">
            <span class="message-meta">{{ currentPersona?.name || 'AI' }} 正在输入</span>
            <div class="message-bubble">
              {{ streamedText }}<span class="cursor">|</span>
            </div>
          </div>
        </div>
      </div>

      <div class="chat-input">
        <el-input
          v-model="input"
          type="textarea"
          :rows="2"
          placeholder="说说你今天遇到的事，或者那个让你犹豫的人…"
          :disabled="streaming"
          resize="none"
          @keydown.enter.exact.prevent="handleSend"
        />
        <div class="input-actions">
          <span class="hint">Enter 发送 · Shift + Enter 换行</span>
          <el-button type="primary" :loading="streaming" @click="handleSend">
            <el-icon><Promotion /></el-icon>
            发送
          </el-button>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Promotion, Check, ChatLineRound, Right } from '@element-plus/icons-vue'
import { listPersonas } from '../api/spots.js'
import { streamChat, getHistory } from '../api/chat.js'

const personas = ref([])
const selectedPersona = ref(null)
const messages = ref([])
const input = ref('')
const streaming = ref(false)
const streamedText = ref('')
const chatBoxRef = ref(null)

const suggestions = [
  '第一次约会，我应该聊什么？',
  '对方回消息越来越慢，我该怎么想？',
  '帮我判断一下，这是心动还是不甘心。',
]

const currentPersona = computed(() =>
  personas.value.find((p) => p.id === selectedPersona.value)
)

function personaInitial(name) {
  return Array.from(name || 'AI')[0]
}

async function loadPersonas() {
  try {
    const data = await listPersonas()
    personas.value = data
    if (data.length > 0) {
      selectedPersona.value = data[0].id
      loadHistory()
    }
  } catch (e) {
    console.error('加载人格列表失败', e)
  }
}

async function loadHistory() {
  if (!selectedPersona.value) return
  try {
    const data = await getHistory(selectedPersona.value)
    messages.value = data.map((m) => ({
      role: m.role,
      content: m.content,
    }))
    scrollToBottom()
  } catch (e) {
    console.error('加载历史失败', e)
  }
}

function selectPersona(id) {
  if (selectedPersona.value === id) return
  selectedPersona.value = id
  messages.value = []
  loadHistory()
}

function useSuggestion(text) {
  input.value = text
}

function scrollToBottom() {
  nextTick(() => {
    if (chatBoxRef.value) {
      chatBoxRef.value.scrollTop = chatBoxRef.value.scrollHeight
    }
  })
}

async function handleSend() {
  const text = input.value.trim()
  if (!text || streaming.value) return

  messages.value.push({ role: 'user', content: text })
  input.value = ''
  streamedText.value = ''
  streaming.value = true
  scrollToBottom()

  try {
    const resp = await streamChat(selectedPersona.value, text)
    const reader = resp.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const events = buffer.split('\n\n')
      buffer = events.pop() || ''

      for (const event of events) {
        const data = event
          .split('\n')
          .filter((line) => line.startsWith('data:'))
          .map((line) => line.slice(5).replace(/^ /, ''))
          .join('\n')

        if (!data || data === '[DONE]') continue

        try {
          const payload = JSON.parse(data)
          if (payload.type === 'error') {
            throw new Error(payload.data || '对话失败')
          }
          if (payload.type === 'chunk') {
            streamedText.value += payload.data
          }
        } catch (err) {
          if (err instanceof SyntaxError) {
            streamedText.value += data
          } else {
            throw err
          }
        }
      }
      scrollToBottom()
    }

    if (!streamedText.value.trim()) {
      throw new Error('未收到回复')
    }

    messages.value.push({
      role: 'assistant',
      content: streamedText.value,
    })
  } catch (e) {
    ElMessage.error('对话失败，请重试')
    console.error(e)
  } finally {
    streaming.value = false
    streamedText.value = ''
    scrollToBottom()
  }
}

onMounted(loadPersonas)
</script>

<style scoped>
.chat-page {
  display: grid;
  grid-template-columns: 252px minmax(0, 1fr);
  gap: 16px;
  height: calc(100vh - 156px);
  min-height: 560px;
}

.persona-panel {
  display: flex;
  flex-direction: column;
  padding: 20px 14px 14px;
  border: 1px solid var(--color-hairline);
  border-radius: var(--radius-lg);
  background:
    linear-gradient(165deg, rgba(255, 255, 255, 0.035), transparent 40%),
    rgba(36, 21, 25, 0.8);
  overflow: hidden;
}

.persona-head {
  padding: 2px 8px 18px;
  border-bottom: 1px solid var(--color-hairline-soft);
}

.persona-head h2 {
  margin: 0 0 6px;
  font-family: var(--font-serif);
  font-size: 21px;
  font-weight: 500;
  letter-spacing: -0.4px;
  color: var(--color-ink);
}

.persona-head p:last-child {
  margin: 0;
  color: var(--color-muted-soft);
  font-size: 10.5px;
  line-height: 1.6;
}

.persona-list {
  display: flex;
  flex-direction: column;
  gap: 5px;
  padding: 14px 0;
  overflow-y: auto;
}

.persona-item {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 10px;
  border: 1px solid transparent;
  border-radius: 11px;
  background: none;
  color: var(--color-muted);
  text-align: left;
  cursor: pointer;
  transition: all var(--dur-fast) var(--ease-out);
}

.persona-item:hover {
  background: rgba(255, 255, 255, 0.035);
  color: var(--color-body);
}

.persona-item.active {
  border-color: var(--color-hairline);
  background:
    linear-gradient(100deg, rgba(255, 107, 157, 0.1), transparent 80%),
    rgba(255, 255, 255, 0.04);
  color: var(--color-ink);
}

.persona-avatar {
  width: 34px;
  height: 34px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  border: 1px solid var(--color-hairline);
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.04);
  color: var(--color-muted);
  font-family: var(--font-serif);
  font-size: 14px;
}

.persona-item.active .persona-avatar {
  border-color: var(--color-primary-line);
  background: var(--color-primary-soft);
  color: var(--color-primary);
}

.persona-copy {
  display: flex;
  flex-direction: column;
  gap: 1px;
  min-width: 0;
  flex: 1;
}

.persona-copy strong {
  font-size: 12px;
  font-weight: 500;
}

.persona-copy em {
  color: var(--color-muted-soft);
  font-size: 9.5px;
  font-style: normal;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.persona-check {
  flex-shrink: 0;
  color: var(--color-primary);
  font-size: 12px;
}

.persona-note {
  margin-top: auto;
  padding: 14px 12px 6px;
  border-top: 1px solid var(--color-hairline-soft);
}

.persona-note span {
  color: var(--color-primary);
  font-size: 11px;
}

.persona-note p {
  margin: 7px 0 0;
  color: var(--color-muted-soft);
  font-family: var(--font-serif);
  font-size: 11px;
  line-height: 1.7;
}

.chat-stage {
  display: flex;
  flex-direction: column;
  min-width: 0;
  border: 1px solid var(--color-hairline);
  border-radius: var(--radius-lg);
  background:
    radial-gradient(600px 380px at 100% 0%, rgba(255, 107, 157, 0.055), transparent 65%),
    rgba(24, 14, 17, 0.72);
  overflow: hidden;
}

.chat-head {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  border-bottom: 1px solid var(--color-hairline-soft);
  background: rgba(255, 255, 255, 0.015);
}

.stage-mark {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  border: 1px solid var(--color-primary-line);
  border-radius: 50%;
  background: var(--color-primary-soft);
  color: var(--color-primary);
  font-size: 15px;
}

.chat-head-copy {
  min-width: 0;
}

.chat-head-copy h2 {
  margin: 0 0 1px;
  font-family: var(--font-serif);
  font-size: 17px;
  font-weight: 500;
  color: var(--color-ink);
}

.chat-head-copy p {
  margin: 0;
  color: var(--color-muted-soft);
  font-size: 10px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.online-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-left: auto;
  padding: 4px 10px;
  border: 1px solid var(--color-hairline);
  border-radius: var(--radius-full);
  color: var(--color-muted);
  font-size: 9.5px;
}

.online-pill i {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #8fd3b6;
  box-shadow: 0 0 0 3px rgba(143, 211, 182, 0.1);
}

.chat-box {
  flex: 1;
  padding: 24px 26px;
  overflow-y: auto;
  scroll-behavior: smooth;
}

.chat-welcome {
  max-width: 560px;
  margin: 6vh auto 0;
  text-align: center;
}

.welcome-mark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 46px;
  height: 46px;
  margin-bottom: 18px;
  border: 1px solid var(--color-primary-line);
  border-radius: 50%;
  background: var(--color-primary-soft);
  color: var(--color-primary);
  font-size: 18px;
}

.chat-welcome h3 {
  margin: 0 0 10px;
  font-family: var(--font-serif);
  font-size: 26px;
  font-weight: 500;
  letter-spacing: -0.4px;
  color: var(--color-ink);
}

.chat-welcome p {
  margin: 0 auto 24px;
  max-width: 420px;
  color: var(--color-muted);
  font-size: 12.5px;
  line-height: 1.8;
}

.suggestions {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-width: 420px;
  margin: 0 auto;
}

.suggestions button {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 11px 15px;
  border: 1px solid var(--color-hairline);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.025);
  color: var(--color-body);
  font-size: 11.5px;
  text-align: left;
  cursor: pointer;
  transition: all var(--dur-fast) var(--ease-out);
}

.suggestions button:hover {
  border-color: var(--color-primary-line);
  background: rgba(255, 107, 157, 0.06);
  color: var(--color-ink);
  transform: translateX(2px);
}

.suggestions button .el-icon {
  color: var(--color-muted-soft);
  font-size: 11px;
}

.message {
  display: flex;
  gap: 8px;
  max-width: 720px;
  margin-bottom: 14px;
  animation: fade-rise 260ms var(--ease-out) both;
}

.message.user {
  flex-direction: row-reverse;
  margin-left: auto;
}

.message-avatar {
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 16px;
  border: 1px solid var(--color-hairline);
  border-radius: 50%;
  background: var(--color-primary-soft);
  color: var(--color-primary);
  font-family: var(--font-serif);
  font-size: 12px;
}

.message-body {
  display: flex;
  flex-direction: column;
  gap: 5px;
  min-width: 0;
}

.message.user .message-body {
  align-items: flex-end;
}

.message-meta {
  color: var(--color-muted-soft);
  font-size: 9px;
  letter-spacing: 0.6px;
}

.message-bubble {
  padding: 12px 16px;
  border: 1px solid var(--color-hairline-soft);
  border-left: 3px solid var(--color-primary);
  border-radius: 4px 14px 14px 14px;
  background: rgba(255, 255, 255, 0.06);
  color: var(--color-body);
  font-size: 13px;
  line-height: 1.8;
  white-space: pre-wrap;
  word-break: break-word;
  /* 微阴影提层次, 玫瑰色左缘带区分 AI 与用户 */
  box-shadow: 0 4px 18px rgba(16, 8, 10, 0.35);
}

.message.user .message-bubble {
  border: 0;
  border-radius: 14px 4px 14px 14px;
  background: linear-gradient(135deg, #ff8db4, #e24f86);
  color: #1c0d12;
  box-shadow: 0 10px 26px rgba(255, 107, 157, 0.16);
}

.cursor {
  color: var(--color-primary);
  animation: blink 0.7s infinite;
}

@keyframes blink {
  50% {
    opacity: 0;
  }
}

.chat-input {
  padding: 14px 18px 16px;
  border-top: 1px solid var(--color-hairline-soft);
  background: rgba(255, 255, 255, 0.02);
}

.chat-input :deep(.el-textarea__inner) {
  min-height: 58px !important;
  padding: 11px 14px;
  background: rgba(17, 9, 12, 0.55) !important;
  font-size: 12.5px;
  line-height: 1.6;
}

.input-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  margin-top: 9px;
}

.hint {
  color: var(--color-muted-soft);
  font-size: 9.5px;
}

@media (max-width: 900px) {
  .chat-page {
    grid-template-columns: minmax(0, 1fr);
    height: auto;
    min-height: 0;
  }

  .persona-panel {
    padding: 14px;
  }

  .persona-head {
    display: none;
  }

  .persona-list {
    flex-direction: row;
    padding: 0 0 4px;
    overflow-x: auto;
  }

  .persona-item {
    width: auto;
    flex-shrink: 0;
    padding: 7px 10px;
  }

  .persona-item .persona-copy em,
  .persona-note {
    display: none;
  }

  .chat-stage {
    height: calc(100vh - 210px);
    min-height: 520px;
  }
}

@media (max-width: 620px) {
  .chat-box {
    padding: 18px 15px;
  }

  .chat-welcome {
    margin-top: 3vh;
  }

  .chat-welcome h3 {
    font-size: 22px;
  }

  .chat-stage {
    height: calc(100vh - 190px);
  }

  .message {
    max-width: 94%;
  }

  .hint {
    display: none;
  }

  .input-actions {
    justify-content: flex-end;
  }
}
</style>
