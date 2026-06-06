<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import AgentPageHeader from '@/components/AgentPageHeader.vue'
import {
  createTestDataTemplate,
  generateTestData,
  getTestDataTemplates,
  type TestDataField,
  type TestDataFieldType,
  type TestDataFormat,
  type TestDataGenerateResponse,
  type TestDataLanguage,
  type TestDataTemplate,
} from '@/api/testData'

defineOptions({ name: 'TestDataGenerator' })

const count = ref(10)
const format = ref<TestDataFormat>('json')
const lang = ref<TestDataLanguage>('zh')
const hint = ref('')
const loading = ref(false)
const saving = ref(false)
const templates = ref<TestDataTemplate[]>([])
const selectedTemplateId = ref<number | null>(null)
const result = ref<TestDataGenerateResponse | null>(null)
const fields = ref<TestDataField[]>([
  { name: 'id', type: 'number', rule: '从1开始递增' },
  { name: 'username', type: 'string', rule: '用户名' },
  { name: 'pass', type: 'string', rule: '密码' },
])

const typeOptions: Array<{ label: string; value: TestDataFieldType }> = [
  { label: '数字', value: 'number' },
  { label: '字符串', value: 'string' },
  { label: '邮箱', value: 'email' },
  { label: '手机号', value: 'phone' },
  { label: '日期', value: 'date' },
  { label: '布尔值', value: 'boolean' },
]

const contentTitle = computed(() => (format.value === 'csv' ? 'CSV 预览' : 'JSON 预览'))

function buildPayload() {
  return {
    count: count.value,
    format: format.value,
    lang: lang.value,
    hint: hint.value,
    fields: fields.value.filter((field) => field.name.trim()),
  }
}

function addField() {
  fields.value.push({ name: '', type: 'string', rule: '' })
}

function removeField(index: number) {
  if (fields.value.length === 1) {
    ElMessage.warning('至少保留一个字段')
    return
  }
  fields.value.splice(index, 1)
}

async function runGenerate() {
  const payload = buildPayload()
  if (!payload.fields.length) {
    ElMessage.warning('请至少配置一个字段')
    return
  }

  loading.value = true
  try {
    result.value = await generateTestData(payload)
    ElMessage.success(`生成成功，耗时${result.value.elapsed_ms}ms`)
  } finally {
    loading.value = false
  }
}

async function saveTemplate() {
  const payload = buildPayload()
  if (!payload.fields.length) {
    ElMessage.warning('请至少配置一个字段')
    return
  }

  saving.value = true
  try {
    const template = await createTestDataTemplate({
      ...payload,
      name: `测试数据模板 ${new Date().toLocaleString('zh-CN')}`,
      description: hint.value || 'AI测试数据生成模板',
    })
    templates.value.unshift(template)
    selectedTemplateId.value = template.id
    ElMessage.success('模板已保存')
  } finally {
    saving.value = false
  }
}

function loadTemplate(templateId: number) {
  const template = templates.value.find((item) => item.id === templateId)
  if (!template) return
  count.value = template.count
  format.value = template.format
  lang.value = template.lang
  hint.value = template.hint || ''
  fields.value = template.fields.map((field) => ({ ...field }))
  ElMessage.success('模板已加载')
}

async function copyContent() {
  if (!result.value?.content) {
    ElMessage.warning('暂无可复制内容')
    return
  }
  try {
    await navigator.clipboard.writeText(result.value.content)
    ElMessage.success('已复制到剪贴板')
  } catch {
    ElMessage.error('复制失败')
  }
}

function downloadContent() {
  if (!result.value?.content) {
    ElMessage.warning('暂无可下载内容')
    return
  }
  const blob = new Blob([result.value.content], {
    type: format.value === 'csv' ? 'text/csv;charset=utf-8' : 'application/json;charset=utf-8',
  })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `test-data.${format.value}`
  link.click()
  URL.revokeObjectURL(url)
}

onMounted(async () => {
  try {
    templates.value = await getTestDataTemplates()
  } catch {
    templates.value = []
  }
})
</script>

