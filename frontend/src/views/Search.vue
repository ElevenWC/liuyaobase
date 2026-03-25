<template>
  <div class="search-page">
    <el-container>
      <!-- 左侧面板：字段库和推荐方案 -->
      <el-aside width="280px" class="left-panel">
        <el-tabs v-model="leftTab">
          <el-tab-pane label="字段库" name="fields">
            <FieldLibrary @field-drag="handleFieldDrag" />
          </el-tab-pane>
          <el-tab-pane label="推荐方案" name="schemes">
            <RecommendedSchemes
              :current-conditions="conditions"
              @load-scheme="loadScheme"
            />
          </el-tab-pane>
        </el-tabs>
      </el-aside>

      <!-- 中间面板：条件构建 -->
      <el-main class="center-panel">
        <div class="panel-header">
          <span class="title">检索条件</span>
          <el-space>
            <!-- 多窗检索功能 -->
            <WindowManager
              ref="windowManagerRef"
              :conditions="conditions"
              @compare="openCompareMode"
              @merge="handleMerge"
              @conditions-update="handleConditionsUpdate"
            />
            <el-button size="small" @click="clearConditions" :disabled="conditions.length === 0">
              清空条件
            </el-button>
            <el-button
              type="primary"
              size="small"
              @click="executeSearch"
              :loading="searching"
              :disabled="conditions.length === 0"
            >
              执行检索
            </el-button>
          </el-space>
        </div>

        <!-- 窗口标识 -->
        <div v-if="isChildWindow" class="window-notice">
          <el-alert type="info" :closable="false">
            <template #title>
              <el-icon><InfoFilled /></el-icon>
              子窗口 - 条件已从主窗口继承
            </template>
          </el-alert>
        </div>

        <ConditionBuilder
          ref="conditionBuilderRef"
          v-model="conditions"
        />

        <!-- 表达式预览 -->
        <div v-if="conditions.length > 0" class="expression-preview">
          <div class="preview-header">
            <span>表达式预览</span>
            <el-space>
              <el-button type="primary" link size="small" @click="shareConditions">
                <el-icon><Share /></el-icon>
                分享条件
              </el-button>
              <el-button type="primary" link size="small" @click="copyExpression">
                复制
              </el-button>
            </el-space>
          </div>
          <pre class="expression-code">{{ expressionPreview }}</pre>
        </div>
      </el-main>

      <!-- 右侧面板：检索结果 -->
      <el-aside width="400px" class="right-panel">
        <ResultList
          :results="searchResults"
          :total="totalResults"
          :loading="searching"
          @page-change="handlePageChange"
          @view-detail="viewDetail"
          @export="exportResults"
        />
      </el-aside>
    </el-container>

    <!-- 对比模式对话框 -->
    <CompareMode
      v-model:show="compareModeVisible"
      :windows="childWindows"
      :current-conditions="conditions"
      @merge="handleMerge"
      @load-conditions="loadConditionsFromCompare"
    />

    <!-- 分享条件对话框 -->
    <el-dialog v-model="shareDialogVisible" title="分享检索条件" width="500px">
      <el-form label-width="80px">
        <el-form-item label="分享链接">
          <el-input v-model="shareUrl" readonly>
            <template #append>
              <el-button @click="copyShareUrl">复制</el-button>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="二维码">
          <div class="qrcode-placeholder">
            <el-icon size="50"><Picture /></el-icon>
            <p>可使用二维码分享</p>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="shareDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { InfoFilled, Share, Picture } from '@element-plus/icons-vue'
import FieldLibrary from '@/components/Search/FieldLibrary.vue'
import ConditionBuilder from '@/components/Search/ConditionBuilder.vue'
import RecommendedSchemes from '@/components/Search/RecommendedSchemes.vue'
import ResultList from '@/components/Search/ResultList.vue'
import WindowManager from '@/components/Search/WindowManager.vue'
import CompareMode from '@/components/Search/CompareMode.vue'
import { searchGuali } from '@/api'

const router = useRouter()
const route = useRoute()

