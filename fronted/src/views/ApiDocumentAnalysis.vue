<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, type UploadFile } from 'element-plus'
import {
  analyzeApiDocument,
  createApiDocument,
  deleteApiDocument,
  getApiDocuments,
  updateApiDocument,
  type ApiDocument,
  type ApiDocumentFinding,
} from '@/api/apiDocument'

defineOptions({ name: 'ApiDocumentAnalysis' })

const router = useRouter()
const projectId = 1
const documents = ref<ApiDocument[]>([])
const selectedId = ref<number | null>(null)
const editorContent = ref('')
const addDialogVisible = ref(false)
const importDialogVisible = ref(false)
const analysisVisible = ref(false)
const processingVisible = ref(false)
const newDirectoryName = ref('')
const replaceExisting = ref(false)
const titleLevel = ref('一级标题')
const extraPrompt = ref('')
const findings = ref<ApiDocumentFinding[]>([])
const activeTab = ref<'analysis' | 'history'>('analysis')
const expandedFinding = ref<string | null>(null)
const importedFileName = ref('')
const importedContent = ref('')

const selectedDocument = computed(() => documents.value.find((item) => item.id === selectedId.value) || null)
const rootDocuments = computed(() => documents.value.filter((item) => !item.parent_id))

function childrenOf(parentId: number) {
  return documents.value.filter((item) => item.parent_id === parentId)
}

function currentPath(document: ApiDocument | null) {
  if (!document) return '当前查看：未选择接口文档'
  const parent = document.parent_id ? documents.value.find((item) => item.id === document.parent_id) : null
  return `当前查看 - ${parent ? `${parent.name}` : '接口文档'}${document.is_directory ? '' : `\\${document.name}`}`
}

function seedContent() {
  return `# 一、接口信息

## 1. 简要描述
用于实现账号登录功能，验证用户提交的账号、密码等信息，完成身份校验并返回登录结果。

## 2. 请求 URL

\`\`\`
http://kaoshi.project.hctestedu.com/api/user/login
\`\`\`

## 3. 请求方式

\`\`\`
POST
\`\`\`

# 二、公共参数

# 三、请求参数

| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| username | string | 是 | 登录账号 |
| password | string | 是 | 登录密码 |

# 四、响应参数

`
}

async function loadDocuments() {
  documents.value = await getApiDocuments(projectId)
  if (!documents.value.length) {
    const parent = await createApiDocument({
      project_id: projectId,
      name: '学生端登录接口文档',
      title: '学生端登录接口文档',
      is_directory: true,
    })
    const child = await createApiDocument({
      project_id: projectId,
      parent_id: parent.id,
      name: '学生端登录接口文档20050830',
      title: '学生端登录接口文档20050830',
      content: seedContent(),
      is_directory: false,
    })
    documents.value = [parent, child]
  }
  if (!selectedId.value) {
    selectDocument(documents.value.find((item) => !item.is_directory) || documents.value[0])
  }
}

function selectDocument(document: ApiDocument) {
  selectedId.value = document.id
  editorContent.value = document.content || ''
  findings.value = document.ai_suggest || []
}

async function confirmAddDirectory() {
  const name = newDirectoryName.value.trim()
  if (!name) {
    ElMessage.warning('请输入目录名称')
    return
  }
  const created = await createApiDocument({
    project_id: projectId,
    name,
    title: name,
    is_directory: true,
  })
  documents.value.push(created)
  selectDocument(created)
  newDirectoryName.value = ''
  addDialogVisible.value = false
  ElMessage.success('目录已添加')
}

async function addChild(parent: ApiDocument) {
  const baseName = parent.is_directory ? parent.name : selectedDocument.value?.name || '接口文档'
  const created = await createApiDocument({
    project_id: projectId,
    parent_id: parent.is_directory ? parent.id : parent.parent_id,
    name: `${baseName}${new Date().getMonth() + 1}${new Date().getDate()}`,
    title: `${baseName}接口详情`,
    content: seedContent(),
    is_directory: false,
  })
  documents.value.push(created)
  selectDocument(created)
}

