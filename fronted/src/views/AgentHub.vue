<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/store/store'
import { getAgents, type AgentInfo } from '@/api/agent'

defineOptions({ name: 'AgentHub' })

const router = useRouter()
const userStore = useUserStore()
const agents = ref<AgentInfo[]>([])
const loading = ref(true)

function handleExit() {
  ElMessage.info('退出项目')
  router.push('/projects')
}

function handleCommand(cmd: string) {
  if (cmd === 'logout') { userStore.logout(); router.push('/login') }
}

function handleUse(agent: AgentInfo) {
  if (agent.is_placeholder) { ElMessage.info('敬请期待'); return }
  if (agent.icon === 'data' || agent.name.includes('测试数据生成')) {
    router.push('/test-data-generator')
    return
  }
  if (agent.icon === 'ui' || agent.name.includes('界面UI')) {
    ElMessage.warning('界面UI自动化脚本开发中，即将开放')
    return
  }
  if (agent.icon === 'api-auto' || agent.name.includes('接口自动化')) {
    router.push('/api-automation')
    return
  }
  if (agent.icon === 'perf' || agent.name.includes('性能数据分析')) {
    router.push('/performance-analysis')
    return
  }
  if (agent.icon === 'api-case' || agent.name.includes('接口用例')) {
    router.push('/ai-test-cases')
    return
  }
  if (agent.icon === 'testcase' || agent.name.includes('测试用例')) {
    router.push('/ai-test-cases')
    return
  }
  if (agent.icon === 'api-doc' || agent.name.includes('接口文档分析')) {
    router.push('/interface-document-analysis')
    return
  }
  if (agent.icon === 'doc' || agent.name.includes('需求')) {
    router.push('/requirement-review')
    return
  }
  ElMessage.warning('功能开发中，即将开放')
}

function parseTags(raw?: string): string[] {
  if (!raw) return []
  try { return JSON.parse(raw) } catch { return [] }
}

