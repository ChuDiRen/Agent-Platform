<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import AgentPageHeader from '@/components/AgentPageHeader.vue'
import {
  copyUiAutomationExec,
  createUiAutomationExec,
  deleteUiAutomationExec,
  getUiAutomationCases,
  getUiAutomationExecs,
  type UiAutomationCase,
  type UiAutomationExec,
  type UiExecutionResult,
} from '@/api/uiAutomation'

defineOptions({ name: 'UiAutomationAgent' })

const projectId = 1
const caseLoading = ref(false)
const execLoading = ref(false)
const taskSubmitting = ref(false)
const cases = ref<UiAutomationCase[]>([])
const execs = ref<UiAutomationExec[]>([])
const selectedCases = ref<UiAutomationCase[]>([])
const selectedExecs = ref<UiAutomationExec[]>([])
const detailVisible = ref(false)
const taskVisible = ref(false)
const recordsVisible = ref(false)
const reportVisible = ref(false)
const currentCase = ref<UiAutomationCase | null>(null)
const currentReport = ref<UiAutomationExec | null>(null)

const filters = reactive({
  name: '',
  priority: '',
  moduleId: '',
  execType: 'WEB 网页',
})

const taskForm = reactive({
  name: '',
  execType: 'WEB 网页',
  baseUrl: '',
  username: '',
  password: '',
  browser: 'Chromium',
  desc: '',
})

const moduleOptions = [
  { label: '全部模块', value: '' },
]

const selectedCaseNames = computed(() => selectedCases.value.map((item) => item.name).join('、'))

function priorityType(priority: number) {
  if (priority === 1) return 'danger'
  if (priority === 2) return 'warning'
  if (priority === 3) return 'primary'
  return 'info'
}

function formatTime(value?: string | null) {
  if (!value) return '-'
  return new Date(value).toLocaleString('zh-CN', { hour12: false })
}

async function loadCases() {
  caseLoading.value = true
  try {
    cases.value = await getUiAutomationCases({
      project_id: projectId,
      name: filters.name || undefined,
      priority: filters.priority ? Number(filters.priority) : undefined,
      module_id: filters.moduleId ? Number(filters.moduleId) : undefined,
      exec_type: filters.execType || undefined,
    })
  } finally {
    caseLoading.value = false
  }
}

async function loadExecs() {
  execLoading.value = true
  try {
    execs.value = await getUiAutomationExecs(projectId)
  } finally {
    execLoading.value = false
  }
}

function resetFilters() {
  Object.assign(filters, { name: '', priority: '', moduleId: '', execType: 'WEB 网页' })
  loadCases()
}

function openCase(row: UiAutomationCase) {
  currentCase.value = row
  detailVisible.value = true
}

function openTaskDialog() {
  if (!selectedCases.value.length) {
    ElMessage.warning('请先勾选需要执行的UI用例')
    return
  }
  taskForm.name = `AI UI自动化任务-${new Date().toLocaleString('zh-CN', { hour12: false })}`
  taskVisible.value = true
}

async function submitTask() {
  if (!taskForm.name.trim()) {
    ElMessage.warning('请输入任务名称')
    return
  }
  taskSubmitting.value = true
  try {
    const created = await createUiAutomationExec({
      project_id: projectId,
      name: taskForm.name,
      exec_type: taskForm.execType,
      case_ids: selectedCases.value.map((item) => item.id),
      desc: taskForm.desc,
      exec_param: {
        base_url: taskForm.baseUrl,
        browser: taskForm.browser,
        credential: { username: taskForm.username, password: taskForm.password },
      },
    })
    ElMessage.success('AI UI自动化任务已执行完成')
    taskVisible.value = false
    currentReport.value = created
    reportVisible.value = true
    await loadExecs()
  } finally {
    taskSubmitting.value = false
  }
}

function openRecords() {
  recordsVisible.value = true
  loadExecs()
}

function openReport(row: UiAutomationExec) {
  currentReport.value = row
  reportVisible.value = true
}

