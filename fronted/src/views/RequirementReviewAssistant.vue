<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  createDocument,
  deleteDocument,
  getDocuments,
  reviewRequirement,
  updateDocument,
  type RequirementDocument,
  type RequirementFinding,
} from '@/api/document'

defineOptions({ name: 'RequirementReviewAssistant' })

const router = useRouter()
const projectId = 1
const documents = ref<RequirementDocument[]>([])
const selectedId = ref<number | null>(null)
const editorContent = ref('')
const reviewVisible = ref(false)
const reviewing = ref(false)
const extraPrompt = ref('')
const findings = ref<RequirementFinding[]>([])
const expandedFinding = ref<string | null>(null)

const selectedDocument = computed(() => documents.value.find((item) => item.id === selectedId.value) || null)
const roots = computed(() => documents.value.filter((item) => !item.parent_id))

function childrenOf(parentId: number) {
  return documents.value.filter((item) => item.parent_id === parentId)
}

function pathText(document: RequirementDocument | null) {
  if (!document) return '当前查看：未选择文档'
  const parent = document.parent_id ? documents.value.find((item) => item.id === document.parent_id) : null
  return `当前查看：${parent ? `${parent.name} - ` : ''}${document.name}`
}

async function loadDocuments() {
  documents.value = await getDocuments(projectId)
  if (!selectedId.value && documents.value.length) {
    selectDocument(documents.value.find((item) => !item.is_directory) || documents.value[0])
  }
}

function selectDocument(document: RequirementDocument) {
  selectedId.value = document.id
  editorContent.value = document.content || ''
  findings.value = document.ai_suggest || []
}

async function addRoot() {
  const { value } = await ElMessageBox.prompt('请输入名称', '添加根目录', {
    confirmButtonText: '确认',
    cancelButtonText: '取消',
    inputPattern: /\S+/,
    inputErrorMessage: '名称必填',
  })
  const created = await createDocument({
    project_id: projectId,
    name: value,
    title: value,
    is_directory: true,
  })
  documents.value.push(created)
  selectDocument(created)
}

async function addChild(parent: RequirementDocument) {
  const name = `${parent.name}子项`
  const created = await createDocument({
    project_id: projectId,
    parent_id: parent.id,
    name,
    title: name,
    content: '# 功能性需求\n\n请在此处编辑详细说明。',
    is_directory: false,
  })
  documents.value.push(created)
  selectDocument(created)
}

async function importDocument() {
  const content = `# 功能性需求

## 系统登录功能

### 功能概述
- 功能描述：出租屋管理系统登录功能，提供用户身份验证入口，确保系统访问安全。用户需输入正确账号密码才能进入系统。
- 功能入口：系统首页或直接访问登录URL时展示的登录表单。

### 界面原型
账号输入框
密码输入框
登录按钮
`
  const existing = documents.value.find((item) => item.name === '系统登录功能')
  if (existing) {
    const updated = await updateDocument(existing.id, { content, title: '系统登录功能' })
    documents.value = documents.value.map((item) => (item.id === updated.id ? updated : item))
    selectDocument(updated)
  } else {
    const parent = roots.value.find((item) => item.is_directory) || await createDocument({
      project_id: projectId,
      name: '功能性需求',
      title: '功能性需求',
      is_directory: true,
    })
    if (!documents.value.some((item) => item.id === parent.id)) documents.value.push(parent)
    const created = await createDocument({
      project_id: projectId,
      parent_id: parent.id,
      name: '系统登录功能',
      title: '系统登录功能',
      content,
      is_directory: false,
    })
    documents.value.push(created)
    selectDocument(created)
  }
  ElMessage.success('文档已导入')
}

async function saveCurrent() {
  if (!selectedDocument.value) {
    ElMessage.warning('请先选择文档')
    return
  }
  const updated = await updateDocument(selectedDocument.value.id, {
    content: editorContent.value,
    ai_suggest: findings.value,
  })
  documents.value = documents.value.map((item) => (item.id === updated.id ? updated : item))
  ElMessage.success('需求已保存')
}

async function removeDocument(document: RequirementDocument) {
  await deleteDocument(document.id)
  documents.value = documents.value.filter((item) => item.id !== document.id && item.parent_id !== document.id)
  if (selectedId.value === document.id) {
    selectedId.value = null
    editorContent.value = ''
  }
  ElMessage.success('已删除')
}

async function runReview() {
  if (!selectedDocument.value || !editorContent.value.trim()) {
    ElMessage.warning('请先选择并填写需求内容')
    return
  }
  reviewVisible.value = true
  reviewing.value = true
  try {
    const response = await reviewRequirement({
      document_id: selectedDocument.value.id,
      title: selectedDocument.value.title,
      content: editorContent.value,
      extra_prompt: extraPrompt.value,
    })
    findings.value = response.findings
    expandedFinding.value = findings.value[1]?.id || findings.value[0]?.id || null
  } finally {
    reviewing.value = false
  }
}

