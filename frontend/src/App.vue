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
  width: 48px; height: 48px; border-radius: 50%;
  background: var(--color-accent); color: #fff; font-size: 22px;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; box-shadow: var(--shadow-lg);
  transition: transform var(--transition-fast), box-shadow var(--transition-fast);
  user-select: none;
}
.note-fab:hover { transform: scale(1.1); box-shadow: var(--shadow-glow); }
</style>
