<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  copyApiAutomationExec,
  createApiAutomationExec,
  deleteApiAutomationExec,
  getApiAutomationCases,
  getApiAutomationExecs,
  type ApiAutomationCase,
  type ApiAutomationExec,
  type ApiExecutionResult,
  type ApiRequestDetails,
} from '@/api/apiAutomation'

defineOptions({ name: 'ApiAutomationAgent' })

const router = useRouter()
const projectId = 1
const caseLoading = ref(false)
const execLoading = ref(false)
const taskSubmitting = ref(false)
const cases = ref<ApiAutomationCase[]>([])
const execs = ref<ApiAutomationExec[]>([])
const selectedCases = ref<ApiAutomationCase[]>([])
const selectedExecs = ref<ApiAutomationExec[]>([])
const detailVisible = ref(false)
const taskVisible = ref(false)
const recordsVisible = ref(false)
const reportVisible = ref(false)
const currentCase = ref<ApiAutomationCase | null>(null)
const currentReport = ref<ApiAutomationExec | null>(null)

const filters = reactive({
  name: '',
  priority: '',
  moduleId: '',
  execType: 'HTTP 请求',
})

const taskForm = reactive({
  name: '互联网小说网站登录接口冒烟测试',
  execType: 'HTTP 请求',
  baseUrl: 'http://novel.hctestedu.com',
  username: '18511114444',
  password: '123456',
  desc: '',
})

const moduleOptions = [
  { label: '全部模块', value: '' },
  { label: '用户登录', value: 4101 },
  { label: '小说搜索', value: 4102 },
  { label: '章节详情', value: 4103 },
]

const priorityOptions = [
  { label: '全部优先级', value: '' },
  { label: 'P1', value: 1 },
  { label: 'P2', value: 2 },
  { label: 'P3', value: 3 },
  { label: 'P4', value: 4 },
  { label: 'P5', value: 5 },
]

const selectedCaseNames = computed(() => selectedCases.value.map((item) => item.name).join('、'))

function handleExit() {
  router.push('/agent-hub')
}

function toJson(value: unknown) {
  return JSON.stringify(value ?? {}, null, 2)
}

function priorityText(priority: number) {
  return `P${priority}`
}

function priorityType(priority: number) {
  if (priority === 1) return 'danger'
  if (priority === 2) return 'warning'
  if (priority === 3) return 'primary'
  return 'info'
}

