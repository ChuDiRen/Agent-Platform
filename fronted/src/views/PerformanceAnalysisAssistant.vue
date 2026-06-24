<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import AgentPageHeader from '@/components/AgentPageHeader.vue'
import { useAgentTaskRunner } from '@/composables/useAgentTaskRunner'
import {
  analyzePerformance,
  deletePerformanceRecord,
  getPerformanceRecords,
  type PerformanceMetric,
  type PerformanceAnalyzeResponse,
  type PerformanceRecord,
} from '@/api/performance'

defineOptions({ name: 'PerformanceAnalysisAssistant' })

const projectId = 1
const loading = ref(false)
const recordsLoading = ref(false)
const records = ref<PerformanceRecord[]>([])
const currentRecord = ref<PerformanceRecord | null>(null)
const detailRecord = ref<PerformanceRecord | null>(null)
const detailVisible = ref(false)
const taskRunner = useAgentTaskRunner<PerformanceAnalyzeResponse>('performance')
taskRunner.onFinished((task) => {
  const response = task.result_payload?.output
  if (task.status === 'succeeded' && response?.record) {
    currentRecord.value = response.record
    records.value.unshift(response.record)
    loading.value = false
    ElMessage.success(`AI分析完成，耗时${response.elapsed_ms}ms`)
  }
  if (task.status === 'failed') loading.value = false
})

const form = reactive({
  name: '',
  scenario: '',
  rawText: '',
})

const metrics = ref<PerformanceMetric[]>([
  { name: '', value: 0, unit: '', threshold: 0 },
])

const latestAnalysis = computed(() => currentRecord.value?.configs.analysis || null)
const latestMetrics = computed(() => currentRecord.value?.configs.metrics || metrics.value)

function isDemoPerformanceRecord(record: PerformanceRecord) {
  const config = record.configs
  const metricNames = new Set((config.metrics || []).map((item) => item.name))
  return (
    config.name === 'smoke' ||
    config.scenario.includes('互联网小说') ||
    (
      metricNames.has('平均响应时间') &&
      metricNames.has('P95响应时间') &&
      metricNames.has('错误率') &&
      metricNames.has('吞吐量') &&
      metricNames.has('CPU使用率')
    )
  )
}

function metricStatus(metric: PerformanceMetric) {
  if (metric.threshold === undefined || metric.threshold === null) return 'info'
  if (metric.name === '吞吐量') return metric.value >= metric.threshold ? 'success' : 'danger'
  return metric.value <= metric.threshold ? 'success' : 'danger'
}

function severityType(severity: string) {
  if (severity === 'high') return 'danger'
  if (severity === 'medium') return 'warning'
  return 'success'
}

function addMetric() {
  metrics.value.push({ name: '', value: 0, unit: '', threshold: 0 })
}

function removeMetric(index: number) {
  if (metrics.value.length === 1) {
    ElMessage.warning('至少保留一个指标')
    return
  }
  metrics.value.splice(index, 1)
}

async function runAnalyze() {
  if (!form.name.trim()) {
    ElMessage.warning('请输入报告名称')
    return
  }
  loading.value = true
  try {
    await taskRunner.run({
      project_id: projectId,
      name: form.name,
      scenario: form.scenario,
      raw_text: form.rawText,
      metrics: metrics.value.filter((item) => item.name.trim()),
    })
    if (!taskRunner.result.value) ElMessage.success('任务已提交，正在后台执行')
  } finally {
    loading.value = taskRunner.loading.value
  }
}

async function loadRecords() {
  recordsLoading.value = true
  try {
    const data = await getPerformanceRecords(projectId)
    records.value = data.filter((item) => !isDemoPerformanceRecord(item))
  } finally {
    recordsLoading.value = false
  }
}

function openRecord(record: PerformanceRecord) {
  detailRecord.value = record
  detailVisible.value = true
}

async function removeRecord(record: PerformanceRecord) {
  await ElMessageBox.confirm(`确认删除“${record.configs.name}”？`, '删除性能分析记录', {
    type: 'warning',
    confirmButtonText: '删除',
    cancelButtonText: '取消',
  })
  await deletePerformanceRecord(record.id)
  records.value = records.value.filter((item) => item.id !== record.id)
  if (currentRecord.value?.id === record.id) currentRecord.value = null
  if (detailRecord.value?.id === record.id) detailRecord.value = null
  ElMessage.success('已删除')
}

function formatTime(value?: string | null) {
  if (!value) return '-'
  return new Date(value).toLocaleString('zh-CN', { hour12: false })
}

onMounted(loadRecords)
</script>