async function adoptSelected() {
  if (!selectedDocument.value) return
  const adopted = findings.value.filter((item) => item.adopted)
  const updated = await updateDocument(selectedDocument.value.id, { ai_suggest: adopted })
  documents.value = documents.value.map((item) => (item.id === updated.id ? updated : item))
  findings.value = updated.ai_suggest
  ElMessage.success('已采纳选中建议')
}

onMounted(async () => {
  await loadDocuments()
})
</script>

<template>
  <div class="review-page">
    <header class="topbar">
      <div class="brand" @click="router.push('/agent-hub')">
        <div class="logo-mark" />
        <span>华测 AI+需求助手</span>
      </div>
      <div class="top-links">
        <span>{{ selectedDocument?.title || '华测教育001接口--干寻' }}</span>
        <button @click="router.push('/projects')">退出项目</button>
      </div>
    </header>

    <main class="layout">
      <aside class="sidebar">
        <div class="side-actions">
          <button class="blue-btn" @click="addRoot">添加根目录</button>
          <button class="blue-btn" @click="importDocument">导入文档</button>
        </div>

        <div class="tree">
          <div v-for="root in roots" :key="root.id" class="tree-group">
            <div class="tree-row" :class="{ active: root.id === selectedId }" @click="selectDocument(root)">
              <span class="caret">⌄</span>
              <input type="checkbox" />
              <span class="node-name">{{ root.name }}</span>
              <button @click.stop="addChild(root)">添加</button>
              <button @click.stop="selectDocument(root)">编辑</button>
              <button class="danger" @click.stop="removeDocument(root)">删除</button>
            </div>
            <div
              v-for="child in childrenOf(root.id)"
              :key="child.id"
              class="tree-row child"
              :class="{ active: child.id === selectedId }"
              @click="selectDocument(child)"
            >
              <input type="checkbox" />
              <span class="node-name">{{ child.name }}</span>
              <button @click.stop="addChild(child)">添加</button>
              <button @click.stop="selectDocument(child)">编辑</button>
              <button class="danger" @click.stop="removeDocument(child)">删除</button>
            </div>
          </div>
        </div>
      </aside>

      <section class="workspace">
        <div class="workspace-head">
          <span>{{ pathText(selectedDocument) }}</span>
          <div>
            <button class="green-btn" @click="runReview">AI需求评审</button>
            <button class="blue-btn" @click="saveCurrent">保存需求</button>
          </div>
        </div>

        <div class="editor-shell">
          <div class="toolbar">
            <span>☺</span><span>H</span><span>B</span><span>I</span><span>S</span><span>🔗</span>
            <span>☷</span><span>☑</span><span>▷</span><span>—</span><span>&lt;/&gt;</span><span>↕</span>
            <span>↧</span><span>☁</span><span>▦</span><span>↗</span><span>✎</span><span>…</span>
          </div>
          <textarea
            v-model="editorContent"
            class="editor"
            placeholder="请选择或导入需求文档，在此编辑详细说明。"
          />
        </div>
      </section>
    </main>

    <footer>© 2025 华测教育 - AI智能测试研究院.版权所有</footer>

    <el-dialog v-model="reviewVisible" :title="`AI 评审 - ${selectedDocument?.name || '需求'}`" width="760px">
      <div class="tabs">
        <span class="tab active">需求评审</span>
        <span class="tab">采纳记录</span>
      </div>

      <div v-if="reviewing" class="review-loading">AI正在处理...</div>
      <template v-else>
        <div v-if="!findings.length" class="empty-review">暂无评审结果，请点击立即开始</div>
        <div v-for="(finding, index) in findings" :key="finding.id" class="finding">
          <div class="finding-title" @click="expandedFinding = expandedFinding === finding.id ? null : finding.id">
            <el-checkbox v-model="finding.adopted" />
            <span>{{ index + 1 }}. {{ finding.title }}</span>
            <b>{{ expandedFinding === finding.id ? '⌄' : '›' }}</b>
          </div>
          <p v-if="expandedFinding === finding.id">{{ finding.description }}</p>
        </div>
      </template>

      <el-input
        v-model="extraPrompt"
        type="textarea"
        :rows="3"
        placeholder="如果你对需求评审有特殊要求，请补充。"
      />

      <template #footer>
        <button class="blue-btn wide" :disabled="reviewing" @click="runReview">立即开始 AI 需求评审</button>
        <button class="green-btn" @click="adoptSelected">采纳</button>
        <button class="plain-btn" @click="saveCurrent">保存</button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped lang="scss">
