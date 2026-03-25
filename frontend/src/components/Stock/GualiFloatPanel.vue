<template>
  <el-dialog
    v-model="visible"
    :title="`卦例详情 - ${date}`"
    width="700px"
    :close-on-click-modal="false"
    draggable
    @close="handleClose"
  >
    <div class="guali-float-panel">
      <!-- 无卦例情况 -->
      <div v-if="!gualiGroup || !gualiGroup.gualis || gualiGroup.gualis.length === 0" class="no-guali">
        <el-empty description="当日无对应卦例" />
      </div>

      <!-- 有卦例情况 -->
      <div v-else class="guali-content">
        <!-- 多卦例提示和选择 -->
        <div v-if="gualiGroup.gualis.length > 1" class="multi-guali-header">
          <el-alert type="info" :closable="false" show-icon>
            <template #title>
              当日共有 {{ gualiGroup.gualis.length }} 个卦例
            </template>
          </el-alert>
          <div class="primary-select">
            <span>选择基准卦例（决定K线颜色）：</span>
            <el-select v-model="selectedPrimaryId" size="small" @change="onPrimaryChange">
              <el-option
                v-for="g in gualiGroup.gualis"
                :key="g.id"
                :label="`${g.zhan_wen || '无占问'} (ID:${g.id})`"
                :value="g.id"
              >
                <span>{{ g.zhan_wen || '无占问' }}</span>
                <span style="color: #909399; margin-left: 10px">ID:{{ g.id }}</span>
                <el-tag v-if="g.yanqing_status" :type="getYanqingTagType(g.yanqing_status)" size="small" style="margin-left: 10px">
                  {{ g.yanqing_status }}
                </el-tag>
              </el-option>
            </el-select>
          </div>
        </div>

        <!-- 主卦例信息 -->
        <div class="main-guali" v-if="currentGuali">
          <!-- 占问占断（可编辑） -->
          <div class="zhan-info">
            <div class="zhan-item">
              <span class="label">占问：</span>
              <span class="value">{{ currentGuali.zhan_wen || '无' }}</span>
            </div>
            <div class="zhan-item">
              <span class="label">占断：</span>
              <div class="zhanduan-edit">
                <el-input
                  v-if="editingZhanDuan"
                  v-model="editedZhanDuan"
                  type="textarea"
                  :rows="2"
                  placeholder="输入占断内容..."
                  size="small"
                />
                <span v-else class="value">{{ currentGuali.zhan_duan || '无' }}</span>
                <el-button
                  v-if="!editingZhanDuan"
                  type="primary"
                  link
                  size="small"
                  @click="startEditZhanDuan"
                >
                  编辑
                </el-button>
                <template v-else>
                  <el-button type="primary" size="small" @click="saveZhanDuan" :loading="savingZhanDuan">
                    保存
                  </el-button>
                  <el-button size="small" @click="cancelEditZhanDuan">取消</el-button>
                </template>
              </div>
            </div>
          </div>

          <!-- 时间信息 -->
          <div class="time-info">
            <span>{{ date }}</span>
            <span class="ganzhi" v-if="currentGuali.ganzhi">
              {{ currentGuali.ganzhi.year || '' }} {{ currentGuali.ganzhi.month || '' }} {{ currentGuali.ganzhi.day || '' }}
            </span>
          </div>

          <!-- 卦象信息 -->
          <div class="gua-info">
            <div class="gua-name">
              <span>本卦：{{ currentGuali.ben_gua_name || '-' }}</span>
              <span v-if="currentGuali.zhi_gua_name">之卦：{{ currentGuali.zhi_gua_name }}</span>
            </div>
            <div class="gongwei">
              <span>{{ currentGuali.gongwei || '-' }} {{ currentGuali.gongwei_index || '' }}</span>
            </div>
          </div>

          <!-- 占验情况标注 -->
          <div class="yanqing-section">
            <div class="yanqing-header">
              <span>占验情况：</span>
              <el-tag :type="getYanqingTagType(currentGuali.yanqing_status)">
                {{ currentGuali.yanqing_status || '未标注' }}
              </el-tag>
            </div>

            <div class="yanqing-actions">
              <el-radio-group v-model="selectedYanqing" size="small">
                <el-radio-button label="应验">应验</el-radio-button>
                <el-radio-button label="模糊">模糊</el-radio-button>
                <el-radio-button label="不验">不验</el-radio-button>
              </el-radio-group>
              <el-button
                type="primary"
                size="small"
                :loading="savingYanqing"
                @click="saveYanqing"
                :disabled="!selectedYanqing || selectedYanqing === currentGuali.yanqing_status"
              >
                保存
              </el-button>
            </div>

            <el-input
              v-model="yanqingNote"
              type="textarea"
              :rows="2"
              placeholder="添加备注..."
              style="margin-top: 10px"
            />
          </div>

          <!-- 查看详情按钮 -->
          <div class="actions">
            <el-button type="primary" @click="goToDetail(currentGuali.id)">
              查看完整详情
            </el-button>
          </div>
        </div>

        <!-- 其他卦例列表（可展开） -->
        <div v-if="gualiGroup.gualis.length > 1" class="other-gualis">
          <el-collapse v-model="activeCollapse">
            <el-collapse-item name="other">
              <template #title>
                <span class="collapse-title">
                  其他卦例 ({{ otherGualis.length }}个)
                </span>
              </template>
              <div class="other-guali-list">
                <div
                  v-for="guali in otherGualis"
                  :key="guali.id"
                  class="other-guali-item"
                >
                  <div class="guali-summary">
                    <div class="summary-row">
                      <span class="guali-id">ID: {{ guali.id }}</span>
                      <el-tag :type="getYanqingTagType(guali.yanqing_status)" size="small">
                        {{ guali.yanqing_status || '未标注' }}
                      </el-tag>
                    </div>
                    <div class="summary-row">
                      <span class="label">占问：</span>
                      <span>{{ guali.zhan_wen || '无' }}</span>
                    </div>
                    <div class="summary-row zhanduan-row">
                      <span class="label">占断：</span>
                      <div class="zhanduan-cell">
                        <el-input
                          v-if="editingOtherId === guali.id"
                          v-model="editingOtherZhanDuan"
                          type="textarea"
                          :rows="1"
                          size="small"
                        />
                        <span v-else>{{ guali.zhan_duan || '无' }}</span>
                      </div>
                      <el-button
                        v-if="editingOtherId !== guali.id"
                        type="primary"
                        link
                        size="small"
                        @click="startEditOther(guali)"
                      >
                        编辑
                      </el-button>
                      <template v-else>
                        <el-button type="primary" size="small" @click="saveOtherZhanDuan(guali.id)" :loading="savingOther">
                          保存
                        </el-button>
                        <el-button size="small" @click="cancelEditOther">取消</el-button>
                      </template>
                    </div>
                    <div class="summary-row">
                      <span class="label">卦象：</span>
                      <span>{{ guali.ben_gua_name }}{{ guali.zhi_gua_name ? ' → ' + guali.zhi_gua_name : '' }}</span>
                    </div>
                    <div class="summary-actions">
                      <el-button type="primary" size="small" @click="goToDetail(guali.id)">
                        查看详情
                      </el-button>
                      <el-button size="small" @click="setAsPrimary(guali)">
                        设为基准
                      </el-button>
                    </div>
                  </div>
                </div>
              </div>
            </el-collapse-item>
          </el-collapse>
        </div>
      </div>
    </div>
  </el-dialog>
