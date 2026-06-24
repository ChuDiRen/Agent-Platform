<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import AgentPageHeader from '@/components/AgentPageHeader.vue'
import {
  cancelAgentTask,
  getAgentTask,
  getAgentTaskArtifacts,
  getAgentTaskEvents,
  getAgentTasks,
  retryAgentTask,
  type AgentArtifact,
  type AgentTask,
  type AgentTaskEvent,
  type AgentTaskStatus,
} from '@/api/agentTask'

defineOptions({ name: 'AgentTasks' })

const route = useRoute()
const router = useRouter()
const tasks = ref<AgentTask[]>([])
const events = ref<AgentTaskEvent[]>([])
const artifacts = ref<AgentArtifact[]>([])
const selected = ref<AgentTask | null>(null)
const loading = ref(false)
const detailLoading = ref(false)
const statusFilter = ref<AgentTaskStatus | ''>('')
let timer: number | undefined

const ACTIVE_STATUSES = new Set<AgentTaskStatus>(['created', 'queued', 'running'])

const statusOptions: Array<{ label: string; value: AgentTaskStatus | '' }> = [
  { label: '全部', value: '' },
  { label: '排队中', value: 'queued' },
  { label: '运行中', value: 'running' },
  { label: '成功', value: 'succeeded' },
  { label: '失败', value: 'failed' },
  { label: '已取消', value: 'cancelled' },
]

const outputPreview = computed(() => JSON.stringify(selected.value?.result_payload?.output ?? {}, null, 2))

function statusText(status: AgentTaskStatus) {
  return {
    created: '已创建',
    queued: '排队中',
    running: '运行中',
    succeeded: '成功',
    failed: '失败',
    cancelled: '已取消',
  }[status]
}

function statusClass(status: AgentTaskStatus) {
  return `status-${status}`
}

async function loadTasks() {
  loading.value = true
  try {
    const data = await getAgentTasks({
      status: statusFilter.value || undefined,
      limit: 100,
    })
    tasks.value = data.items
    if (selected.value) {
      const latest = tasks.value.find((item) => item.id === selected.value?.id)
      if (latest) selected.value = latest
    } else if (tasks.value.length) {
      await selectTask(tasks.value[0])
    }
  } finally {
    loading.value = false
  }
}

async function selectTask(task: AgentTask, syncQuery = true) {
  selected.value = await getAgentTask(task.id)
  if (syncQuery) {
    router.replace({ path: '/agent-tasks', query: { ...route.query, task_id: String(task.id) } })
  }
  await loadDetails()
}

async function loadDetails() {
  if (!selected.value) return
  detailLoading.value = true
  try {
    const [eventData, artifactData] = await Promise.all([
      getAgentTaskEvents(selected.value.id),
      getAgentTaskArtifacts(selected.value.id),
    ])
    events.value = eventData
    artifacts.value = artifactData
  } finally {
    detailLoading.value = false
  }
}

async function refreshCurrent() {
  await loadTasks()
  if (selected.value) {
    selected.value = await getAgentTask(selected.value.id)
    await loadDetails()
  }
}

async function loadFromRoute() {
  const queryTaskId = Number(route.query.task_id)
  await loadTasks()
  if (Number.isFinite(queryTaskId) && queryTaskId > 0) {
    const task = await getAgentTask(queryTaskId)
    await selectTask(task, false)
  }
}

function startAutoRefresh() {
  timer = window.setInterval(() => {
    const hasActiveTask = tasks.value.some((item) => ACTIVE_STATUSES.has(item.status)) ||
      (selected.value ? ACTIVE_STATUSES.has(selected.value.status) : false)
    if (hasActiveTask) {
      refreshCurrent().catch(() => undefined)
    }
  }, 2000)
}

async function retrySelected() {
  if (!selected.value) return
  selected.value = await retryAgentTask(selected.value.id)
  ElMessage.success('任务已重新入队')
  await loadTasks()
}

async function cancelSelected() {
  if (!selected.value) return
  selected.value = await cancelAgentTask(selected.value.id)
  ElMessage.success('任务已取消')
  await loadTasks()
}

onMounted(async () => {
  await loadFromRoute()
  startAutoRefresh()
})

onBeforeUnmount(() => {
  if (timer) window.clearInterval(timer)
})
</script>