<template>
  <div class="performance-page">
    <AgentPageHeader title="性能分析助手" />

    <main class="workspace">
      <section class="analysis-panel">
        <div class="panel-head">
          <div>
            <h1>AI性能数据分析助手</h1>
            <p>导入压测指标，自动识别瓶颈、断言风险并生成优化建议。</p>
          </div>
          <div class="head-actions">
            <el-button type="primary" :loading="loading" @click="runAnalyze">开始 AI 分析</el-button>
          </div>
        </div>

        <el-form label-width="96px" class="config-form">
          <el-form-item label="报告名称">
            <el-input v-model="form.name" />
          </el-form-item>
          <el-form-item label="测试场景">
            <el-input v-model="form.scenario" />
          </el-form-item>
          <el-form-item label="原始数据">
            <el-input v-model="form.rawText" type="textarea" :rows="4" />
          </el-form-item>
        </el-form>

        <div class="metric-header">
          <strong>关键指标</strong>
          <el-button text type="primary" @click="addMetric">添加指标</el-button>
        </div>
        <div class="metric-editor">
          <div v-for="(metric, index) in metrics" :key="index" class="metric-row">
            <el-input v-model="metric.name" placeholder="指标名称" />
            <el-input-number v-model="metric.value" :min="0" />
            <el-input v-model="metric.unit" placeholder="单位" />
            <el-input-number v-model="metric.threshold" :min="0" placeholder="阈值" />
            <el-button text type="danger" @click="removeMetric(index)">删除</el-button>
          </div>
        </div>
      </section>

      <aside class="result-panel">
        <div v-if="latestAnalysis" class="score-card">
          <div class="score">{{ latestAnalysis.score }}</div>
          <div>
            <strong>性能健康分</strong>
            <p>{{ latestAnalysis.summary }}</p>
          </div>
        </div>
        <div v-else class="empty-result">暂无分析结果</div>

        <div v-if="latestAnalysis" class="metric-grid">
          <div v-for="metric in latestMetrics" :key="metric.name" class="metric-card">
            <span>{{ metric.name }}</span>
            <strong>{{ metric.value }}{{ metric.unit }}</strong>
            <el-tag size="small" :type="metricStatus(metric)">阈值 {{ metric.threshold ?? '-' }}{{ metric.unit }}</el-tag>
          </div>
        </div>

        <div v-if="latestAnalysis" class="finding-list">
          <h2>AI风险结论</h2>
          <div v-for="finding in latestAnalysis.findings" :key="finding.title" class="finding-item">
            <div class="finding-title">
              <strong>{{ finding.title }}</strong>
              <el-tag :type="severityType(finding.severity)" size="small">{{ finding.severity }}</el-tag>
            </div>
            <p>{{ finding.description }}</p>
            <span>{{ finding.suggestion }}</span>
          </div>
        </div>
      </aside>

      <section class="history-panel">
        <div class="history-head">
          <h2>性能分析记录</h2>
          <el-button @click="loadRecords">刷新</el-button>
        </div>
        <el-table v-loading="recordsLoading" :data="records" stripe>
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column label="创建时间" width="180">
            <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
          </el-table-column>
          <el-table-column label="报告名称" min-width="260">
            <template #default="{ row }">
              <button class="link-btn" @click="openRecord(row)">{{ row.configs.name }}</button>
            </template>
          </el-table-column>
          <el-table-column label="健康分" width="100">
            <template #default="{ row }">{{ row.configs.analysis?.score ?? '-' }}</template>
          </el-table-column>
          <el-table-column label="操作" width="120">
            <template #default="{ row }">
              <el-button text type="danger" @click="removeRecord(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </section>
    </main>

    <el-dialog v-model="detailVisible" title="性能分析报告" width="860px">
      <div v-if="detailRecord" class="report-detail">
        <div class="score-card compact">
          <div class="score">{{ detailRecord.configs.analysis?.score ?? '-' }}</div>
          <div>
            <strong>{{ detailRecord.configs.name }}</strong>
            <p>{{ detailRecord.configs.analysis?.summary }}</p>
          </div>
        </div>
        <h3>趋势判断</h3>
        <ul>
          <li v-for="trend in detailRecord.configs.analysis?.trends || []" :key="trend">{{ trend }}</li>
        </ul>
        <h3>配置 JSON</h3>
        <pre>{{ JSON.stringify(detailRecord.configs, null, 2) }}</pre>
      </div>
    </el-dialog>
  </div>
</template>

<style lang="scss" scoped>
.performance-page {
  min-height: 100vh;
  background: #f5f7fb;
  color: #1f2937;
}

.topbar {
  height: 72px;
  padding: 0 32px;
  background: #171a22;
  color: #fff;
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
}

.brand,
.top-actions,
.exit-btn,
.link-btn {
  border: 0;
  background: transparent;
  cursor: pointer;
}

.brand {
  justify-self: start;
  color: inherit;
  display: inline-flex;
  align-items: center;
  gap: 12px;
  font-size: 22px;
  font-weight: 800;
}

