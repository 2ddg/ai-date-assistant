<template>
  <div class="spots-page fade-rise">
    <header class="spots-hero">
      <div class="hero-copy">
        <p class="page-kicker">REAL PLACES · REAL DATES</p>
        <h1 class="page-title">把约会，<br />放进真实的世界里。</h1>
        <p class="page-subtitle">
          接入百度地图真实地点数据。不是一份氛围清单，是能走进去、坐下来、点单的地方。
        </p>
      </div>
      <div class="hero-meta">
        <div><span>真实地址</span><strong>POI</strong></div>
        <span class="meta-rule" />
        <div><span>评分 / 电话</span><strong>LIVE</strong></div>
        <span class="meta-rule" />
        <div><span>数据来源</span><strong>百度地图</strong></div>
      </div>
    </header>

    <section class="search-panel">
      <div class="panel-top">
        <span class="panel-step">01 / 设定场景</span>
        <span class="panel-source">POWERED BY BAIDU MAP</span>
      </div>

      <el-form :model="form" label-position="top" class="search-form">
        <div class="form-grid">
          <el-form-item label="城市">
            <el-input
              v-model="form.city"
              placeholder="例如：成都、北京、上海、广州"
              size="large"
              clearable
            />
          </el-form-item>
          <el-form-item label="预算">
            <el-input
              v-model="form.budget"
              placeholder="如：人均 50、免费、300 以内、不限"
              size="large"
              clearable
            />
          </el-form-item>
        </div>

        <el-form-item label="场景">
          <el-checkbox-group v-model="form.categories" class="choice-row">
            <el-checkbox v-for="c in categoryOptions" :key="c" :value="c">
              {{ c }}
            </el-checkbox>
          </el-checkbox-group>
        </el-form-item>

        <el-form-item label="氛围标签">
          <el-checkbox-group v-model="form.tags" class="choice-row">
            <el-checkbox v-for="t in tagOptions" :key="t" :value="t">
              {{ t }}
            </el-checkbox>
          </el-checkbox-group>
        </el-form-item>

        <el-form-item label="额外要求">
          <el-input
            v-model="form.extra"
            type="textarea"
            :rows="2"
            placeholder="例如：三里屯附近、第一次约会、女生喜欢猫、安静一点…"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>

        <div class="form-actions">
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
            @click="openMap"
          >
            <el-icon><MapLocation /></el-icon>
            在地图上查看
          </el-button>
          <span class="form-note">先选场景，再选心情。</span>
        </div>
      </el-form>
    </section>

    <section class="results-section">
      <div class="results-head">
        <div>
          <p class="page-kicker">02 / RESULTS</p>
          <h2>为你找到的地点</h2>
        </div>
        <span class="result-count">
          {{ loading ? '搜索中' : `${spots.length} 个地点` }}
        </span>
      </div>

      <div v-if="loading" class="state-box">
        <span class="loader-ring" />
        <p>正在调用百度地图，寻找真实地点…</p>
        <span class="state-sub">地址、评分、电话会一并带回来</span>
      </div>

      <div v-else-if="spots.length === 0" class="state-box">
        <span class="state-mark"><el-icon><LocationFilled /></el-icon></span>
        <p>输入城市和需求，让 AI 从百度地图里找一间真正能去的店。</p>
        <span class="state-sub">第一次约会，地点比话术更重要。</span>
      </div>

      <div v-else class="spot-grid">
        <article
          v-for="(spot, idx) in spots"
          :key="spot.name + idx"
          class="spot-card hover-lift"
        >
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
              <span>{{ String(idx + 1).padStart(2, '0') }}</span>
              <el-icon :size="30"><Picture /></el-icon>
            </div>
            <span class="spot-badge">{{ spot.category || '地点' }}</span>
            <span v-if="spot.overall_rating" class="spot-rating">
              <el-icon><Star /></el-icon>
              {{ spot.overall_rating }}
            </span>
          </div>

          <div class="spot-body">
            <div class="spot-title">
              <h3 :title="spot.name">{{ spot.name }}</h3>
              <span v-if="spot.price_level" class="price">{{ spot.price_level }}</span>
            </div>

            <p v-if="spot.city || spot.area" class="spot-city">
              <el-icon><Location /></el-icon>
              {{ spot.city }}{{ spot.area ? ' · ' + spot.area : '' }}
            </p>

            <p class="spot-desc">{{ spot.description || '这家店还没有被写进攻略，也许正适合你们。' }}</p>

            <div v-if="spot.tags" class="spot-tags">
              <span
                v-for="t in (spot.tags || '').split(',').slice(0, 4)"
                :key="t"
                class="spot-tag"
              >
                {{ t.trim() }}
              </span>
            </div>

            <div class="spot-facts">
              <p v-if="spot.address">
                <el-icon><MapLocation /></el-icon>
                <span>{{ spot.address }}</span>
              </p>
              <p v-if="spot.phone">
                <el-icon><Phone /></el-icon>
                <span>{{ spot.phone }}</span>
              </p>
              <p v-if="spot.comment_num">
                <el-icon><ChatLineSquare /></el-icon>
                <span>{{ spot.comment_num }} 条真实评价</span>
              </p>
            </div>
          </div>
        </article>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import {
  LocationFilled, Location, MapLocation, MagicStick, Picture, Star, Phone, ChatLineSquare,
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
      ElMessage.success(`百度地图找到 ${spots.value.length} 个真实地点`)
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

function onImgError(e) {
  const img = e.target
  img.style.display = 'none'
  const wrap = img.parentElement
  if (wrap && !wrap.querySelector('.spot-placeholder')) {
    const ph = document.createElement('div')
    ph.className = 'spot-placeholder'
    ph.innerHTML = '<span>✳</span>'
    wrap.appendChild(ph)
  }
}
</script>

<style scoped>
.spots-page {
  max-width: 1240px;
  margin: 0 auto;
}

.spots-hero {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 30px;
  padding: 14px 2px 34px;
}

.hero-copy .page-title {
  margin-top: 4px;
}

.hero-meta {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 18px;
  border: 1px solid var(--color-hairline);
  border-radius: var(--radius-md);
  background: rgba(255, 255, 255, 0.025);
}

.hero-meta div {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.hero-meta span:first-child {
  color: var(--color-muted-soft);
  font-size: 8px;
  letter-spacing: 1.2px;
  text-transform: uppercase;
}

.hero-meta strong {
  color: var(--color-body);
  font-family: var(--font-serif);
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
}

.meta-rule {
  width: 1px;
  height: 26px;
  background: var(--color-hairline);
}

.search-panel {
  padding: 20px 24px 22px;
  border: 1px solid var(--color-hairline);
  border-radius: var(--radius-lg);
  background:
    radial-gradient(600px 350px at 100% 0%, rgba(255, 107, 157, 0.07), transparent 65%),
    rgba(36, 21, 25, 0.82);
  box-shadow: var(--shadow-md);
}

.panel-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 18px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--color-hairline-soft);
}