.review-page {
  min-height: 100vh;
  background: #f2f4f7;
  color: #17212b;
}

.topbar {
  height: 80px;
  padding: 0 100px;
  background: #1d2328;
  color: #fff;
  @include flex-between;
}

.brand,
.top-links,
.side-actions,
.workspace-head,
.toolbar,
.finding-title {
  display: flex;
  align-items: center;
}

.brand {
  gap: 14px;
  font-size: 26px;
  font-weight: 800;
  cursor: pointer;
}

.logo-mark {
  width: 38px;
  height: 38px;
  border: 4px solid #0ea5e9;
  border-bottom-color: #f59e0b;
  border-radius: 50%;
}

.top-links {
  gap: 72px;
  font-size: 16px;

  button {
    border: 0;
    background: transparent;
    color: #fff;
    cursor: pointer;
    font-size: 16px;
  }
}

.layout {
  display: grid;
  grid-template-columns: 325px 1fr;
  gap: 20px;
  max-width: 1720px;
  margin: 20px auto 0;
  padding: 0 20px;
}

.sidebar,
.workspace {
  background: #fff;
  border: 1px solid #dce3eb;
  border-radius: 6px;
  box-shadow: $shadow-sm;
}

.sidebar {
  min-height: 770px;
}

.side-actions {
  gap: 12px;
  padding: 22px 16px 28px;
  border-bottom: 1px solid #e8edf3;
}

button {
  font-family: inherit;
}

.blue-btn,
.green-btn,
.plain-btn {
  height: 34px;
  padding: 0 16px;
  border: 0;
  border-radius: 4px;
  color: #fff;
  cursor: pointer;
  font-weight: 600;
}

.blue-btn {
  background: #2f91f4;
}

.green-btn {
  background: linear-gradient(135deg, #2f91f4, #62bb35);
}

.plain-btn {
  color: #4b5563;
  background: #fff;
  border: 1px solid #d8dee6;
}

.wide {
  min-width: 190px;
}

.tree {
  padding: 16px;
}

.tree-row {
  display: grid;
  grid-template-columns: 18px 18px 1fr 34px 34px 34px;
  align-items: center;
  gap: 6px;
  min-height: 26px;
  padding: 2px 8px;
  font-size: 14px;
  cursor: pointer;

  &.child {
    padding-left: 34px;
    grid-template-columns: 18px 1fr 34px 34px 34px;
  }

  &.active {
    background: #e8f2ff;
  }

  button {
    border: 0;
    background: transparent;
    color: #2f91f4;
    cursor: pointer;
    font-size: 12px;
  }

  .danger {
    color: #ef4444;
  }
}

.node-name {
  @include ellipsis;
}

.workspace {
  min-height: 770px;
  padding: 18px 20px;
}

.workspace-head {
  justify-content: space-between;
  height: 62px;
  padding: 0 20px;
  background: #eaf4ff;
  color: #1683ff;
  font-weight: 700;

  div {
    display: flex;
    gap: 12px;
  }
}

.editor-shell {
  margin-top: 20px;
  border: 1px solid #cfd8e3;
}

.toolbar {
  gap: 12px;
  height: 34px;
  padding: 0 310px;
  background: #f4f7fa;
  border-bottom: 1px solid #cfd8e3;
  color: #5f6b78;
}

.editor {
  width: 100%;
  min-height: 520px;
  padding: 34px 16%;
  border: 0;
  resize: vertical;
  outline: none;
  color: #111827;
  font-size: 16px;
  line-height: 1.9;
  white-space: pre-wrap;
}

footer {
  padding: 24px;
  text-align: center;
  color: #4b5563;
}

.tabs {
  display: flex;
  gap: 36px;
  border-bottom: 1px solid #dbe2ea;
}

.tab {
  padding: 12px 0;
  color: #333;

  &.active {
    color: #1683ff;
    border-bottom: 2px solid #1683ff;
  }
}

.review-loading,
.empty-review {
  height: 260px;
  @include flex-center;
  color: #8b96a5;
}

.finding {
  border-bottom: 1px solid #e5ebf2;
  padding: 14px 0;

  p {
    margin: 14px 0 4px;
    color: #303946;
    line-height: 1.8;
  }
}

.finding-title {
  gap: 8px;
  cursor: pointer;

  span {
    flex: 1;
  }
}

@media (max-width: 980px) {
  .topbar {
    padding: 0 18px;
  }

  .layout {
    grid-template-columns: 1fr;
  }

  .toolbar {
    padding: 0 12px;
    overflow-x: auto;
  }

  .editor {
    padding: 24px;
  }
}
</style>
