import { computed, onBeforeUnmount, ref, watch } from 'vue'
import {
  cancelAgentTask,
  createAgentTask,
  getAgentTask,
  getAgentTaskArtifacts,
  getAgentTaskEvents,
  retryAgentTask,
  type AgentArtifact,
  type AgentTask,
  type AgentTaskEvent,
} from '@/api/agentTask'

const TERMINAL_STATUS = new Set(['succeeded', 'failed', 'cancelled'])

export function useAgentTaskRunner<TOutput = unknown>(agentKey: string) {
  const task = ref<AgentTask<TOutput> | null>(null)
  const events = ref<AgentTaskEvent[]>([])
  const artifacts = ref<AgentArtifact[]>([])
  const loading = ref(false)
  const polling = ref(false)
  const finishedCallbacks: Array<(task: AgentTask<TOutput>) => void> = []
  let timer: number | undefined

  const result = computed(() => task.value?.result_payload?.output as TOutput | undefined)
  const status = computed(() => task.value?.status)
  const errorMessage = computed(() => task.value?.error_message || '')
  const progress = computed(() => {
    const latest = [...events.value].reverse().find((event) => typeof event.progress === 'number')
    return latest?.progress ?? (task.value?.status === 'succeeded' ? 100 : 0)
  })

  watch(
    task,
    (current) => {
      if (current && TERMINAL_STATUS.has(current.status)) {
        finishedCallbacks.forEach((callback) => callback(current))
      }
    },
    { deep: true },
  )

  function stopPolling() {
    if (timer) {
      window.clearInterval(timer)
      timer = undefined
    }
    polling.value = false
  }

  async function refresh() {
    if (!task.value) return
    task.value = await getAgentTask<TOutput>(task.value.id)
    events.value = await getAgentTaskEvents(task.value.id)
    artifacts.value = await getAgentTaskArtifacts(task.value.id)
    if (TERMINAL_STATUS.has(task.value.status)) {
      stopPolling()
      loading.value = false
    }
  }

  function startPolling() {
    stopPolling()
    polling.value = true
    timer = window.setInterval(() => {
      refresh().catch(() => {
        stopPolling()
        loading.value = false
      })
    }, 1500)
  }

  async function run(inputPayload: Record<string, unknown>, projectId?: number | null) {
    loading.value = true
    events.value = []
    artifacts.value = []
    task.value = await createAgentTask<TOutput>({
      agent_key: agentKey,
      project_id: projectId,
      input_payload: inputPayload,
    })
    await refresh()
    if (task.value && !TERMINAL_STATUS.has(task.value.status)) {
      startPolling()
    } else {
      loading.value = false
    }
    return task.value
  }

  async function retry() {
    if (!task.value) return null
    loading.value = true
    task.value = await retryAgentTask<TOutput>(task.value.id)
    await refresh()
    if (task.value && !TERMINAL_STATUS.has(task.value.status)) startPolling()
    return task.value
  }

  async function cancel() {
    if (!task.value) return null
    task.value = await cancelAgentTask<TOutput>(task.value.id)
    await refresh()
    return task.value
  }

  onBeforeUnmount(stopPolling)

  return {
    task,
    events,
    artifacts,
    loading,
    polling,
    result,
    status,
    progress,
    errorMessage,
    run,
    refresh,
    retry,
    cancel,
    onFinished(callback: (task: AgentTask<TOutput>) => void) {
      finishedCallbacks.push(callback)
    },
    stopPolling,
  }
}