const leftTab = ref('fields')
const conditions = ref([])
const searchResults = ref([])
const totalResults = ref(0)
const searching = ref(false)
const conditionBuilderRef = ref(null)
const windowManagerRef = ref(null)

// 多窗检索状态
const compareModeVisible = ref(false)
const childWindows = ref([])
const shareDialogVisible = ref(false)
const shareUrl = ref('')

// 是否为子窗口
const isChildWindow = computed(() => !!window.opener)

// 分页
const pagination = ref({
  page: 1,
  pageSize: 20
})

// 表达式预览
const expressionPreview = computed(() => {
  if (conditions.value.length === 0) return ''

  const parts = conditions.value.map((c, index) => {
    let part = ''

    if (index > 0) {
      part += ` ${c.logic?.toUpperCase() || 'AND'} `
    }

    if (c.operator === 'WITH') {
      part += `${c.fieldLabel} WITH ${c.targetField || '?'} (${getRelationLabel(c.relationType)})`
    } else if (c.operator === '与') {
      part += `${c.fieldLabel} 与 ${c.targetField || '?'} = ${getRelationLabel(c.relationType)}`
    } else {
      const value = c.subValue || c.value || '?'
      part += `${c.fieldLabel} ${c.operator} ${value}`
    }

    return part
  })

  return parts.join('')
})

function getRelationLabel(type) {
  const labels = { he: '相合', chong: '相冲', sheng: '相生', ke: '相克' }
  return labels[type] || type
}

// 处理字段拖拽
function handleFieldDrag(field) {
  // 可以在这里添加拖拽提示
}

// 加载方案
function loadScheme(schemeConditions) {
  conditions.value = JSON.parse(JSON.stringify(schemeConditions))
  ElMessage.success('方案已加载')
}

// 清空条件
function clearConditions() {
  conditions.value = []
}

// 执行检索
async function executeSearch() {
  if (conditions.value.length === 0) {
    ElMessage.warning('请先添加检索条件')
    return
  }

  // 验证条件
  const hasError = conditions.value.some(c => {
    if (c.operator !== 'WITH' && !c.value && !c.subValue) {
      c.error = '请输入值'
      return true
    }
    c.error = null
    return false
  })

  if (hasError) {
    ElMessage.warning('请完善检索条件')
    return
  }

  searching.value = true

  try {
    const searchParams = buildSearchParams()
    const result = await searchGuali(searchParams)
    searchResults.value = result.items || []
    totalResults.value = result.total || 0

    if (result.items?.length === 0) {
      ElMessage.info('未找到匹配的卦例')
    } else {
      ElMessage.success(`找到 ${result.total} 个匹配的卦例`)
    }
  } catch (error) {
    ElMessage.error('检索失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    searching.value = false
  }
}

// 构建检索参数
function buildSearchParams() {
  return {
    conditions: conditions.value.map(c => ({
      field: c.key || c.field,
      operator: c.operator,
      value: c.subValue || c.value,
      relation_type: c.relationType,
      target_field: c.targetField,
      logic: c.logic || 'and'
    })),
    page: pagination.value.page,
    page_size: pagination.value.pageSize
  }
}

// 分页变化
function handlePageChange(page, pageSize) {
  pagination.value.page = page
  pagination.value.pageSize = pageSize
  executeSearch()
}

// 查看详情
function viewDetail(id) {
  router.push(`/detail/${id}`)
}

// 导出结果
async function exportResults() {
  if (searchResults.value.length === 0) {
    ElMessage.warning('没有可导出的结果')
    return
  }

  try {
    // 导出为CSV
    const headers = ['ID', '公历时间', '日柱', '本卦', '之卦', '卦宫', '宫位', '占问事由']
    const rows = searchResults.value.map(item => [
      item.id,
      `${item.solar_year}-${item.solar_month}-${item.solar_day}`,
      item.ganzhi_day,
      item.ben_gua_name,
      item.zhi_gua_name || '',
      item.gongwei,
      item.gongwei_index,
      item.zhan_wen || ''
    ])

    const csvContent = [headers.join(','), ...rows.map(r => r.join(','))].join('\n')

    // 下载文件
    const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `search_results_${Date.now()}.csv`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)

    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error('导出失败: ' + error.message)
  }
}

