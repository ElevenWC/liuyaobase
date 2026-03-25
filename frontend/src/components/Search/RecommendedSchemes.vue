<template>
  <div class="recommended-schemes">
    <div class="header">
      <span class="title">推荐方案</span>
      <el-button type="primary" size="small" @click="showSaveDialog = true">
        保存当前方案
      </el-button>
    </div>

    <el-divider />

    <!-- 预设方案 -->
    <div class="scheme-section">
      <div class="section-title">预设方案</div>
      <div class="scheme-list">
        <el-tag
          v-for="scheme in presetSchemes"
          :key="scheme.id"
          class="scheme-tag"
          @click="loadScheme(scheme)"
        >
          {{ scheme.name }}
        </el-tag>
      </div>
    </div>

    <!-- 用户自定义方案 -->
    <div class="scheme-section" v-if="customSchemes.length > 0">
      <div class="section-title">自定义方案</div>
      <div class="scheme-list">
        <el-tag
          v-for="scheme in customSchemes"
          :key="scheme.id"
          class="scheme-tag custom"
          closable
          @click="loadScheme(scheme)"
          @close="deleteScheme(scheme.id)"
        >
          {{ scheme.name }}
        </el-tag>
      </div>
    </div>

    <!-- 方案详情对话框 -->
    <el-dialog
      v-model="showSchemeDetail"
      :title="currentScheme?.name"
      width="500px"
    >
      <div v-if="currentScheme" class="scheme-detail">
        <div class="detail-item" v-for="(condition, index) in currentScheme.conditions" :key="index">
          <span class="logic" v-if="index > 0">{{ condition.logic?.toUpperCase() || 'AND' }}</span>
          <el-tag size="small">{{ condition.fieldLabel }}</el-tag>
          <span class="operator">{{ condition.operator }}</span>
          <span class="value">{{ formatConditionValue(condition) }}</span>
        </div>
      </div>
      <template #footer>
        <el-button @click="showSchemeDetail = false">取消</el-button>
        <el-button type="primary" @click="confirmLoadScheme">加载方案</el-button>
      </template>
    </el-dialog>

    <!-- 保存方案对话框 -->
    <el-dialog
      v-model="showSaveDialog"
      title="保存当前方案"
      width="400px"
    >
      <el-form label-width="80px">
        <el-form-item label="方案名称">
          <el-input v-model="newSchemeName" placeholder="请输入方案名称" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showSaveDialog = false">取消</el-button>
        <el-button type="primary" @click="saveCurrentScheme" :disabled="!newSchemeName">
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  currentConditions: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['load-scheme'])

const showSchemeDetail = ref(false)
const showSaveDialog = ref(false)
const currentScheme = ref(null)
const newSchemeName = ref('')

// 预设方案
const presetSchemes = ref([
  {
    id: 'preset_1',
    name: '世爻为子孙爻',
    preset: true,
    conditions: [
      { key: 'world_yao.liuqin', field: 'world_yao.liuqin', fieldLabel: '世爻.六亲', operator: '=', value: '子孙', logic: 'and' }
    ]
  },
  {
    id: 'preset_2',
    name: '带干禄且地支为卯',
    preset: true,
    conditions: [
      { key: 'ganlu', field: 'ganlu', fieldLabel: '干禄', operator: '=', value: 'dai', logic: 'and' },
      { key: 'dizhi', field: 'dizhi', fieldLabel: '地支', operator: '=', value: '卯', logic: 'and' }
    ]
  },
  {
    id: 'preset_3',
    name: '六合卦且世爻为官鬼',
    preset: true,
    conditions: [
      { key: 'special_type', field: 'special_type', fieldLabel: '特殊类型', operator: '=', value: 'liuhe', logic: 'and' },
      { key: 'world_yao.liuqin', field: 'world_yao.liuqin', fieldLabel: '世爻.六亲', operator: '=', value: '官鬼', logic: 'and' }
    ]
  },
  {
    id: 'preset_4',
    name: '游魂卦',
    preset: true,
    conditions: [
      { key: 'gongwei_index', field: 'gongwei_index', fieldLabel: '宫位', operator: '=', value: '游魂', logic: 'and' }
    ]
  },
  {
    id: 'preset_5',
    name: '带伏神的卦例',
    preset: true,
    conditions: [
      { key: 'fushen_feishen', field: 'fushen_feishen', fieldLabel: '伏神飞神', operator: '=', value: 'has_fushen', logic: 'and' }
    ]
  },
  {
    id: 'preset_6',
    name: '易冒反吟',
    preset: true,
    conditions: [
      { key: 'fanyin_fuyin', field: 'fanyin_fuyin', fieldLabel: '反吟伏吟', operator: '=', value: 'yimao_fanyin', logic: 'and' }
    ]
  },
  {
    id: 'preset_7',
    name: '六冲卦',
    preset: true,
    conditions: [
      { key: 'special_type', field: 'special_type', fieldLabel: '特殊类型', operator: '=', value: 'liuchong', logic: 'and' }
    ]
  },
  {
    id: 'preset_8',
    name: '驿马和桃花',
    preset: true,
    conditions: [
      { key: 'yima', field: 'yima', fieldLabel: '驿马', operator: '=', value: 'is', logic: 'and' },
      { key: 'taohua', field: 'taohua', fieldLabel: '桃花', operator: '=', value: 'is', logic: 'and' }
    ]
  },
  {
    id: 'preset_9',
    name: '官鬼持世',
    preset: true,
    conditions: [
      { key: 'world_yao.liuqin', field: 'world_yao.liuqin', fieldLabel: '世爻.六亲', operator: '=', value: '官鬼', logic: 'and' }
    ]
  },
  {
    id: 'preset_10',
    name: '子孙爻被合',
    preset: true,
    conditions: [
      { key: 'zisun_yao.dizhi', field: 'zisun_yao.dizhi', fieldLabel: '子孙爻.地支', operator: '与', relationType: 'he', targetField: 'day_dizhi', logic: 'and' }
    ]
  },
  {
    id: 'preset_11',
    name: '日支与妻财爻相冲',
    preset: true,
    conditions: [
      { key: 'day_dizhi', field: 'day_dizhi', fieldLabel: '日支', operator: '与', relationType: 'chong', targetField: 'qicai_yao.dizhi', logic: 'and' }
    ]
  },
  {
    id: 'preset_12',
    name: '存在爻与日支相冲',
    preset: true,
    conditions: [
      { key: 'dizhi', field: 'dizhi', fieldLabel: '地支', operator: 'WITH', relationType: 'chong', targetField: 'day_dizhi', logic: 'and' }
    ]
  }
])

