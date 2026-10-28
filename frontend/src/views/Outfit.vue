<template>
  <div class="outfit-page fade-rise">
    <header class="outfit-hero">
      <div>
        <p class="page-kicker">THE LOOK · AI STYLIST</p>
        <h1 class="page-title">穿对衣服，<br />也穿对自己。</h1>
        <p class="page-subtitle">
          上传今天的穿搭，AI 从配色、比例与场合三个维度给出评审。不是评判你，是帮你更自在地出现。
        </p>
      </div>
      <div class="hero-note">
        <span>✳</span>
        <p>你不需要穿成别人喜欢的样子，<br />只需要穿成自己敢出门的样子。</p>
      </div>
    </header>

    <div class="outfit-grid">
      <section class="upload-panel">
        <div class="panel-top">
          <span class="panel-step">01 / 上传穿搭</span>
          <span class="panel-source">JPG · PNG · WEBP</span>
        </div>

        <el-upload
          :show-file-list="false"
          :auto-upload="false"
          :on-change="handleFileChange"
          accept="image/*"
          class="upload-area"
        >
          <div v-if="previewUrl" class="preview-wrap">
            <img :src="previewUrl" class="preview-img" alt="穿搭预览" />
            <span class="replace-hint">点击更换照片</span>
          </div>
          <div v-else class="upload-empty">
            <span class="upload-icon"><el-icon><UploadFilled /></el-icon></span>
            <p>把今天的穿搭放进来</p>
            <span>点击或拖拽上传 · 单张不超过 5MB</span>
          </div>
        </el-upload>

        <div class="occasion-field">
          <label>约会场合</label>
          <el-select v-model="occasion" placeholder="选择今天的场合" clearable>
            <el-option label="餐厅约会" value="餐厅" />
            <el-option label="公园散步" value="公园" />
            <el-option label="电影院" value="电影院" />
            <el-option label="咖啡厅" value="咖啡厅" />
            <el-option label="正式场合" value="正式场合" />
          </el-select>
        </div>

        <el-button
          type="primary"
          size="large"
          :loading="analyzing"
          :disabled="!uploadedImageId"
          class="analyze-btn"
          @click="handleAnalyze"
        >
          <el-icon><BrushFilled /></el-icon>
          {{ analyzing ? '正在看你的穿搭…' : 'AI 穿搭评审' }}
        </el-button>
        <p class="panel-note">上传后可直接分析；更换照片不会删除历史记录。</p>
      </section>

      <section class="result-panel">
        <div class="panel-top">
          <span class="panel-step">02 / 评审结果</span>
          <span class="panel-source">AI STYLIST</span>
        </div>

        <div v-if="analysisResult" class="analysis-wrap">
          <div class="analysis-head">
            <span class="analysis-mark">✳</span>
            <div>
              <h2>今日穿搭笔记</h2>
              <p>{{ occasion || '未指定场合' }}</p>
            </div>
          </div>
          <pre class="analysis-text">{{ analysisResult }}</pre>
        </div>

        <div v-else class="result-empty">
          <span class="result-mark"><el-icon><Reading /></el-icon></span>
          <h3>还没有评审结果。</h3>
          <p>上传一张全身照，选择场合，AI 会告诉你哪里好看、哪里可以更好。</p>
          <ol>
            <li><span>01</span>上传清晰、光线自然的照片</li>
            <li><span>02</span>选择今天的约会场合</li>
            <li><span>03</span>点击「AI 穿搭评审」</li>
          </ol>
        </div>
      </section>
    </div>

    <section class="history-section">
      <div class="history-head">
        <div>
          <p class="page-kicker">03 / ARCHIVE</p>
          <h2>穿搭档案</h2>
        </div>
        <el-button link @click="loadHistory">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>

      <div v-if="historyList.length === 0" class="history-empty">
        还没有记录。第一张照片，可以是今天。
      </div>

      <div v-else class="history-grid">
        <article
          v-for="item in historyList"
          :key="item.id"
          class="history-card hover-lift"
          @click="openDetail(item)"
        >
          <div class="history-img-wrap">
            <img v-if="item.url" :src="item.url" class="history-img" :alt="item.occasion || '穿搭记录'" />
            <div v-else class="history-placeholder">
              <el-icon :size="24"><Picture /></el-icon>
            </div>
            <span v-if="item.occasion" class="history-occasion">{{ item.occasion }}</span>
          </div>
          <div class="history-body">
            <p>{{ item.analysis ? item.analysis.slice(0, 72) + '…' : '这张照片还没做穿搭分析。' }}</p>
            <span>{{ formatTime(item.time) }}</span>
          </div>
        </article>
      </div>
    </section>

    <el-drawer
      v-model="detailVisible"
      title="穿搭记录"
      direction="rtl"
      size="480px"
    >
      <div v-if="currentDetail" class="detail-wrap">
        <div class="detail-img-wrap">
          <img v-if="currentDetail.url" :src="currentDetail.url" class="detail-img" alt="穿搭详情" />
          <div v-else class="detail-img placeholder">
            <el-icon :size="42"><Picture /></el-icon>
          </div>
        </div>

        <div class="detail-meta">
          <div class="meta-row">
            <span class="meta-label">场合</span>
            <span>{{ currentDetail.occasion || '未指定' }}</span>
          </div>
          <div class="meta-row">
            <span class="meta-label">时间</span>
            <span>{{ formatTime(currentDetail.time) }}</span>
          </div>
        </div>

        <div class="detail-analysis-section">
          <p class="page-kicker">STYLE NOTE</p>
          <h3>AI 穿搭建议</h3>
          <div v-if="currentDetail.analysis" class="detail-analysis">
            {{ currentDetail.analysis }}
          </div>
          <div v-else class="detail-empty">
            <p>这张照片还没做穿搭分析。</p>
            <el-button
              v-if="currentDetail.id"
              type="primary"
              :loading="loadingDetailAnalysis"
              @click="analyzeFromDetail(currentDetail.id)"
            >
              立即分析
            </el-button>
          </div>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  UploadFilled, Picture, BrushFilled, Reading, Refresh,
} from '@element-plus/icons-vue'
import {
  uploadImage, analyzeOutfit, listImages, getImageDetail,
} from '../api/outfit.js'

