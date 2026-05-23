<script setup>
import { ref, watch } from 'vue'
import { fetchGuaci } from '../../api/index.js'

const props = defineProps({
  guaCode: { type: String, required: true },
  guaName: { type: String, required: true },
  visible: { type: Boolean, default: true },
})

const emit = defineEmits(['close'])

const data = ref(null)
const loading = ref(false)
const posX = ref(window.innerWidth / 2 - 200)
const posY = ref(window.innerHeight / 2 - 250)
const dragging = ref(false)
const dragStart = ref({ x: 0, y: 0 })
const zIndex = ref(0)

let zCounter = 100

watch(() => props.guaCode, fetchData, { immediate: true })

async function fetchData() {
  loading.value = true
  try {
    const res = await fetchGuaci(props.guaCode)
    if (res.data.code === 200) data.value = res.data.data
  } finally { loading.value = false }
}

function onMouseDown(e) {
  dragging.value = true
  dragStart.value = { x: e.clientX - posX.value, y: e.clientY - posY.value }
  zIndex.value = ++zCounter
  document.addEventListener('mousemove', onMouseMove)
  document.addEventListener('mouseup', onMouseUp)
}
function onMouseMove(e) {
  if (!dragging.value) return
  posX.value = Math.max(0, Math.min(e.clientX - dragStart.value.x, window.innerWidth - 420))
  posY.value = Math.max(0, Math.min(e.clientY - dragStart.value.y, window.innerHeight - 100))
}
function onMouseUp() {
  dragging.value = false
  document.removeEventListener('mousemove', onMouseMove)
  document.removeEventListener('mouseup', onMouseUp)
}
function yaociLines() {
  if (!data.value?.yao_ci) return []
  return Object.entries(data.value.yao_ci).map(([k, v]) => `${k}: ${v}`)
}
function wenyanParagraphs() {
  if (!data.value?.wenyan) return []
  return data.value.wenyan.split('|')
}
</script>

<template>
  <div v-if="visible" class="guaci-float" :style="{ left: posX + 'px', top: posY + 'px', zIndex }">
    <div class="float-header" @mousedown="onMouseDown">
      <span>{{ guaName }}（{{ guaCode }}）</span>
      <button class="close-btn" @click="$emit('close')">&times;</button>
    </div>
    <div class="float-body">
      <div v-if="loading">加载中...</div>
      <template v-else-if="data">
        <p><b>卦辞：</b>{{ data.gua_ci }}</p>
        <p><b>彖传：</b>{{ data.tuan_zhuan }}</p>
        <p><b>象传：</b>{{ data.xiang_zhuan }}</p>
        <p v-if="yaociLines().length">
          <b>爻辞：</b>
          <span v-for="(line, i) in yaociLines()" :key="i">{{ line }}<br /></span>
        </p>
        <div v-if="wenyanParagraphs().length">
          <b>文言：</b>
          <p v-for="(p, i) in wenyanParagraphs()" :key="i">{{ p }}</p>
        </div>
        <p v-if="data.yong"><b>{{ data.yong }}</b></p>
      </template>
    </div>
  </div>
</template>

<style scoped>
.guaci-float {
  position: fixed; width: 400px; max-height: 500px;
  background: var(--color-bg-overlay); backdrop-filter: blur(8px);
  border: 1px solid var(--color-border-primary); border-radius: var(--radius-xl);
  box-shadow: var(--shadow-lg); overflow: hidden;
  user-select: none; color: var(--color-text-primary);
}
.float-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: var(--space-2) var(--space-3); background: var(--color-bg-tertiary);
  border-radius: var(--radius-xl) var(--radius-xl) 0 0;
  cursor: grab;
}
.float-header:active { cursor: grabbing; }
.float-header span { font-weight: bold; color: var(--color-text-primary); }
.close-btn {
  background: none; border: none; font-size: 18px; cursor: pointer;
  color: var(--color-text-secondary); transition: color var(--transition-fast);
}
.close-btn:hover { color: var(--color-text-primary); }
.float-body {
  padding: var(--space-3); overflow-y: auto; max-height: 420px;
  font-size: var(--font-size-base); line-height: var(--line-height);
  color: var(--color-text-primary);
}
.float-body b { color: var(--color-accent); }
.float-body::-webkit-scrollbar { width: 5px; }
.float-body::-webkit-scrollbar-thumb { background: var(--color-border-primary); border-radius: 3px; }
</style>
