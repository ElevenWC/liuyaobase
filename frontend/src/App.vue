<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import NavBar from './components/NavBar.vue'
import NoteFloat from './components/shared/NoteFloat.vue'

const showNote = ref(false)

function toggleNote() { showNote.value = !showNote.value }

function onKeydown(e) {
  if (e.ctrlKey && e.shiftKey && e.code === 'Space') {
    e.preventDefault()
    toggleNote()
  }
}

onMounted(() => document.addEventListener('keydown', onKeydown))
onUnmounted(() => document.removeEventListener('keydown', onKeydown))
</script>

<template>
  <NavBar />
  <NoteFloat :visible="showNote" @close="showNote = false" />
  <main>
    <router-view />
  </main>
  <div class="note-fab" v-if="!showNote" @click="showNote = true" title="笔记 (Ctrl+Shift+Space)">📝</div>
</template>

<style>
.note-fab {
  position: fixed; bottom: 24px; right: 24px; z-index: 99;
  width: 42px; height: 42px; border-radius: 50%;
  background: var(--color-bg-glass); backdrop-filter: blur(6px);
  border: 1px solid var(--color-border-subtle);
  color: var(--color-text-muted); font-size: 18px;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; box-shadow: var(--shadow-sm);
  transition: all var(--transition-fast);
  user-select: none;
}
.note-fab:hover {
  color: var(--color-accent-light); border-color: var(--color-accent);
  box-shadow: var(--shadow-md); transform: scale(1.05);
}
</style>