async function removeExec(row: UiAutomationExec) {
  await ElMessageBox.confirm(`确认删除执行记录“${row.name}”？`, '删除确认', {
    type: 'warning',
    confirmButtonText: '删除',
    cancelButtonText: '取消',
  })
  await deleteUiAutomationExec(row.id)
  ElMessage.success('已删除执行记录')
  await loadExecs()
}

async function copyExec(row: UiAutomationExec) {
  const copied = await copyUiAutomationExec(row.id)
  ElMessage.success('已复制执行')
  await loadExecs()
  openReport(copied)
}

async function batchDelete() {
  if (!selectedExecs.value.length) {
    ElMessage.warning('请先勾选执行记录')
    return
  }
  await Promise.all(selectedExecs.value.map((item) => deleteUiAutomationExec(item.id)))
  selectedExecs.value = []
  ElMessage.success('批量删除完成')
  await loadExecs()
}

function resultType(result: UiExecutionResult) {
  return result.status === '测试成功' ? 'success' : 'danger'
}

onMounted(async () => {
  await Promise.all([loadCases(), loadExecs()])
})
</script>

<template>
  <div class="ui-page">
    <AgentPageHeader title="UI自动化助手" />

    <main class="workspace">
      <section class="filter-panel">
        <el-form :inline="true" label-width="80px" @submit.prevent>
          <el-form-item label="用例名称">
            <el-input v-model="filters.name" placeholder="请输入UI用例名称" clearable />
          </el-form-item>
          <el-form-item label="优先级">
            <el-select v-model="filters.priority" placeholder="全部优先级" clearable>
              <el-option label="全部优先级" value="" />
              <el-option label="P1" :value="1" />
              <el-option label="P2" :value="2" />
              <el-option label="P3" :value="3" />
            </el-select>
          </el-form-item>
          <el-form-item label="指定模块">
            <el-select v-model="filters.moduleId" placeholder="全部模块" clearable>
              <el-option v-for="item in moduleOptions" :key="String(item.value)" :label="item.label" :value="item.value" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="loadCases">查询</el-button>
            <el-button @click="resetFilters">重置</el-button>
          </el-form-item>
        </el-form>
      </section>

      <section class="case-panel">
        <div class="panel-toolbar">
          <div class="toolbar-left">
            <el-select v-model="filters.execType" class="type-select" @change="loadCases">
              <el-option label="WEB 网页" value="WEB 网页" />
              <el-option label="移动应用端" value="移动应用端" />
            </el-select>
            <span class="hint">已选择 {{ selectedCases.length }} 条UI用例</span>
          </div>
          <div class="toolbar-actions">
            <el-button type="primary" @click="openTaskDialog">创建 AI 测试任务</el-button>
            <el-button @click="openRecords">AI 测试执行记录</el-button>
          </div>
        </div>

        <el-table
          v-loading="caseLoading"
          :data="cases"
          stripe
          @selection-change="(rows: UiAutomationCase[]) => selectedCases = rows"
        >
          <el-table-column type="selection" width="48" />
          <el-table-column prop="id" label="ID" width="88" />
          <el-table-column label="优先级" width="96">
            <template #default="{ row }">
              <el-tag :type="priorityType(row.priority)">P{{ row.priority }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="module_name" label="模块" width="140" />
          <el-table-column label="用例名称" min-width="320">
            <template #default="{ row }">
              <button class="link-btn" @click="openCase(row)">{{ row.name }}</button>
            </template>
          </el-table-column>
          <el-table-column prop="page_url" label="页面路径" width="190" />
          <el-table-column prop="viewport" label="视口" width="100" />
        </el-table>
      </section>
    </main>

    <el-dialog v-model="detailVisible" title="UI用例详情" width="780px">
      <div v-if="currentCase" class="detail-block">
        <h3>{{ currentCase.name }}</h3>
        <div class="info-grid">
          <span>页面路径</span><strong>{{ currentCase.page_url }}</strong>
          <span>执行端</span><strong>{{ currentCase.viewport }}</strong>
          <span>预期结果</span><strong>{{ currentCase.expected }}</strong>
        </div>
        <el-table :data="currentCase.steps" border>
          <el-table-column prop="action" label="动作" width="120" />
          <el-table-column prop="target" label="目标控件" />
          <el-table-column prop="value" label="输入值" />
        </el-table>
      </div>
    </el-dialog>

    <el-dialog v-model="taskVisible" title="AI UI测试任务" width="820px">
      <el-form label-width="150px" class="task-form">
        <el-form-item label="名称" required>
          <el-input v-model="taskForm.name" />
        </el-form-item>
        <el-form-item label="类型">
          <el-radio-group v-model="taskForm.execType">
            <el-radio-button label="WEB 网页" />
            <el-radio-button label="移动应用端" />
          </el-radio-group>
        </el-form-item>
        <el-form-item label="用例参数配置">
          <div class="case-summary">{{ selectedCaseNames }}</div>
        </el-form-item>
        <el-divider content-position="left">0.AI自动化系统配置参数</el-divider>
        <el-form-item label="服务端地址">
          <el-input v-model="taskForm.baseUrl" />
        </el-form-item>
        <el-form-item label="浏览器">
          <el-select v-model="taskForm.browser">
            <el-option label="Chromium" value="Chromium" />
            <el-option label="Firefox" value="Firefox" />
            <el-option label="WebKit" value="WebKit" />
          </el-select>
        </el-form-item>
        <el-form-item label="登录凭据">
          <div class="credential-row">
            <el-input v-model="taskForm.username" placeholder="username" />
            <el-input v-model="taskForm.password" placeholder="password" show-password />
          </div>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="taskForm.desc" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="taskVisible = false">取消</el-button>
        <el-button type="primary" :loading="taskSubmitting" @click="submitTask">提交执行</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="recordsVisible" title="AI UI测试执行记录" width="980px">
      <div class="record-toolbar">
        <el-button @click="recordsVisible = false">返回</el-button>
        <el-button @click="loadExecs">刷新</el-button>
        <el-button type="danger" @click="batchDelete">批量删除</el-button>
      </div>
      <el-table
        v-loading="execLoading"
        :data="execs"
        stripe
        @selection-change="(rows: UiAutomationExec[]) => selectedExecs = rows"
      >
        <el-table-column type="selection" width="48" />
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column label="创建时间" width="190">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column prop="exec_status" label="执行状态" width="120" />
        <el-table-column label="测试计划" min-width="280">
          <template #default="{ row }">
            <button class="link-btn" @click="openReport(row)">{{ row.name }}</button>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180">
          <template #default="{ row }">
            <el-button text type="danger" @click="removeExec(row)">删除</el-button>
            <el-button text type="primary" @click="copyExec(row)">复制执行</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <el-dialog v-model="reportVisible" title="AI UI执行报告" width="960px">
      <div v-if="currentReport?.details" class="report">
        <div class="summary">
          <strong>成功{{ currentReport.details.summary.success }}个用例，失败{{ currentReport.details.summary.failed }}个用例</strong>
          <span>共 {{ currentReport.details.summary.total }} 条 · {{ currentReport.name }}</span>
        </div>
        <div v-for="result in currentReport.details.results" :key="result.case_id" class="result-card">
          <div class="result-head">
            <h3>{{ result.case_name }}</h3>
            <el-tag :type="resultType(result)">{{ result.status }}</el-tag>
          </div>
          <div class="compare-grid">
            <div><strong>预期结果</strong><p>{{ result.expected }}</p></div>
            <div><strong>AI视觉执行记录</strong><p>{{ result.ai_record }}</p></div>
          </div>
          <div class="artifact-line">
            <span>页面：{{ result.page_url }}</span>
            <span>截图：{{ result.screenshot }}</span>
          </div>
          <el-table :data="result.steps" border>
            <el-table-column prop="action" label="动作" width="120" />
            <el-table-column prop="target" label="目标控件" />
            <el-table-column prop="value" label="输入值" />
          </el-table>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<style lang="scss" scoped>
.ui-page {
  min-height: 100vh;
  background: #f4f6f9;
  color: #1f2937;
}

.topbar {
  height: 72px;
  padding: 0 32px;
  background: #151922;
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
  display: inline-flex;
  align-items: center;
  gap: 12px;
  color: inherit;
  font-size: 22px;
  font-weight: 800;
  justify-self: start;
}

.brand-mark {
  width: 38px;
  height: 38px;
  border-radius: 8px;
  display: inline-grid;
  place-items: center;
  background: linear-gradient(135deg, #ec4899, #f43f5e);
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
  padding: 24px 32px 40px;
}

.filter-panel,
.case-panel {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.05);
}

.filter-panel {
  padding: 20px 22px 2px;
  margin-bottom: 18px;
}

.filter-panel :deep(.el-input),
.filter-panel :deep(.el-select) {
  width: 220px;
}

.case-panel {
  overflow: hidden;
}

.panel-toolbar,
.record-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 18px 22px;
  border-bottom: 1px solid #e5e7eb;
}