// 用户自定义方案
const customSchemes = ref([])

// 加载自定义方案
onMounted(() => {
  const saved = localStorage.getItem('customSearchSchemes')
  if (saved) {
    try {
      customSchemes.value = JSON.parse(saved)
    } catch (e) {
      console.error('加载自定义方案失败:', e)
    }
  }
})

// 加载方案
function loadScheme(scheme) {
  currentScheme.value = scheme
  showSchemeDetail.value = true
}

// 确认加载方案
function confirmLoadScheme() {
  if (currentScheme.value) {
    emit('load-scheme', currentScheme.value.conditions)
    showSchemeDetail.value = false
    ElMessage.success(`已加载方案: ${currentScheme.value.name}`)
  }
}

// 保存当前方案
function saveCurrentScheme() {
  if (!newSchemeName.value) {
    ElMessage.warning('请输入方案名称')
    return
  }

  if (props.currentConditions.length === 0) {
    ElMessage.warning('当前没有条件可保存')
    return
  }

  const newScheme = {
    id: `custom_${Date.now()}`,
    name: newSchemeName.value,
    preset: false,
    conditions: JSON.parse(JSON.stringify(props.currentConditions))
  }

  customSchemes.value.push(newScheme)
  localStorage.setItem('customSearchSchemes', JSON.stringify(customSchemes.value))

  showSaveDialog.value = false
  newSchemeName.value = ''
  ElMessage.success('方案保存成功')
}

// 删除自定义方案
function deleteScheme(id) {
  const index = customSchemes.value.findIndex(s => s.id === id)
  if (index > -1) {
    customSchemes.value.splice(index, 1)
    localStorage.setItem('customSearchSchemes', JSON.stringify(customSchemes.value))
    ElMessage.success('方案已删除')
  }
}

// 格式化条件值显示
function formatConditionValue(condition) {
  if (condition.operator === 'WITH') {
    return `存在与${condition.targetField}${getRelationLabel(condition.relationType)}`
  }
  if (condition.relationType) {
    return `与${condition.targetField}${getRelationLabel(condition.relationType)}`
  }
  return condition.subValue || condition.value || ''
}

// 获取关系标签
function getRelationLabel(type) {
  const labels = {
    he: '相合',
    chong: '相冲',
    sheng: '相生',
    ke: '相克'
  }
  return labels[type] || ''
}
</script>

<style scoped>
.recommended-schemes {
  padding: 10px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  font-weight: bold;
  font-size: 14px;
}

.scheme-section {
  margin-bottom: 15px;
}

.section-title {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-bottom: 8px;
}

.scheme-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.scheme-tag {
  cursor: pointer;
  transition: all 0.2s;
}

.scheme-tag:hover {
  transform: scale(1.05);
}

.scheme-tag.custom {
  background-color: var(--el-color-warning-light-5);
  border-color: var(--el-color-warning-light-3);
}

.scheme-detail {
  padding: 10px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  padding: 8px;
  background: var(--el-fill-color-light);
  border-radius: 4px;
}

.detail-item .logic {
  color: var(--el-color-primary);
  font-weight: bold;
  font-size: 12px;
}

.detail-item .operator {
  color: var(--el-color-success);
  font-weight: bold;
}

.detail-item .value {
  color: var(--el-text-color-primary);
}
</style>
