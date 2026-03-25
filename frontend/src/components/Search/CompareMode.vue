<template>
  <el-dialog
    v-model="visible"
    title="多窗口对比模式"
    width="90%"
    top="5vh"
    :close-on-click-modal="false"
    class="compare-dialog"
  >
    <template #header>
      <div class="compare-header">
        <span>多窗口对比模式</span>
        <el-space>
          <el-button size="small" @click="refreshAll">
            <el-icon><Refresh /></el-icon>
            刷新数据
          </el-button>
          <el-button size="small" type="primary" @click="mergeSelected" :disabled="selectedWindows.length < 2">
            <el-icon><Operation /></el-icon>
            合并选中条件
          </el-button>
        </el-space>
      </div>
    </template>

    <div class="compare-content">
      <!-- 窗口选择区 -->
      <div class="window-selector">
        <el-checkbox-group v-model="selectedWindows">
          <el-checkbox
            v-for="win in availableWindows"
            :key="win.id"
            :label="win.id"
            border
            class="window-checkbox"
          >
            {{ win.name }}
            <el-tag size="small" type="info">{{ win.conditionCount }} 条条件</el-tag>
          </el-checkbox>
        </el-checkbox-group>
      </div>

      <!-- 对比表格 -->
      <div v-if="selectedWindows.length >= 2" class="compare-table-wrapper">
        <el-table :data="compareData" border stripe max-height="400">
          <el-table-column prop="aspect" label="对比维度" width="150" fixed />
          <el-table-column
            v-for="winId in selectedWindows"
            :key="winId"
            :label="getWindowName(winId)"
            min-width="200"
          >
            <template #default="{ row }">
              <div class="compare-cell" :class="getCompareClass(row, winId)">
                {{ row.data[winId] || '-' }}
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 空状态 -->
      <el-empty
        v-else
        description="请选择至少2个窗口进行对比"
        :image-size="100"
      />

      <!-- 条件详情对比 -->
      <div v-if="selectedWindows.length >= 2" class="condition-detail">
        <el-divider>条件详情对比</el-divider>
        <el-row :gutter="20">
          <el-col
            v-for="winId in selectedWindows"
            :key="winId"
            :span="24 / selectedWindows.length"
          >
            <el-card shadow="hover" class="condition-card">
              <template #header>
                <div class="card-header">
                  <span>{{ getWindowName(winId) }}</span>
                  <el-button
                    type="primary"
                    size="small"
                    link
                    @click="loadConditions(winId)"
                  >
                    加载此条件
                  </el-button>
                </div>
              </template>
              <div class="condition-list">
                <el-tag
                  v-for="(cond, idx) in getWindowConditions(winId)"
                  :key="idx"
                  class="condition-tag"
                  :type="getConditionType(cond)"
                >
                  {{ formatCondition(cond) }}
                </el-tag>
                <el-empty
                  v-if="!getWindowConditions(winId)?.length"
                  description="无条件"
                  :image-size="50"
                />
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </div>

    <template #footer>
      <el-button @click="visible = false">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Refresh, Operation } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  windows: {
    type: Array,
    default: () => []
  },
  currentConditions: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:show', 'merge', 'load-conditions'])

const visible = computed({
  get: () => props.show,
  set: (val) => emit('update:show', val)
})

const selectedWindows = ref([])
const windowConditions = ref({})

// 可用窗口列表（包含当前窗口）
const availableWindows = computed(() => {
  const windows = [...props.windows]

  // 添加当前窗口
  windows.unshift({
    id: 'current',
    name: '当前窗口',
    conditionCount: props.currentConditions.length,
    conditions: props.currentConditions,
    isCurrent: true
  })

  return windows
})

// 对比数据
const compareData = computed(() => {
  if (selectedWindows.value.length < 2) return []

  const aspects = [
    { key: 'conditionCount', label: '条件数量' },
    { key: 'resultCount', label: '结果数量' },
    { key: 'timeFields', label: '时间类条件' },
    { key: 'guaFields', label: '卦类条件' },
    { key: 'yaoFields', label: '爻类条件' },
    { key: 'otherFields', label: '其他条件' }
  ]

  return aspects.map(aspect => {
    const row = {
      aspect: aspect.label,
      data: {}
    }

    selectedWindows.value.forEach(winId => {
      const conds = getWindowConditions(winId) || []
      row.data[winId] = getAspectValue(aspect.key, conds, winId)
    })

    return row
  })
})

