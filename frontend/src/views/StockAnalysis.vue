<template>
  <div class="stock-analysis">
    <!-- 顶部搜索区 -->
    <div class="search-section">
      <el-autocomplete
        v-model="searchKeyword"
        :fetch-suggestions="searchStockImpl"
        placeholder="输入股票名称或代码搜索..."
        @select="handleSelectStock"
        clearable
        style="width: 300px"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
        <template #default="{ item }">
          <span>{{ item.name }}</span>
          <span style="color: #909399; margin-left: 10px">{{ item.code }}</span>
        </template>
      </el-autocomplete>

      <el-date-picker
        v-model="dateRange"
        type="daterange"
        range-separator="至"
        start-placeholder="开始日期"
        end-placeholder="结束日期"
        :shortcuts="dateShortcuts"
        style="margin-left: 20px"
      />

      <el-button type="primary" @click="loadData" :loading="loading" style="margin-left: 20px">
        加载K线
      </el-button>

      <el-button @click="openNewWindow" :disabled="!currentStock.code">
        <el-icon><Monitor /></el-icon>
        新窗口
      </el-button>
    </div>

    <!-- K线图区域 -->
    <div class="chart-section">
      <KlineChart
        ref="klineChartRef"
        :kline-data="klineData"
        :guali-mapping="gualiMapping"
        :stock-name="currentStock.name"
        :stock-code="currentStock.code"
        height="600px"
        @dblclick="handleKlineDblClick"
        @ready="onChartReady"
      />
    </div>

    <!-- 状态栏 -->
    <div class="status-bar">
      <span v-if="currentStock.code">
        当前股票: {{ currentStock.name }} ({{ currentStock.code }})
      </span>
      <span v-if="klineData.length > 0">
        | K线数据: {{ klineData.length }} 条
      </span>
      <span v-if="Object.keys(gualiMapping).length > 0">
        | 匹配卦例: {{ Object.keys(gualiMapping).length }} 个
      </span>
    </div>

    <!-- 分时图浮窗 -->
    <IntradayChart
      v-model="showIntraday"
      :stock-code="currentStock.code"
      :stock-name="currentStock.name"
      :date="selectedDate"
    />

    <!-- 卦例浮窗 -->
    <GualiFloatPanel
      v-model="showGualiPanel"
      :guali-group="selectedGualiGroup"
      :date="selectedDate"
      @yanqing-updated="handleYanqingUpdated"
      @primary-changed="handlePrimaryChanged"
      @zhanduan-updated="handleZhanDuanUpdated"
    />
  </div>
</template>

<script setup>
/**
 * 股票分析页面
 *
 * 功能:
 * - 股票搜索
 * - K线图展示
 * - 卦例与K线关联
 * - 多窗口支持
 */
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search, Monitor } from '@element-plus/icons-vue'
import KlineChart from '@/components/Stock/KlineChart.vue'
import IntradayChart from '@/components/Stock/IntradayChart.vue'
import GualiFloatPanel from '@/components/Stock/GualiFloatPanel.vue'
import { searchStock, getKlineData, getGualiMapping } from '@/api'

const route = useRoute()

// 搜索相关
const searchKeyword = ref('')
const dateRange = ref([])
const currentStock = ref({ code: '', name: '' })

// 数据
const klineData = ref([])
const gualiMapping = ref({})
const loading = ref(false)

// 浮窗
const showIntraday = ref(false)
const showGualiPanel = ref(false)
const selectedDate = ref('')
const selectedGualiGroup = ref(null)

// 引用
const klineChartRef = ref(null)

// 日期快捷选项
const dateShortcuts = [
  {
    text: '最近1月',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 30 * 24 * 3600 * 1000)
      return [start, end]
    }
  },
  {
    text: '最近3月',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 90 * 24 * 3600 * 1000)
      return [start, end]
    }
  },
  {
    text: '最近6月',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 180 * 24 * 3600 * 1000)
      return [start, end]
    }
  },
  {
    text: '最近1年',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 365 * 24 * 3600 * 1000)
      return [start, end]
    }
  }
]

/**
 * 搜索股票建议
 */
async function searchStockImpl(keyword, cb) {
  if (!keyword) {
    cb([])
    return
  }

  try {
    const res = await searchStock(keyword)
    if (res.success && res.data) {
      cb(res.data)
    } else {
      cb([])
    }
  } catch (e) {
    cb([])
  }
}

/**
 * 选择股票
 */
function handleSelectStock(item) {
  currentStock.value = {
    code: item.code,
    name: item.name
  }
}

/**
 * 加载K线和卦例数据
 */