async function loadCases() {
  caseLoading.value = true
  try {
    cases.value = await getApiAutomationCases({
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
    execs.value = await getApiAutomationExecs(projectId)
  } finally {
    execLoading.value = false
  }
}

function resetFilters() {
  Object.assign(filters, { name: '', priority: '', moduleId: '', execType: 'HTTP 请求' })
  loadCases()
}

function openCase(row: ApiAutomationCase) {
  currentCase.value = row
  detailVisible.value = true
}

function openTaskDialog() {
  if (!selectedCases.value.length) {
    ElMessage.warning('请先勾选需要执行的接口用例')
    return
  }
  taskForm.name = `AI自动化任务-${new Date().toLocaleString('zh-CN', { hour12: false })}`
  taskVisible.value = true
}

async function submitTask() {
  if (!taskForm.name.trim()) {
    ElMessage.warning('请输入任务名称')
    return
  }
  taskSubmitting.value = true
  try {
    const created = await createApiAutomationExec({
      project_id: projectId,
      name: taskForm.name,
      exec_type: taskForm.execType,
      case_ids: selectedCases.value.map((item) => item.id),
      desc: taskForm.desc,
      exec_param: {
        base_url: taskForm.baseUrl,
        credential: {
          username: taskForm.username,
          password: taskForm.password,
        },
        case_params: Object.fromEntries(
          selectedCases.value.map((item) => [
            String(item.id),
            { username: taskForm.username, password: taskForm.password },
          ]),
        ),
      },
    })
    ElMessage.success('AI界面测试任务已执行完成')
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

function openReport(row: ApiAutomationExec) {
  currentReport.value = row
  reportVisible.value = true
}

async function removeExec(row: ApiAutomationExec) {
  await ElMessageBox.confirm(`确认删除执行记录“${row.name}”？`, '删除确认', {
    type: 'warning',
    confirmButtonText: '删除',
    cancelButtonText: '取消',
  })
  await deleteApiAutomationExec(row.id)
  ElMessage.success('已删除执行记录')
  await loadExecs()
}

async function copyExec(row: ApiAutomationExec) {
  const copied = await copyApiAutomationExec(row.id)
  ElMessage.success('已复制执行')
  await loadExecs()
  openReport(copied)
}

async function batchDelete() {
  if (!selectedExecs.value.length) {
    ElMessage.warning('请先勾选执行记录')
    return
  }
  await ElMessageBox.confirm(`确认删除 ${selectedExecs.value.length} 条执行记录？`, '批量删除', {
    type: 'warning',
    confirmButtonText: '删除',
    cancelButtonText: '取消',
  })
  await Promise.all(selectedExecs.value.map((item) => deleteApiAutomationExec(item.id)))
  selectedExecs.value = []
  ElMessage.success('批量删除完成')
  await loadExecs()
}

function formatTime(value?: string | null) {
  if (!value) return '-'
  return new Date(value).toLocaleString('zh-CN', { hour12: false })
}

function requestRows(request?: ApiRequestDetails | null) {
  if (!request) return []
  return [
    ['程序入口', request.path],
    ['执行方式', request.method],
    ['URL参数', toJson(request.url_params)],
    ['表单参数', toJson(request.form)],
    ['页面动作参数', toJson(request.json)],
    ['Cookies', toJson(request.cookies)],
    ['Headers', toJson(request.headers)],
  ]
}

function resultType(result: ApiExecutionResult) {
  return result.status === '测试成功' ? 'success' : 'danger'
}

onMounted(async () => {
  await Promise.all([loadCases(), loadExecs()])
})
</script>

<template>
  <div class="automation-page">
    <header class="topbar">
      <button class="brand" @click="router.push('/agent-hub')">
        <span class="brand-mark">AI</span>
        <span>华测 AI+接口自动化</span>
      </button>
      <div class="project-name">互联网小说网站</div>
      <button class="exit-btn" @click="handleExit">退出项目</button>
    </header>

    <main class="workspace">
      <section class="filter-panel">
        <el-form :inline="true" label-width="80px" @submit.prevent>
          <el-form-item label="用例名称">
            <el-input v-model="filters.name" placeholder="请输入用例名称" clearable />
          </el-form-item>
          <el-form-item label="优先级">
            <el-select v-model="filters.priority" placeholder="全部优先级" clearable>
              <el-option v-for="item in priorityOptions" :key="String(item.value)" :label="item.label" :value="item.value" />
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
              <el-option label="HTTP 接口" value="HTTP 请求" />
              <el-option label="WEB 网页" value="WEB 网页" />
            </el-select>
            <span class="hint">已选择 {{ selectedCases.length }} 条用例</span>
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
          @selection-change="(rows: ApiAutomationCase[]) => selectedCases = rows"
        >
          <el-table-column type="selection" width="48" />
          <el-table-column prop="id" label="ID" width="96" />
          <el-table-column label="优先级" width="100">
            <template #default="{ row }">
              <el-tag :type="priorityType(row.priority)" effect="light">{{ priorityText(row.priority) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="module_name" label="指定模块" width="150" />
          <el-table-column label="用例名称" min-width="320">
            <template #default="{ row }">
              <button class="link-btn" @click="openCase(row)">{{ row.name }}</button>
            </template>
          </el-table-column>
          <el-table-column prop="exec_type" label="类型" width="120" />
          <el-table-column label="创建时间" width="180">
            <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
          </el-table-column>
        </el-table>
      </section>
    </main>

    <el-dialog v-model="detailVisible" title="用例详情" width="760px">
      <div v-if="currentCase" class="detail-block">
        <h3>{{ currentCase.name }}</h3>
        <div class="request-grid">
          <template v-for="[label, value] in requestRows(currentCase.request)" :key="label">
            <div class="request-label">{{ label }}</div>
            <pre>{{ value }}</pre>
          </template>
        </div>
        <div class="expected-box">
          <strong>预期结果</strong>
          <p>{{ currentCase.expected }}</p>
        </div>
      </div>
    </el-dialog>

    <el-dialog v-model="taskVisible" title="AI 测试任务" width="820px">
      <el-form label-width="160px" class="task-form">
        <el-form-item label="名称" required>
          <el-input v-model="taskForm.name" />
        </el-form-item>
        <el-form-item label="类型">
          <el-radio-group v-model="taskForm.execType">
            <el-radio-button label="HTTP 请求" />
            <el-radio-button label="WEB 网页" />
          </el-radio-group>
        </el-form-item>
        <el-form-item label="用例参数配置">
          <div class="case-summary">{{ selectedCaseNames }}</div>
        </el-form-item>
        <el-divider content-position="left">0.AI自动化系统配置参数</el-divider>
        <el-form-item label="程序入口">
          <el-input v-model="taskForm.baseUrl" />
        </el-form-item>
        <el-form-item label="登录凭据">
          <div class="credential-row">
            <el-input v-model="taskForm.username" placeholder="username" />
            <el-input v-model="taskForm.password" placeholder="password" show-password />
          </div>
        </el-form-item>
        <el-form-item
          v-for="(item, index) in selectedCases"
          :key="item.id"
          :label="`${index + 1}.${item.module_name}`"
        >
          <el-input :model-value="`username=${taskForm.username}; password=${taskForm.password}`" readonly />
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

    <el-dialog v-model="recordsVisible" title="AI 测试执行记录" width="980px">
      <div class="record-toolbar">
        <el-button @click="recordsVisible = false">返回</el-button>
        <el-button @click="loadExecs">刷新</el-button>
        <el-button type="danger" @click="batchDelete">批量删除</el-button>
      </div>
      <el-table
        v-loading="execLoading"
        :data="execs"
        stripe
        @selection-change="(rows: ApiAutomationExec[]) => selectedExecs = rows"
      >
        <el-table-column type="selection" width="48" />
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column label="创建时间" width="190">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column prop="exec_status" label="执行状态" width="120" />
        <el-table-column label="测试计划" min-width="260">
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

    <el-dialog v-model="reportVisible" title="AI 执行报告" width="960px">
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
            <div>
              <strong>预期结果</strong>
              <p>{{ result.expected }}</p>
            </div>
            <div>
              <strong>AI执行记录</strong>
              <p>{{ result.ai_record }}</p>
            </div>
          </div>
          <el-collapse>
            <el-collapse-item title="执行详情" name="response">
              <pre>{{ toJson(result.response) }}</pre>
            </el-collapse-item>
            <el-collapse-item title="页面动作详情" name="request">
              <div class="request-grid compact">
                <template v-for="[label, value] in requestRows(result.request)" :key="label">
                  <div class="request-label">{{ label }}</div>
                  <pre>{{ value }}</pre>
                </template>
              </div>
            </el-collapse-item>
          </el-collapse>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<style lang="scss" scoped>
.automation-page {
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
.exit-btn {
  border: 0;
  background: transparent;
  color: inherit;
  cursor: pointer;
}

.brand {
  display: inline-flex;
  align-items: center;
  gap: 12px;
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
  background: linear-gradient(135deg, #2563eb, #16a34a);
  font-size: 14px;
}

.project-name {
  font-size: 20px;
  font-weight: 700;
}

.exit-btn {
  justify-self: end;
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
  border: 0;
  background: transparent;
  color: #2563eb;
  font-weight: 700;
  cursor: pointer;
  text-align: left;
}

.detail-block h3,
.result-card h3 {
  margin: 0 0 14px;
  font-size: 18px;
}

.request-grid {
  display: grid;
  grid-template-columns: 120px minmax(0, 1fr);
  border: 1px solid #e5e7eb;
  border-bottom: 0;
}

.request-grid.compact {
  grid-template-columns: 100px minmax(0, 1fr);
}

.request-label,
.request-grid pre {
  margin: 0;
  padding: 10px 12px;
  border-bottom: 1px solid #e5e7eb;
}

.request-label {
  background: #f8fafc;
  color: #475569;
  font-weight: 700;
}

pre {
  white-space: pre-wrap;
  word-break: break-word;
  font-family: Consolas, Monaco, monospace;
  font-size: 13px;
}

.expected-box {
  margin-top: 16px;
  padding: 14px 16px;
  background: #f8fafc;
  border-radius: 6px;
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
  background: #f0f9ff;
  border: 1px solid #bae6fd;
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
</style>
