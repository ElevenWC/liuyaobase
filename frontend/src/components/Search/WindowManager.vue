<template>
  <div class="window-manager">
    <el-dropdown trigger="click" @command="handleCommand">
      <el-button type="primary" size="small">
        <el-icon><Monitor /></el-icon>
        多窗检索
        <el-badge v-if="windowCount > 0" :value="windowCount" class="window-badge" />
      </el-button>
      <template #dropdown>
        <el-dropdown-menu>
          <el-dropdown-item command="newWindow">
            <el-icon><Plus /></el-icon>
            新建检索窗口
          </el-dropdown-item>
          <el-dropdown-item command="newWindowInherit" :disabled="!hasConditions">
            <el-icon><CopyDocument /></el-icon>
            新建窗口（继承条件）
          </el-dropdown-item>
          <el-dropdown-item divided command="compare" :disabled="windowCount < 1">
            <el-icon><DataAnalysis /></el-icon>
            对比模式
          </el-dropdown-item>
          <el-dropdown-item command="merge" :disabled="windowCount < 1">
            <el-icon><Operation /></el-icon>
            合并窗口条件
          </el-dropdown-item>
          <el-dropdown-item divided command="closeAll" :disabled="windowCount === 0">
            <el-icon><Close /></el-icon>
            关闭所有子窗口
          </el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>

    <!-- 窗口列表弹窗 -->
    <el-dialog
      v-model="windowListVisible"
      title="打开的检索窗口"
      width="500px"
    >
      <el-table :data="childWindows" empty-text="暂无其他检索窗口">
        <el-table-column prop="name" label="窗口名称" />
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button size="small" @click="focusWindow(row)">聚焦</el-button>
            <el-button size="small" type="danger" @click="closeWindow(row)">关闭</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Monitor, Plus, CopyDocument, DataAnalysis, Operation, Close } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const props = defineProps({
  conditions: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['compare', 'merge', 'conditions-update'])

// 子窗口列表
const childWindows = ref([])
const windowListVisible = ref(false)

// 窗口计数
const windowCount = computed(() => childWindows.value.length)

// 是否有条件
const hasConditions = computed(() => props.conditions && props.conditions.length > 0)

// 窗口ID前缀
const WINDOW_ID_PREFIX = 'search_window_'
const STORAGE_KEY = 'search_windows_registry'

// 生成唯一窗口ID
function generateWindowId() {
  return `${WINDOW_ID_PREFIX}${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}

// 获取当前窗口ID
const currentWindowId = ref(window.name || generateWindowId())

// 初始化
onMounted(() => {
  // 设置窗口名称
  if (!window.name) {
    window.name = currentWindowId.value
  }

  // 注册窗口
  registerWindow()

  // 监听来自其他窗口的消息
  window.addEventListener('message', handleMessage)

  // 监听窗口关闭
  window.addEventListener('beforeunload', unregisterWindow)

  // 定期同步窗口列表
  syncWindowList()
})

onUnmounted(() => {
  window.removeEventListener('message', handleMessage)
  window.removeEventListener('beforeunload', unregisterWindow)
  unregisterWindow()
})

// 注册窗口
function registerWindow() {
  try {
    const registry = getRegistry()
    const windowName = window.location.pathname.includes('/search') ? '检索窗口' : '主窗口'
    registry[currentWindowId.value] = {
      id: currentWindowId.value,
      name: `${windowName} (${new Date().toLocaleTimeString()})`,
      url: window.location.href,
      createdAt: Date.now()
    }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(registry))
  } catch (e) {
    console.error('注册窗口失败:', e)
  }
}

// 注销窗口
function unregisterWindow() {
  try {
    const registry = getRegistry()
    delete registry[currentWindowId.value]
    localStorage.setItem(STORAGE_KEY, JSON.stringify(registry))
  } catch (e) {
    console.error('注销窗口失败:', e)
  }
}

// 获取窗口注册表
function getRegistry() {
  try {
    const data = localStorage.getItem(STORAGE_KEY)
    return data ? JSON.parse(data) : {}
  } catch (e) {
    return {}
  }
}

// 同步窗口列表
function syncWindowList() {
  const registry = getRegistry()
  childWindows.value = Object.values(registry).filter(w => w.id !== currentWindowId.value)
}

// 处理命令
function handleCommand(command) {
  switch (command) {
    case 'newWindow':
      openNewWindow(false)
      break
    case 'newWindowInherit':
      openNewWindow(true)
      break
    case 'compare':
      emit('compare')
      break
    case 'merge':
      emit('merge')
      break
    case 'closeAll':
      closeAllWindows()
      break
  }
}

// 打开新窗口
function openNewWindow(inheritConditions) {
  let url = window.location.pathname

  if (inheritConditions && hasConditions.value) {
    const conditionParam = encodeURIComponent(JSON.stringify(props.conditions))
    url += `?condition=${conditionParam}`
  }

  const newWindow = window.open(url, generateWindowId(), 'width=1200,height=800')

  if (newWindow) {
    ElMessage.success('已打开新检索窗口')
    // 延迟同步窗口列表
    setTimeout(syncWindowList, 1000)
  } else {
    ElMessage.error('打开新窗口失败，请检查浏览器弹窗设置')
  }
}

// 聚焦窗口
function focusWindow(windowInfo) {
  // 由于安全限制，无法直接聚焦其他窗口
  // 这里只是打开URL
  window.open(windowInfo.url, windowInfo.id)
  windowListVisible.value = false
}

// 关闭窗口
function closeWindow(windowInfo) {
  // 无法直接关闭其他窗口，只能从注册表中移除
  try {
    const registry = getRegistry()
    delete registry[windowInfo.id]
    localStorage.setItem(STORAGE_KEY, JSON.stringify(registry))
    syncWindowList()
    ElMessage.success('已从列表中移除该窗口')
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

// 关闭所有子窗口
async function closeAllWindows() {
  try {
    await ElMessageBox.confirm('确定要关闭所有子窗口吗？', '提示', {
      type: 'warning'
    })

    // 广播关闭消息
    broadcastMessage({ type: 'close' })

    // 清空注册表（保留当前窗口）
    const registry = {}
    registry[currentWindowId.value] = getRegistry()[currentWindowId.value]
    localStorage.setItem(STORAGE_KEY, JSON.stringify(registry))

    syncWindowList()
    ElMessage.success('已发送关闭信号')
  } catch (e) {
    // 用户取消
  }
}

// 处理消息
function handleMessage(event) {
  // 安全检查
  if (event.origin !== window.location.origin) return

  const { type, data } = event.data || {}

  switch (type) {
    case 'conditions-update':
      emit('conditions-update', data)
      break
    case 'close':
      // 如果是子窗口，关闭自己
      if (window.opener) {
        window.close()
      }
      break
    case 'sync-request':
      // 响应同步请求
      syncWindowList()
      break
  }
}

// 广播消息
function broadcastMessage(message) {
  // 通过localStorage广播
  localStorage.setItem('search_broadcast', JSON.stringify({
    ...message,
    from: currentWindowId.value,
    timestamp: Date.now()
  }))
  // 清理
  setTimeout(() => localStorage.removeItem('search_broadcast'), 100)
}

// 发送条件更新
function sendConditionsUpdate(conditions) {
  broadcastMessage({
    type: 'conditions-update',
    data: conditions
  })
}

// 暴露方法
defineExpose({
  sendConditionsUpdate,
  syncWindowList,
  windowCount
})
</script>

<style scoped>
.window-manager {
  display: inline-block;
}

.window-badge {
  margin-left: 5px;
}

:deep(.el-badge__content) {
  transform: scale(0.8);
}
</style>
