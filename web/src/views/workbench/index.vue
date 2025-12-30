<template>
  <AppPage :show-footer="false">
    <div flex-1>
      <n-card rounded-10>
        <div flex items-center justify-between>
          <div flex items-center>
            <img rounded-full width="60" :src="userStore.avatar" />
            <div ml-10>
              <p text-20 font-semibold>
                {{ $t('views.workbench.text_hello', { username: userStore.name }) }}
              </p>
              <p mt-5 text-14 op-60>{{ $t('views.workbench.text_welcome') }}</p>
            </div>
          </div>
        </div>
      </n-card>

      <div class="dashboard-panels">
        <div v-for="panel in dashboardPanels" :key="panel.id" class="panel-card" :class="panel.tone">
          <div class="panel-header">
            <div>
              <div class="panel-label">{{ panel.label }}</div>
              <div class="panel-value">{{ panel.value }}</div>
            </div>
            <div class="panel-meta">
              <span class="panel-badge">{{ panel.badge }}</span>
              <span class="panel-sub">{{ panel.sub }}</span>
            </div>
          </div>
          <div class="panel-chart">
            <span
              v-for="(v, idx) in panel.series"
              :key="idx"
              class="panel-bar"
              :style="{ height: `${v}%` }"
            />
          </div>
          <div class="panel-footer">
            <span>{{ panel.footer }}</span>
            <span class="panel-trend">{{ panel.trend }}</span>
          </div>
        </div>
      </div>

      <div class="dashboard-charts">
        <div class="chart-card">
          <div class="chart-title">生成任务甘特图</div>
          <div class="chart-sub">最近 8 条生成记录</div>
          <div v-if="ganttItems.length === 0" class="chart-empty">暂无数据</div>
          <div v-else class="gantt-list">
            <div v-for="item in ganttItems" :key="item.id" class="gantt-row">
              <div class="gantt-label">{{ item.label }}</div>
              <div class="gantt-bar-wrap">
                <div class="gantt-bar" :style="{ width: `${item.percent}%` }"></div>
              </div>
              <div class="gantt-meta">{{ item.duration }}s</div>
            </div>
          </div>
        </div>

        <div class="chart-card">
          <div class="chart-title">思政主题分布</div>
          <div class="chart-sub">案例主题占比</div>
          <div v-if="!pieSegments.length" class="chart-empty">暂无数据</div>
          <div v-else class="pie-wrap">
            <div class="pie" :style="{ background: pieStyle }"></div>
            <div class="pie-legend">
              <div v-for="item in pieSegments" :key="item.label" class="pie-legend-item">
                <span class="pie-dot" :style="{ background: item.color }"></span>
                <span class="pie-label">{{ item.label }}</span>
                <span class="pie-value">{{ item.value }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="chart-card">
          <div class="chart-title">近 7 日生成趋势</div>
          <div class="chart-sub">个人生成记录</div>
          <div v-if="!trendSeries.length" class="chart-empty">暂无数据</div>
          <div v-else class="trend-wrap">
            <svg viewBox="0 0 100 100" class="trend-chart" aria-hidden="true">
              <polygon :points="trendAreaPoints" class="trend-area" />
              <polyline :points="trendPoints" class="trend-line" />
            </svg>
            <div class="trend-labels">
              <span v-for="label in trendLabels" :key="label">{{ label }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="dashboard-recommend">
        <div class="recommend-card">
          <div class="chart-title">猜你喜欢 · 案例推荐</div>
          <div class="chart-sub">基于你的使用偏好</div>
          <div v-if="!recommendedCases.length" class="chart-empty">暂无推荐</div>
          <div v-else class="recommend-list">
            <div v-for="item in recommendedCases" :key="item.id" class="recommend-item">
              <div class="recommend-title">{{ item.title }}</div>
              <div class="recommend-desc">{{ item.content || item.summary || '' }}</div>
            </div>
          </div>
        </div>

        <div class="recommend-card">
          <div class="chart-title">猜你喜欢 · 教学资源</div>
          <div class="chart-sub">可能对你有用的资源</div>
          <div v-if="!recommendedResources.length" class="chart-empty">暂无推荐</div>
          <div v-else class="recommend-list">
            <div v-for="item in recommendedResources" :key="item.id" class="recommend-item">
              <div class="recommend-title">{{ item.title }}</div>
              <div class="recommend-desc">{{ item.description || item.resource_type || '' }}</div>
            </div>
          </div>
        </div>
      </div>

<!--      <n-card-->
<!--        :title="$t('views.workbench.label_project')"-->
<!--        size="small"-->
<!--        :segmented="true"-->
<!--        mt-15-->
<!--        rounded-10-->
<!--      >-->
<!--        <template #header-extra>-->
<!--          <n-button text type="primary">{{ $t('views.workbench.label_more') }}</n-button>-->
<!--        </template>-->
<!--        <div flex flex-wrap justify-between>-->
<!--          <n-card-->
<!--            v-for="i in 9"-->
<!--            :key="i"-->
<!--            class="mb-10 mt-10 w-300 cursor-pointer"-->
<!--            hover:card-shadow-->
<!--            title="Vue FastAPI Admin"-->
<!--            size="small"-->
<!--          >-->
<!--            <p op-60>{{ dummyText }}</p>-->
<!--          </n-card>-->
<!--        </div>-->
<!--      </n-card>-->
    </div>
  </AppPage>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useUserStore } from '@/store'
import { useI18n } from 'vue-i18n'
import { casesApi, resourcesApi, templatesApi, themeCategoriesApi } from '@/api/ideological'
import { getGenerationHistory } from '@/api/aigc-history'

// const dummyText = '一个基于 Vue3.0、FastAPI、Naive UI 的轻量级后台管理模板'
const { t } = useI18n({ useScope: 'global' })

const dashboardStats = reactive({
  resourcesTotal: 0,
  resourcesRecent: 0,
  casesTotal: 0,
  casesRecent: 0,
  templatesTotal: 0,
  systemTemplates: 0,
  historyTotal: 0,
  avgGenerationSeconds: 0,
  recentGenerations: 0,
})

const ganttItems = ref([])
const pieSegments = ref([])
const trendSeries = ref([])
const trendLabels = ref([])
const recommendedCases = ref([])
const recommendedResources = ref([])

const dashboardPanels = computed(() => [
  {
    id: 0,
    label: '教学资源总量',
    value: `${dashboardStats.resourcesTotal}`,
    badge: '资源',
    sub: `近7日新增 ${dashboardStats.resourcesRecent}`,
    footer: '资源上传',
    trend: `${dashboardStats.resourcesTotal ? '▲' : ''}`,
    series: buildSeriesFromTotal(dashboardStats.resourcesTotal),
    tone: 'tone-emerald',
  },
  {
    id: 1,
    label: '案例总量',
    value: `${dashboardStats.casesTotal}`,
    badge: '案例',
    sub: `近7日新增 ${dashboardStats.casesRecent}`,
    footer: '案例产出',
    trend: `${dashboardStats.casesTotal ? '▲' : ''}`,
    series: buildSeriesFromTotal(dashboardStats.casesTotal),
    tone: 'tone-amber',
  },
  {
    id: 2,
    label: '模板总量',
    value: `${dashboardStats.templatesTotal}`,
    badge: '模板',
    sub: `系统模板 ${dashboardStats.systemTemplates}`,
    footer: '模板库',
    trend: `${dashboardStats.templatesTotal ? '▲' : ''}`,
    series: buildSeriesFromTotal(dashboardStats.templatesTotal),
    tone: 'tone-sky',
  },
  {
    id: 3,
    label: '平均生成耗时',
    value: `${dashboardStats.avgGenerationSeconds}s`,
    badge: '近7日',
    sub: `生成 ${dashboardStats.recentGenerations}`,
    footer: '生成历史',
    trend: `${dashboardStats.recentGenerations ? '▲' : ''}`,
    series: buildSeriesFromTotal(dashboardStats.recentGenerations),
    tone: 'tone-rose',
  },
])

const pieStyle = computed(() => {
  const total = pieSegments.value.reduce((sum, item) => sum + item.value, 0)
  if (!total) return ''
  let acc = 0
  const parts = pieSegments.value.map((item) => {
    const start = acc
    const percent = (item.value / total) * 100
    acc += percent
    return `${item.color} ${start.toFixed(2)}% ${acc.toFixed(2)}%`
  })
  return `conic-gradient(${parts.join(', ')})`
})

const trendPoints = computed(() => {
  if (!trendSeries.value.length) return ''
  const maxVal = Math.max(...trendSeries.value, 1)
  const stepX = 100 / (trendSeries.value.length - 1 || 1)
  return trendSeries.value
    .map((val, idx) => {
      const x = (idx * stepX).toFixed(2)
      const y = (100 - (val / maxVal) * 80 - 10).toFixed(2)
      return `${x},${y}`
    })
    .join(' ')
})

const trendAreaPoints = computed(() => {
  if (!trendPoints.value) return ''
  return `${trendPoints.value} 100,100 0,100`
})

const userStore = useUserStore()

const loadingCharts = ref(false)

function buildSeriesFromTotal(total) {
  const base = Math.max(6, Math.min(90, Math.floor(total)))
  const seed = [22, 34, 45, 40, 52, 58, 64, 70, 62, 76, 68, 84]
  return seed.map((v) => Math.min(96, Math.max(12, Math.round(v + (base % 12)))))
}

function normalizeListResponse(res) {
  const data = res?.data || res || {}
  const items = Array.isArray(data.items) ? data.items : Array.isArray(data) ? data : []
  const total = typeof data.total === 'number' ? data.total : items.length
  return { items, total }
}

function countRecent(items, days = 7) {
  const cutoff = Date.now() - days * 24 * 60 * 60 * 1000
  return items.filter((item) => {
    const time = new Date(item?.created_at || item?.createdAt || 0).getTime()
    return Number.isFinite(time) && time >= cutoff
  }).length
}

function buildTrendFromHistory(items, days = 7) {
  const labels = []
  const counts = []
  const now = new Date()
  for (let i = days - 1; i >= 0; i -= 1) {
    const d = new Date(now)
    d.setDate(now.getDate() - i)
    const key = d.toISOString().slice(0, 10)
    labels.push(key.slice(5))
    counts.push(0)
  }
  items.forEach((item) => {
    const key = String(item?.created_at || '').slice(0, 10)
    const idx = labels.findIndex((label) => key.slice(5) === label)
    if (idx >= 0) counts[idx] += 1
  })
  trendLabels.value = labels
  trendSeries.value = counts
}

function buildGantt(items) {
  if (!items.length) {
    ganttItems.value = []
    return
  }
  const typeLabels = {
    aigc_chat: '对话生成',
    case_generation: '案例生成',
    discussion_generation: '讨论题生成',
    thinking_generation: '思考题生成',
    content_optimization: '内容优化',
    teaching_design: '教学设计',
    knowledge_point: '知识点讲解',
    project_design: '项目实践设计',
    knowledge_explanation: '知识点解析',
    evaluation_design: '评价与考核设计',
    practice: '实践练习',
  }
  const durations = items.map((item) => item.generation_time || 0)
  const max = Math.max(...durations, 1)
  ganttItems.value = items.map((item) => {
    const durationMs = item.generation_time || 0
    const label = typeLabels[item.generation_type] || item.generation_type || '生成任务'
    return {
      id: item.id,
      label,
      duration: (durationMs / 1000).toFixed(1),
      percent: Math.min(100, Math.round((durationMs / max) * 100)),
      time: item.created_at ? item.created_at.slice(5, 16).replace('T', ' ') : '',
    }
  })
}

async function fetchWorkbenchData() {
  loadingCharts.value = true
  try {
    const [
      resourcesRes,
      casesRes,
      templatesRes,
      systemTemplatesRes,
      historyRes,
      recommendedCasesRes,
      recommendedResourcesRes,
      themeStatsRes,
      themeListRes,
    ] = await Promise.all([
      resourcesApi.getList({ page: 1, page_size: 20 }),
      casesApi.getList({ page: 1, page_size: 20 }),
      templatesApi.getList({ page: 1, page_size: 20 }),
      templatesApi.getSystem(),
      getGenerationHistory({ page: 1, page_size: 80 }),
      casesApi.getRecommended({ limit: 6 }),
      resourcesApi.getRecommended({ limit: 6 }),
      themeCategoriesApi.getCaseCountStats(),
      themeCategoriesApi.getList(),
    ])

    const resourcesData = normalizeListResponse(resourcesRes)
    const casesData = normalizeListResponse(casesRes)
    const templatesData = normalizeListResponse(templatesRes)
    const historyData = normalizeListResponse(historyRes)
    const systemTemplates = systemTemplatesRes?.data || systemTemplatesRes || []

    dashboardStats.resourcesTotal = resourcesData.total
    dashboardStats.resourcesRecent = countRecent(resourcesData.items)
    dashboardStats.casesTotal = casesData.total
    dashboardStats.casesRecent = countRecent(casesData.items)
    dashboardStats.templatesTotal = templatesData.total
    dashboardStats.systemTemplates = Array.isArray(systemTemplates) ? systemTemplates.length : 0
    dashboardStats.historyTotal = historyData.total

    const historyItems = historyData.items || []
    const avgMs = historyItems.length
      ? historyItems.reduce((sum, item) => sum + (item.generation_time || 0), 0) / historyItems.length
      : 0
    dashboardStats.avgGenerationSeconds = avgMs ? (avgMs / 1000).toFixed(1) : '0.0'
    dashboardStats.recentGenerations = countRecent(historyItems)

    buildTrendFromHistory(historyItems)
    buildGantt(historyItems.slice(0, 8))

    const themeStatsRaw = themeStatsRes?.data || themeStatsRes || {}
    const themeListRaw = themeListRes?.data || themeListRes || []
    const themeMap = Array.isArray(themeListRaw)
      ? themeListRaw.reduce((acc, item) => {
          acc[item.id] = item.name
          return acc
        }, {})
      : {}
    const colors = ['#34d399', '#fbbf24', '#38bdf8', '#fb7185', '#a78bfa', '#f97316', '#22c55e']
    const segments = Object.entries(themeStatsRaw)
      .filter(([, value]) => Number(value) > 0)
      .map(([key, value], idx) => ({
        label: themeMap[Number(key)] || `主题 ${key}`,
        value: Number(value),
        color: colors[idx % colors.length],
      }))
      .slice(0, 6)
    pieSegments.value = segments

    const casesRecommendedRaw = recommendedCasesRes?.data || recommendedCasesRes || []
    recommendedCases.value = Array.isArray(casesRecommendedRaw) ? casesRecommendedRaw.slice(0, 6) : []
    const resourcesRecommendedRaw = recommendedResourcesRes?.data || recommendedResourcesRes || []
    recommendedResources.value = Array.isArray(resourcesRecommendedRaw)
      ? resourcesRecommendedRaw.slice(0, 6)
      : []
  } catch (error) {
    // keep defaults on error
  } finally {
    loadingCharts.value = false
  }
}

onMounted(() => {
  fetchWorkbenchData()
})
</script>

<style scoped>
.dashboard-panels {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
  margin-top: 14px;
}

.panel-card {
  border-radius: 12px;
  padding: 14px 16px;
  background: #ffffff;
  border: 1px solid rgba(15, 23, 42, 0.06);
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.05);
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 180px;
  position: relative;
  overflow: hidden;
}