onMounted(async () => {
  try {
    const data = await getAgents()
    agents.value = [...data].sort((a, b) => a.sort_order - b.sort_order)
  } catch {
    ElMessage.error('加载智能体列表失败')
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="agent-hub">
    <!-- Header -->
    <header class="topbar">
      <div class="logo">
        <div class="logo-icon">熊</div>
        <span>大熊AI智能体</span>
      </div>
      <div class="topbar-right">
        <button class="exit-btn" @click="handleExit">退出项目</button>
        <el-dropdown trigger="click" @command="handleCommand">
          <div class="admin">
            <div class="avatar">{{ (userStore.userName || '管')[0].toUpperCase() }}</div>
            <span>{{ userStore.userName || '管理员' }}</span>
            <svg class="dropdown-arrow" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9" /></svg>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </header>

    <!-- Hero -->
    <section class="hero">
      <h1>智能<span class="hl">"数字员工"</span>中心，让测试<span class="hl">"降本增效"</span></h1>
      <p>AI驱动的全链路测试工具平台，九大智能体覆盖需求 → 用例 → 执行 → 报告全流程</p>
    </section>

    <!-- Loading -->
    <div v-if="loading" class="loading-box">
      <div class="spinner" /><span>加载中…</span>
    </div>

    <!-- Cards Grid -->
    <section v-else class="grid">
      <div
        v-for="agent in agents" :key="agent.id"
        class="card"
      >
        <div class="card-icon" :style="{ background: agent.gradient || 'linear-gradient(135deg,#e3f2fd,#bbdefb)' }">
          <svg v-if="agent.icon" width="22" height="22" viewBox="0 0 24 24" fill="none"
            stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
            v-html="ICON_SVG[agent.icon] || ICON_SVG['more']"
          />
          <span v-else>🤖</span>
        </div>
        <div class="card-body">
          <div class="card-title">{{ agent.name }}</div>
          <div class="card-desc">{{ agent.description }}</div>
          <div v-if="parseTags(agent.tags).length" class="tags">
            <span v-for="t in parseTags(agent.tags)" :key="t" class="tag">{{ t }}</span>
          </div>
        </div>
        <button
          v-if="agent.is_placeholder"
          class="btn-disabled"
          @click="handleUse(agent)"
        >敬请期待 →</button>
        <button
          v-else
          class="btn-use"
          @click="handleUse(agent)"
        >立即使用 <span class="arrow">→</span></button>
      </div>
    </section>

    <!-- Footer -->
    <footer class="footer">© 大熊AI智能体 · 数字员工中心</footer>
  </div>
</template>

<script lang="ts">
const ICON_SVG: Record<string, string> = {
  doc: `<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/>`,
  testcase: `<path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>`,
  ui: `<rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/>`,
  'api-doc': `<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/><polyline points="8 7 12 11 16 7"/>`,
  'api-case': `<polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/>`,
  'api-auto': `<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>`,
  data: `<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>`,
  perf: `<line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/>`,
  more: `<circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/><circle cx="5" cy="12" r="1"/>`,
}
</script>

<style lang="scss" scoped>
/* ── Page shell ── */
.agent-hub {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif;
  overflow-y: auto;
  overflow-x: hidden;
}

/* ── Header ── */
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1280px;
  width: 100%;
  margin: 0 auto;
  padding: 20px 24px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 22px;
  font-weight: 700;
  color: #1E88E5;
}

.logo-icon {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #1E88E5, #1565C0);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 16px;
  font-weight: 800;
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.admin {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #5f6c80;
}

.dropdown-arrow {
  color: #9ca3af;
  transition: transform 0.2s;
}

:deep(.el-dropdown) {
  cursor: pointer;
}

.avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #1E88E5, #7c3aed);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 14px;
  font-weight: 600;
}

.exit-btn {
  padding: 6px 16px;
  border: 1px solid #d0d5dd;
  border-radius: 8px;
  background: #fff;
  color: #5f6c80;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    border-color: #1E88E5;
    color: #1E88E5;
  }
}

/* ── Hero ── */
.hero {
  text-align: center;
  padding: 32px 24px 40px;
  max-width: 800px;
  margin: 0 auto;

  h1 {
    font-size: 32px;
    font-weight: 800;
    line-height: 1.4;
    color: #1f2a3e;
  }

  .hl { color: #1E88E5; }

  p {
    margin-top: 16px;
    font-size: 16px;
    color: #5f6c80;
    line-height: 1.7;
  }
}

/* ── Loading ── */
.loading-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  gap: 10px;
  color: #5f6c80;
  font-size: 14px;
  padding: 60px 0;
}

.spinner {
  width: 28px;
  height: 28px;
  border: 3px solid #e5e7eb;
  border-top-color: #1E88E5;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

/* ── Grid ── */
.grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  row-gap: 24px;
  column-gap: 24px;
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 24px 48px;
}

/* ── Card ── */
.card {
  background: #fff;
  border-radius: 24px;
  padding: 24px 20px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  transition: transform 0.2s, box-shadow 0.2s;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 28px rgba(0, 0, 0, 0.10);
  }
}

.card-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  margin-bottom: 16px;
}

.card-title {
  font-size: 20px;
  font-weight: 700;
  color: #1f2a3e;
  margin-bottom: 10px;
}

.card-desc {
  font-size: 14px;
  color: #5f6c80;
  line-height: 1.7;
}

.card-body {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.tags {
  margin-top: auto;
  padding-top: 16px;
  display: flex;
  flex-wrap: wrap;
  gap: 0;
}

.tag {
  display: inline-block;
  background: #f0f2f5;
  color: #1f2a3e;
  border-radius: 20px;
  padding: 4px 12px;
  font-size: 12px;
  margin: 4px 4px 0 0;
}

/* ── Buttons ── */
.btn-use {
  margin-top: 16px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: linear-gradient(135deg, #1E88E5, #1565C0);
  color: #fff;
  border: none;
  border-radius: 40px;
  padding: 8px 20px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  align-self: flex-start;

  &:hover {
    background: linear-gradient(135deg, #1565C0, #0d47a1);
  }

  &:hover .arrow { transform: translateX(2px); }

  .arrow { display: inline-block; transition: transform 0.2s; }
}

.btn-disabled {
  margin-top: 16px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: #e0e0e0;
  color: #9e9e9e;
  border: none;
  border-radius: 40px;
  padding: 8px 20px;
  font-size: 14px;
  cursor: default;
  align-self: flex-start;
}

/* ── Footer ── */
.footer {
  text-align: center;
  padding: 16px 24px 32px;
  font-size: 12px;
  color: #9e9e9e;
}

/* ── Responsive ── */
@media (max-width: 960px) {
  .grid { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 600px) {
  .grid { grid-template-columns: 1fr; }
  .hero h1 { font-size: 24px; }
  .topbar { padding: 16px; }
}
</style>
