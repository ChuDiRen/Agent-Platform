<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import type { ComponentPublicInstance } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  applyGeneratedTestCases,
  deleteTestCase,
  generateTestCases,
  getTestCases,
  updateTestCase,
  type RequirementModule,
  type TestCase,
  type TestCasePayload,
} from '@/api/testCase'

defineOptions({ name: 'AITestCaseAgent' })

interface TreeNode extends RequirementModule {
  type: 'group' | 'module'
  children?: TreeNode[]
}

const router = useRouter()
const projectId = 1
const loading = ref(false)
const applying = ref(false)
const tableLoading = ref(false)
const extraRequirement = ref('')
const selectedModuleId = ref(4101)
const selectedRows = ref<TestCase[]>([])
const generatedVisible = ref(false)
const processingVisible = ref(false)
const editVisible = ref(false)
const generatedTableRef = ref<ComponentPublicInstance & { toggleRowSelection: (row: TestCasePayload, selected?: boolean) => void }>()
const generatedCases = ref<TestCasePayload[]>([])
const selectedGenerated = ref<TestCasePayload[]>([])
const testCases = ref<TestCase[]>([])

const editForm = reactive<TestCasePayload>({
  name: '',
  priority: 2,
  precondition: '',
  steps: '',
  expected: '',
})
const editingId = ref<number | null>(null)

const treeData: TreeNode[] = [
  { id: 100, type: 'group', title: '学生端登录接口文档0901002', content: '', children: [
    {
      id: 4101,
      type: 'module',
      title: '学生端登录接口文档0901002',
      content: `# 学生端登录接口文档

## 一、接口信息

### 1. 简要描述
用于实现账号登录功能，验证用户提交的账号、密码等信息，完成身份校验并返回登录结果。

### 2. 请求 URL

\`\`\`
http://kaoshi.project.hctestedu.com/api/user/login
\`\`\`

### 3. 请求方式

\`\`\`
POST
\`\`\`

## 二、请求参数

| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| userName | string | 是 | 登录用户名 |
| password | string | 是 | 登录密码 |
| remember | boolean | 否 | 是否记住登录状态 |`,
    },
    {
      id: 4102,
      type: 'module',
      title: '商品浏览历史列表接口文档',
      content: `# 商品浏览历史列表接口文档

### 2. 请求 URL
\`\`\`
/api/goods/history
\`\`\`

### 3. 请求方式
\`\`\`
GET
\`\`\`

| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| page | number | 否 | 页码 |
| pageSize | number | 否 | 每页数量 |`,
    },
    { id: 4103, type: 'module', title: '加入购物车接口文档', content: '请求 URL\n```/api/cart/add```\n请求方式\n```POST```\n| 参数名 | 类型 | 必填 | 说明 |\n| goods_id | number | 是 | 商品ID |\n| count | number | 是 | 数量 |' },
  ] },
]

const selectedModule = computed(() => {
  for (const group of treeData) {
    const match = group.children?.find((item) => item.id === selectedModuleId.value)
    if (match) return match
  }
  return treeData[0].children?.[0] as RequirementModule
})

const currentTitle = computed(() => selectedModule.value?.title || '未选择模块')

async function loadCases() {
  tableLoading.value = true
  try {
    testCases.value = await getTestCases({ project_id: projectId, module_id: selectedModuleId.value })
  } finally {
    tableLoading.value = false
  }
}

async function selectModule(module: RequirementModule) {
  selectedModuleId.value = module.id
  selectedRows.value = []
  await loadCases()
}

async function previewModule(module: RequirementModule) {
  await ElMessageBox.alert(
    `<h2>${module.title}</h2><p>${module.content}</p>`,
    module.title,
    {
      dangerouslyUseHTMLString: true,
      confirmButtonText: '关闭',
      customClass: 'module-preview-dialog',
    },
  )
}

async function runGenerate() {
  if (!selectedModule.value) {
    ElMessage.warning('请先选择模块')
    return
  }
  processingVisible.value = true
  loading.value = true
  try {
    const response = await generateTestCases({
      project_id: projectId,
      module: selectedModule.value,
      extra_requirement: extraRequirement.value,
    })
    generatedCases.value = response.cases
    selectedGenerated.value = [...response.cases]
    ElMessage.success(`AI生成完成，耗时${response.elapsed_ms}ms`)
    generatedVisible.value = true
    setTimeout(() => {
      generatedCases.value.forEach((item) => generatedTableRef.value?.toggleRowSelection(item, true))
    })
  } finally {
    loading.value = false
    processingVisible.value = false
  }
}

