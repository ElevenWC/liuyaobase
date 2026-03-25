<template>
  <el-card class="yanqing-annotation" shadow="hover">
    <template #header>
      <div class="card-header">
        <span>占验情况</span>
        <el-tag v-if="yanqing" :type="statusTagType" size="small">
          {{ yanqing.status }}
        </el-tag>
      </div>
    </template>

    <!-- 未标注状态 -->
    <div v-if="!yanqing && !isEditing" class="no-annotation">
      <el-empty description="暂无占验标注" :image-size="60">
        <el-button type="primary" @click="startEdit">
          添加标注
        </el-button>
      </el-empty>
    </div>

    <!-- 已标注状态 - 显示模式 -->
    <div v-else-if="yanqing && !isEditing" class="annotation-display">
      <el-descriptions :column="1" border size="small">
        <el-descriptions-item label="占验状态">
          <el-tag :type="statusTagType" size="small">
            {{ yanqing.status }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="备注说明">
          {{ yanqing.note || '无' }}
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">
          {{ formatTime(yanqing.created_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="更新时间">
          {{ formatTime(yanqing.updated_at) }}
        </el-descriptions-item>
      </el-descriptions>

      <div class="action-buttons">
        <el-button size="small" @click="startEdit">编辑</el-button>
        <el-popconfirm
          title="确定要删除此占验标注吗？"
          @confirm="handleDelete"
        >
          <template #reference>
            <el-button size="small" type="danger">删除</el-button>
          </template>
        </el-popconfirm>
      </div>
    </div>

    <!-- 编辑模式 -->
    <div v-else class="annotation-edit">
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="80px"
        size="small"
      >
        <el-form-item label="占验状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio-button label="应验">
              <el-icon><CircleCheck /></el-icon> 应验
            </el-radio-button>
            <el-radio-button label="模糊">
              <el-icon><QuestionFilled /></el-icon> 模糊
            </el-radio-button>
            <el-radio-button label="不验">
              <el-icon><CircleClose /></el-icon> 不验
            </el-radio-button>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="备注说明" prop="note">
          <el-input
            v-model="form.note"
            type="textarea"
            :rows="3"
            placeholder="请输入备注说明（可选）"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="loading">
            {{ yanqing ? '更新' : '提交' }}
          </el-button>
          <el-button @click="cancelEdit">取消</el-button>
        </el-form-item>
      </el-form>
    </div>
  </el-card>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { CircleCheck, QuestionFilled, CircleClose } from '@element-plus/icons-vue'
import { getYanqing, annotateYanqing, updateYanqing, deleteYanqing } from '@/api'

const props = defineProps({
  gualiId: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['updated'])

// 状态
const yanqing = ref(null)
const isEditing = ref(false)
const loading = ref(false)
const formRef = ref(null)

// 表单数据
const form = ref({
  status: '应验',
  note: ''
})

// 表单验证规则
const rules = {
  status: [
    { required: true, message: '请选择占验状态', trigger: 'change' }
  ]
}

// 计算属性 - 状态标签类型
const statusTagType = computed(() => {
  if (!yanqing.value) return 'info'
  switch (yanqing.value.status) {
    case '应验':
      return 'success'
    case '模糊':
      return 'warning'
    case '不验':
      return 'danger'
    default:
      return 'info'
  }
})

// 格式化时间
function formatTime(isoString) {
  if (!isoString) return '-'
  const date = new Date(isoString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 加载占验情况
async function loadYanqing() {
  try {
    const data = await getYanqing(props.gualiId)
    yanqing.value = data
  } catch (error) {
    // 404表示暂无标注，不显示错误
    if (error.response?.status !== 404) {
      console.error('加载占验情况失败:', error)
    }
    yanqing.value = null
  }
}

// 开始编辑
function startEdit() {
  if (yanqing.value) {
    form.value.status = yanqing.value.status
    form.value.note = yanqing.value.note || ''
  } else {
    form.value.status = '应验'
    form.value.note = ''
  }
  isEditing.value = true
}

// 取消编辑
function cancelEdit() {
  isEditing.value = false
  formRef.value?.resetFields()
}

// 提交表单
async function handleSubmit() {
  try {
    await formRef.value.validate()
  } catch {
    return
  }

  loading.value = true
  try {
    let data
    if (yanqing.value) {
      // 更新
      data = await updateYanqing(props.gualiId, {
        guali_id: props.gualiId,
        ...form.value
      })
    } else {
      // 创建
      data = await annotateYanqing({
        guali_id: props.gualiId,
        ...form.value
      })
    }

    yanqing.value = data
    isEditing.value = false
    ElMessage.success(yanqing.value ? '更新成功' : '标注成功')
    emit('updated', data)
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error(error.response?.data?.detail || '操作失败')
  } finally {
    loading.value = false
  }
}

// 删除标注
async function handleDelete() {
  try {
    await deleteYanqing(props.gualiId)
    yanqing.value = null
    ElMessage.success('删除成功')
    emit('updated', null)
  } catch (error) {
    console.error('删除失败:', error)
    ElMessage.error(error.response?.data?.detail || '删除失败')
  }
}

// 监听gualiId变化
watch(() => props.gualiId, () => {
  loadYanqing()
}, { immediate: true })

onMounted(() => {
  loadYanqing()
})
</script>

<style scoped>
.yanqing-annotation {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.no-annotation {
  padding: 20px 0;
  text-align: center;
}

.annotation-display {
  margin-bottom: 10px;
}

.action-buttons {
  margin-top: 15px;
  display: flex;
  gap: 10px;
}

.annotation-edit {
  padding: 10px 0;
}

:deep(.el-radio-button__inner) {
  display: flex;
  align-items: center;
  gap: 4px;
}
</style>