async function removeDocument(document: ApiDocument) {
  await ElMessageBox.confirm(`确认删除「${document.name}」？`, '删除确认', {
    confirmButtonText: '删除',
    cancelButtonText: '取消',
    type: 'warning',
  })
  const removedIds = [document.id, ...childrenOf(document.id).map((item) => item.id)]
  await deleteApiDocument(document.id)
  documents.value = documents.value.filter((item) => !removedIds.includes(item.id))
  if (selectedId.value && removedIds.includes(selectedId.value)) {
    selectedId.value = null
    editorContent.value = ''
    if (documents.value.length) selectDocument(documents.value.find((item) => !item.is_directory) || documents.value[0])
  }
  ElMessage.success('已删除')
}

async function saveCurrent() {
  if (!selectedDocument.value) {
    ElMessage.warning('请先选择接口文档')
    return
  }
  const updated = await updateApiDocument(selectedDocument.value.id, {
    content: editorContent.value,
    ai_suggest: findings.value,
  })
  documents.value = documents.value.map((item) => (item.id === updated.id ? updated : item))
  ElMessage.success('保存成功')
}

function beforeUpload(file: UploadFile) {
  importedFileName.value = file.name
  const raw = file.raw
  if (!raw) return false
  const reader = new FileReader()
  reader.onload = () => {
    importedContent.value = String(reader.result || '')
  }
  reader.readAsText(raw)
  return false
}

async function confirmImport() {
  const name = importedFileName.value.replace(/\.(md|docx?)$/i, '') || `接口文档${Date.now()}`
  const content = importedContent.value || seedContent()
  const target = selectedDocument.value && !selectedDocument.value.is_directory ? selectedDocument.value : null

  if (replaceExisting.value && target) {
    const updated = await updateApiDocument(target.id, {
      name,
      title: name,
      content,
      ai_suggest: [],
    })
    documents.value = documents.value.map((item) => (item.id === updated.id ? updated : item))
    selectDocument(updated)
  } else {
    const parent = rootDocuments.value.find((item) => item.is_directory) || await createApiDocument({
      project_id: projectId,
      name: '接口文档',
      title: '接口文档',
      is_directory: true,
    })
    if (!documents.value.some((item) => item.id === parent.id)) documents.value.push(parent)
    const created = await createApiDocument({
      project_id: projectId,
      parent_id: parent.id,
      name,
      title: name,
      content,
      is_directory: false,
    })
    documents.value.push(created)
    selectDocument(created)
  }

  importDialogVisible.value = false
  importedFileName.value = ''
  importedContent.value = ''
  ElMessage.success(`已按${titleLevel.value}导入`)
}

async function runAnalysis() {
  if (!selectedDocument.value || selectedDocument.value.is_directory || !editorContent.value.trim()) {
    ElMessage.warning('请先选择并填写接口文档')
    return
  }
  analysisVisible.value = false
  processingVisible.value = true
  try {
    const response = await analyzeApiDocument({
      document_id: selectedDocument.value.id,
      title: selectedDocument.value.title,
      content: editorContent.value,
      extra_prompt: extraPrompt.value,
    })
    findings.value = response.findings
    expandedFinding.value = findings.value[0]?.id || null
    const updated = await updateApiDocument(selectedDocument.value.id, {
      content: editorContent.value,
      ai_suggest: findings.value,
    })
    documents.value = documents.value.map((item) => (item.id === updated.id ? updated : item))
    processingVisible.value = false
    analysisVisible.value = true
  } catch {
    processingVisible.value = false
  }
}

async function applyFindings() {
  if (!selectedDocument.value) return
  const adopted = findings.value.map((item) => ({ ...item, adopted: item.adopted }))
  const updated = await updateApiDocument(selectedDocument.value.id, { ai_suggest: adopted })
  documents.value = documents.value.map((item) => (item.id === updated.id ? updated : item))
  ElMessage.success('评审结果已应用')
}

onMounted(loadDocuments)
</script>