async function applyCases() {
  if (!selectedGenerated.value.length) {
    ElMessage.warning('请至少勾选一条测试用例')
    return
  }
  applying.value = true
  try {
    await applyGeneratedTestCases(selectedGenerated.value)
    ElMessage.success('已保存到数据库')
    generatedVisible.value = false
    await loadCases()
  } finally {
    applying.value = false
  }
}

function openCreateDialog() {
  editingId.value = null
  Object.assign(editForm, {
    project_id: projectId,
    module_id: selectedModuleId.value,
    name: '',
    priority: 2,
    precondition: '',
    steps: '',
    expected: '',
  })
  editVisible.value = true
}

function openEditDialog(row: TestCase) {
  editingId.value = row.id
  Object.assign(editForm, {
    project_id: row.project_id,
    module_id: row.module_id,
    name: row.name,
    priority: row.priority,
    precondition: row.precondition || '',
    steps: row.steps || '',
    expected: row.expected || '',
  })
  editVisible.value = true
}

async function saveEdit() {
  if (!editForm.name.trim()) {
    ElMessage.warning('请输入用例名称')
    return
  }
  if (editingId.value) {
    const updated = await updateTestCase(editingId.value, editForm)
    testCases.value = testCases.value.map((item) => (item.id === updated.id ? updated : item))
    ElMessage.success('用例已更新')
  } else {
    const created = await applyGeneratedTestCases([{ ...editForm, project_id: projectId, module_id: selectedModuleId.value }])
    testCases.value = [...created, ...testCases.value]
    ElMessage.success('用例已新增')
  }
  editVisible.value = false
}

async function removeCase(row: TestCase) {
  await deleteTestCase(row.id)
  testCases.value = testCases.value.filter((item) => item.id !== row.id)
  ElMessage.success('已删除')
}

async function removeSelected() {
  if (!selectedRows.value.length) {
    ElMessage.warning('请先勾选需要删除的用例')
    return
  }
  await Promise.all(selectedRows.value.map((row) => deleteTestCase(row.id)))
  const selectedIds = new Set(selectedRows.value.map((row) => row.id))
  testCases.value = testCases.value.filter((item) => !selectedIds.has(item.id))
  selectedRows.value = []
  ElMessage.success('批量删除完成')
}

