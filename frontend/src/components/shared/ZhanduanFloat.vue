<script setup>
import { ref, watch } from 'vue'
import { nextZIndex } from '../../shared/zCounter.js'

const props = defineProps({
  gualiId: { type: Number, required: true },
  content: { type: String, default: '' },
  visible: { type: Boolean, default: true },
})

const emit = defineEmits(['close', 'save'])

const posX = ref(Math.max(100, window.innerWidth / 2 - 200))
const posY = ref(Math.max(100, window.innerHeight / 2 - 200))
const zIndex = ref(nextZIndex())
const dragStart = ref({ x: 0, y: 0 })
const dragging = ref(false)
const elWidth = ref(500)
const elHeight = ref(400)

const text = ref(props.content)
watch(() => props.content, (v) => { text.value = v })

function onMouseDown(e) {
  if (e.target.closest('.zf-resize')) return
  dragStart.value = { x: e.clientX - posX.value, y: e.clientY - posY.value }
  zIndex.value = nextZIndex()
  dragging.value = true
  const onMove = (ev) => {
    posX.value = Math.max(0, Math.min(ev.clientX - dragStart.value.x, window.innerWidth - elWidth.value))
    posY.value = Math.max(0, Math.min(ev.clientY - dragStart.value.y, window.innerHeight - 60))
  }
  const onUp = () => { document.removeEventListener('mousemove', onMove); document.removeEventListener('mouseup', onUp); dragging.value = false }
  document.addEventListener('mousemove', onMove)
  document.addEventListener('mouseup', onUp)
}

function onResizeDown(e) {
  e.stopPropagation(); e.preventDefault()
  const start = { x: e.clientX, y: e.clientY }
  const onMove = (ev) => {
    elWidth.value = Math.max(300, elWidth.value + ev.clientX - start.x)
    elHeight.value = Math.max(200, elHeight.value + ev.clientY - start.y)
    start.x = ev.clientX; start.y = ev.clientY
  }
  const onUp = () => { document.removeEventListener('mousemove', onMove); document.removeEventListener('mouseup', onUp) }
  document.addEventListener('mousemove', onMove)
  document.addEventListener('mouseup', onUp)
}

function doClose() {
  if (text.value !== props.content) emit('save', text.value)
  emit('close')
}
</script>

<template>
  <div v-if="visible" class="zf-float" :style="{ left: posX + 'px', top: posY + 'px', zIndex, width: elWidth + 'px', height: elHeight + 'px' }">
    <div class="zf-header" @mousedown="onMouseDown" :class="{ dragging }">
      <span class="zf-title">占断内容</span>
      <button class="zf-close" @click="doClose">&times;</button>
    </div>
    <textarea v-model="text" class="zf-textarea" placeholder="输入占断内容..."></textarea>
    <div class="zf-resize" @mousedown="onResizeDown"></div>
  </div>
</template>

<style scoped>
.zf-float {
  position: fixed; min-width: 300px; min-height: 200px;
  background: var(--color-bg-overlay); backdrop-filter: blur(10px);
  border: 1px solid var(--color-border-primary); border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg); user-select: none;
  display: flex; flex-direction: column; overflow: hidden;
}
.zf-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 6px 10px; cursor: grab; background: var(--color-bg-tertiary);
  flex-shrink: 0;
}
.zf-header.dragging { cursor: grabbing; }
.zf-title { font-size: var(--font-size-lg); font-weight: bold; color: var(--color-text-primary); }
.zf-close { width: 24px; height: 24px; border: none; background: none; color: var(--color-text-muted); font-size: 18px; cursor: pointer; border-radius: var(--radius-sm); }
.zf-close:hover { background: var(--color-danger); color: #fff; }
.zf-textarea {
  flex: 1; padding: 12px 14px; border: none; outline: none; resize: none;
  background: transparent; color: var(--color-text-primary);
  font-size: 0.95rem; font-family: var(--font-family);
  line-height: 1.7; min-height: 0;
}
.zf-textarea::placeholder { color: var(--color-text-muted); }
.zf-resize { position: absolute; bottom: 0; right: 0; width: 20px; height: 20px; cursor: nwse-resize; z-index: 1; }
</style>
