import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

function parseProjectId(value: unknown): number | null {
  const raw = Array.isArray(value) ? value[0] : value
  if (raw === undefined || raw === null || raw === '') return null
  const projectId = Number(raw)
  if (!Number.isInteger(projectId) || projectId <= 0) return null
  return projectId
}

export function useProjectContext() {
  const route = useRoute()
  const router = useRouter()

  const projectId = computed(() => parseProjectId(route.query.projectId))
  const hasProjectContext = computed(() => projectId.value !== null)

  function requireProjectId(): number {
    if (projectId.value !== null) return projectId.value
    ElMessage.warning('请先选择项目')
    router.replace('/projects')
    throw new Error('缺少有效的项目上下文')
  }

  return {
    projectId,
    hasProjectContext,
    requireProjectId,
  }
}
