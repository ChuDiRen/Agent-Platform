<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/store/store'
import { getProjects, createProject, updateProject, deleteProject, getProject, type ProjectInfo, type ProjectCreate } from '@/api/project'

defineOptions({ name: 'Project' })

const router = useRouter()
const userStore = useUserStore()
const projects = ref<ProjectInfo[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref<number | null>(null)

const passwordDialogVisible = ref(false)
const passwordInput = ref('')
const passwordError = ref('')
const pendingProject = ref<ProjectInfo | null>(null)

const defaultForm: ProjectCreate = {
  name: '', description: '', password: '',
  llm_url: 'https://token-plan-sgp.xiaomimimo.com/v1', llm_key: '', llm_model: 'mimo-v2.5-pro',
  lvm_url: 'https://token-plan-sgp.xiaomimimo.com/v1', lvm_key: '', lvm_model: 'mimo-v2.5',
}
const form = ref<ProjectCreate>({ ...defaultForm })
const dialogTitle = computed(() => (isEdit.value ? '编辑项目' : '新建项目'))

async function loadProjects() {
  loading.value = true
  try { projects.value = await getProjects() }
  catch { ElMessage.error('加载项目列表失败') }
  finally { loading.value = false }
}

function openCreateDialog() {
  isEdit.value = false; editId.value = null
  form.value = { ...defaultForm }; dialogVisible.value = true
}

function openEditDialog(proj: ProjectInfo) {
  isEdit.value = true; editId.value = proj.id
  form.value = {
    name: proj.name, description: proj.description ?? '', password: proj.password ?? '',
    llm_url: proj.llm_url ?? '', llm_key: proj.llm_key ?? '', llm_model: proj.llm_model ?? '',
    lvm_url: proj.lvm_url ?? '', lvm_key: proj.lvm_key ?? '', lvm_model: proj.lvm_model ?? '',
  }
  dialogVisible.value = true
}

async function handleSubmit() {
  if (!form.value.name.trim()) { ElMessage.warning('请输入项目名称'); return }
  try {
    if (isEdit.value && editId.value !== null) {
      await updateProject(editId.value, form.value); ElMessage.success('项目已更新')
    } else {
      await createProject(form.value); ElMessage.success('项目已创建')
    }
    dialogVisible.value = false; await loadProjects()
  } catch { ElMessage.error(isEdit.value ? '更新失败' : '创建失败') }
}

async function handleDelete(proj: ProjectInfo) {
  try {
    await ElMessageBox.confirm(`确定删除项目「${proj.name}」？`, '确认删除', { confirmButtonText: '删除', cancelButtonText: '取消', type: 'warning' })
    await deleteProject(proj.id); ElMessage.success('已删除'); await loadProjects()
  } catch {}
}

function enterProject() { router.push('/agent-hub') }

function handleEnterProject(proj: ProjectInfo) {
  if (proj.password) {
    pendingProject.value = proj; passwordInput.value = ''; passwordError.value = ''
    passwordDialogVisible.value = true
  } else { enterProject() }
}

async function verifyPassword() {
  if (!pendingProject.value) return
  if (!passwordInput.value) { passwordError.value = '请输入项目密码'; return }
  try {
    const fresh = await getProject(pendingProject.value.id)
    if (fresh.password && fresh.password !== passwordInput.value) { passwordError.value = '密码错误，请重试'; return }
    passwordDialogVisible.value = false; enterProject()
  } catch { ElMessage.error('验证失败，请重试') }
}

function formatDate(dateStr?: string) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' })
}

function truncate(text: string, max: number) {
  return text.length > max ? text.slice(0, max) + '...' : text
}

function handleCommand(cmd: string) {
  if (cmd === 'logout') { userStore.logout(); router.push('/login') }
}

onMounted(loadProjects)
</script>