<template>
  <div class="generator-page">
    <AgentPageHeader title="测试数据生成助手" />

    <main class="workspace">
      <section class="panel config-panel">
        <div class="panel-head">
          <h1>AI测试数据生成系统</h1>
          <div class="actions">
            <button class="primary-btn" :disabled="loading" @click="runGenerate">
              {{ loading ? '生成中' : '运行生成' }}
            </button>
            <button class="success-btn" :disabled="saving" @click="saveTemplate">保存为模板</button>
            <el-select
              v-model="selectedTemplateId"
              placeholder="加载模板"
              class="template-select"
              @change="loadTemplate"
            >
              <el-option
                v-for="template in templates"
                :key="template.id"
                :label="template.name"
                :value="template.id"
              />
            </el-select>
          </div>
        </div>

        <div class="section-title">
          <span>基础配置</span>
        </div>
        <div class="basic-grid">
          <label>
            <span>数据量</span>
            <el-input-number v-model="count" :min="1" :max="500" size="small" />
          </label>
          <label>
            <span>数据格式</span>
            <el-select v-model="format" size="small">
              <el-option label="JSON" value="json" />
              <el-option label="CSV" value="csv" />
            </el-select>
          </label>
          <label>
            <span>语言</span>
            <el-select v-model="lang" size="small">
              <el-option label="中文" value="zh" />
              <el-option label="English" value="en" />
            </el-select>
          </label>
        </div>

        <div class="section-title">
          <span>结果要求</span>
        </div>
        <el-input
          v-model="hint"
          type="textarea"
          :rows="4"
          resize="vertical"
          placeholder="输入你期望的数据特征、约束或额外要求"
        />

        <div class="field-head">
          <div class="section-title">
            <span>字段配置</span>
          </div>
          <button class="outline-btn" @click="addField">添加字段</button>
        </div>

        <div class="field-list">
          <div v-for="(field, index) in fields" :key="index" class="field-row">
            <el-input v-model="field.name" placeholder="字段名" size="small" />
            <el-select v-model="field.type" size="small">
              <el-option
                v-for="option in typeOptions"
                :key="option.value"
                :label="option.label"
                :value="option.value"
              />
            </el-select>
            <el-input v-model="field.rule" placeholder="生成规则，如：从1开始递增 / 用户名 / 密码" size="small" />
            <button class="danger-icon" aria-label="删除字段" @click="removeField(index)">×</button>
          </div>
        </div>
      </section>

      <section class="panel result-panel">
        <div class="result-head">
          <div class="section-title">
            <span>生成结果</span>
          </div>
          <div class="result-actions">
            <button class="ghost-btn" @click="copyContent">复制JSON</button>
            <button class="ghost-btn" @click="downloadContent">下载文件</button>
          </div>
        </div>

        <div v-if="result" class="success-bar">
          生成成功，共 {{ result.count }} 条，耗时 {{ result.elapsed_ms }}ms
        </div>
        <div v-else class="empty-bar">配置字段后点击运行生成</div>

        <div class="preview">
          <div class="preview-title">{{ contentTitle }}</div>
          <pre>{{ result?.content || '{\n  "data": []\n}' }}</pre>
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped lang="scss">
.generator-page {
  min-height: 100vh;
  background: #f4f6f9;
  color: $text-primary;
}

.topbar {
  height: 56px;
  padding: 0 40px;
  background: #18212a;
  color: #fff;
  @include flex-between;
}

.brand,
.top-actions,
.actions,
.result-actions,
.field-head,
.result-head {
  display: flex;
  align-items: center;
}

.top-actions {
  gap: 28px;
}

.brand {
  gap: 10px;
  font-size: 17px;
  font-weight: 700;
}

.logo-mark {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: $accent-gradient;
  @include flex-center;
  font-size: 11px;
  font-weight: 800;
}

.text-btn {
  border: 0;
  background: transparent;
  color: #fff;
  cursor: pointer;
}

.workspace {
  width: min(1040px, calc(100vw - 40px));
  margin: 36px auto;
}

.panel {
  background: #fff;
  border: 1px solid $border-color;
  border-radius: 8px;
  box-shadow: $shadow-md;
}

.config-panel {
  padding: 20px 28px 12px;
}

.panel-head {
  @include flex-between;
  margin-bottom: 22px;

  h1 {
    font-size: 22px;
    color: $accent-primary;
    font-weight: 800;
  }
}

.actions {
  gap: 12px;
}

button {
  font-family: inherit;
}

.primary-btn,
.success-btn,
.outline-btn,
.ghost-btn {
  height: 30px;
  padding: 0 14px;
  border-radius: 4px;
  border: 1px solid transparent;
  cursor: pointer;
  font-size: 12px;
}