.panel-step {
  color: var(--color-primary);
  font-size: 9px;
  letter-spacing: 1.8px;
}

.panel-source {
  color: var(--color-muted-soft);
  font-size: 8px;
  letter-spacing: 1.4px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0 18px;
}

.search-form :deep(.el-form-item) {
  margin-bottom: 15px;
}

.search-form :deep(.el-form-item__label) {
  padding-bottom: 5px;
  font-size: 10.5px;
  letter-spacing: 0.4px;
}

.choice-row {
  display: flex;
  flex-wrap: wrap;
  gap: 2px 0;
}

.search-form :deep(.el-checkbox) {
  margin-right: 16px;
  height: 24px;
}

.search-form :deep(.el-checkbox__label) {
  font-size: 11.5px;
  color: var(--color-muted);
}

.search-form :deep(.el-checkbox.is-checked .el-checkbox__label) {
  color: var(--color-primary);
}

.form-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  padding-top: 4px;
}

.form-note {
  margin-left: auto;
  color: var(--color-muted-soft);
  font-family: var(--font-serif);
  font-size: 10.5px;
  font-style: italic;
}

.results-section {
  margin-top: 34px;
}

.results-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 18px;
  margin-bottom: 16px;
}

.results-head h2 {
  margin: 0;
  font-family: var(--font-serif);
  font-size: 25px;
  font-weight: 500;
  letter-spacing: -0.4px;
  color: var(--color-ink);
}

.result-count {
  color: var(--color-muted);
  font-size: 10.5px;
  letter-spacing: 0.5px;
}

.state-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 260px;
  padding: 40px 24px;
  border: 1px dashed var(--color-hairline);
  border-radius: var(--radius-lg);
  background: rgba(255, 255, 255, 0.018);
  text-align: center;
}

