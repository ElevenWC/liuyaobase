<script setup>
import { ref, watch, computed } from 'vue'
import { nextZIndex } from '../../shared/zCounter.js'
import { fetchCalendar } from '../../api/index.js'

const props = defineProps({
  zhanwenTime: { type: String, required: true },
  visible: { type: Boolean, default: true },
})

const emit = defineEmits(['close'])

const WEEKDAYS = ['一', '二', '三', '四', '五', '六', '日']

const posX = ref(window.innerWidth / 2 - 170)
const posY = ref(window.innerHeight / 2 - 220)
const zIndex = ref(nextZIndex())
const dragStart = ref({ x: 0, y: 0 })
const dragging = ref(false)

// 当前展示的年月
const zt = new Date(props.zhanwenTime)
const selYear = ref(zt.getFullYear())
const selMonth = ref(zt.getMonth() + 1)
const selDay = ref(zt.getDate())
const selectedDate = computed(() => `${selYear.value}-${String(selMonth.value).padStart(2, '0')}-${String(selDay.value).padStart(2, '0')}`)

const calendarYear = ref(zt.getFullYear())
const calendarMonth = ref(zt.getMonth() + 1)
const calendarData = ref(null)
const loading = ref(false)

// 选中日期的干支（从日历数据中提取）
const selectedGanzhi = computed(() => {
  if (!calendarData.value) return { year: '', month: '', day: '' }
  const d = calendarData.value.days.find(d => d.day === selDay.value)
  return d ? { year: d.year_ganzhi, month: d.month_ganzhi, day: d.day_ganzhi } : { year: '', month: '', day: '' }
})

async function loadMonth() {
  loading.value = true
  try {
    const res = await fetchCalendar(calendarYear.value, calendarMonth.value)
    if (res.data.code === 200) calendarData.value = res.data.data
  } catch { /* ok */ }
  finally { loading.value = false }
}

watch([calendarYear, calendarMonth], loadMonth, { immediate: true })
watch(() => props.zhanwenTime, (t) => {
  const d = new Date(t)
  selYear.value = d.getFullYear(); selMonth.value = d.getMonth() + 1; selDay.value = d.getDate()
  calendarYear.value = d.getFullYear(); calendarMonth.value = d.getMonth() + 1
})

function selectDate(year, month, day) {
  selYear.value = year; selMonth.value = month; selDay.value = day
  calendarYear.value = year; calendarMonth.value = month
}

function backToZhanwen() {
  const d = new Date(props.zhanwenTime)
  selYear.value = d.getFullYear(); selMonth.value = d.getMonth() + 1; selDay.value = d.getDate()
  calendarYear.value = d.getFullYear(); calendarMonth.value = d.getMonth() + 1
}

function prevMonth() { if (calendarMonth.value === 1) { calendarYear.value--; calendarMonth.value = 12 } else { calendarMonth.value-- } }
function nextMonth() { if (calendarMonth.value === 12) { calendarYear.value++; calendarMonth.value = 1 } else { calendarMonth.value++ } }

// ── 拖动 ──
function onMouseDown(e) {
  dragStart.value = { x: e.clientX - posX.value, y: e.clientY - posY.value }
  zIndex.value = nextZIndex()
  dragging.value = true
  const onMove = (ev) => {
    posX.value = Math.max(0, Math.min(ev.clientX - dragStart.value.x, window.innerWidth - 360))
    posY.value = Math.max(0, Math.min(ev.clientY - dragStart.value.y, window.innerHeight - 440))
  }
  const onUp = () => { document.removeEventListener('mousemove', onMove); document.removeEventListener('mouseup', onUp); dragging.value = false }
  document.addEventListener('mousemove', onMove)
  document.addEventListener('mouseup', onUp)
}

// ── 日历网格 ──
const grid = computed(() => {
  if (!calendarData.value) return []
  const days = calendarData.value.days
  if (!days.length) return []
  const firstWd = days[0].weekday  // 0=Mon
  const rows = []
  let week = Array(firstWd).fill(null)
  for (const d of days) {
    week.push(d)
    if (week.length === 7) { rows.push(week); week = [] }
  }
  if (week.length) rows.push(week.concat(Array(7 - week.length).fill(null)))
  return rows
})
</script>