.primary-btn {
  background: #409eff;
  color: #fff;
}

.success-btn {
  background: #54b435;
  color: #fff;
}

.outline-btn {
  background: #eef6ff;
  color: #409eff;
  border-color: #b9dcff;
}

.ghost-btn {
  background: #fff;
  color: $text-regular;
  border-color: $border-color;
}

.template-select {
  width: 128px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 12px 0 10px;
  color: $text-primary;
  font-size: 13px;
  font-weight: 700;

  &::before {
    content: '';
    width: 8px;
    height: 8px;
    border-radius: 2px;
    background: #409eff;
  }
}

.basic-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(180px, 1fr));
  gap: 20px;
  width: 64%;
  min-width: 620px;
  margin-bottom: 8px;

  label {
    display: grid;
    grid-template-columns: 64px 1fr;
    align-items: center;
    gap: 8px;
    font-size: 12px;
    color: $text-regular;
  }
}

.field-head,
.result-head {
  justify-content: space-between;
}

.field-list {
  border: 1px solid #ffd6d6;
  padding: 8px;
}

.field-row {
  display: grid;
  grid-template-columns: 132px 112px 1fr 28px;
  gap: 56px;
  align-items: center;
  padding: 8px 4px;
  background: #f2f3f5;

  & + & {
    margin-top: 8px;
  }
}

.danger-icon {
  width: 24px;
  height: 24px;
  border: 1px solid #ffb4b4;
  border-radius: 50%;
  background: #fff;
  color: #ff7070;
  cursor: pointer;
  font-size: 18px;
  line-height: 18px;
}

.result-panel {
  margin-top: 14px;
  padding: 16px 14px 18px;
}

.result-actions {
  gap: 12px;
}

.success-bar,
.empty-bar {
  margin-top: 10px;
  padding: 8px 12px;
  font-size: 12px;
  border-radius: 4px;
}

.success-bar {
  background: #ecf9e8;
  color: #36a329;
}

.empty-bar {
  background: #f6f8fb;
  color: $text-secondary;
}

.preview {
  margin-top: 14px;
  border: 1px solid $border-color;
  border-radius: 6px;
  overflow: hidden;
  background: #f8fafc;
}

.preview-title {
  padding: 10px 14px;
  background: #f1f5f9;
  font-size: 13px;
  font-weight: 700;
}

pre {
  min-height: 240px;
  max-height: 460px;
  margin: 0;
  padding: 16px;
  overflow: auto;
  font-size: 13px;
  line-height: 1.65;
  color: #1f2937;
}

@media (max-width: 820px) {
  .topbar {
    padding: 0 16px;
  }

  .workspace {
    width: calc(100vw - 24px);
    margin: 16px auto;
  }

  .panel-head,
  .result-head {
    align-items: flex-start;
    flex-direction: column;
    gap: 12px;
  }

  .actions,
  .result-actions {
    flex-wrap: wrap;
  }

  .basic-grid {
    width: 100%;
    min-width: 0;
    grid-template-columns: 1fr;
  }

  .field-row {
    grid-template-columns: 1fr;
    gap: 8px;
  }
}
.generator-page {
  background: #f5f7fa;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

.workspace {
  max-width: 1280px;
  width: min(1280px, calc(100vw - 48px));
  margin: 0 auto 48px;
}

.panel {
  border: 0;
  border-radius: 24px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.05);
}

.panel-head h1 {
  color: #1f2a3e;
}

.generator-page {
  min-height: 100vh;
  overflow-x: hidden;
}

.workspace {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 18px;
  width: min(1040px, calc(100vw - 48px));
  max-width: none;
  margin: 0 auto 40px;
}

.panel {
  min-width: 0;
}

.config-panel {
  padding: 22px 24px;
}

.panel-head,
.result-head {
  gap: 14px;
}

.actions,
.result-actions {
  flex-wrap: wrap;
  justify-content: flex-end;
}

.basic-grid {
  width: 100%;
  min-width: 0;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.field-row {
  grid-template-columns: minmax(120px, 1fr) minmax(120px, 160px) minmax(160px, 1fr) 42px;
}

@media (max-width: 900px) {
  .workspace {
    width: min(100%, calc(100vw - 32px));
  }

  .basic-grid,
  .field-row {
    grid-template-columns: 1fr;
  }
}
</style>
