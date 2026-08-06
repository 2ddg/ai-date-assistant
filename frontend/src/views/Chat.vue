<template>
  <div class="chat-container">
    <div class="persona-bar">
      <span class="label">选择人格：</span>
      <el-radio-group v-model="selectedPersona" @change="handlePersonaChange">
        <el-radio-button
          v-for="p in personas"
          :key="p.id"
          :value="p.id"
        >
          {{ p.name }}
        </el-radio-button>
      </el-radio-group>
      <el-tag v-if="currentPersona" type="info" size="small" class="persona-info">
        {{ currentPersona.speaking_style?.slice(0, 20) }}
      </el-tag>
    </div>

    <div ref="chatBoxRef" class="chat-box">
      <div
        v-for="(msg, idx) in messages"
        :key="idx"
        class="chat-bubble"
        :class="msg.role"
      >
        <span v-if="msg.role === 'assistant'" class="persona-tag">
          {{ currentPersona?.name || 'AI' }}
        </span>
        <span class="msg-content">{{ msg.content }}</span>
      </div>
      <div v-if="streaming" class="chat-bubble assistant">
        <span class="persona-tag">{{ currentPersona?.name || 'AI' }}</span>
        <span class="msg-content">{{ streamedText }}<span class="cursor">|</span></span>
      </div>
    </div>

    <div class="chat-input">
      <el-input
        v-model="input"
        type="textarea"
        :rows="3"
        placeholder="和 AI 约会助手聊聊你的恋爱问题..."
        :disabled="streaming"
        @keydown.enter.exact.prevent="handleSend"
        resize="none"
      />
      <div class="input-actions">
        <span class="hint">Enter 发送 / Shift+Enter 换行</span>
        <el-button
          type="primary"
          :loading="streaming"
          @click="handleSend"
        >
          <el-icon><Promotion /></el-icon>
          发送
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Promotion } from '@element-plus/icons-vue'
import { listPersonas } from '../api/spots.js'
import { streamChat, getHistory } from '../api/chat.js'

const personas = ref([])
const selectedPersona = ref(null)
const messages = ref([])
const input = ref('')
const streaming = ref(false)
const streamedText = ref('')
const chatBoxRef = ref(null)

const currentPersona = computed(() =>
  personas.value.find((p) => p.id === selectedPersona.value)
)

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

function handlePersonaChange() {
  messages.value = []
  loadHistory()
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
      const lines = buffer.split('\n')
      buffer = lines.pop()

      for (const line of lines) {
        const trimmed = line.trim()
        if (trimmed.startsWith('data: ')) {
          const data = trimmed.slice(6)
          if (data === '[DONE]') break
          streamedText.value += data
        }
      }
      scrollToBottom()
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
.chat-container {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 120px);
  max-width: 800px;
  margin: 0 auto;
}

.persona-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: #fff;
  border-radius: 12px;
  margin-bottom: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.persona-bar .label {
  font-weight: 600;
  color: #303133;
}

.persona-info {
  margin-left: auto;
  max-width: 200px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chat-box {
  flex: 1;
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  overflow-y: auto;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  display: flex;
  flex-direction: column;
}

.chat-bubble {
  max-width: 70%;
  padding: 10px 14px;
  border-radius: 12px;
  margin-bottom: 10px;
  line-height: 1.6;
  word-break: break-word;
  white-space: pre-wrap;
}

.chat-bubble.user {
  background: #ff6b9d;
  color: #fff;
  margin-left: auto;
}

.chat-bubble.assistant {
  background: #f4f4f5;
  color: #303133;
  border: 1px solid #e9e9eb;
}

.persona-tag {
  display: inline-block;
  font-size: 11px;
  color: #909399;
  margin-right: 6px;
}

.msg-content {
  font-size: 14px;
}

.cursor {
  animation: blink 0.6s infinite;
}

@keyframes blink {
  50% { opacity: 0; }
}

.chat-input {
  margin-top: 12px;
  background: #fff;
  border-radius: 12px;
  padding: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
}

.hint {
  font-size: 12px;
  color: #c0c4cc;
}
</style>
