<template>
  <div class="kline-chart" ref="chartContainer">
    <div v-if="loading" class="loading-overlay">
      <el-icon class="is-loading"><Loading /></el-icon>
      <span>加载中...</span>
    </div>
    <div v-if="error" class="error-overlay">
      <el-icon><Warning /></el-icon>
      <span>{{ error }}</span>
    </div>
    <div ref="chartRef" class="chart-inner" :style="{ width: chartWidth, height: chartHeight }"></div>
  </div>
</template>

<script setup>
/**
 * K线图组件
 *
 * 功能:
 * - 显示股票日K线图（同花顺风格）
 * - 横轴双时间显示（公历 + 干支）
 * - 三种K线样式（无卦例/应验/模糊不验）
 * - 支持缩放和拖拽
 * - 双击显示详情浮窗
 */
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { Loading, Warning } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

const props = defineProps({
  // K线数据
  klineData: {
    type: Array,
    default: () => []
  },
  // 卦例映射数据（按日期）
  gualiMapping: {
    type: Object,
    default: () => ({})
  },
  // 图表宽度
  width: {
    type: String,
    default: '100%'
  },
  // 图表高度
  height: {
    type: String,
    default: '500px'
  },
  // 股票名称
  stockName: {
    type: String,
    default: ''
  },
  // 股票代码
  stockCode: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['dblclick', 'ready'])

const chartRef = ref(null)
const chartContainer = ref(null)
const loading = ref(false)
const error = ref('')
const chartWidth = ref(props.width)
const chartHeight = ref(props.height)
let chartInstance = null

// 干支时间转换函数（简化版，使用映射表）
const ganzhiCache = {}

/**
 * 获取日期对应的干支时间
 */
function getGanzhi(year, month, day) {
  const key = `${year}-${month}-${day}`
  if (ganzhiCache[key]) {
    return ganzhiCache[key]
  }
  // 这里需要调用后端接口获取干支，暂时返回占位
  // 实际应该在加载数据时由后端返回
  return ''
}

/**
 * 根据占验情况获取K线样式
 * @param {string} date - 日期
 * @param {Object} gualiGroup - 卦例组数据（包含多个卦例和基准卦例ID）
 * @returns {Object} 样式配置
 *   - type: 'hollow' | 'solid' | 'yellow'
 *   - borderColor: 边框颜色
 *   - fillColor: 填充颜色
 */
function getKlineStyle(date) {
  const gualiGroup = props.gualiMapping[date]
  if (!gualiGroup || !gualiGroup.gualis || gualiGroup.gualis.length === 0) {
    // 无对应卦例：空心
    return {
      type: 'hollow',
      borderColor: null,  // 使用默认红绿
      fillColor: 'transparent'
    }
  }

  // 使用基准卦例的占验状态
  const status = gualiGroup.yanqing_status
  if (status === '应验') {
    // 应验：实心
    return {
      type: 'solid',
      borderColor: null,
      fillColor: null  // 使用默认红绿
    }
  } else if (status === '模糊' || status === '不验') {
    // 模糊/不验：空心+黄色填充
    return {
      type: 'yellow',
      borderColor: null,
      fillColor: '#FFD700'  // 金黄色
    }
  }

  // 默认空心
  return {
    type: 'hollow',
    borderColor: null,
    fillColor: 'transparent'
  }
}

/**
 * 处理K线数据
 */
function processData() {
  if (!props.klineData || props.klineData.length === 0) {
    return { dates: [], kline: [], volumes: [], styles: [] }
  }

  const dates = []
  const kline = []
  const volumes = []
  const styles = []

  props.klineData.forEach(item => {
    // 日期
    const dateStr = item.date
    dates.push(dateStr)

    // K线数据 [open, close, low, high]
    kline.push([
      item.open,
      item.close,
      item.low,
      item.high
    ])

    // 成交量
    volumes.push(item.volume)

    // 样式
    styles.push(getKlineStyle(dateStr))
  })

  return { dates, kline, volumes, styles }
}

/**
 * 初始化图表
 */
function initChart() {
  if (!chartRef.value) return

  if (chartInstance) {
    chartInstance.dispose()
  }

  chartInstance = echarts.init(chartRef.value)

  // 双击事件
  chartInstance.on('dblclick', (params) => {
    if (params.seriesType === 'candlestick') {
      const dataIndex = params.dataIndex
      const date = props.klineData[dataIndex]?.date
      emit('dblclick', {
        date,
        dataIndex,
        data: props.klineData[dataIndex],
        gualiGroup: props.gualiMapping[date]
      })
    }
  })

  updateChart()
}

/**
 * 更新图表
 */
function updateChart() {
  if (!chartInstance) return

  const { dates, kline, volumes, styles } = processData()

  if (dates.length === 0) {
    chartInstance.clear()
    return
  }

  // 构建K线样式数据
  const klineDataWithStyle = kline.map((item, index) => {
    const style = styles[index]
    const isRise = item[1] >= item[0] // 收盘 >= 开盘 为涨
    const color = isRise ? '#FF4136' : '#2ECC40'  // 红涨绿跌

    if (style.type === 'yellow') {
      // 黄色填充
      return {
        value: item,
        itemStyle: {
          color: style.fillColor,
          color0: style.fillColor,
          borderColor: color,
          borderColor0: color
        }
      }
    } else if (style.type === 'solid') {
      // 实心
      return {
        value: item,
        itemStyle: {
          color: color,
          color0: color,
          borderColor: color,
          borderColor0: color
        }
      }
    } else {
      // 空心
      return {
        value: item,
        itemStyle: {
          color: 'transparent',
          color0: 'transparent',
          borderColor: color,
          borderColor0: color
        }
      }
    }
  })

  // 构建X轴标签（双行显示：公历 + 干支）
  const xAxisLabels = dates.map((date, index) => {
    const klineItem = props.klineData[index]
    const ganzhi = klineItem?.ganzhi
    if (ganzhi && (ganzhi.month || ganzhi.day)) {
      return `${date}\n${ganzhi.month || ''}${ganzhi.day || ''}`
    }
    return date
  })

  const option = {
    animation: false,
    title: {
      text: `${props.stockName} (${props.stockCode})`,
      left: 'center',
      top: 10,
      textStyle: {
        fontSize: 16,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      },
      formatter: function(params) {
        const klineParam = params.find(p => p.seriesName === 'K线')
        const volumeParam = params.find(p => p.seriesName === '成交量')

        if (!klineParam) return ''

        const data = klineParam.data
        const date = dates[klineParam.dataIndex]
        const klineItem = props.klineData[klineParam.dataIndex]
        const gualiGroup = props.gualiMapping[date]

        let html = `<div style="font-weight:bold">${date}</div>`

        // 显示干支时间
        if (klineItem?.ganzhi) {
          html += `<div style="color:#909399">${klineItem.ganzhi.month || ''} ${klineItem.ganzhi.day || ''}</div>`
        }

        html += `<div>开盘: ${data.value[0]}</div>`
        html += `<div>收盘: ${data.value[1]}</div>`
        html += `<div>最低: ${data.value[2]}</div>`
        html += `<div>最高: ${data.value[3]}</div>`
        if (volumeParam) {
          html += `<div>成交量: ${(volumeParam.data / 10000).toFixed(2)}万</div>`
        }

        // 显示卦例信息（支持多卦例）
        if (gualiGroup && gualiGroup.gualis && gualiGroup.gualis.length > 0) {
          const count = gualiGroup.gualis.length
          if (count === 1) {
            const guali = gualiGroup.gualis[0]
            html += `<div style="color:#409EFF;margin-top:5px">卦例: ${guali.zhan_wen || '无'}</div>`
            html += `<div>占验: ${guali.yanqing_status || '未标注'}</div>`
          } else {
            html += `<div style="color:#409EFF;margin-top:5px">卦例: ${count}个</div>`
            html += `<div>基准占验: ${gualiGroup.yanqing_status || '未标注'}</div>`
          }
        }
        return html
      }
    },
    legend: {
      data: ['K线', '成交量'],
      top: 40
    },
    grid: [
      {
        left: '10%',
        right: '8%',
        top: 80,
        height: '55%'
      },
      {
        left: '10%',
        right: '8%',
        top: '75%',
        height: '15%'
      }
    ],
    xAxis: [
      {
        type: 'category',
        data: xAxisLabels,
        boundaryGap: true,
        axisLine: { onZero: false },
        splitLine: { show: false },
        min: 'dataMin',
        max: 'dataMax',
        axisLabel: {
          interval: 'auto',
          formatter: function(value) {
            // 显示双行：公历日期 + 干支
            const lines = value.split('\n')
            if (lines.length >= 2) {
              const dateParts = lines[0].split('-')
              const dateStr = dateParts.length >= 3 ? `${dateParts[1]}-${dateParts[2]}` : lines[0]
              return `${dateStr}\n${lines[1]}`
            }
            return value
          }
        }
      },
      {
        type: 'category',
        gridIndex: 1,
        data: dates,
        boundaryGap: true,
        axisLine: { onZero: false },
        axisTick: { show: false },
        splitLine: { show: false },
        axisLabel: { show: false },
        min: 'dataMin',
        max: 'dataMax'
      }
    ],
    yAxis: [
      {
        scale: true,
        splitArea: {
          show: true
        }
      },
      {
        scale: true,
        gridIndex: 1,
        splitNumber: 2,
        axisLabel: { show: false },
        axisLine: { show: false },
        axisTick: { show: false },
        splitLine: { show: false }
      }
    ],
    dataZoom: [
      {
        type: 'inside',
        xAxisIndex: [0, 1],
        start: 70,
        end: 100
      },
      {
        show: true,
        xAxisIndex: [0, 1],
        type: 'slider',
        top: '92%',
        start: 70,
        end: 100
      }
    ],
    series: [
      {
        name: 'K线',
        type: 'candlestick',
        data: klineDataWithStyle,
        large: true,
        largeThreshold: 200
      },
      {
        name: '成交量',
        type: 'bar',
        xAxisIndex: 1,
        yAxisIndex: 1,
        data: volumes.map((v, i) => {
          const k = kline[i]
          const isRise = k[1] >= k[0]
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
  emit('ready')
}

/**
 * 处理窗口大小变化
 */
function handleResize() {
  if (chartInstance) {
    chartInstance.resize()
  }
}

// 监听数据变化
watch(() => props.klineData, () => {
  nextTick(() => {
    updateChart()
  })
}, { deep: true })

watch(() => props.gualiMapping, () => {
  nextTick(() => {
    updateChart()
  })
}, { deep: true })

watch(() => props.width, (val) => {
  chartWidth.value = val
  nextTick(handleResize)
})

watch(() => props.height, (val) => {
  chartHeight.value = val
  nextTick(handleResize)
})

onMounted(() => {
  initChart()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
})

// 暴露方法
defineExpose({
  resize: handleResize,
  clear: () => {
    if (chartInstance) {
      chartInstance.clear()
    }
  }
})
</script>

<style scoped>
.kline-chart {
  position: relative;
  width: 100%;
  min-height: 400px;
}

.chart-inner {
  width: 100%;
  height: 100%;
}

.loading-overlay,
.error-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background-color: rgba(255, 255, 255, 0.8);
  z-index: 10;
}

.loading-overlay .el-icon {
  font-size: 32px;
  margin-bottom: 10px;
}

.error-overlay {
  color: #F56C6C;
}

.error-overlay .el-icon {
  font-size: 32px;
  margin-bottom: 10px;
}
</style>