</template>

<script setup>
/**
 * 卦例浮窗组件
 *
 * 功能：
 * - 显示选中日期对应的所有卦例
 * - 支持多卦例显示，用户选择基准卦例决定K线颜色
 * - 支持编辑占断字段
 * - 支持修改占验情况
 */
import { ref, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { annotateYanqing, updateGuali } from '@/api'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  // 卦例组数据（包含多个卦例）
  gualiGroup: {
    type: Object,
    default: null
  },
  date: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue', 'close', 'yanqing-updated', 'primary-changed', 'zhanduan-updated'])

const router = useRouter()
const visible = ref(props.modelValue)
const selectedYanqing = ref('')
const yanqingNote = ref('')
const savingYanqing = ref(false)
const selectedPrimaryId = ref(null)
const activeCollapse = ref([])

// 占断编辑相关
const editingZhanDuan = ref(false)
const editedZhanDuan = ref('')
const savingZhanDuan = ref(false)

// 其他卦例编辑相关
const editingOtherId = ref(null)
const editingOtherZhanDuan = ref('')
const savingOther = ref(false)

// 当前显示的主卦例
const currentGuali = computed(() => {
  if (!props.gualiGroup?.gualis) return null
  const id = selectedPrimaryId.value || props.gualiGroup.primary_guali_id
  return props.gualiGroup.gualis.find(g => g.id === id) || props.gualiGroup.gualis[0]
})

// 其他卦例列表（排除主卦例）
const otherGualis = computed(() => {
  if (!props.gualiGroup?.gualis) return []
  const currentId = currentGuali.value?.id
  return props.gualiGroup.gualis.filter(g => g.id !== currentId)
})

/**
 * 获取占验标签类型
 */
function getYanqingTagType(status) {
  const types = {
    '应验': 'success',
    '模糊': 'warning',
    '不验': 'danger'
  }
  return types[status] || 'info'
}

/**
 * 开始编辑占断
 */
function startEditZhanDuan() {
  if (currentGuali.value) {
    editedZhanDuan.value = currentGuali.value.zhan_duan || ''
    editingZhanDuan.value = true
  }
}

/**
 * 取消编辑占断
 */
function cancelEditZhanDuan() {
  editingZhanDuan.value = false
  editedZhanDuan.value = ''
}

/**
 * 保存占断
 */
async function saveZhanDuan() {
  if (!currentGuali.value) return

  savingZhanDuan.value = true
  try {
    await updateGuali(currentGuali.value.id, { zhan_duan: editedZhanDuan.value })
    ElMessage.success('占断已保存')

    // 更新本地数据
    currentGuali.value.zhan_duan = editedZhanDuan.value

    // 通知父组件
    emit('zhanduan-updated', {
      gualiId: currentGuali.value.id,
      zhanDuan: editedZhanDuan.value
    })

    editingZhanDuan.value = false
  } catch (e) {
    ElMessage.error('保存失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    savingZhanDuan.value = false
  }
}

/**
 * 开始编辑其他卦例的占断
 */
function startEditOther(guali) {
  editingOtherId.value = guali.id
  editingOtherZhanDuan.value = guali.zhan_duan || ''
}

/**
 * 取消编辑其他卦例
 */
function cancelEditOther() {
  editingOtherId.value = null
  editingOtherZhanDuan.value = ''
}

/**
 * 保存其他卦例的占断
 */
async function saveOtherZhanDuan(gualiId) {
  savingOther.value = true
  try {
    await updateGuali(gualiId, { zhan_duan: editingOtherZhanDuan.value })
    ElMessage.success('占断已保存')

    // 更新本地数据
    const guali = props.gualiGroup.gualis.find(g => g.id === gualiId)
    if (guali) {
      guali.zhan_duan = editingOtherZhanDuan.value
    }

    emit('zhanduan-updated', {
      gualiId: gualiId,
      zhanDuan: editingOtherZhanDuan.value
    })

    editingOtherId.value = null
    editingOtherZhanDuan.value = ''
  } catch (e) {
    ElMessage.error('保存失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    savingOther.value = false
  }
}

/**
 * 保存占验情况
 */
async function saveYanqing() {
  if (!currentGuali.value || !selectedYanqing.value) return

  savingYanqing.value = true
  try {
    await annotateYanqing({
      guali_id: currentGuali.value.id,
      status: selectedYanqing.value,
      note: yanqingNote.value
    })

    ElMessage.success('占验情况已保存')

    // 更新本地状态
    currentGuali.value.yanqing_status = selectedYanqing.value

    // 通知父组件
    emit('yanqing-updated', {
      gualiId: currentGuali.value.id,
      status: selectedYanqing.value,
      note: yanqingNote.value
    })
  } catch (e) {
    ElMessage.error('保存失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    savingYanqing.value = false
  }
}

/**
 * 基准卦例变更
 */
function onPrimaryChange(gualiId) {
  emit('primary-changed', {
    date: props.date,
    primaryGualiId: gualiId
  })
}

/**
 * 设置其他卦例为基准
 */
function setAsPrimary(guali) {
  selectedPrimaryId.value = guali.id
  onPrimaryChange(guali.id)
  ElMessage.success('已设置为基准卦例')
}

/**
 * 跳转到详情页
 */
function goToDetail(gualiId) {
  router.push(`/guali/${gualiId}`)
  handleClose()
}

/**
 * 关闭弹窗
 */
function handleClose() {
  emit('update:modelValue', false)
  emit('close')
}

// 监听visible变化
watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val && props.gualiGroup) {
    selectedPrimaryId.value = props.gualiGroup.primary_guali_id
    if (currentGuali.value) {
      selectedYanqing.value = currentGuali.value.yanqing_status || ''
      yanqingNote.value = ''
    }
    editingZhanDuan.value = false
    editingOtherId.value = null
    activeCollapse.value = []
  }
})

watch(visible, (val) => {
  emit('update:modelValue', val)
})
</script>

<style scoped>
.guali-float-panel {
  max-height: 70vh;
  overflow-y: auto;
}

.no-guali {
  padding: 40px 0;
}

.guali-content {
  padding: 10px 0;
}

.multi-guali-header {
  margin-bottom: 15px;
}

.primary-select {
  margin-top: 10px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.primary-select span {
  color: #606266;
  font-size: 14px;
}

.main-guali {
  padding: 10px;
  background-color: #fafafa;
  border-radius: 8px;
}

.zhan-info {
  margin-bottom: 15px;
}

.zhan-item {
  margin-bottom: 8px;
}

.zhan-item .label {
  font-weight: bold;
  color: #303133;
}

.zhan-item .value {
  color: #606266;
}

.zhanduan-edit {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin-top: 5px;
}

.zhanduan-edit .value {
  flex: 1;
}

.time-info {
  display: flex;
  justify-content: space-between;
  padding: 10px;
  background-color: #f0f2f5;
  border-radius: 4px;
  margin-bottom: 15px;
}

.time-info .ganzhi {
  color: #909399;
}

.gua-info {
  margin-bottom: 15px;
}

.gua-name {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 5px;
}

.gua-name span {
  margin-right: 20px;
}

.gongwei {
  color: #909399;
  font-size: 14px;
}

.yanqing-section {
  padding: 15px;
  background-color: #fff;
  border-radius: 4px;
  margin-bottom: 15px;
  border: 1px solid #e4e7ed;
}

.yanqing-header {
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.yanqing-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.actions {
  text-align: center;
  margin-top: 15px;
}

.other-gualis {
  margin-top: 20px;
  border-top: 1px solid #e4e7ed;
  padding-top: 15px;
}

.collapse-title {
  font-weight: bold;
  color: #409EFF;
}

.other-guali-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.other-guali-item {
  padding: 15px;
  background-color: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
}

.guali-summary {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.summary-row {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
}

.summary-row .label {
  color: #909399;
  min-width: 50px;
}

.summary-row.zhanduan-row {
  align-items: flex-start;
}

.zhanduan-cell {
  flex: 1;
}

.guali-id {
  color: #909399;
  font-size: 12px;
}

.summary-actions {
  margin-top: 10px;
  display: flex;
  gap: 10px;
}
</style>