async function loadData() {
  if (!currentStock.value.code) {
    ElMessage.warning('请先选择股票')
    return
  }

  if (!dateRange.value || dateRange.value.length !== 2) {
    ElMessage.warning('请选择日期范围')
    return
  }

  loading.value = true
  klineData.value = []
  gualiMapping.value = {}

  try {
    const startDate = formatDate(dateRange.value[0])
    const endDate = formatDate(dateRange.value[1])

    // 并行加载K线数据和卦例映射
    const [klineRes, mappingRes] = await Promise.all([
      getKlineData({
        code: currentStock.value.code,
        start_date: startDate,
        end_date: endDate
      }),
      getGualiMapping({
        name: currentStock.value.name,
        start_date: startDate,
        end_date: endDate
      })
    ])

    if (klineRes.success && klineRes.data) {
      klineData.value = klineRes.data
    }

    if (mappingRes.success && mappingRes.data) {
      // 转换为按日期索引的对象（新数据格式）
      const mapping = {}
      mappingRes.data.forEach(group => {
        mapping[group.date] = group
      })
      gualiMapping.value = mapping
    }

    ElMessage.success(`加载完成: ${klineData.value.length}条K线, ${Object.keys(gualiMapping.value).length}个卦例`)

  } catch (e) {
    ElMessage.error('加载数据失败: ' + e.message)
  } finally {
    loading.value = false
  }
}

/**
 * 格式化日期
 */
function formatDate(date) {
  if (typeof date === 'string') return date
  const d = new Date(date)
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

/**
 * K线双击事件
 */
function handleKlineDblClick({ date, data, gualiGroup }) {
  selectedDate.value = date
  selectedGualiGroup.value = gualiGroup || null

  // 同时打开两个浮窗
  showIntraday.value = true
  showGualiPanel.value = true
}

/**
 * 图表准备完成
 */
function onChartReady() {
  console.log('K线图已准备完成')
}

/**
 * 占验情况更新
 */
function handleYanqingUpdated({ gualiId, status, note }) {
  // 更新本地映射
  if (selectedDate.value && gualiMapping.value[selectedDate.value]) {
    const group = gualiMapping.value[selectedDate.value]
    const guali = group.gualis.find(g => g.id === gualiId)
    if (guali) {
      guali.yanqing_status = status
    }
    // 如果更新的是基准卦例，也更新组的占验状态
    if (group.primary_guali_id === gualiId) {
      group.yanqing_status = status
    }
  }

  // 刷新K线图
  if (klineChartRef.value) {
    klineChartRef.value.resize()
  }
}

/**
 * 基准卦例变更
 */
function handlePrimaryChanged({ date, primaryGualiId }) {
  if (gualiMapping.value[date]) {
    const group = gualiMapping.value[date]
    group.primary_guali_id = primaryGualiId
    // 更新组的占验状态
    const primaryGuali = group.gualis.find(g => g.id === primaryGualiId)
    if (primaryGuali) {
      group.yanqing_status = primaryGuali.yanqing_status
    }
  }

  // 刷新K线图
  if (klineChartRef.value) {
    klineChartRef.value.resize()
  }
}

/**
 * 占断更新
 */
function handleZhanDuanUpdated({ gualiId, zhanDuan }) {
  // 更新本地映射
  if (selectedDate.value && gualiMapping.value[selectedDate.value]) {
    const group = gualiMapping.value[selectedDate.value]
    const guali = group.gualis.find(g => g.id === gualiId)
    if (guali) {
      guali.zhan_duan = zhanDuan
    }
  }
}

/**
 * 打开新窗口
 */
function openNewWindow() {
  const params = new URLSearchParams()
  if (currentStock.value.code) {
    params.set('code', currentStock.value.code)
    params.set('name', currentStock.value.name)
  }
  if (dateRange.value && dateRange.value.length === 2) {
    params.set('start', formatDate(dateRange.value[0]))
    params.set('end', formatDate(dateRange.value[1]))
  }

  const url = `${window.location.origin}/stock?${params.toString()}`
  window.open(url, '_blank', 'width=1400,height=900')
}

/**
 * 从URL参数加载
 */
function loadFromUrl() {
  const { code, name, start, end } = route.query

  if (code && name) {
    currentStock.value = {
      code,
      name
    }
    searchKeyword.value = name
  }

  if (start && end) {
    dateRange.value = [new Date(start), new Date(end)]
  }

  // 如果参数完整，自动加载数据
  if (code && name && start && end) {
    loadData()
  }
}

onMounted(() => {
  loadFromUrl()
})
</script>

<style scoped>
.stock-analysis {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: calc(100vh - 60px);
}

.search-section {
  display: flex;
  align-items: center;
  padding: 20px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.chart-section {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 20px;
  margin-bottom: 20px;
}

.status-bar {
  padding: 10px 20px;
  background-color: #fff;
  border-radius: 8px;
  font-size: 14px;
  color: #909399;
}

.status-bar span {
  margin-right: 10px;
}
</style>
