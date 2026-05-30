<script setup>
import { ref, watch, nextTick } from 'vue'
import { useEditor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import GuaLinkExtension from './GuaLinkExtension.js'
import { nextZIndex } from '../../shared/zCounter.js'

const STORAGE_KEY = 'c3_notes'

const props = defineProps({
  visible: { type: Boolean, default: true },
})
const emit = defineEmits(['close'])

// ── 拖动 ──
const posX = ref(Math.max(100, window.innerWidth / 2 - 300))
const posY = ref(Math.max(60, window.innerHeight / 2 - 400))
const zIndex = ref(nextZIndex())
const dragStart = ref({ x: 0, y: 0 })
const dragging = ref(false)
const elWidth = ref(700)
const elHeight = ref(800)

function onMouseDown(e) {
  if (e.target.closest('.nf-resize')) return
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

// ── 缩放 ──
const resizing = ref(false)
const resizeStart = ref({ x: 0, y: 0 })

function onResizeDown(e) {
  e.stopPropagation(); e.preventDefault()
  resizeStart.value = { x: e.clientX, y: e.clientY }
  resizing.value = true
  const onMove = (ev) => {
    elWidth.value = Math.max(360, elWidth.value + ev.clientX - resizeStart.value.x)
    elHeight.value = Math.max(300, elHeight.value + ev.clientY - resizeStart.value.y)
    resizeStart.value = { x: ev.clientX, y: ev.clientY }
  }
  const onUp = () => { document.removeEventListener('mousemove', onMove); document.removeEventListener('mouseup', onUp); resizing.value = false }
  document.addEventListener('mousemove', onMove)
  document.addEventListener('mouseup', onUp)
}

// ── 笔记数据 ──
function loadNotes() {
  try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]') } catch { return [] }
}
function saveNotes(n) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(n))
}

const notes = ref(loadNotes())
const currentId = ref(notes.value[0]?.id || null)

const currentNote = () => notes.value.find(n => n.id === currentId.value)

function newNote() {
  const id = Date.now().toString(36) + Math.random().toString(36).slice(2, 6)
  const note = { id, title: '', content: '<p></p>', createdAt: new Date().toISOString(), updatedAt: new Date().toISOString() }
  notes.value.push(note)
  saveNotes(notes.value)
  currentId.value = id
  loadEditorContent()
}

function deleteNote(id) {
  if (!confirm('删除这篇笔记？')) return
  notes.value = notes.value.filter(n => n.id !== id)
  saveNotes(notes.value)
  if (currentId.value === id) {
    currentId.value = notes.value[0]?.id || null
    loadEditorContent()
  }
}

function selectNote(id) {
  saveCurrentContent()
  currentId.value = id
  loadEditorContent()
}

function saveCurrentContent() {
  const n = currentNote()
  if (n && editor.value) {
    n.content = editor.value.getHTML()
    n.updatedAt = new Date().toISOString()
    saveNotes(notes.value)
  }
}

// ── Tiptap 编辑器 ──
const editor = useEditor({
  extensions: [StarterKit.configure({ bold: false }), GuaLinkExtension],
  content: '',
  editable: true,
})

// watch 编辑器内容变化自动保存（替代 onUpdate，更可靠）
watch(() => editor.value?.getHTML(), (html) => {
  if (!html) return
  const n = currentNote()
  if (n) {
    n.content = html
    n.updatedAt = new Date().toISOString()
    saveNotes(notes.value)
  }
})

function loadEditorContent() {
  nextTick(() => {
    if (editor.value) {
      const n = currentNote()
      editor.value.commands.setContent(n?.content || '<p></p>')
    }
  })
}

// guaLink 点击跳转（事件委托）
function onEditorClick(e) {
  const link = e.target.closest('.gua-link')
  if (link) {
    const id = link.dataset.id
    if (id) window.open(`/guali?id=${id}`, '_blank')
  }
}

watch(currentId, () => loadEditorContent())

function lastSaved() {
  const n = currentNote()
  if (!n) return ''
  const d = new Date(n.updatedAt)
  return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')} ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`
}
</script>

<template>
  <div v-if="visible" class="nf-float" :style="{ left: posX + 'px', top: posY + 'px', zIndex, width: elWidth + 'px', height: elHeight + 'px' }">
    <div class="nf-header" @mousedown="onMouseDown" :class="{ dragging }">
      <span class="nf-title">
        <svg class="nf-icon" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>
        笔记
      </span>
      <button class="nf-close" @click="saveCurrentContent(); emit('close')">&times;</button>
    </div>

    <div class="nf-body">
      <div class="nf-list">
        <div v-for="n in notes" :key="n.id" class="nf-item" :class="{ active: n.id === currentId }" @click="selectNote(n.id)">
          <span class="nf-item-title">{{ n.title || '无标题' }}</span>
          <button class="nf-del" @click.stop="deleteNote(n.id)">×</button>
        </div>
        <button class="nf-new" @click="newNote">＋ 新建笔记</button>
      </div>

      <div class="nf-editor-wrap" @click="zIndex = nextZIndex()">
        <div v-if="currentId">
          <input :value="currentNote()?.title || ''" class="nf-title-input" placeholder="笔记标题..."
            @input="(e) => { const n = currentNote(); if (n) { n.title = e.target.value; n.updatedAt = new Date().toISOString(); saveNotes(notes.value) } }" />
          <div class="nf-editor" @click="onEditorClick">
            <EditorContent :editor="editor" />
          </div>
        </div>
        <div v-else class="nf-empty">选择或新建一篇笔记</div>
        <div class="nf-footer" v-if="currentId">最后保存: {{ lastSaved() }}</div>
      </div>
    </div>

    <div class="nf-resize" @mousedown="onResizeDown"></div>
  </div>