// 获取维度值
function getAspectValue(key, conditions, winId) {
  switch (key) {
    case 'conditionCount':
      return conditions.length + ' 条'
    case 'resultCount':
      return windowConditions.value[winId]?.resultCount || '-'
    case 'timeFields':
      return countFieldsByCategory(conditions, 'time')
    case 'guaFields':
      return countFieldsByCategory(conditions, 'gua')
    case 'yaoFields':
      return countFieldsByCategory(conditions, 'yao')
    case 'otherFields':
      return countFieldsByCategory(conditions, 'other')
    default:
      return '-'
  }
}

// 按分类统计字段
function countFieldsByCategory(conditions, category) {
  const fields = conditions.filter(c => c.category === category)
  if (fields.length === 0) return '无'

  const fieldNames = fields.map(f => f.fieldLabel || f.key)
  return fieldNames.join(', ')
}

// 获取窗口名称
function getWindowName(winId) {
  const win = availableWindows.value.find(w => w.id === winId)
  return win?.name || winId
}

// 获取窗口条件
function getWindowConditions(winId) {
  if (winId === 'current') {
    return props.currentConditions
  }

  const win = props.windows.find(w => w.id === winId)
  return win?.conditions || windowConditions.value[winId]?.conditions || []
}

// 获取对比样式类
function getCompareClass(row, winId) {
  const values = selectedWindows.value.map(id => row.data[id])
  const uniqueValues = [...new Set(values)]

  // 如果所有值相同
  if (uniqueValues.length === 1) {
    return 'same'
  }

  // 如果当前值与其他不同
  const currentValue = row.data[winId]
  const otherValues = values.filter(v => v !== currentValue)

  if (otherValues.length > 0 && !otherValues.includes(currentValue)) {
    return 'different'
  }

  return ''
}

// 获取条件类型
function getConditionType(condition) {
  const categoryTypes = {
    time: '',
    gua: 'success',
    yao: 'primary',
    relation: 'warning',
    shensha: 'danger',
    other: 'info'
  }
  return categoryTypes[condition.category] || ''
}

// 格式化条件
function formatCondition(condition) {
  if (!condition) return ''

  const field = condition.fieldLabel || condition.key || condition.field
  const op = condition.operator
  const value = condition.subValue || condition.value || ''

  if (condition.operator === 'WITH') {
    return `${field} WITH ${condition.targetField || '?'}`
  }

  return `${field} ${op} ${value}`
}

// 刷新所有窗口数据
function refreshAll() {
  // 这里可以通过消息机制刷新其他窗口的数据
  ElMessage.success('已发送刷新请求')
}

// 合并选中窗口的条件
function mergeSelected() {
  if (selectedWindows.value.length < 2) {
    ElMessage.warning('请至少选择2个窗口')
    return
  }

  const mergedConditions = []
  const seenKeys = new Set()

  selectedWindows.value.forEach(winId => {
    const conds = getWindowConditions(winId) || []
    conds.forEach(cond => {
      const key = cond.key || cond.field
      if (!seenKeys.has(key + cond.operator + (cond.subValue || cond.value))) {
        seenKeys.add(key + cond.operator + (cond.subValue || cond.value))
        mergedConditions.push({
          ...cond,
          logic: mergedConditions.length === 0 ? 'and' : 'or' // 合并时使用OR
        })
      }
    })
  })

  emit('merge', mergedConditions)
  visible.value = false
  ElMessage.success(`已合并 ${mergedConditions.length} 条条件`)
}

// 加载窗口条件
function loadConditions(winId) {
  const conds = getWindowConditions(winId)
  emit('load-conditions', conds)
  visible.value = false
  ElMessage.success('已加载条件')
}

// 监听显示状态
watch(() => props.show, (val) => {
  if (val) {
    // 对话框打开时，默认选择当前窗口
    selectedWindows.value = ['current']
  }
})
</script>

<style scoped>
.compare-dialog :deep(.el-dialog__body) {
  padding: 15px 20px;
}

.compare-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.window-selector {
  margin-bottom: 20px;
}

.window-checkbox {
  margin: 5px 10px 5px 0;
}

.window-checkbox :deep(.el-checkbox__label) {
  display: flex;
  align-items: center;
  gap: 8px;
}

.compare-table-wrapper {
  margin: 20px 0;
}

.compare-cell {
  padding: 5px;
  border-radius: 4px;
}

.compare-cell.same {
  background-color: #f0f9eb;
}

.compare-cell.different {
  background-color: #fef0f0;
}

.condition-detail {
  margin-top: 20px;
}

.condition-card {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.condition-list {
  max-height: 300px;
  overflow-y: auto;
}

.condition-tag {
  margin: 3px;
  display: inline-block;
}
</style>