<template>
  <div class="project-page">
    <header class="topbar">
      <div class="topbar-left">
        <button class="back-btn" @click="router.push('/projects')">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6" /></svg>
        </button>
        <div class="logo">
          <div class="logo-icon">项</div>
          <span>项目管理</span>
        </div>
      </div>
      <div class="topbar-right">
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
        <button class="create-btn" @click="openCreateDialog">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19" /><line x1="5" y1="12" x2="19" y2="12" /></svg>
          <span>新建项目</span>
        </button>
      </div>
    </header>

    <main class="main-content">
      <div v-if="loading" class="loading-box">
        <div class="spinner" /><span>加载中…</span>
      </div>

      <div v-else-if="projects.length === 0" class="empty-state">
        <div class="empty-icon">📂</div>
        <h3>还没有项目</h3>
        <p>创建你的第一个项目，开始使用智能数字员工</p>
        <button class="create-btn" @click="openCreateDialog">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19" /><line x1="5" y1="12" x2="19" y2="12" /></svg>
          <span>新建项目</span>
        </button>
      </div>

      <div v-else class="project-grid">
        <div
          v-for="proj in projects" :key="proj.id"
          class="project-card"
          @click="handleEnterProject(proj)"
        >
          <div class="card-header">
            <div class="card-icon">📁</div>
            <div class="card-tags">
              <span v-if="proj.llm_model" class="tag tag-llm">LLM: {{ proj.llm_model }}</span>
              <span v-if="proj.lvm_model" class="tag tag-lvm">LVM: {{ proj.lvm_model }}</span>
              <span v-if="proj.password" class="tag tag-lock">🔒 需密码</span>
            </div>
          </div>

          <h3 class="card-title">{{ proj.name }}</h3>
          <p class="card-desc">{{ proj.description ? truncate(proj.description, 80) : '暂无描述' }}</p>

          <div class="card-footer">
            <span class="card-date">{{ formatDate(proj.created_at) }}</span>
            <div class="card-actions">
              <button class="action-btn" @click.stop="openEditDialog(proj)">编辑</button>
              <button class="action-btn action-enter" @click.stop="handleEnterProject(proj)">进入</button>
              <button class="action-btn action-danger" @click.stop="handleDelete(proj)">删除</button>
            </div>
          </div>
        </div>
      </div>
    </main>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px" :close-on-click-modal="false" class="project-dialog">
      <el-form :model="form" label-position="top" class="project-form">
        <el-form-item label="项目名称" required>
          <el-input v-model="form.name" placeholder="请输入项目名称" maxlength="255" />
        </el-form-item>
        <el-form-item label="项目描述">
          <el-input v-model="form.description" type="textarea" :rows="2" placeholder="简要描述项目用途" />
        </el-form-item>
        <el-form-item label="项目密码">
          <el-input v-model="form.password" placeholder="留空则无需密码" show-password />
        </el-form-item>

        <div class="form-divider"><span>大语言模型 (LLM)</span></div>
        <div class="form-row">
          <div class="form-col">
            <el-form-item label="API 地址">
              <el-input v-model="form.llm_url" placeholder="https://token-plan-sgp.xiaomimimo.com/v1" />
            </el-form-item>
          </div>
          <div class="form-col">
            <el-form-item label="模型名称">
              <el-input v-model="form.llm_model" placeholder="mimo-v2.5-pro" />
            </el-form-item>
          </div>
        </div>
        <el-form-item label="API Key">
          <el-input v-model="form.llm_key" placeholder="sk-..." show-password />
        </el-form-item>

        <div class="form-divider"><span>视觉模型 (LVM)</span></div>
        <div class="form-row">
          <div class="form-col">
            <el-form-item label="API 地址">
              <el-input v-model="form.lvm_url" placeholder="https://token-plan-sgp.xiaomimimo.com/v1" />
            </el-form-item>
          </div>
          <div class="form-col">
            <el-form-item label="模型名称">
              <el-input v-model="form.lvm_model" placeholder="mimo-v2.5" />
            </el-form-item>
          </div>
        </div>
        <el-form-item label="API Key">
          <el-input v-model="form.lvm_key" placeholder="sk-..." show-password />
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <button class="btn-cancel" @click="dialogVisible = false">取消</button>
          <button class="btn-submit" @click="handleSubmit">{{ isEdit ? '保存修改' : '创建项目' }}</button>
        </div>
      </template>
    </el-dialog>

    <el-dialog v-model="passwordDialogVisible" title="项目验证" width="400px" :close-on-click-modal="false" class="project-dialog">
      <div class="password-verify">
        <div class="password-icon">🔐</div>
        <p class="password-hint">该项目需要密码才能进入</p>
        <el-input v-model="passwordInput" placeholder="请输入项目密码" show-password style="max-width: 280px" @keyup.enter="verifyPassword" />
        <p v-if="passwordError" class="password-error">{{ passwordError }}</p>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <button class="btn-cancel" @click="passwordDialogVisible = false">取消</button>
          <button class="btn-submit" @click="verifyPassword">确认进入</button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<style lang="scss" scoped>
.project-page {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif;
  overflow-y: auto;
  overflow-x: hidden;
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1280px;
  width: 100%;
  margin: 0 auto;
  padding: 20px 24px;
  flex-shrink: 0;
}

.topbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.back-btn {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  border: 1px solid #e5e7eb;
  background: #fff;
  color: #5f6c80;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  &:hover { border-color: #1E88E5; color: #1E88E5; }
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 20px;
  font-weight: 700;
  color: #1f2a3e;
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
  font-size: 14px;
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

.create-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 20px;
  border-radius: 40px;
  background: linear-gradient(135deg, #1E88E5, #1565C0);
  border: none;
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  &:hover {
    background: linear-gradient(135deg, #1565C0, #0d47a1);
    box-shadow: 0 4px 14px rgba(30, 136, 229, 0.3);
  }
}

.main-content {
  flex: 1;
  max-width: 1280px;
  width: 100%;
  margin: 0 auto;
  padding: 0 24px 48px;
}

.loading-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: #5f6c80;
  font-size: 14px;
  padding: 100px 0;
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

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 120px 0;
  .empty-icon { font-size: 56px; margin-bottom: 8px; }
  h3 { font-size: 20px; font-weight: 700; color: #1f2a3e; }
  p { font-size: 14px; color: #5f6c80; margin-bottom: 8px; }
}

.project-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 24px;
}

.project-card {
  display: flex;
  flex-direction: column;
  background: #fff;
  border-radius: 24px;
  padding: 24px 20px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.05);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 28px rgba(0, 0, 0, 0.10);
  }
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}

.card-icon {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  background: linear-gradient(135deg, #e3f2fd, #bbdefb);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.card-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.tag {
  display: inline-block;
  border-radius: 20px;
  padding: 3px 10px;
  font-size: 11px;
  font-weight: 500;
  white-space: nowrap;
}

.tag-llm { background: rgba(30, 136, 229, 0.08); color: #1E88E5; }
.tag-lvm { background: rgba(124, 58, 237, 0.08); color: #7c3aed; }
.tag-lock { background: rgba(245, 158, 11, 0.08); color: #d97706; }

.card-title {
  font-size: 18px;
  font-weight: 700;
  color: #1f2a3e;
  margin-bottom: 8px;
}

.card-desc {
  font-size: 14px;
  color: #5f6c80;
  line-height: 1.65;
  margin-bottom: 16px;
  flex: 1;
  min-height: 46px;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 14px;
  border-top: 1px solid #f0f2f5;
}

.card-date { font-size: 12px; color: #9ca3af; }
.card-actions { display: flex; gap: 8px; }

.action-btn {
  padding: 5px 14px;
  border-radius: 8px;
  background: #fff;
  border: 1px solid #e5e7eb;
  color: #5f6c80;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  &:hover { border-color: #1E88E5; color: #1E88E5; background: rgba(30, 136, 229, 0.04); }
}

.action-enter {
  background: rgba(30, 136, 229, 0.06);
  border-color: rgba(30, 136, 229, 0.2);
  color: #1E88E5;
  &:hover { background: rgba(30, 136, 229, 0.12); }
}

.action-danger {
  &:hover { border-color: #ef4444; color: #ef4444; background: rgba(239, 68, 68, 0.04); }
}

.project-dialog {
  :deep(.el-dialog) { border-radius: 20px; }
  :deep(.el-dialog__header) { padding: 24px 24px 0; font-weight: 700; }
  :deep(.el-dialog__body) { padding: 20px 24px; }
  :deep(.el-dialog__footer) { padding: 0 24px 24px; }
}

.project-form {
  :deep(.el-form-item__label) { font-weight: 600; color: #1f2a3e; font-size: 13px; }
  :deep(.el-input__wrapper), :deep(.el-textarea__inner) { border-radius: 10px; }
}

.form-divider {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 8px 0 16px;
  &::before, &::after { content: ''; flex: 1; height: 1px; background: #e5e7eb; }
  span { font-size: 12px; color: #5f6c80; font-weight: 600; letter-spacing: 0.05em; white-space: nowrap; }
}

.form-row {
  display: flex;
  gap: 16px;
  .form-col { flex: 1; }
}

.dialog-footer { display: flex; justify-content: flex-end; gap: 10px; }

.btn-cancel {
  padding: 8px 20px;
  border-radius: 10px;
  background: #fff;
  border: 1px solid #e5e7eb;
  color: #5f6c80;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  &:hover { background: #f5f6f8; }
}

.btn-submit {
  padding: 8px 24px;
  border-radius: 10px;
  background: linear-gradient(135deg, #1E88E5, #1565C0);
  border: none;
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  &:hover {
    background: linear-gradient(135deg, #1565C0, #0d47a1);
    box-shadow: 0 4px 14px rgba(30, 136, 229, 0.3);
  }
}

.password-verify {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 8px 0;
}

.password-icon { font-size: 48px; }
.password-hint { font-size: 14px; color: #5f6c80; text-align: center; }
.password-error { font-size: 12px; color: #ef4444; margin: -8px 0 0; }

@media (max-width: 768px) {
  .topbar { padding: 16px; }
  .main-content { padding: 0 16px 32px; }
  .project-grid { grid-template-columns: 1fr; }
  .form-row { flex-direction: column; gap: 0; }
  .card-actions { gap: 4px; }
  .action-btn { padding: 4px 10px; font-size: 11px; }
}
</style>