const previewUrl = ref('')
const uploadedImageId = ref(null)
const occasion = ref('')
const analyzing = ref(false)
const analysisResult = ref('')
const historyList = ref([])

const detailVisible = ref(false)
const currentDetail = ref(null)
const loadingDetailAnalysis = ref(false)

async function handleFileChange(file) {
  if (!file.raw) return
  previewUrl.value = URL.createObjectURL(file.raw)
  try {
    const data = await uploadImage(file.raw)
    uploadedImageId.value = data.image_id
    analysisResult.value = ''
    ElMessage.success('上传成功，选择场合后即可分析')
    loadHistory()
  } catch (e) {
    ElMessage.error('上传失败')
    console.error(e)
  }
}

async function handleAnalyze() {
  if (!uploadedImageId.value) {
    ElMessage.warning('请先上传照片')
    return
  }
  analyzing.value = true
  try {
    const data = await analyzeOutfit(uploadedImageId.value, occasion.value)
    analysisResult.value = data.analysis
    ElMessage.success('分析完成')
    loadHistory()
  } catch (e) {
    ElMessage.error('分析失败，请重试')
    console.error(e)
  } finally {
    analyzing.value = false
  }
}

function formatTime(t) {
  if (!t) return ''
  const d = new Date(t)
  return d.toLocaleString('zh-CN')
}

async function loadHistory() {
  try {
    historyList.value = await listImages()
  } catch (e) {
    console.error(e)
  }
}

async function openDetail(item) {
  detailVisible.value = true
  try {
    currentDetail.value = await getImageDetail(item.id)
  } catch (e) {
    currentDetail.value = item
    console.error(e)
  }
}

async function analyzeFromDetail(imageId) {
  loadingDetailAnalysis.value = true
  try {
    const data = await analyzeOutfit(imageId, currentDetail.value?.occasion || '')
    if (currentDetail.value) currentDetail.value.analysis = data.analysis
    analysisResult.value = data.analysis
    ElMessage.success('分析完成')
    loadHistory()
  } catch (e) {
    ElMessage.error('分析失败')
    console.error(e)
  } finally {
    loadingDetailAnalysis.value = false
  }
}

onMounted(loadHistory)
</script>

<style scoped>
.outfit-page {
  max-width: 1240px;
  margin: 0 auto;
}

.outfit-hero {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 40px;
  padding: 14px 2px 32px;
}

.outfit-hero .page-title {
  margin-top: 4px;
}

.hero-note {
  max-width: 290px;
  padding: 16px 18px;
  border: 1px solid var(--color-hairline);
  border-radius: 3px 14px 14px 3px;
  background: rgba(255, 255, 255, 0.025);
}

.hero-note span {
  color: var(--color-primary);
  font-size: 11px;
}

.hero-note p {
  margin: 7px 0 0;
  color: var(--color-muted);
  font-family: var(--font-serif);
  font-size: 11.5px;
  line-height: 1.8;
}

.outfit-grid {
  display: grid;
  grid-template-columns: minmax(0, 0.95fr) minmax(0, 1.05fr);
  gap: 16px;
  align-items: stretch;
}