// 复制表达式
function copyExpression() {
  navigator.clipboard.writeText(expressionPreview.value)
    .then(() => ElMessage.success('已复制到剪贴板'))
    .catch(() => ElMessage.error('复制失败'))
}

// 打开对比模式
function openCompareMode() {
  if (windowManagerRef.value) {
    windowManagerRef.value.syncWindowList()
    childWindows.value = [...windowManagerRef.value.windowCount > 0 ? [] : []]
  }
  compareModeVisible.value = true
}

// 处理合并条件
function handleMerge(mergedConditions) {
  if (mergedConditions && mergedConditions.length > 0) {
    conditions.value = mergedConditions
    ElMessage.success(`已合并 ${mergedConditions.length} 条条件`)
  }
}

// 处理来自其他窗口的条件更新
function handleConditionsUpdate(newConditions) {
  if (newConditions && newConditions.length > 0) {
    ElMessageBox.confirm(
      '收到来自其他窗口的条件更新，是否加载？',
      '条件更新',
      {
        confirmButtonText: '加载',
        cancelButtonText: '取消',
        type: 'info'
      }
    ).then(() => {
      conditions.value = newConditions
    }).catch(() => {})
  }
}

// 从对比模式加载条件
function loadConditionsFromCompare(conds) {
  if (conds && conds.length > 0) {
    conditions.value = JSON.parse(JSON.stringify(conds))
  }
}

// 分享条件
function shareConditions() {
  if (conditions.value.length === 0) {
    ElMessage.warning('没有可分享的条件')
    return
  }

  const conditionParam = encodeURIComponent(JSON.stringify(conditions.value))
  shareUrl.value = `${window.location.origin}${window.location.pathname}?condition=${conditionParam}`
  shareDialogVisible.value = true
}

// 复制分享链接
function copyShareUrl() {
  navigator.clipboard.writeText(shareUrl.value)
    .then(() => ElMessage.success('链接已复制到剪贴板'))
    .catch(() => ElMessage.error('复制失败'))
}

// 处理URL参数
onMounted(() => {
  const conditionParam = route.query.condition
  if (conditionParam) {
    try {
      const decoded = JSON.parse(decodeURIComponent(conditionParam))
      if (Array.isArray(decoded)) {
        conditions.value = decoded
        ElMessage.success('已从URL加载检索条件')
      }
    } catch (e) {
      console.error('解析URL参数失败:', e)
    }
  }

  // 监听localStorage变化（用于窗口间通信）
  window.addEventListener('storage', handleStorageChange)
})

onUnmounted(() => {
  window.removeEventListener('storage', handleStorageChange)
})

// 处理storage变化
function handleStorageChange(event) {
  if (event.key === 'search_broadcast') {
    try {
      const message = JSON.parse(event.newValue)
      if (message.type === 'conditions-update' && message.data) {
        handleConditionsUpdate(message.data)
      }
    } catch (e) {
      console.error('处理广播消息失败:', e)
    }
  }
}
</script>

<style scoped>
.search-page {
  height: calc(100vh - 120px);
}

.el-container {
  height: 100%;
}

.left-panel {
  background: var(--el-bg-color);
  border-right: 1px solid var(--el-border-color);
  overflow-y: auto;
}

.center-panel {
  background: var(--el-bg-color-page);
  display: flex;
  flex-direction: column;
  padding: 15px;
  overflow-y: auto;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--el-border-color);
}

.panel-header .title {
  font-size: 16px;
  font-weight: bold;
}

.window-notice {
  margin-bottom: 15px;
}

.right-panel {
  background: var(--el-bg-color);
  border-left: 1px solid var(--el-border-color);
  overflow-y: auto;
}

.expression-preview {
  margin-top: 15px;
  background: var(--el-fill-color-light);
  border-radius: 8px;
  overflow: hidden;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  background: var(--el-fill-color);
  border-bottom: 1px solid var(--el-border-color-lighter);
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.expression-code {
  margin: 0;
  padding: 15px;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 12px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-all;
  color: var(--el-text-color-primary);
}

.qrcode-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
  color: var(--el-text-color-secondary);
}
</style>
