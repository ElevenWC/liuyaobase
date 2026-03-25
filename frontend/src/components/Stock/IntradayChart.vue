<template>
  <el-dialog
    v-model="visible"
    :title="`分时图 - ${stockName} (${stockCode})`"
    width="800px"
    :close-on-click-modal="false"
    draggable
    @close="handleClose"
  >
    <div class="intraday-chart">
      <div v-if="loading" class="loading">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>加载中...</span>
      </div>
      <div v-else-if="error" class="error">
        <el-icon><Warning /></el-icon>
        <span>{{ error }}</span>
      </div>
      <div v-else>
        <div class="price-info">
          <span>开盘: {{ dayData.open }}</span>
          <span>收盘: {{ dayData.close }}</span>
          <span>最高: {{ dayData.high }}</span>
          <span>最低: {{ dayData.low }}</span>
        </div>
        <div ref="chartRef" class="chart-container"></div>
      </div>
    </div>
  </el-dialog>
</template>

<script setup>
/**
 * 分时图浮窗组件
 *
 * 显示当日分时走势图
 */
import { ref, watch, nextTick, onUnmounted } from 'vue'
import { Loading, Warning } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { getIntradayData } from '@/api'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  stockCode: {
    type: String,
    default: ''
  },
  stockName: {
    type: String,
    default: ''
  },
  date: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue', 'close'])

const visible = ref(props.modelValue)
const chartRef = ref(null)
const loading = ref(false)
const error = ref('')
const dayData = ref({
  open: 0,
  close: 0,
  high: 0,
  low: 0
})
let chartInstance = null

/**
 * 加载分时数据
 */
async function loadIntradayData() {
  if (!props.stockCode) return

  loading.value = true
  error.value = ''

  try {
    const res = await getIntradayData(props.stockCode)
    if (res.success && res.data && res.data.length > 0) {
      renderChart(res.data)

      // 计算当日价格信息
      const data = res.data
      dayData.value = {
        open: data[0]?.open || 0,
        close: data[data.length - 1]?.close || 0,
        high: Math.max(...data.map(d => d.high)),
        low: Math.min(...data.map(d => d.low))
      }
    } else {
      error.value = '暂无分时数据'
    }
  } catch (e) {
    error.value = e.message || '获取分时数据失败'
  } finally {
    loading.value = false
  }
}

/**
 * 渲染分时图
 */
function renderChart(data) {
  if (!chartRef.value) return

  if (chartInstance) {
    chartInstance.dispose()
  }

  chartInstance = echarts.init(chartRef.value)

  const times = data.map(d => d.time)
  const prices = data.map(d => d.close)
  const volumes = data.map(d => d.volume)

  // 计算基准价格（开盘价）
  const basePrice = data[0]?.open || prices[0]

  const option = {
    animation: false,
    tooltip: {
      trigger: 'axis',
      formatter: function(params) {
        const priceParam = params.find(p => p.seriesName === '价格')
        const volumeParam = params.find(p => p.seriesName === '成交量')

        let html = `<div>${priceParam?.axisValue}</div>`
        if (priceParam) {
          html += `<div>价格: ${priceParam.data}</div>`
        }
        if (volumeParam) {
          html += `<div>成交量: ${(volumeParam.data / 10000).toFixed(2)}万</div>`
        }
        return html
      }
    },
    grid: [
      {
        left: '10%',
        right: '8%',
        top: 40,
        height: '50%'
      },
      {
        left: '10%',
        right: '8%',
        top: '68%',
        height: '20%'
      }
    ],
    xAxis: [
      {
        type: 'category',
        data: times,
        boundaryGap: false,
        axisLabel: {
          interval: 30,
          rotate: 45
        }
      },
      {
        type: 'category',
        data: times,
        gridIndex: 1,
        boundaryGap: false,
        axisLabel: { show: false }
      }
    ],
    yAxis: [
      {
        scale: true,
        splitLine: {
          show: true,
          lineStyle: {
            type: 'dashed'
          }
        }
      },
      {
        scale: true,
        gridIndex: 1,
        axisLabel: { show: false },
        splitLine: { show: false }
      }
    ],
    series: [
      {
        name: '价格',
        type: 'line',
        data: prices,
        smooth: true,
        lineStyle: {
          color: '#409EFF',
          width: 1
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
              { offset: 1, color: 'rgba(64, 158, 255, 0.05)' }
            ]
          }
        },
        markLine: {
          silent: true,
          data: [
            {
              yAxis: basePrice,
              lineStyle: {
                color: '#909399',
                type: 'dashed'
              },
              label: {
                formatter: '基准'
              }
            }
          ]
        }
      },
      {
        name: '成交量',
        type: 'bar',
        xAxisIndex: 1,
        yAxisIndex: 1,
        data: volumes.map((v, i) => {
          const prevPrice = i > 0 ? prices[i - 1] : basePrice
          const currPrice = prices[i]
          const isRise = currPrice >= prevPrice
          return {
            value: v,
            itemStyle: {
              color: isRise ? '#FF4136' : '#2ECC40'
            }
          }
        })
      }
    ]
  }

  chartInstance.setOption(option)
}

/**
 * 关闭弹窗
 */
function handleClose() {
  emit('update:modelValue', false)
  emit('close')
}

/**
 * 处理窗口大小变化
 */
function handleResize() {
  if (chartInstance) {
    chartInstance.resize()
  }
}

// 监听visible变化
watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val && props.stockCode) {
    nextTick(() => {
      loadIntradayData()
    })
  }
})

watch(visible, (val) => {
  emit('update:modelValue', val)
})

// 监听股票代码变化
watch(() => props.stockCode, (code) => {
  if (visible.value && code) {
    loadIntradayData()
  }
})

onUnmounted(() => {
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
})

defineExpose({
  resize: handleResize
})
</script>

<style scoped>
.intraday-chart {
  min-height: 400px;
}

.loading,
.error {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 400px;
}

.loading .el-icon,
.error .el-icon {
  font-size: 32px;
  margin-bottom: 10px;
}

.error {
  color: #F56C6C;
}

.price-info {
  display: flex;
  justify-content: space-around;
  padding: 10px;
  margin-bottom: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.price-info span {
  font-size: 14px;
  color: #606266;
}

.chart-container {
  width: 100%;
  height: 350px;
}
</style>
