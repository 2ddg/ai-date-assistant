<template>
  <div class="spots-container">
    <el-card class="ai-card">
      <template #header>
        <div class="card-header">
          <el-icon :size="20"><MagicStick /></el-icon>
          <span>约会地点推荐 · 接入百度地图真实 POI</span>
          <el-tag type="success" size="small" effect="dark" style="margin-left: 8px">真实地址 / 电话 / 评分</el-tag>
        </div>
      </template>

      <el-form :model="form" label-width="80px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="城市">
              <el-input
                v-model="form.city"
                placeholder="例如：成都、北京、上海、广州"
                size="large"
                clearable
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="预算">
              <el-input
                v-model="form.budget"
                placeholder="如：人均50、免费、300以内、不限"
                size="large"
                clearable
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="场景">
          <el-checkbox-group v-model="form.categories">
            <el-checkbox v-for="c in categoryOptions" :key="c" :label="c">{{ c }}</el-checkbox>
          </el-checkbox-group>
        </el-form-item>

        <el-form-item label="标签">
          <el-checkbox-group v-model="form.tags">
            <el-checkbox v-for="t in tagOptions" :key="t" :label="t">{{ t }}</el-checkbox>
          </el-checkbox-group>
        </el-form-item>

        <el-form-item label="额外要求">
          <el-input
            v-model="form.extra"
            type="textarea"
            :rows="2"
            placeholder="例如：三里屯附近、第一次约会、女生喜欢猫、安静一点..."
            maxlength="100"
            show-word-limit
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            @click="handleRecommend"
          >
            <el-icon><MagicStick /></el-icon>
            搜索真实地点
          </el-button>
          <el-button
            v-if="mapUrl"
            size="large"
            type="success"
            plain
            @click="openMap"
          >
            <el-icon><MapLocation /></el-icon>
            在地图上查看
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="result-card" style="margin-top: 16px">
      <template #header>
        <div class="card-header">
          <el-icon :size="20"><LocationFilled /></el-icon>
          <span>
            推荐结果
            <el-tag size="small" type="info" style="margin-left: 8px">{{ spots.length }} 个</el-tag>
            <el-tag v-if="spots.length > 0" size="small" type="success" style="margin-left: 4px">真实地图数据</el-tag>
          </span>
        </div>
      </template>

      <div v-if="loading" class="empty">
        <el-icon :size="48" class="loading-icon"><Loading /></el-icon>
        <p>正在调用百度地图搜索真实地点...</p>
      </div>
      <div v-else-if="spots.length === 0" class="empty">
        <el-empty description="输入城市和需求，让 AI 从百度地图找真实约会地点" />
      </div>

      <el-row v-else :gutter="16">
        <el-col
          v-for="(spot, idx) in spots"
          :key="(spot.name) + idx"
          :xs="24"
          :sm="12"
          :md="8"
          :lg="6"
          style="margin-bottom: 16px"
        >
          <el-card :body-style="{ padding: 0 }" class="spot-card" shadow="hover">
            <div class="spot-img-wrap">
              <img
                v-if="spot.image_url"
                :src="spot.image_url"
                :alt="spot.name"
                class="spot-img"
                loading="lazy"
                referrerpolicy="no-referrer"
                @error="onImgError"
              />
              <div v-else class="spot-placeholder">
                <el-icon :size="40" color="#ff6b9d"><Picture /></el-icon>
              </div>
              <div class="spot-badge">
                <el-tag :type="getTagType(spot.category)" size="small">
                  {{ spot.category || '其他' }}
                </el-tag>
              </div>
              <div v-if="spot.overall_rating" class="spot-rating">
                <el-icon color="#ffb400"><Star /></el-icon>
                {{ spot.overall_rating }}
              </div>
            </div>
            <div class="spot-body">
              <div class="spot-title">
                <h3 class="spot-name" :title="spot.name">{{ spot.name }}</h3>
                <span class="price">{{ spot.price_level }}</span>
              </div>
              <div v-if="spot.city || spot.area" class="spot-city">
                <el-icon><Location /></el-icon>
                {{ spot.city }}{{ spot.area ? ' · ' + spot.area : '' }}
              </div>
              <p class="spot-desc">{{ spot.description }}</p>
              <div v-if="spot.tags" class="spot-tags">
                <el-tag
                  v-for="t in (spot.tags || '').split(',').slice(0, 4)"
                  :key="t"
                  size="small"
                  effect="plain"
                  class="spot-tag"
                >
                  {{ t.trim() }}
                </el-tag>
              </div>
              <div v-if="spot.address" class="spot-address">
                <el-icon><MapLocation /></el-icon>
                <span>{{ spot.address }}</span>
              </div>
              <div v-if="spot.phone" class="spot-address">
                <el-icon><Phone /></el-icon>
                <span>{{ spot.phone }}</span>
              </div>
              <div v-if="spot.comment_num" class="spot-meta">
                <el-icon><ChatLineSquare /></el-icon>
                {{ spot.comment_num }} 条评价
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import {
  LocationFilled, Location, MapLocation, MagicStick, Loading, Picture, Star, Phone, ChatLineSquare
} from '@element-plus/icons-vue'
import { aiRecommendSpots } from '../api/spots.js'

