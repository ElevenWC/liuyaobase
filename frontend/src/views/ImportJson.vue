<script setup>
import { ref } from 'vue'
import { importJson } from '../api/index.js'

const fileInput = ref(null)
const droppedFile = ref(null)
const result = ref(null)
const error = ref('')
const uploading = ref(false)

function onFileSelect(e) {
  droppedFile.value = null
  const f = e.target.files?.[0]
  if (!f) return
  if (!f.name.endsWith('.json')) { error.value = '仅支持 JSON 文件'; return }
  error.value = ''
}

async function upload() {
  const file = droppedFile.value || fileInput.value?.files?.[0]
  if (!file) { error.value = '请选择 JSON 文件'; return }
  uploading.value = true; error.value = ''; result.value = null
  try {
    const res = await importJson(file)
    if (res.data.code === 200) result.value = res.data.data
    else error.value = res.data.message || '导入失败'
  } catch (e) {
    error.value = e.response?.data?.message || '导入失败'
  } finally { uploading.value = false }
}

function onDrop(e) {
  e.preventDefault()
  const f = e.dataTransfer.files?.[0]
  if (!f) return
  if (!f.name.endsWith('.json')) { error.value = '仅支持 JSON 文件'; return }
  droppedFile.value = f
  error.value = ''
}

function triggerBrowse() { fileInput.value?.click() }
</script>

<template>
  <div class="import-page">
    <h2>JSON 批量导入</h2>
    <input ref="fileInput" type="file" accept=".json" @change="onFileSelect" hidden />
    <div class="drop-zone" @dragover.prevent @drop="onDrop" @click="triggerBrowse">
      <p>{{ droppedFile ? droppedFile.name : '选择 JSON 文件或拖拽到此处' }}</p>
      <button @click.stop="upload" :disabled="uploading || (!droppedFile && !fileInput?.files?.length)" class="btn-upload">
        {{ uploading ? '导入中...' : '开始导入' }}
      </button>
    </div>
    <p v-if="error" class="error">{{ error }}</p>
    <div v-if="result" class="result">
      <p>导入：{{ result.imported }} 条</p>
      <p>跳过：{{ result.skipped }} 条</p>
    </div>
  </div>
</template>

<style scoped>
.import-page { max-width: 500px; margin: var(--space-5) auto; color: var(--color-text-primary); padding: var(--space-4); }
h2 { margin-bottom: var(--space-4); }
.drop-zone { border: 2px dashed var(--color-border-primary); border-radius: var(--radius-lg); padding: var(--space-8); text-align: center; background: var(--color-bg-secondary); cursor: pointer; transition: border-color var(--transition-fast); }
.drop-zone:hover { border-color: var(--color-accent); }
.drop-zone p { margin-bottom: var(--space-3); color: var(--color-text-secondary); }
.btn-upload { padding: var(--space-2) var(--space-6); background: var(--color-accent-gradient); color: #fff; border: none; border-radius: var(--radius-md); cursor: pointer; font-size: var(--font-size-base); }
.btn-upload:disabled { opacity: 0.5; cursor: not-allowed; }
.error { color: var(--color-danger); margin-top: var(--space-3); }
.result { margin-top: var(--space-4); padding: var(--space-3); background: var(--color-bg-secondary); border-radius: var(--radius-lg); }
.result p { color: var(--color-text-primary); }
</style>