<template>
  <div class="task-page">
    <AgentPageHeader title="Agent任务中心" />

    <main class="workspace">
      <section class="task-list">
        <div class="toolbar">
          <el-select v-model="statusFilter" size="small" class="status-select" @change="loadTasks">
            <el-option v-for="item in statusOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
          <button class="ghost-btn" :disabled="loading" @click="refreshCurrent">刷新</button>
        </div>

        <div v-if="!tasks.length" class="empty">暂无任务</div>
        <button
          v-for="task in tasks"
          :key="task.id"
          class="task-row"
          :class="{ active: selected?.id === task.id }"
          @click="selectTask(task)"
        >
          <span class="task-main">#{{ task.id }} · {{ task.agent_key }}</span>
          <span class="task-status" :class="statusClass(task.status)">{{ statusText(task.status) }}</span>
          <span class="task-time">{{ new Date(task.created_at).toLocaleString('zh-CN', { hour12: false }) }}</span>
        </button>
      </section>

      <section class="task-detail">
        <template v-if="selected">
          <div class="detail-head">
            <div>
              <h1>任务 #{{ selected.id }}</h1>
              <p>{{ selected.agent_key }} · {{ statusText(selected.status) }}</p>
            </div>
            <div class="actions">
              <button v-if="selected.status === 'failed'" class="primary-btn" @click="retrySelected">重试</button>
              <button v-if="['created', 'queued', 'running'].includes(selected.status)" class="danger-btn" @click="cancelSelected">取消</button>
            </div>
          </div>

          <div v-if="selected.error_message" class="error-box">{{ selected.error_message }}</div>

          <div class="detail-grid">
            <article>
              <h2>执行事件</h2>
              <div v-if="detailLoading" class="muted">加载中...</div>
              <div v-else-if="!events.length" class="muted">暂无事件</div>
              <div v-for="event in events" :key="event.id" class="event-row">
                <span>{{ event.message }}</span>
                <b v-if="event.progress !== null && event.progress !== undefined">{{ event.progress }}%</b>
              </div>
            </article>

            <article>
              <h2>产物</h2>
              <div v-if="!artifacts.length" class="muted">暂无产物</div>
              <div v-for="artifact in artifacts" :key="artifact.id || artifact.storage_path" class="artifact-row">
                <span>{{ artifact.name }}</span>
                <code>{{ artifact.storage_path }}</code>
              </div>
            </article>
          </div>

          <article class="result-box">
            <h2>结果</h2>
            <pre>{{ outputPreview }}</pre>
          </article>
        </template>

        <div v-else class="empty large">选择一个任务查看详情</div>
      </section>
    </main>
  </div>
</template>

<style scoped lang="scss">
.task-page {
  min-height: 100vh;
  background: #f5f7fa;
  color: #1f2a3e;
}

.workspace {
  width: min(1240px, calc(100vw - 40px));
  margin: 0 auto 40px;
  display: grid;
  grid-template-columns: 360px minmax(0, 1fr);
  gap: 18px;
}

.task-list,
.task-detail,
article {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.task-list {
  padding: 14px;
}

.toolbar,
.detail-head,
.actions,
.task-row,
.event-row,
.artifact-row {
  display: flex;
  align-items: center;
}

.toolbar,
.detail-head {
  justify-content: space-between;
  gap: 12px;
}

.status-select {
  width: 130px;
}

.task-row {
  width: 100%;
  margin-top: 10px;
  padding: 12px;
  border: 1px solid #edf0f5;
  border-radius: 6px;
  background: #fff;
  cursor: pointer;
  flex-direction: column;
  align-items: flex-start;
  gap: 6px;
  text-align: left;
}

.task-row.active,
.task-row:hover {
  border-color: #2563eb;
  background: #f8fbff;
}

.task-main {
  font-weight: 700;
}

.task-time,
.muted,
.empty {
  color: #667085;
  font-size: 13px;
}

.task-status {
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 12px;
  background: #eef2ff;
  color: #4338ca;
}

.status-succeeded { background: #ecfdf3; color: #027a48; }
.status-failed { background: #fef3f2; color: #b42318; }
.status-cancelled { background: #f2f4f7; color: #475467; }
.status-running { background: #eff8ff; color: #175cd3; }

.task-detail {
  min-width: 0;
  padding: 18px;
}

.detail-head h1 {
  font-size: 22px;
  margin: 0 0 6px;
}

.detail-head p {
  margin: 0;
  color: #667085;
}

.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
  margin-top: 16px;
}

article {
  padding: 14px;
}

article h2 {
  margin: 0 0 12px;
  font-size: 15px;
}

.event-row,
.artifact-row {
  justify-content: space-between;
  gap: 12px;
  padding: 9px 0;
  border-top: 1px solid #f0f2f5;
  font-size: 13px;
}

.artifact-row {
  align-items: flex-start;
  flex-direction: column;
}

.artifact-row code {
  word-break: break-all;
  color: #475467;
}

.result-box {
  margin-top: 14px;
}

pre {
  margin: 0;
  max-height: 360px;
  overflow: auto;
  font-size: 13px;
  line-height: 1.6;
}

.error-box {
  margin-top: 14px;
  padding: 10px 12px;
  border-radius: 6px;
  background: #fef3f2;
  color: #b42318;
}

.ghost-btn,
.primary-btn,
.danger-btn {
  height: 32px;
  padding: 0 12px;
  border-radius: 6px;
  border: 1px solid #d0d5dd;
  background: #fff;
  cursor: pointer;
}

.primary-btn {
  background: #2563eb;
  color: #fff;
  border-color: #2563eb;
}

.danger-btn {
  background: #fff;
  color: #b42318;
  border-color: #fda29b;
}

.empty.large {
  min-height: 360px;
  display: grid;
  place-items: center;
}

@media (max-width: 900px) {
  .workspace,
  .detail-grid {
    grid-template-columns: 1fr;
  }
}
</style>