const form = ref({
  city: '成都',
  categories: [],
  tags: [],
  budget: '',
  extra: '',
})
const categoryOptions = ['餐厅', '咖啡厅', '酒吧', '公园', '电影院', '展览', '户外', '娱乐', '体验', '书店']
const tagOptions = ['浪漫', '安静', '热闹', '免费', '夜景', '网红', '小众', '有宠物', '文艺', '互动', '适合聊天', '拍照']

const spots = ref([])
const loading = ref(false)
const mapUrl = ref('')

async function handleRecommend() {
  if (!form.value.city.trim()) {
    ElMessage.warning('请输入城市')
    return
  }
  loading.value = true
  mapUrl.value = ''
  try {
    const data = await aiRecommendSpots({ ...form.value })
    spots.value = Array.isArray(data.spots) ? data.spots : []
    mapUrl.value = data.map_url || ''
    if (spots.value.length === 0) {
      ElMessage.warning(data.error || '没有找到匹配的真实地点，换个条件试试')
    } else {
      ElMessage.success(`百度地图找到 ${spots.value.length} 个真实地点！`)
    }
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '调用百度地图失败，请重试')
    console.error(e)
  } finally {
    loading.value = false
  }
}

function openMap() {
  if (mapUrl.value) {
    window.open(mapUrl.value, '_blank')
  }
}

function getTagType(category) {
  const map = {
    餐厅: 'danger', 咖啡厅: 'info', 酒吧: 'warning', 公园: 'success',
    电影院: 'danger', 展览: '', 户外: 'success', 娱乐: 'warning', 体验: '', 书店: 'info',
    美食: 'danger',
  }
  return map[category] || 'info'
}

function onImgError(e) {
  const img = e.target
  img.style.display = 'none'
  const wrap = img.parentElement
  if (wrap && !wrap.querySelector('.spot-placeholder')) {
    const ph = document.createElement('div')
    ph.className = 'spot-placeholder'
    ph.innerHTML = '<svg viewBox="0 0 24 24" width="40" height="40" fill="#ff6b9d"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5a2.5 2.5 0 0 1 0-5 2.5 2.5 0 0 1 0 5z"/></svg>'
    wrap.appendChild(ph)
  }
}
</script>

<style scoped>
.spots-container {
  max-width: 1300px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.ai-card,
.result-card {
  border-radius: 12px;
}

.empty {
  text-align: center;
  color: #909399;
  padding: 40px 0;
}

.loading-icon {
  animation: spin 1s linear infinite;
  color: #ff6b9d;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.spot-card {
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s;
  height: 100%;
  border: 1px solid #ebeef5;
}

.spot-card:hover {
  transform: translateY(-4px);
  border-color: #ff6b9d;
  box-shadow: 0 12px 32px rgba(255, 107, 157, 0.18);
}

.spot-img-wrap {
  position: relative;
  width: 100%;
  height: 140px;
  overflow: hidden;
  background: linear-gradient(135deg, #ffe4ec, #fff3d6);
}

.spot-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.spot-card:hover .spot-img {
  transform: scale(1.05);
}

.spot-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.spot-badge {
  position: absolute;
  top: 8px;
  left: 8px;
}

.spot-rating {
  position: absolute;
  top: 8px;
  right: 8px;
  background: rgba(0, 0, 0, 0.6);
  color: #ffb400;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 2px;
}

.spot-body {
  padding: 12px 14px;
}

.spot-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 4px;
}

.spot-name {
  margin: 0;
  font-size: 15px;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
}

.price {
  font-weight: bold;
  color: #ff6b9d;
  font-size: 13px;
  white-space: nowrap;
}

.spot-city {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #909399;
  margin-bottom: 6px;
}

.spot-desc {
  font-size: 12.5px;
  color: #606266;
  line-height: 1.6;
  margin: 0 0 8px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: 2.5em;
}

.spot-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-bottom: 6px;
}

.spot-tag {
  font-size: 11px;
}

.spot-address {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.spot-meta {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: #c0c4cc;
  margin-top: 4px;
}
</style>