<template>
  <div class="api-page">
    <header class="app-header">
      <div class="brand" @click="router.push('/agent-hub')">
        <span class="brand-mark" />
        <span>华测 AI+接口助手</span>
      </div>
      <div class="project-actions">
        <span>华测教育001接口--干寻</span>
        <button @click="router.push('/projects')">退出项目</button>
      </div>
    </header>

    <main class="api-layout">
      <aside class="sidebar">
        <div class="side-actions">
          <button class="primary-btn" @click="addDialogVisible = true">添加目录</button>
          <button class="primary-btn" @click="importDialogVisible = true">导入文档</button>
        </div>

        <div class="doc-list">
          <template v-for="root in rootDocuments" :key="root.id">
            <div class="doc-row" :class="{ active: root.id === selectedId }" @click="selectDocument(root)">
              <el-checkbox />
              <span class="doc-name">{{ root.name }}</span>
              <button @click.stop="selectDocument(root)">查看</button>
              <button @click.stop="addChild(root)">编辑</button>
              <button class="danger" @click.stop="removeDocument(root)">删除</button>
            </div>
            <div
              v-for="child in childrenOf(root.id)"
              :key="child.id"
              class="doc-row child"
              :class="{ active: child.id === selectedId }"
              @click="selectDocument(child)"
            >
              <el-checkbox />
              <span class="doc-name">{{ child.name }}</span>
              <button @click.stop="selectDocument(child)">查看</button>
              <button @click.stop="addChild(child)">编辑</button>
              <button class="danger" @click.stop="removeDocument(child)">删除</button>
            </div>
          </template>
        </div>
      </aside>

      <section class="workspace">
        <div class="workspace-head">
          <span>{{ currentPath(selectedDocument) }}</span>
          <div class="head-buttons">
            <button class="analysis-btn" @click="analysisVisible = true">AI 接口评审</button>
            <button class="primary-btn" @click="saveCurrent">保存修改</button>
          </div>
        </div>

        <div class="editor-panel">
          <div class="toolbar">
            <span>☺</span><span>H</span><span>B</span><span>I</span><span>S</span><span>↗</span>
            <span>☷</span><span>☑</span><span>▷</span><span>—</span><span>&lt;/&gt;</span><span>↕</span>
            <span>↧</span><span>☁</span><span>▦</span><span>○</span><span>✎</span><span>…</span>
          </div>
          <textarea
            v-model="editorContent"
            class="editor"
            placeholder="请选择或导入接口文档，在此编辑接口说明。"
          />
        </div>
      </section>
    </main>

    <el-dialog v-model="addDialogVisible" title="添加目录" width="448px">
      <el-form label-width="72px">
        <el-form-item label="名称" required>
          <el-input v-model="newDirectoryName" placeholder="请输入名称" />
        </el-form-item>
      </el-form>
      <template #footer>
        <button class="plain-btn" @click="addDialogVisible = false">取消</button>
        <button class="primary-btn" @click="confirmAddDirectory">确认</button>
      </template>
    </el-dialog>

    <el-dialog v-model="importDialogVisible" title="导入文档" width="430px">
      <div class="import-body">
        <div class="field-label">选择文档</div>
        <el-upload drag :auto-upload="false" :show-file-list="false" :on-change="beforeUpload">
          <div class="upload-icon">☁</div>
          <div class="upload-text">拖拽文件到此处或 <span>点击上传</span></div>
        </el-upload>
        <p class="hint">支持格式: WORD(docx)、Markdown(.md)</p>
        <p v-if="importedFileName" class="file-name">{{ importedFileName }}</p>

        <div class="field-label">导入选项</div>
        <el-checkbox v-model="replaceExisting">替换现有文档如果勾选，将删除当前项目的所有，并替换为文档内容</el-checkbox>

        <div class="field-label">标题层级</div>
        <el-select v-model="titleLevel" class="full">
          <el-option label="一级标题" value="一级标题" />
          <el-option label="二级标题" value="二级标题" />
        </el-select>
        <p class="hint">选中的层级将作为标题</p>
      </div>
      <template #footer>
        <button class="plain-btn" @click="importDialogVisible = false">取消</button>
        <button class="primary-btn" @click="confirmImport">导入</button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="analysisVisible"
      :title="`AI 评审 - ${selectedDocument?.name || '接口文档'}`"
      width="720px"
      class="analysis-dialog"
    >
      <div class="tabs">
        <button :class="{ active: activeTab === 'analysis' }" @click="activeTab = 'analysis'">文档评审</button>
        <button :class="{ active: activeTab === 'history' }" @click="activeTab = 'history'">历史记录</button>
      </div>

      <template v-if="activeTab === 'analysis'">
        <div v-if="!findings.length" class="empty">暂无评审结果</div>
        <div v-for="(finding, index) in findings" :key="finding.id" class="finding">
          <div class="finding-head" @click="expandedFinding = expandedFinding === finding.id ? null : finding.id">
            <el-checkbox v-model="finding.adopted" />
            <span>{{ index + 1 }}. {{ finding.title }}</span>
            <b>{{ expandedFinding === finding.id ? '⌄' : '›' }}</b>
          </div>
          <p v-if="expandedFinding === finding.id">{{ finding.description }}</p>
        </div>
      </template>
      <div v-else class="empty">历史记录将保存最近一次接口文档评审结果</div>

      <el-input
        v-model="extraPrompt"
        type="textarea"
        :rows="3"
        placeholder="如果你对文档评审有特殊要求，请补充。"
      />

      <template #footer>
        <button class="primary-btn wide" @click="runAnalysis">立即开始 AI 文档评审</button>
        <button class="apply-btn" @click="applyFindings">应用</button>
        <button class="plain-btn" @click="saveCurrent">保存</button>
      </template>
    </el-dialog>

    <el-dialog v-model="processingVisible" width="720px" :show-close="false" :close-on-click-modal="false">
      <div class="processing">
        <h3>华测教育 - AI智能体数字员工 - 工作中...</h3>
        <p class="spin">AI正在处理中...</p>
        <pre>开始生成内容...