.panel-card::after {
  content: '';
  position: absolute;
  inset: 0;
  opacity: 0.12;
  pointer-events: none;
}

.tone-emerald::after {
  background: radial-gradient(circle at top right, #34d399, transparent 55%);
}

.tone-amber::after {
  background: radial-gradient(circle at top right, #fbbf24, transparent 55%);
}

.tone-sky::after {
  background: radial-gradient(circle at top right, #38bdf8, transparent 55%);
}

.tone-rose::after {
  background: radial-gradient(circle at top right, #fb7185, transparent 55%);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: flex-start;
}

.panel-label {
  font-size: 13px;
  color: rgba(15, 23, 42, 0.7);
}

.panel-value {
  font-size: 22px;
  font-weight: 600;
  color: rgba(15, 23, 42, 0.95);
  margin-top: 6px;
}

.panel-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 6px;
  font-size: 12px;
  color: rgba(15, 23, 42, 0.6);
}

.panel-badge {
  padding: 2px 8px;
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.06);
  font-weight: 600;
}

.panel-chart {
  display: grid;
  grid-auto-flow: column;
  grid-auto-columns: 1fr;
  align-items: end;
  gap: 4px;
  height: 64px;
}

.panel-bar {
  display: block;
  width: 100%;
  background: linear-gradient(180deg, rgba(15, 23, 42, 0.65), rgba(15, 23, 42, 0.1));
  border-radius: 8px 8px 4px 4px;
}

.tone-emerald .panel-bar {
  background: linear-gradient(180deg, rgba(16, 185, 129, 0.9), rgba(16, 185, 129, 0.15));
}

.tone-amber .panel-bar {
  background: linear-gradient(180deg, rgba(245, 158, 11, 0.9), rgba(245, 158, 11, 0.15));
}

.tone-sky .panel-bar {
  background: linear-gradient(180deg, rgba(14, 165, 233, 0.9), rgba(14, 165, 233, 0.15));
}

.tone-rose .panel-bar {
  background: linear-gradient(180deg, rgba(244, 63, 94, 0.9), rgba(244, 63, 94, 0.15));
}

.panel-footer {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: rgba(15, 23, 42, 0.6);
}

.panel-trend {
  font-weight: 600;
}

.dashboard-charts {
  margin-top: 16px;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.chart-card {
  border-radius: 14px;
  padding: 16px;
  background: #ffffff;
  border: 1px solid rgba(15, 23, 42, 0.06);
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.05);
  min-height: 220px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.chart-title {
  font-size: 14px;
  font-weight: 600;
  color: rgba(15, 23, 42, 0.9);
}

.chart-sub {
  font-size: 12px;
  color: rgba(15, 23, 42, 0.55);
}

.chart-empty {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(15, 23, 42, 0.4);
  font-size: 12px;
}

.gantt-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.gantt-row {
  display: grid;
  grid-template-columns: 120px 1fr 52px;
  align-items: center;
  gap: 10px;
  font-size: 12px;
}

.gantt-label {
  color: rgba(15, 23, 42, 0.75);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.gantt-bar-wrap {
  height: 10px;
  background: rgba(15, 23, 42, 0.06);
  border-radius: 999px;
  position: relative;
  overflow: hidden;
}

.gantt-bar {
  height: 100%;
  background: linear-gradient(90deg, rgba(52, 211, 153, 0.9), rgba(14, 165, 233, 0.9));
  border-radius: inherit;
}

.gantt-meta {
  text-align: right;
  color: rgba(15, 23, 42, 0.6);
}

.pie-wrap {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
}

.pie {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  position: relative;
}

.pie::after {
  content: '';
  position: absolute;
  inset: 18px;
  background: #fff;
  border-radius: 50%;
  box-shadow: inset 0 0 0 1px rgba(15, 23, 42, 0.04);
}

.pie-legend {
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-size: 12px;
  color: rgba(15, 23, 42, 0.7);
}

.pie-legend-item {
  display: grid;
  grid-template-columns: 12px 1fr 36px;
  gap: 8px;
  align-items: center;
}

.pie-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.pie-label {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.pie-value {
  text-align: right;
  color: rgba(15, 23, 42, 0.6);
}

.trend-wrap {
  display: flex;
  flex-direction: column;
  gap: 10px;
  flex: 1;
}

.trend-chart {
  width: 100%;
  height: 120px;
}

.trend-area {
  fill: rgba(56, 189, 248, 0.2);
}

.trend-line {
  fill: none;
  stroke: rgba(56, 189, 248, 0.9);
  stroke-width: 2;
}

.trend-labels {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  font-size: 11px;
  color: rgba(15, 23, 42, 0.5);
  text-align: center;
}

.dashboard-recommend {
  margin-top: 16px;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.recommend-card {
  border-radius: 14px;
  padding: 16px;
  background: #ffffff;
  border: 1px solid rgba(15, 23, 42, 0.06);
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.05);
  min-height: 220px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.recommend-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.recommend-item {
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid rgba(15, 23, 42, 0.06);
  background: rgba(248, 250, 252, 0.8);
}

.recommend-title {
  font-size: 13px;
  font-weight: 600;
  color: rgba(15, 23, 42, 0.9);
  margin-bottom: 4px;
}

.recommend-desc {
  font-size: 12px;
  color: rgba(15, 23, 42, 0.6);
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

@media (max-width: 1200px) {
  .dashboard-panels {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .dashboard-charts {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .dashboard-recommend {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .dashboard-panels {
    grid-template-columns: 1fr;
  }

  .dashboard-charts {
    grid-template-columns: 1fr;
  }
}
</style>