.toolbar-left,
.toolbar-actions,
.credential-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.type-select {
  width: 150px;
}

.hint,
.case-summary {
  color: #64748b;
  font-size: 14px;
}

.case-panel :deep(.el-table) {
  padding: 0 14px 18px;
}

.link-btn {
  color: #2563eb;
  font-weight: 700;
  text-align: left;
}

.detail-block h3,
.result-card h3 {
  margin: 0 0 14px;
  font-size: 18px;
}

.info-grid {
  display: grid;
  grid-template-columns: 110px minmax(0, 1fr);
  gap: 10px 14px;
  padding: 14px;
  background: #f8fafc;
  border-radius: 6px;
  margin-bottom: 16px;
}

.task-form {
  max-height: 62vh;
  overflow: auto;
  padding-right: 8px;
}

.credential-row .el-input {
  width: 220px;
}

.record-toolbar {
  padding: 0 0 14px;
  border-bottom: 0;
  justify-content: flex-start;
}

.summary {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  padding: 14px 16px;
  background: #fdf2f8;
  border: 1px solid #fbcfe8;
  border-radius: 6px;
  margin-bottom: 16px;
}

.result-card {
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 16px;
  margin-bottom: 14px;
}

.result-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.compare-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
  margin: 12px 0;

  div {
    background: #f8fafc;
    border-radius: 6px;
    padding: 12px;
  }

  p {
    margin: 8px 0 0;
    line-height: 1.7;
  }
}