.brand-mark {
  width: 38px;
  height: 38px;
  border-radius: 8px;
  display: inline-grid;
  place-items: center;
  background: linear-gradient(135deg, #ef4444, #f97316);
  font-size: 14px;
}

.project-name {
  font-size: 20px;
  font-weight: 700;
}

.top-actions {
  justify-self: end;
  display: flex;
  align-items: center;
  gap: 28px;
}

.exit-btn,
.link-btn {
  color: inherit;
  font-size: 16px;
}

.workspace {
  display: grid;
  grid-template-columns: minmax(520px, 1.1fr) minmax(420px, 0.9fr);
  gap: 20px;
  padding: 24px 32px 40px;
}

.analysis-panel,
.result-panel,
.history-panel {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.05);
}

.analysis-panel,
.result-panel {
  padding: 22px;
}

.panel-head,
.history-head,
.finding-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.panel-head {
  margin-bottom: 18px;

  h1 {
    margin: 0 0 8px;
    font-size: 24px;
  }

  p {
    margin: 0;
    color: #64748b;
  }
}

.head-actions,
.metric-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.metric-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 8px 0 12px;
}

.metric-editor {
  display: grid;
  gap: 10px;
}

.metric-row {
  grid-template-columns: 1fr 130px 100px 130px 64px;
}

.score-card {
  display: grid;
  grid-template-columns: 96px minmax(0, 1fr);
  gap: 16px;
  padding: 16px;
  background: #fff7ed;
  border: 1px solid #fed7aa;
  border-radius: 6px;
  margin-bottom: 16px;

  &.compact {
    grid-template-columns: 76px minmax(0, 1fr);
  }

  p {
    margin: 8px 0 0;
    color: #475569;
    line-height: 1.7;
  }
}

.score {
  width: 76px;
  height: 76px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  background: #ef4444;
  color: #fff;
  font-size: 28px;
  font-weight: 800;
}

.empty-result {
  padding: 36px;
  text-align: center;
  color: #94a3b8;
  border: 1px dashed #cbd5e1;
  border-radius: 6px;
  margin-bottom: 16px;
}

.metric-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.metric-card {
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 14px;
  display: grid;
  gap: 8px;

  span {
    color: #64748b;
  }

  strong {
    font-size: 22px;
  }
}

.finding-list {
  margin-top: 18px;

  h2 {
    font-size: 18px;
    margin: 0 0 12px;
  }
}

.finding-item {
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 14px;
  margin-bottom: 12px;

  p {
    margin: 10px 0;
    color: #475569;
  }

  span {
    color: #2563eb;
    line-height: 1.7;
  }
}

.history-panel {
  grid-column: 1 / -1;
  padding: 18px 22px 22px;
}

.history-head {
  margin-bottom: 12px;

  h2 {
    margin: 0;
    font-size: 20px;
  }
}

.link-btn {
  color: #2563eb;
  font-weight: 700;
}

.report-detail {
  h3 {
    margin: 18px 0 10px;
  }

  pre {
    max-height: 360px;
    overflow: auto;
    background: #f8fafc;
    border: 1px solid #e5e7eb;
    border-radius: 6px;
    padding: 14px;
    white-space: pre-wrap;
  }
}

@media (max-width: 1060px) {
  .workspace {
    grid-template-columns: 1fr;
    padding: 16px;
  }

  .topbar {
    height: auto;
    grid-template-columns: 1fr;
    gap: 10px;
    padding: 16px;
  }

  .project-name,
  .exit-btn {
    justify-self: start;
  }

  .metric-row,
  .metric-grid {
    grid-template-columns: 1fr;
  }
}
.performance-page {
  background: #f5f7fa;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

.workspace {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 24px 48px;
}

.analysis-panel,
.result-panel,
.history-panel {
  border: 0;
  border-radius: 24px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.05);
}

.performance-page {
  min-height: 100vh;
  overflow-x: hidden;
}

.workspace {
  display: grid;
  grid-template-columns: minmax(0, 1.05fr) minmax(320px, 0.95fr);
  gap: 24px;
  width: min(1280px, calc(100vw - 48px));
  max-width: none;
  padding: 0 0 40px;
}

.analysis-panel,
.result-panel,
.history-panel {
  min-width: 0;
}

.analysis-panel,
.result-panel {
  padding: 22px 24px;
}

.panel-head {
  align-items: flex-start;
  flex-wrap: wrap;
}

.head-actions {
  margin-left: auto;
}

.metric-row {
  grid-template-columns: minmax(140px, 1fr) minmax(120px, 150px) minmax(90px, 120px) minmax(120px, 150px) auto;
}

.metric-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.history-panel {
  padding: 18px 20px 22px;
}

@media (max-width: 1060px) {
  .workspace {
    grid-template-columns: 1fr;
    width: min(100%, calc(100vw - 32px));
  }

  .metric-row,
  .metric-grid {
    grid-template-columns: 1fr;
  }
}
</style>
