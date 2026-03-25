<template>
  <div class="condition-builder">
    <!-- 条件卡片列表 -->
    <div class="conditions-container">
      <template v-for="(condition, index) in conditions" :key="index">
        <!-- 逻辑运算符（非第一个条件前显示） -->
        <div v-if="index > 0" class="logic-operator">
          <el-radio-group v-model="condition.logic" size="small">
            <el-radio-button value="and">AND</el-radio-button>
            <el-radio-button value="or">OR</el-radio-button>
          </el-radio-group>
        </div>

        <!-- 条件卡片 -->
        <el-card class="condition-card" :class="{ 'has-error': condition.error }">
          <div class="condition-header">
            <el-tag :type="getFieldType(condition.field)" size="small">
              {{ condition.fieldLabel || condition.field }}
            </el-tag>
            <el-button
              type="danger"
              size="small"
              circle
              @click="removeCondition(index)"
            >
              <el-icon><Close /></el-icon>
            </el-button>
          </div>

          <div class="condition-body">
            <!-- 运算符选择 -->
            <el-select
              v-model="condition.operator"
              placeholder="选择运算符"
              size="small"
              class="operator-select"
              @change="onOperatorChange(condition)"
            >
              <el-option
                v-for="op in getAvailableOperators(condition)"
                :key="op.value"
                :label="op.label"
                :value="op.value"
              />
            </el-select>

            <!-- 值输入 - 根据字段类型显示不同输入方式 -->
            <template v-if="needValueInput(condition)">
              <!-- 下拉选择 -->
              <el-select
                v-if="condition.inputType === 'select'"
                v-model="condition.value"
                :placeholder="`选择${condition.fieldLabel}`"
                size="small"
                class="value-select"
                filterable
              >
                <el-option
                  v-for="opt in condition.options || []"
                  :key="opt.value"
                  :label="opt.label"
                  :value="opt.value"
                />
              </el-select>

              <!-- 文本输入 -->
              <el-input
                v-else-if="condition.inputType === 'input'"
                v-model="condition.value"
                :placeholder="`输入${condition.fieldLabel}`"
                size="small"
                class="value-input"
              />

              <!-- 数字输入 -->
              <el-input-number
                v-else-if="condition.valueType === 'number'"
                v-model="condition.value"
                size="small"
                class="value-input"
              />

              <!-- 复合字段 - 显示子属性选择 -->
              <template v-else-if="condition.inputType === 'compound'">
                <el-select
                  v-model="condition.subValue"
                  placeholder="选择值"
                  size="small"
                  class="value-select"
                >
                  <el-option
                    v-for="opt in getCompoundOptions(condition)"
                    :key="opt.value"
                    :label="opt.label"
                    :value="opt.value"
                  />
                </el-select>
              </template>
            </template>

            <!-- 关系运算符特殊处理 -->
            <template v-if="condition.operator === '与' || condition.operator === 'WITH'">
              <el-select
                v-model="condition.relationType"
                placeholder="选择关系"
                size="small"
                class="relation-select"
              >
                <el-option label="相合" value="he" />
                <el-option label="相冲" value="chong" />
                <el-option label="相生" value="sheng" />
                <el-option label="相克" value="ke" />
              </el-select>
            </template>

            <!-- 目标字段选择（用于关系运算） -->
            <template v-if="condition.operator === 'WITH'">
              <el-select
                v-model="condition.targetField"
                placeholder="选择目标字段"
                size="small"
                class="target-select"
              >
                <el-option label="日支" value="day_dizhi" />
                <el-option label="日干" value="day_tiangan" />
                <el-option label="世爻" value="world_yao" />
                <el-option label="应爻" value="response_yao" />
              </el-select>
            </template>
          </div>

          <!-- 错误提示 -->
          <div v-if="condition.error" class="error-message">
            {{ condition.error }}
          </div>
        </el-card>
      </template>
    </div>

    <!-- 空状态 -->
    <el-empty
      v-if="conditions.length === 0"
      description="请从左侧字段库拖拽字段到此处构建检索条件"
      :image-size="100"
    />

    <!-- 拖放接收区 -->
    <div
      class="drop-zone"
      :class="{ 'drag-over': isDragOver }"
      @dragover.prevent="onDragOver"
      @dragleave="onDragLeave"
      @drop="onDrop"
    >
      <el-icon v-if="conditions.length > 0"><Plus /></el-icon>
      <span>拖拽字段到此处添加条件</span>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { Close, Plus } from '@element-plus/icons-vue'

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:modelValue'])

const conditions = ref([...props.modelValue])
const isDragOver = ref(false)

// 监听外部值变化
watch(() => props.modelValue, (newVal) => {
  conditions.value = [...newVal]
}, { deep: true })

// 监听内部值变化
watch(conditions, (newVal) => {
  emit('update:modelValue', newVal)
}, { deep: true })