```json
{{ findings.length ? JSON.stringify(findings[0], null, 2) : '{ "status": "analyzing" }' }}
```</pre>
        <el-progress :percentage="65" :show-text="false" />
      </div>
    </el-dialog>
  </div>
</template>

<style scoped lang="scss">
.api-page {
  min-height: 100vh;
  background: #eef1f5;
  color: #121821;
}

.app-header {
  height: 68px;
  padding: 0 34px;
  background: #1d2429;
  color: #fff;
  @include flex-between;
}

.brand,
.project-actions,
.side-actions,
.workspace-head,
.toolbar,
.finding-head {
  display: flex;
  align-items: center;
}

.brand {
  gap: 12px;
  font-size: 24px;
  font-weight: 800;
  cursor: pointer;
}

.brand-mark {
  width: 34px;
  height: 34px;
  border: 4px solid #1683ff;
  border-bottom-color: #f59e0b;
  border-radius: 50%;
  position: relative;

  &::after {
    content: '';
    position: absolute;
    left: 8px;
    bottom: 3px;
    width: 10px;
    height: 4px;
    background: #f59e0b;
    border-radius: 4px;
  }
}

.project-actions {
  gap: 70px;
  font-size: 14px;

  button {
    border: 0;
    background: transparent;
    color: #fff;
    cursor: pointer;
  }
}

.api-layout {
  display: grid;
  grid-template-columns: 382px 1fr;
  gap: 18px;
  padding: 18px 6px 0;
}

.sidebar,
.workspace {
  background: #fff;
  border: 1px solid #dde4ee;
  box-shadow: 0 2px 14px rgba(15, 23, 42, 0.08);
}

.sidebar {
  min-height: calc(100vh - 86px);
  border-radius: 0 6px 0 0;
}

.side-actions {
  gap: 12px;
  padding: 13px 18px 27px;
  border-bottom: 1px solid #e6ebf2;
}

button {
  font-family: inherit;
}