.upload-panel,
.result-panel {
  display: flex;
  flex-direction: column;
  padding: 20px;
  border: 1px solid var(--color-hairline);
  border-radius: var(--radius-lg);
  background:
    radial-gradient(520px 320px at 100% 0%, rgba(255, 107, 157, 0.055), transparent 70%),
    rgba(36, 21, 25, 0.82);
  box-shadow: var(--shadow-md);
}

.panel-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
  padding-bottom: 11px;
  border-bottom: 1px solid var(--color-hairline-soft);
}

.panel-step {
  color: var(--color-primary);
  font-size: 9px;
  letter-spacing: 1.7px;
}

.panel-source {
  color: var(--color-muted-soft);
  font-size: 8px;
  letter-spacing: 1.4px;
}

.upload-area {
  width: 100%;
}

.upload-area :deep(.el-upload) {
  display: block;
  width: 100%;
}

.upload-empty,
.preview-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  min-height: 260px;
  border: 1px dashed var(--color-hairline);
  border-radius: var(--radius-md);
  background:
    radial-gradient(300px 200px at 50% 0%, rgba(255, 107, 157, 0.07), transparent 70%),
    rgba(17, 9, 12, 0.35);
  cursor: pointer;
  overflow: hidden;
  transition: border-color var(--dur-fast) var(--ease-out), background var(--dur-fast) var(--ease-out);
}

.upload-empty:hover,
.preview-wrap:hover {
  border-color: var(--color-primary-line);
  background: rgba(255, 107, 157, 0.045);
}

.upload-icon {
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 14px;
  border: 1px solid var(--color-primary-line);
  border-radius: 50%;
  background: var(--color-primary-soft);
  color: var(--color-primary);
  font-size: 20px;
}

.upload-empty p {
  margin: 0 0 5px;
  color: var(--color-ink);
  font-family: var(--font-serif);
  font-size: 17px;
}

.upload-empty span:last-child {
  color: var(--color-muted-soft);
  font-size: 9.5px;
}

.preview-wrap {
  position: relative;
  border-style: solid;
}

.preview-img {
  width: 100%;
  height: 300px;
  object-fit: contain;
  background: #140b0e;
}

.replace-hint {
  position: absolute;
  right: 10px;
  bottom: 10px;
  padding: 4px 10px;
  border: 1px solid var(--color-hairline);
  border-radius: var(--radius-full);
  background: rgba(16, 8, 10, 0.72);
  color: var(--color-body);
  font-size: 9px;
  backdrop-filter: blur(8px);
}

.occasion-field {
  display: flex;
  flex-direction: column;
  gap: 5px;
  margin: 15px 0 13px;
}

.occasion-field label {
  color: var(--color-muted);
  font-size: 10.5px;
  letter-spacing: 0.4px;
}

.occasion-field :deep(.el-select) {
  width: 100%;
}

.analyze-btn {
  width: 100%;
  height: 44px;
}

.panel-note {
  margin: 10px 0 0;
  color: var(--color-muted-soft);
  font-size: 9.5px;
  text-align: center;
}

.result-panel {
  min-height: 430px;
}

.analysis-wrap {
  animation: fade-rise 260ms var(--ease-out) both;
}

.analysis-head {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.analysis-mark {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--color-primary-line);
  border-radius: 50%;
  background: var(--color-primary-soft);
  color: var(--color-primary);
  font-size: 15px;
}

.analysis-head h2 {
  margin: 0 0 2px;
  font-family: var(--font-serif);
  font-size: 20px;
  font-weight: 500;
  color: var(--color-ink);
}

.analysis-head p {
  margin: 0;
  color: var(--color-muted-soft);
  font-size: 9.5px;
}

.analysis-text {
  max-height: 460px;
  margin: 0;
  padding: 18px 19px;
  border: 1px solid var(--color-hairline-soft);
  border-left: 2px solid var(--color-primary);
  border-radius: 3px 12px 12px 3px;
  background: rgba(17, 9, 12, 0.35);
  color: var(--color-body);
  font-family: var(--font-family);
  font-size: 12.5px;
  line-height: 1.9;
  white-space: pre-wrap;
  overflow-y: auto;
}

.result-empty {
  display: flex;
  flex-direction: column;
  justify-content: center;
  flex: 1;
  padding: 12px 26px 24px;
}

.result-mark {
  width: 46px;
  height: 46px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
  border: 1px solid var(--color-hairline);
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.03);
  color: var(--color-muted);
  font-size: 18px;
}

.result-empty h3 {
  margin: 0 0 8px;
  font-family: var(--font-serif);
  font-size: 24px;
  font-weight: 500;
  color: var(--color-ink);
}

.result-empty > p {
  max-width: 380px;
  margin: 0 0 24px;
  color: var(--color-muted);
  font-size: 12px;
  line-height: 1.8;
}