.artifact-line {
  display: flex;
  gap: 20px;
  color: #64748b;
  margin: 8px 0 14px;
}

@media (max-width: 860px) {
  .topbar {
    grid-template-columns: 1fr;
    height: auto;
    gap: 10px;
    padding: 16px;
  }

  .project-name,
  .exit-btn {
    justify-self: start;
  }

  .workspace {
    padding: 16px;
  }

  .panel-toolbar,
  .toolbar-left,
  .toolbar-actions,
  .summary,
  .compare-grid {
    display: flex;
    flex-direction: column;
    align-items: stretch;
  }
}
.ui-page {
  background: #f5f7fa;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

.workspace {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 24px 48px;
}

.filter-panel,
.case-panel {
  border: 0;
  border-radius: 24px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.05);
}

.ui-page {
  min-height: 100vh;
  overflow-x: hidden;
}

.workspace {
  width: min(1280px, calc(100vw - 48px));
  max-width: none;
  padding: 0 0 40px;
}

.filter-panel,
.case-panel {
  min-width: 0;
}

.filter-panel {
  padding: 18px 20px 4px;
}

.filter-panel :deep(.el-form) {
  display: flex;
  flex-wrap: wrap;
}

.panel-toolbar {
  align-items: flex-start;
  flex-wrap: wrap;
  padding: 18px 20px;
}

.toolbar-left,
.toolbar-actions {
  flex-wrap: wrap;
}

.case-panel :deep(.el-table) {
  width: calc(100% - 40px);
  margin: 0 20px 20px;
}

@media (max-width: 900px) {
  .workspace {
    width: min(100%, calc(100vw - 32px));
  }
}
</style>
