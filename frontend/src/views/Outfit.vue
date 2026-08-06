<template>
  <div class="outfit-container">
    <el-row :gutter="20">
      <el-col :span="24" :lg="12">
        <el-card class="upload-card">
          <template #header>
            <div class="card-header">
              <el-icon :size="20"><UploadFilled /></el-icon>
              <span>上传穿搭照片</span>
            </div>
          </template>

          <el-upload
            :show-file-list="false"
            :auto-upload="false"
            :on-change="handleFileChange"
            accept="image/*"
            class="upload-area"
          >
            <img v-if="previewUrl" :src="previewUrl" class="preview-img" />
            <div v-else>
              <el-icon :size="48" color="#ff6b9d"><Picture /></el-icon>
              <p class="upload-tip">点击或拖拽上传照片</p>
              <p class="upload-hint">支持 JPG / PNG / WebP</p>
            </div>
          </el-upload>

          <div class="analyze-form">
            <el-form-item label="约会场合">
              <el-select v-model="occasion" placeholder="选择场合" clearable>
                <el-option label="餐厅约会" value="餐厅" />
                <el-option label="公园散步" value="公园" />
                <el-option label="电影院" value="电影院" />
                <el-option label="咖啡厅" value="咖啡厅" />
                <el-option label="正式场合" value="正式场合" />
              </el-select>
            </el-form-item>
          </div>

          <el-button
            type="primary"
            :loading="analyzing"
            :disabled="!uploadedImageId"
            @click="handleAnalyze"
            style="width: 100%"
          >
            <el-icon><BrushFilled /></el-icon>
            {{ analyzing ? '分析中...' : 'AI 穿搭分析' }}
          </el-button>
        </el-card>

        <el-card class="result-card" style="margin-top: 16px" v-if="analysisResult">
          <template #header>
            <div class="card-header">
              <el-icon :size="20"><Reading /></el-icon>
              <span>本次分析结果</span>
            </div>
          </template>
          <pre class="result-text">{{ analysisResult }}</pre>
        </el-card>
      </el-col>

      <el-col :span="24" :lg="12">
        <el-card class="history-card">
          <template #header>
            <div class="card-header">
              <el-icon :size="20"><Clock /></el-icon>
              <span>历史穿搭记录（点击查看详情）</span>
              <el-button link size="small" @click="loadHistory" style="margin-left: auto">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </div>
          </template>

          <div v-if="historyList.length === 0" class="empty">
            <el-empty description="暂无历史记录，先上传一张穿搭照片吧" />
          </div>
          <div v-else class="history-list">
            <div
              v-for="item in historyList"
              :key="item.id"
              class="history-item"
              @click="openDetail(item)"
            >
              <img v-if="item.url" :src="item.url" class="history-img" />
              <div v-else class="history-img placeholder">
                <el-icon :size="24" color="#909399"><Picture /></el-icon>
              </div>
              <div class="history-info">
                <div class="history-header">
                  <el-tag v-if="item.occasion" size="small" type="danger">
                    {{ item.occasion }}
                  </el-tag>
                  <span class="time">{{ formatTime(item.time) }}</span>
                </div>
                <p class="history-analysis">
                  <template v-if="item.analysis">
                    {{ item.analysis.slice(0, 60) }}...
                  </template>
                  <span v-else class="no-analysis">（未分析）</span>
                </p>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 穿搭记录详情抽屉 -->
    <el-drawer
      v-model="detailVisible"
      title="穿搭记录详情"
      direction="rtl"
      size="480px"
    >
      <div v-if="currentDetail" class="detail-wrap">
        <div class="detail-img-wrap">
          <img
            v-if="currentDetail.url"
            :src="currentDetail.url"
            class="detail-img"
          />
          <div v-else class="detail-img placeholder">
            <el-icon :size="48" color="#909399"><Picture /></el-icon>
          </div>
        </div>

        <div class="detail-meta">
          <div class="meta-row">
            <span class="meta-label">场合：</span>
            <el-tag v-if="currentDetail.occasion" type="danger" size="small">
              {{ currentDetail.occasion }}
            </el-tag>
            <span v-else class="meta-muted">无</span>
          </div>
          <div class="meta-row">
            <span class="meta-label">分析时间：</span>
            <span>{{ formatTime(currentDetail.time) }}</span>
          </div>
        </div>

        <div class="detail-analysis-section">
          <div class="section-title">
            <el-icon :size="16"><Reading /></el-icon>
            AI 穿搭建议
          </div>
          <div v-if="currentDetail.analysis" class="analysis-text">
            {{ currentDetail.analysis }}
          </div>
          <el-empty
            v-else
            description="这张照片还没做穿搭分析"
            :image-size="80"
          >
            <el-button
              v-if="currentDetail.id"
              type="primary"
              :loading="loadingDetailAnalysis"
              @click="analyzeFromDetail(currentDetail.id)"
            >
              立即分析
            </el-button>
          </el-empty>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  UploadFilled, Picture, BrushFilled, Reading, Clock, Refresh
} from '@element-plus/icons-vue'
import {
  uploadImage, analyzeOutfit, listImages, getImageDetail
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
    ElMessage.success('上传成功，请选择场合后点击分析')
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
    ElMessage.success('分析完成！')
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
    ElMessage.success('分析完成！')
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
.outfit-container {
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.upload-card,
.result-card,
.history-card {
  border-radius: 12px;
}

.upload-area {
  border: 2px dashed #dcdfe6;
  border-radius: 12px;
  padding: 40px;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.3s;
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.upload-area:hover {
  border-color: #ff6b9d;
}

.preview-img {
  max-width: 240px;
  max-height: 240px;
  border-radius: 8px;
  object-fit: cover;
}

.upload-tip {
  margin: 12px 0 4px;
  color: #606266;
  font-weight: 500;
}

.upload-hint {
  margin: 0;
  font-size: 12px;
  color: #909399;
}

.analyze-form {
  margin: 16px 0;
}

.empty {
  padding: 40px 0;
}

.result-text {
  white-space: pre-wrap;
  font-family: inherit;
  font-size: 14px;
  line-height: 1.8;
  color: #303133;
  background: #fafafa;
  padding: 16px;
  border-radius: 8px;
  margin: 0;
  max-height: 340px;
  overflow-y: auto;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 620px;
  overflow-y: auto;
}

.history-item {
  display: flex;
  gap: 12px;
  padding: 10px;
  border: 1px solid #ebeef5;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.25s;
}

.history-item:hover {
  border-color: #ff6b9d;
  box-shadow: 0 6px 18px rgba(255, 107, 157, 0.14);
  transform: translateY(-1px);
}

.history-img {
  width: 72px;
  height: 72px;
  border-radius: 8px;
  object-fit: cover;
  flex-shrink: 0;
}

.history-img.placeholder {
  background: #f4f4f5;
  display: flex;
  align-items: center;
  justify-content: center;
}

.history-info {
  flex: 1;
  min-width: 0;
}

.history-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.time {
  font-size: 12px;
  color: #909399;
  margin-left: auto;
  white-space: nowrap;
}

.history-analysis {
  font-size: 12.5px;
  color: #606266;
  margin: 0;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.no-analysis {
  color: #c0c4cc;
}

/* 详情抽屉 */
.detail-wrap {
  padding: 4px 4px 20px;
}

.detail-img-wrap {
  width: 100%;
  margin-bottom: 20px;
  border-radius: 12px;
  overflow: hidden;
  background: linear-gradient(135deg, #ffe4ec, #fff3d6);
}

.detail-img {
  width: 100%;
  max-height: 320px;
  object-fit: contain;
  display: block;
  background: #fff;
}

.detail-img.placeholder {
  height: 240px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.detail-meta {
  background: #fafafa;
  border-radius: 10px;
  padding: 12px 16px;
  margin-bottom: 18px;
}

.meta-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 0;
  font-size: 13.5px;
}

.meta-label {
  color: #909399;
  width: 72px;
  flex-shrink: 0;
}

.meta-muted {
  color: #c0c4cc;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 10px;
  font-size: 14px;
}

.analysis-text {
  white-space: pre-wrap;
  background: #fff6fa;
  border: 1px solid #ffdce8;
  border-radius: 10px;
  padding: 14px 16px;
  font-size: 13.5px;
  line-height: 1.8;
  color: #303133;
  max-height: 320px;
  overflow-y: auto;
}
</style>