.result-empty ol {
  display: flex;
  flex-direction: column;
  gap: 9px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.result-empty li {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--color-muted);
  font-size: 11px;
}

.result-empty li span {
  color: var(--color-primary);
  font-size: 8.5px;
  letter-spacing: 1px;
}

.history-section {
  margin-top: 32px;
}

.history-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 14px;
}

.history-head h2 {
  margin: 0;
  font-family: var(--font-serif);
  font-size: 25px;
  font-weight: 500;
  color: var(--color-ink);
}

.history-empty {
  padding: 34px 22px;
  border: 1px dashed var(--color-hairline);
  border-radius: var(--radius-lg);
  color: var(--color-muted-soft);
  font-size: 11.5px;
  text-align: center;
}

.history-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.history-card {
  border: 1px solid var(--color-hairline);
  border-radius: 13px;
  background: rgba(36, 21, 25, 0.82);
  overflow: hidden;
  cursor: pointer;
}

.history-img-wrap {
  position: relative;
  height: 180px;
  background:
    radial-gradient(220px 140px at 30% 20%, rgba(255, 107, 157, 0.12), transparent 70%),
    var(--color-surface-strong);
  overflow: hidden;
}

.history-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 520ms var(--ease-out);
}

.history-card:hover .history-img {
  transform: scale(1.04);
}

.history-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-muted-soft);
}

.history-occasion {
  position: absolute;
  top: 9px;
  left: 9px;
  padding: 3px 8px;
  border: 1px solid rgba(255, 107, 157, 0.24);
  border-radius: var(--radius-full);
  background: rgba(16, 8, 10, 0.68);
  color: #ffadc9;
  font-size: 8.5px;
  backdrop-filter: blur(8px);
}

.history-body {
  padding: 12px 13px 13px;
}

.history-body p {
  min-height: 38px;
  margin: 0 0 8px;
  color: var(--color-muted);
  font-size: 10.5px;
  line-height: 1.7;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.history-body span {
  color: var(--color-muted-soft);
  font-size: 8.5px;
}

/* Drawer */
.detail-wrap {
  padding: 2px 2px 24px;
}

.detail-img-wrap {
  width: 100%;
  margin-bottom: 18px;
  border-radius: var(--radius-md);
  background: var(--color-surface-strong);
  overflow: hidden;
}

.detail-img {
  width: 100%;
  max-height: 320px;
  object-fit: contain;
  display: block;
  background: #140b0e;
}

.detail-img.placeholder {
  height: 220px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-muted-soft);
}

.detail-meta {
  margin-bottom: 20px;
  padding: 12px 14px;
  border: 1px solid var(--color-hairline-soft);
  border-radius: var(--radius-sm);
  background: rgba(255, 255, 255, 0.025);
}

.meta-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 3px 0;
  color: var(--color-body);
  font-size: 11.5px;
}

.meta-label {
  width: 46px;
  flex-shrink: 0;
  color: var(--color-muted-soft);
  font-size: 10px;
}

.detail-analysis-section h3 {
  margin: 0 0 10px;
  font-family: var(--font-serif);
  font-size: 19px;
  font-weight: 500;
  color: var(--color-ink);
}

.detail-analysis {
  max-height: 340px;
  padding: 15px 16px;
  border: 1px solid var(--color-hairline-soft);
  border-left: 2px solid var(--color-primary);
  border-radius: 3px 10px 10px 3px;
  background: rgba(255, 255, 255, 0.025);
  color: var(--color-body);
  font-size: 12px;
  line-height: 1.9;
  white-space: pre-wrap;
  overflow-y: auto;
}

.detail-empty {
  padding: 20px;
  border: 1px dashed var(--color-hairline);
  border-radius: var(--radius-md);
  text-align: center;
}

.detail-empty p {
  margin: 0 0 14px;
  color: var(--color-muted);
  font-size: 11.5px;
}

@media (max-width: 1040px) {
  .history-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .outfit-hero {
    align-items: flex-start;
    flex-direction: column;
    gap: 18px;
  }

  .hero-note {
    display: none;
  }

  .outfit-grid {
    grid-template-columns: minmax(0, 1fr);
  }

  .result-panel {
    min-height: 0;
  }
}

@media (max-width: 700px) {
  .outfit-hero {
    padding-top: 4px;
  }

  .history-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .upload-panel,
  .result-panel {
    padding: 16px;
  }

  .result-empty {
    padding: 8px 4px 18px;
  }

  .history-img-wrap {
    height: 150px;
  }
}

@media (max-width: 460px) {
  .history-grid {
    grid-template-columns: minmax(0, 1fr);
  }
}
</style>