// 获取字段类型
function getFieldType(field) {
  if (field.includes('年') || field.includes('月') || field.includes('日') || field.includes('旬空')) {
    return ''
  }
  if (field.includes('卦') || field.includes('宫')) {
    return 'success'
  }
  if (field.includes('爻') || field.includes('六亲') || field.includes('六神') || field.includes('地支')) {
    return 'primary'
  }
  if (field.includes('禄') || field.includes('马') || field.includes('刃') || field.includes('花')) {
    return 'danger'
  }
  if (field.includes('相') || field.includes('生') || field.includes('克') || field.includes('合') || field.includes('冲')) {
    return 'warning'
  }
  return 'info'
}

// 获取可用运算符
function getAvailableOperators(condition) {
  const baseOperators = [
    { value: '=', label: '=' },
    { value: '≠', label: '≠' }
  ]

  const stringOperators = [
    { value: '包含', label: '包含' },
    { value: '不包含', label: '不包含' }
  ]

  const numberOperators = [
    { value: '>', label: '>' },
    { value: '<', label: '<' },
    { value: '≥', label: '≥' },
    { value: '≤', label: '≤' }
  ]

  const relationOperators = [
    { value: '与', label: '与（字段关系）' },
    { value: 'WITH', label: 'WITH（存在性）' }
  ]

  let operators = [...baseOperators]

  // 数值类型添加数值运算符
  if (condition.valueType === 'number') {
    operators = [...operators, ...numberOperators]
  }

  // 字符串类型添加包含运算符
  if (condition.valueType === 'string' || condition.inputType === 'input') {
    operators = [...operators, ...stringOperators]
  }

  // 复合字段添加关系运算符
  if (condition.inputType === 'compound' || condition.category === 'yao') {
    operators = [...operators, ...relationOperators]
  }

  return operators
}

// 判断是否需要值输入
function needValueInput(condition) {
  return condition.operator && condition.operator !== 'WITH'
}

// 获取复合字段选项
function getCompoundOptions(condition) {
  // 根据复合字段的子属性类型返回对应选项
  if (condition.key?.includes('liuqin')) {
    return [
      { value: '父母', label: '父母' },
      { value: '官鬼', label: '官鬼' },
      { value: '子孙', label: '子孙' },
      { value: '妻财', label: '妻财' },
      { value: '兄弟', label: '兄弟' }
    ]
  }
  if (condition.key?.includes('dizhi')) {
    return ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
      .map(d => ({ value: d, label: d }))
  }
  if (condition.key?.includes('liushen')) {
    return ['青龙', '朱雀', '勾陈', '螣蛇', '白虎', '玄武']
      .map(l => ({ value: l, label: l }))
  }
  if (condition.key?.includes('wuxing')) {
    return ['金', '木', '水', '火', '土']
      .map(w => ({ value: w, label: w }))
  }
  return []
}

// 运算符变化处理
function onOperatorChange(condition) {
  // 清空不相关的值
  if (condition.operator === 'WITH') {
    condition.value = null
    condition.subValue = null
  }
}

// 移除条件
function removeCondition(index) {
  conditions.value.splice(index, 1)
}

// 拖拽处理
function onDragOver() {
  isDragOver.value = true
}

function onDragLeave() {
  isDragOver.value = false
}

function onDrop(event) {
  isDragOver.value = false
  const fieldData = event.dataTransfer.getData('field')
  if (fieldData) {
    try {
      const field = JSON.parse(fieldData)
      addCondition(field)
    } catch (e) {
      console.error('解析字段数据失败:', e)
    }
  }
}

// 添加条件
function addCondition(field) {
  const newCondition = {
    key: field.key,
    field: field.key,
    fieldLabel: field.label,
    category: field.category,
    inputType: field.inputType,
    valueType: field.valueType || 'string',
    options: field.options || [],
    operator: '=',
    value: null,
    subValue: null,
    relationType: null,
    targetField: null,
    logic: 'and',
    error: null,
    type: field.type
  }
  conditions.value.push(newCondition)
}

// 暴露方法供外部调用
defineExpose({
  addCondition,
  getConditions: () => conditions.value,
  clearConditions: () => { conditions.value = [] }
})
</script>

<style scoped>
.condition-builder {
  min-height: 300px;
}

.conditions-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.logic-operator {
  display: flex;
  justify-content: center;
  margin: 5px 0;
}

.condition-card {
  margin-bottom: 0;
}

.condition-card.has-error {
  border-color: var(--el-color-danger);
}

.condition-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.condition-body {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
}

.operator-select {
  width: 120px;
}

.value-select,
.value-input,
.relation-select,
.target-select {
  flex: 1;
  min-width: 150px;
}

.error-message {
  color: var(--el-color-danger);
  font-size: 12px;
  margin-top: 8px;
}

.drop-zone {
  border: 2px dashed var(--el-border-color);
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  color: var(--el-text-color-placeholder);
  margin-top: 10px;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.drop-zone.drag-over {
  border-color: var(--el-color-primary);
  background-color: var(--el-color-primary-light-9);
  color: var(--el-color-primary);
}

.drop-zone:hover {
  border-color: var(--el-color-primary-light-3);
}
</style>