<template>
  <div v-if="visible" class="cal-float" :style="{ left: posX + 'px', top: posY + 'px', zIndex }">
    <div class="cal-header" @mousedown="onMouseDown" :class="{ dragging }">
      <button class="cal-nav" @click.stop="prevMonth">◀</button>
      <span class="cal-title">{{ calendarYear }}年{{ calendarMonth }}月</span>
      <button class="cal-nav" @click.stop="nextMonth">▶</button>
      <button class="cal-back" @click.stop="backToZhanwen" title="回到占问日期">⟳</button>
      <button class="cal-close" @click="$emit('close')">&times;</button>
    </div>

    <div class="cal-body">
      <div class="cal-sel-date">{{ selYear }}年{{ selMonth }}月{{ selDay }}日</div>
      <div class="cal-sel-ganzhi">
        <span class="gz-year">{{ selectedGanzhi.year }}年</span>
        <span class="gz-month">{{ selectedGanzhi.month }}月</span>
        <span class="gz-day">{{ selectedGanzhi.day }}日</span>
      </div>

      <div class="cal-grid" v-if="!loading">
        <div class="cal-wd" v-for="w in WEEKDAYS" :key="w">{{ w }}</div>
        <template v-for="(row, ri) in grid" :key="ri">
          <div v-for="(d, di) in row" :key="ri+'-'+di" class="cal-cell"
            :class="{
              'cal-empty': !d,
              'cal-sel': d && d.day === selDay && calendarYear === selYear && calendarMonth === selMonth,
              'cal-jieqi': d && d.jieqi,
            }"
            :title="d?.jieqi || ''"
            @click="d && selectDate(calendarYear, calendarMonth, d.day)">
            <template v-if="d">
              <span class="cal-dn">{{ d.day }}</span>
              <span class="cal-dgz">{{ d.day_ganzhi }}</span>
            </template>
          </div>
        </template>
      </div>
      <div v-else class="cal-loading">加载中...</div>
    </div>
  </div>
</template>

<style scoped>
.cal-float {
  position: fixed; width: 340px;
  background: var(--color-bg-overlay); backdrop-filter: blur(8px);
  border: 1px solid var(--color-border-primary); border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg); user-select: none; overflow: hidden;
}
.cal-header {
  display: flex; align-items: center; gap: 4px;
  padding: 6px 8px; cursor: grab; background: var(--color-bg-tertiary);
}
.cal-header.dragging { cursor: grabbing; }
.cal-title { flex: 1; text-align: center; font-size: var(--font-size-sm); font-weight: 600; color: var(--color-text-primary); }
.cal-nav { width: 24px; height: 24px; border: none; background: none; color: var(--color-text-secondary); font-size: 14px; cursor: pointer; border-radius: var(--radius-sm); display: flex; align-items: center; justify-content: center; }
.cal-nav:hover { background: var(--color-bg-secondary); color: var(--color-accent-light); }
.cal-close { width: 24px; height: 24px; border: none; background: none; color: var(--color-text-muted); font-size: 18px; cursor: pointer; border-radius: var(--radius-sm); }
.cal-close:hover { background: var(--color-danger); color: #fff; }

.cal-body { padding: 8px 10px 10px; }
.cal-sel-date { font-size: var(--font-size-xs); color: var(--color-text-secondary); margin-bottom: 2px; }
.cal-sel-ganzhi { font-size: var(--font-size-md); font-weight: bold; color: var(--color-text-primary); margin-bottom: 8px; display: flex; gap: 6px; }
.gz-year { color: #c49b4a; }
.gz-month { color: #6e78c6; }
.gz-day { color: var(--color-accent-light); }

.cal-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 2px; }
.cal-wd { text-align: center; font-size: var(--font-size-xs); color: var(--color-text-muted); padding: 2px 0; }
.cal-cell {
  text-align: center; padding: 2px 0; border-radius: var(--radius-sm);
  min-height: 38px; display: flex; flex-direction: column; align-items: center; justify-content: center;
  font-size: var(--font-size-xs); border: 2px solid transparent;
}
.cal-cell.cal-empty { background: none; }
.cal-cell.cal-sel { background: var(--color-accent); }
.cal-cell.cal-sel .cal-dn { color: #fff; font-weight: bold; }
.cal-cell.cal-sel .cal-dgz { color: rgba(255,255,255,0.8); }
.cal-cell.cal-jieqi { border-color: var(--color-accent); }
.cal-cell:not(.cal-empty) { cursor: pointer; }
.cal-cell:not(.cal-empty):hover:not(.cal-sel) { background: var(--color-bg-tertiary); }
.cal-dn { font-weight: 500; color: var(--color-text-primary); line-height: 1.2; }
.cal-dgz { font-size: 10px; color: var(--color-text-muted); line-height: 1.2; }
.cal-back { width: 24px; height: 24px; border: none; background: none; color: var(--color-text-secondary); font-size: 16px; cursor: pointer; border-radius: var(--radius-sm); display: flex; align-items: center; justify-content: center; }
.cal-back:hover { background: var(--color-accent-soft); color: var(--color-accent-light); }
.cal-loading { text-align: center; padding: var(--space-5); color: var(--color-text-muted); font-size: var(--font-size-sm); }
</style>