.state-box p {
  margin: 14px 0 4px;
  color: var(--color-body);
  font-family: var(--font-serif);
  font-size: 15px;
  line-height: 1.7;
}

.state-sub {
  color: var(--color-muted-soft);
  font-size: 10px;
}

.state-mark {
  width: 46px;
  height: 46px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--color-primary-line);
  border-radius: 50%;
  background: var(--color-primary-soft);
  color: var(--color-primary);
  font-size: 18px;
}

.loader-ring {
  width: 34px;
  height: 34px;
  border: 1px solid var(--color-hairline);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.9s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.spot-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.spot-card {
  display: flex;
  flex-direction: column;
  border: 1px solid var(--color-hairline);
  border-radius: 15px;
  background: rgba(36, 21, 25, 0.84);
  overflow: hidden;
}

.spot-img-wrap {
  position: relative;
  width: 100%;
  height: 164px;
  overflow: hidden;
  background:
    radial-gradient(240px 160px at 30% 20%, rgba(255, 107, 157, 0.16), transparent 70%),
    var(--color-surface-strong);
}

.spot-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 520ms var(--ease-out);
}

.spot-card:hover .spot-img {
  transform: scale(1.05);
}

.spot-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: rgba(255, 107, 157, 0.5);
}

.spot-placeholder span {
  font-family: var(--font-serif);
  font-size: 22px;
  color: rgba(255, 255, 255, 0.18);
}

.spot-badge {
  position: absolute;
  top: 10px;
  left: 10px;
  padding: 3px 9px;
  border: 1px solid rgba(255, 107, 157, 0.25);
  border-radius: var(--radius-full);
  background: rgba(16, 8, 10, 0.66);
  color: #ffadc9;
  font-size: 9px;
  backdrop-filter: blur(8px);
}

.spot-rating {
  position: absolute;
  top: 10px;
  right: 10px;
  display: flex;
  align-items: center;
  gap: 3px;
  padding: 3px 8px;
  border-radius: var(--radius-full);
  background: rgba(16, 8, 10, 0.68);
  color: var(--color-gold);
  font-size: 9.5px;
  font-weight: 600;
  backdrop-filter: blur(8px);
}

.spot-body {
  display: flex;
  flex-direction: column;
  flex: 1;
  padding: 15px 16px 14px;
}

.spot-title {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 4px;
}

.spot-name,
.spot-title h3 {
  margin: 0;
  min-width: 0;
  flex: 1;
  color: var(--color-ink);
  font-family: var(--font-serif);
  font-size: 16px;
  font-weight: 500;
  line-height: 1.4;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.price {
  flex-shrink: 0;
  color: var(--color-primary);
  font-size: 10.5px;
  font-weight: 500;
}

.spot-city {
  display: flex;
  align-items: center;
  gap: 4px;
  margin: 0 0 8px;
  color: var(--color-muted-soft);
  font-size: 9.5px;
}

.spot-desc {
  min-height: 38px;
  margin: 0 0 10px;
  color: var(--color-muted);
  font-size: 11px;
  line-height: 1.7;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.spot-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-bottom: 11px;
}

.spot-tag {
  padding: 2px 7px;
  border: 1px solid var(--color-hairline-soft);
  border-radius: var(--radius-full);
  background: rgba(255, 255, 255, 0.025);
  color: var(--color-muted);
  font-size: 8.5px;
}

.spot-facts {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-top: auto;
  padding-top: 10px;
  border-top: 1px solid var(--color-hairline-soft);
}

.spot-facts p {
  display: flex;
  align-items: center;
  gap: 5px;
  margin: 0;
  color: var(--color-muted-soft);
  font-size: 9.5px;
  line-height: 1.5;
}

.spot-facts p span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.spot-facts .el-icon {
  flex-shrink: 0;
  color: var(--color-muted-soft);
}

@media (max-width: 1040px) {
  .spot-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .spots-hero {
    align-items: flex-start;
    flex-direction: column;
  }
}

@media (max-width: 680px) {
  .spots-hero {
    padding-top: 4px;
  }

  .hero-meta {
    display: none;
  }

  .search-panel {
    padding: 18px;
  }

  .form-grid {
    grid-template-columns: minmax(0, 1fr);
  }

  .form-note {
    display: none;
  }

  .spot-grid {
    grid-template-columns: minmax(0, 1fr);
  }

  .results-head {
    align-items: flex-start;
    flex-direction: column;
    gap: 4px;
  }
}
</style>