.primary-btn,
.analysis-btn,
.apply-btn,
.plain-btn {
  height: 30px;
  padding: 0 14px;
  border-radius: 3px;
  border: 0;
  color: #fff;
  cursor: pointer;
}

.primary-btn {
  background: #2f91f4;
}

.analysis-btn {
  background: linear-gradient(135deg, #2f91f4, #42b65a);
}

.apply-btn {
  background: #57bd32;
}

.plain-btn {
  color: #4b5563;
  background: #fff;
  border: 1px solid #d8dee6;
}

.doc-list {
  padding: 15px 22px;
}

.doc-row {
  display: grid;
  grid-template-columns: 18px 1fr 28px 28px 28px;
  align-items: center;
  gap: 8px;
  min-height: 23px;
  padding: 1px 8px;
  color: #344051;
  font-size: 13px;
  cursor: pointer;

  &.child {
    padding-left: 22px;
  }

  &.active {
    background: #e8f2ff;
  }

  button {
    border: 0;
    background: transparent;
    color: #1683ff;
    cursor: pointer;
    font-size: 12px;
  }

  .danger {
    color: #ff4d4f;
  }
}

.doc-name {
  @include ellipsis;
}

.workspace {
  min-height: calc(100vh - 86px);
  padding: 15px 18px 0;
  border-radius: 0;
}

.workspace-head {
  justify-content: space-between;
  min-height: 48px;
  padding: 0 18px;
  background: #e9f4ff;
  color: #1683ff;
  font-weight: 700;
}

.head-buttons {
  display: flex;
  gap: 12px;
}

.editor-panel {
  margin-top: 20px;
  border: 1px solid #cfd8e3;
}

.toolbar {
  justify-content: center;
  gap: 11px;
  height: 33px;
  background: #f4f7fa;
  border-bottom: 1px solid #cfd8e3;
  color: #5e6875;
}

.editor {
  width: 100%;
  height: calc(100vh - 225px);
  min-height: 500px;
  padding: 0 20% 28px;
  border: 0;
  resize: none;
  outline: none;
  font-size: 15px;
  line-height: 1.9;
  color: #111827;
}

.import-body {
  .field-label {
    margin: 18px 0 8px;
    color: #344051;
  }

  :deep(.el-upload-dragger) {
    width: 210px;
    height: 156px;
  }
}

.upload-icon {
  margin-top: 24px;
  color: #a2a9b5;
  font-size: 48px;
}

.upload-text {
  color: #5b6573;

  span {
    color: #1683ff;
  }
}

.hint,
.file-name {
  margin-top: 10px;
  color: #687386;
  font-size: 12px;
}

.full {
  width: 100%;
}

.tabs {
  display: flex;
  gap: 36px;
  border-bottom: 1px solid #dbe2ea;

  button {
    padding: 0 0 12px;
    border: 0;
    background: transparent;
    color: #333;
    cursor: pointer;

    &.active {
      color: #1683ff;
      border-bottom: 2px solid #1683ff;
    }
  }
}

.empty {
  height: 190px;
  @include flex-center;
  color: #8b96a5;
}

.finding {
  border-bottom: 1px solid #e5ebf2;
  padding: 13px 0;

  p {
    margin: 12px 0 4px 28px;
    color: #303946;
    line-height: 1.75;
  }
}

.finding-head {
  gap: 8px;
  cursor: pointer;

  span {
    flex: 1;
  }
}

.wide {
  min-width: 190px;
}

.processing {
  h3 {
    font-size: 16px;
    font-weight: 600;
  }

  .spin {
    margin: 18px 0;
    color: #1683ff;
  }

  pre {
    height: 390px;
    padding: 18px;
    overflow: auto;
    background: #f5f7fa;
    border-radius: 6px;
    color: #384252;
    white-space: pre-wrap;
  }
}

@media (max-width: 980px) {
  .app-header {
    padding: 0 16px;
  }

  .project-actions {
    gap: 18px;
  }

  .api-layout {
    grid-template-columns: 1fr;
  }

  .editor {
    padding: 20px;
  }
}
</style>