function exportCases() {
  const source = selectedRows.value.length ? selectedRows.value : testCases.value
  if (!source.length) {
    ElMessage.warning('暂无可导出的用例')
    return
  }
  const header = ['ID', '用例名称', '前置条件', '测试步骤', '预期结果', '优先级']
  const rows = source.map((item) => [
    item.id,
    item.name,
    item.precondition || '',
    item.steps || '',
    item.expected || '',
    item.priority,
  ])
  const csv = [header, ...rows]
    .map((row) => row.map((cell) => `"${String(cell).replace(/"/g, '""')}"`).join(','))
    .join('\n')
  const blob = new Blob([`\uFEFF${csv}`], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${currentTitle.value}-测试用例.csv`
  link.click()
  URL.revokeObjectURL(url)
}

onMounted(loadCases)
</script>

<template>
  <div class="case-page">
    <header class="topbar">
      <div class="brand" @click="router.push('/agent-hub')">
        <div class="logo-mark" />
        <span>华测 AI+接口用例</span>
      </div>
      <div class="top-links">
        <span>互联网小说网站</span>
        <button @click="router.push('/projects')">退出项目</button>
      </div>
    </header>

    <main class="layout">
      <aside class="sidebar">
        <div v-for="group in treeData" :key="group.id" class="tree-group">
          <div class="tree-row group-row">
            <span class="caret">⌄</span>
            <el-checkbox />
            <span class="node-title">{{ group.title }}</span>
            <button @click="previewModule(group)">查看</button>
          </div>
          <div
            v-for="child in group.children"
            :key="child.id"
            class="tree-row child-row"
            :class="{ active: child.id === selectedModuleId }"
            @click="selectModule(child)"
          >
            <span class="spacer" />
            <el-checkbox :model-value="child.id === selectedModuleId" />
            <span class="node-title">{{ child.title }}</span>
            <button @click.stop="previewModule(child)">查看</button>
          </div>
        </div>
      </aside>

      <section class="content">
        <div class="prompt-panel">
          <el-input
            v-model="extraRequirement"
            type="textarea"
            :rows="4"
            resize="vertical"
            placeholder="如果您对于系统生成的测试用例不满意，可以额外补充您的特殊要求"
          />
        </div>

        <div class="case-card">
          <div class="case-toolbar">
            <h1>当前：{{ currentTitle }}</h1>
            <div class="actions">
              <el-button type="primary" :loading="loading" @click="runGenerate">AI测试用例生成</el-button>
              <el-button type="primary" plain @click="openCreateDialog">手动新增</el-button>
              <el-button type="danger" plain @click="removeSelected">批量删除</el-button>
              <el-button type="warning" @click="exportCases">导出</el-button>
            </div>
          </div>

          <el-table
            v-loading="tableLoading"
            :data="testCases"
            border
            height="378"
            @selection-change="(rows: TestCase[]) => (selectedRows = rows)"
          >
            <el-table-column type="selection" width="54" />
            <el-table-column prop="id" label="ID" width="78" />
            <el-table-column prop="name" label="用例名称" min-width="430">
              <template #default="{ row }">
                <button class="case-link" @click="openEditDialog(row)">{{ row.name }}</button>
              </template>
            </el-table-column>
            <el-table-column prop="priority" label="优先级" width="110" align="center" />
            <el-table-column label="操作" width="176" align="center">
              <template #default="{ row }">
                <el-button type="primary" size="small" @click="openEditDialog(row)">编辑</el-button>
                <el-button type="danger" size="small" @click="removeCase(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>

          <div class="pager">
            <span>共 {{ testCases.length }} 条</span>
            <el-select model-value="10" class="page-size" disabled>
              <el-option label="10条/页" value="10" />
            </el-select>
            <span class="page-current">1</span>
            <span>前往</span>
            <el-input model-value="1" class="page-input" readonly />
            <span>页</span>
          </div>
        </div>
      </section>
    </main>

    <el-dialog v-model="processingVisible" title="AI处理中..." width="760px" :close-on-click-modal="false">
      <div class="processing">
        <div class="status-line">
          <span class="spinner" />
          <strong>AI正在处理中...</strong>
        </div>
        <pre>{{ JSON.stringify(generatedCases.length ? generatedCases : [
          { name: '正在分析选中模块...' },
          { name: '正在拆解场景、边界和异常路径...' },
          { name: '正在组织测试步骤和预期结果...' },
        ], null, 2) }}</pre>
        <el-progress :percentage="loading ? 72 : 100" />
      </div>
    </el-dialog>

    <el-dialog v-model="generatedVisible" title="AI生成测试用例" width="88vw" top="10vh">
      <el-tabs model-value="result">
        <el-tab-pane label="生成结果" name="result">
          <el-table
            ref="generatedTableRef"
            :data="generatedCases"
            border
            height="420"
            @selection-change="(rows: TestCasePayload[]) => (selectedGenerated = rows)"
          >
            <el-table-column type="selection" width="50" :selectable="() => true" />
            <el-table-column prop="name" label="测试用例名称" min-width="220" />
            <el-table-column prop="precondition" label="前置条件" min-width="230" />
            <el-table-column prop="steps" label="接口请求参数" min-width="360" />
            <el-table-column prop="expected" label="预期结果" min-width="260" />
            <el-table-column prop="priority" label="优先级" width="88" align="center" />
          </el-table>
        </el-tab-pane>
      </el-tabs>
      <template #footer>
        <el-button type="primary" @click="runGenerate">重新生成</el-button>
        <el-button type="success" :loading="applying" @click="applyCases">应用</el-button>
        <el-button @click="generatedVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="editVisible" :title="editingId ? '编辑测试用例' : '新增测试用例'" width="760px">
      <el-form label-width="96px">
        <el-row :gutter="24">
          <el-col :span="13">
            <el-form-item label="用例名称" required>
              <el-input v-model="editForm.name" />
            </el-form-item>
          </el-col>
          <el-col :span="11">
            <el-form-item label="优先级" required>
              <el-select v-model="editForm.priority">
                <el-option label="1" :value="1" />
                <el-option label="2" :value="2" />
                <el-option label="3" :value="3" />
                <el-option label="4" :value="4" />
                <el-option label="5" :value="5" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="前置条件">
          <el-input v-model="editForm.precondition" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="接口请求参数" required>
          <el-input v-model="editForm.steps" type="textarea" :rows="4" />
        </el-form-item>
        <el-form-item label="预期结果" required>
          <el-input v-model="editForm.expected" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" @click="saveEdit">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style lang="scss" scoped>
.case-page {
  min-height: 100vh;
  background: #f3f4f6;
  color: #272b33;
}

.topbar {
  height: 76px;
  background: #111418;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 9vw;
  color: #f6f7fb;
}

.brand {
  display: flex;
  align-items: center;
  gap: 14px;
  font-size: 24px;
  font-weight: 800;
  cursor: pointer;
}

.logo-mark {
  width: 38px;
  height: 38px;
  border: 4px solid #246cc8;
  border-radius: 50%;
  position: relative;

  &::before,
  &::after {
    content: '';
    position: absolute;
    border-radius: 999px;
  }

  &::before {
    inset: 8px;
    border: 4px solid #d9783d;
    border-top-color: transparent;
  }

  &::after {
    width: 18px;
    height: 4px;
    left: 6px;
    bottom: 3px;
    background: #e3b341;
  }
}

.top-links {
  display: flex;
  gap: 48px;
  align-items: center;
  font-size: 18px;
  color: #e5e7eb;

  button {
    border: 0;
    background: transparent;
    color: inherit;
    font-size: inherit;
    cursor: pointer;
  }
}

.layout {
  display: grid;
  grid-template-columns: 390px minmax(0, 1fr);
  gap: 26px;
  padding: 26px;
}

.sidebar,
.prompt-panel,
.case-card {
  background: #fff;
  border-radius: 4px;
  box-shadow: 0 8px 22px rgba(25, 35, 60, 0.08);
}

.sidebar {
  height: calc(100vh - 128px);
  overflow: auto;
  border-top: 1px solid #7aa7f8;
  padding: 16px 14px;
}

.tree-row {
  display: grid;
  grid-template-columns: 18px 24px minmax(0, 1fr) 48px;
  align-items: center;
  gap: 6px;
  min-height: 32px;
  padding: 2px 8px;
  color: #3f4652;
  cursor: pointer;

  button {
    border: 0;
    background: transparent;
    color: #3b82f6;
    font-size: 15px;
    cursor: pointer;
  }
}

.child-row {
  padding-left: 24px;

  &.active {
    background: #edf3ff;
  }
}

.node-title {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 16px;
}

.content {
  min-width: 0;
}

.prompt-panel {
  padding: 24px 26px;
  margin-bottom: 20px;
}

.case-card {
  overflow: hidden;
}

.case-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  padding: 24px 26px;
  border-bottom: 1px solid #e8edf5;

  h1 {
    font-size: 21px;
    font-weight: 700;
    margin: 0;
  }
}

.actions {
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.case-card :deep(.el-table) {
  margin: 26px;
  width: calc(100% - 52px);
}

.case-link {
  border: 0;
  background: transparent;
  color: #4591ff;
  font-weight: 700;
  font-size: 16px;
  cursor: pointer;
  text-align: left;
}

.pager {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 18px;
  padding: 0 26px 24px;
  color: #4b5563;
}

.page-size {
  width: 140px;
}

.page-input {
  width: 72px;
}

.page-current {
  color: #3b82f6;
  font-weight: 700;
}

.processing {
  pre {
    max-height: 420px;
    overflow: auto;
    background: #f8fafc;
    border-radius: 6px;
    padding: 18px;
    color: #545b67;
    white-space: pre-wrap;
  }
}

.status-line {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #4591ff;
  margin-bottom: 14px;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid #bfdbfe;
  border-top-color: #4591ff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 1100px) {
  .layout {
    grid-template-columns: 1fr;
  }

  .sidebar {
    height: auto;
    max-height: 320px;
  }
}
</style>
