<script setup>
import { ref } from 'vue'
import { importJson } from '../api/index.js'

const fileInput = ref(null)
const result = ref(null)
const error = ref('')
const uploading = ref(false)

async function upload() {
  const file = fileInput.value?.files?.[0]
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
  fileInput.value.files = e.dataTransfer.files
}
</script>

<template>
  <div class="import-page">
    <h2>JSON 批量导入</h2>
    <div class="drop-zone" @dragover.prevent @drop="onDrop">
      <input ref="fileInput" type="file" accept=".json" />
      <p>选择 JSON 文件或拖拽到此处</p>
      <button @click="upload" :disabled="uploading" class="btn-upload">
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
.drop-zone { border: 2px dashed var(--color-border-primary); border-radius: var(--radius-lg); padding: var(--space-8); text-align: center; background: var(--color-bg-secondary); }
.drop-zone p { margin: var(--space-3) 0; color: var(--color-text-secondary); }
.btn-upload { padding: var(--space-2) var(--space-6); background: var(--color-accent-gradient); color: #fff; border: none; border-radius: var(--radius-md); cursor: pointer; font-size: var(--font-size-base); margin-top: var(--space-2); }
.btn-upload:disabled { opacity: 0.5; }
.error { color: var(--color-danger); margin-top: var(--space-3); }
.result { margin-top: var(--space-4); padding: var(--space-3); background: var(--color-bg-secondary); border-radius: var(--radius-lg); }
.result p { color: var(--color-text-primary); }
</style>