</template>

<style scoped>
.nf-float {
  position: fixed; min-width: 360px; min-height: 300px;
  background: var(--color-bg-overlay); backdrop-filter: blur(10px);
  border: 1px solid var(--color-border-primary); border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg); user-select: none; overflow: hidden;
  display: flex; flex-direction: column;
}
.nf-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 6px 10px; cursor: grab; background: var(--color-bg-tertiary);
  flex-shrink: 0;
}
.nf-header.dragging { cursor: grabbing; }
.nf-title { font-size: var(--font-size-sm); font-weight: 600; color: var(--color-text-primary); display: flex; align-items: center; gap: 6px; }
.nf-icon { flex-shrink: 0; color: var(--color-text-secondary); }
.nf-close { width: 24px; height: 24px; border: none; background: none; color: var(--color-text-muted); font-size: 18px; cursor: pointer; border-radius: var(--radius-sm); }
.nf-close:hover { background: var(--color-danger); color: #fff; }

.nf-body { display: flex; flex: 1; min-height: 0; }
.nf-list { width: 180px; flex-shrink: 0; border-right: 1px solid var(--color-border-primary); padding: 6px; overflow-y: auto; display: flex; flex-direction: column; gap: 4px; background: var(--color-bg-secondary); }
.nf-item { display: flex; align-items: center; padding: 8px 8px; border-radius: var(--radius-sm); cursor: pointer; font-size: var(--font-size-sm); color: var(--color-text-secondary); }
.nf-item:hover { background: var(--color-bg-tertiary); }
.nf-item.active { background: var(--color-accent); color: #fff; }
.nf-item-title { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.nf-del { width: 16px; height: 16px; border: none; background: none; color: inherit; font-size: 12px; cursor: pointer; border-radius: 50%; opacity: 0; flex-shrink: 0; }
.nf-item:hover .nf-del { opacity: 0.6; }
.nf-item:hover .nf-del:hover { opacity: 1; background: rgba(255,255,255,0.2); }
.nf-new { padding: 6px 8px; border: 1px dashed var(--color-border-primary); border-radius: var(--radius-sm); background: none; color: var(--color-text-muted); font-size: var(--font-size-sm); cursor: pointer; text-align: left; }
.nf-new:hover { border-color: var(--color-accent); color: var(--color-accent-light); }

.nf-editor-wrap { flex: 1; display: flex; flex-direction: column; padding: 10px 14px; overflow-y: auto; min-width: 0; }
.nf-title-input { width: 100%; padding: 4px 0 8px; margin-bottom: 10px; border: none; border-bottom: 1px solid var(--color-border-subtle); background: none; color: var(--color-text-primary); font-size: 1.4rem; font-weight: bold; outline: none !important; box-shadow: none !important; }
.nf-title-input:focus, .nf-title-input:focus-visible { outline: none !important; box-shadow: none !important; border-bottom-color: var(--color-border-subtle); }

.nf-editor { flex: 1; min-height: 0; }
.nf-editor :deep(.tiptap),
.nf-editor :deep(.ProseMirror) { outline: none !important; box-shadow: none !important; min-height: 200px; font-size: 0.95rem; color: var(--color-text-primary); line-height: 1.7; }
.nf-editor :deep(.tiptap:focus),
.nf-editor :deep(.tiptap:focus-visible),
.nf-editor :deep(.ProseMirror:focus),
.nf-editor :deep(.ProseMirror:focus-visible),
.nf-editor :deep(.ProseMirror-focused) { outline: none !important; box-shadow: none !important; }
.nf-editor :deep(.tiptap p) { margin: 0 0 4px; }
.nf-editor :deep(.gua-link) { color: #5F8EC0; cursor: pointer; text-decoration: none; }
.nf-editor :deep(.gua-link:hover) { text-decoration: underline; }

.nf-empty { flex: 1; display: flex; align-items: center; justify-content: center; color: var(--color-text-muted); font-size: var(--font-size-sm); }
.nf-footer { padding: 6px 0 0; font-size: var(--font-size-xs); color: var(--color-text-muted); border-top: 1px solid var(--color-border-subtle); margin-top: auto; }

.nf-resize { position: absolute; bottom: 0; right: 0; width: 20px; height: 20px; cursor: nwse-resize; z-index: 1; }
</style>
