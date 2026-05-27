<script setup>
import { ref } from 'vue'
import { useSearchStore } from '../../stores/useSearchStore.js'

const store = useSearchStore()
const showPanel = ref(false)
const saveName = ref('')

const schemes = ref([])

function refreshSchemes() {
  schemes.value = store.loadSchemes().sort((a, b) => b.time - a.time)
}
refreshSchemes()

function onSave() {
  const name = saveName.value.trim()
  if (!name) { alert('请输入方案名称'); return }
  store.saveScheme(name)
  saveName.value = ''
  refreshSchemes()
}

function onApply(scheme) {
  if (!confirm(`载入方案"${scheme.name}"？当前条件将被替换`)) return
  store.applyScheme(scheme)
}

function onDelete(name) {
  if (!confirm(`删除方案"${name}"？`)) return
  store.deleteScheme(name)
  refreshSchemes()
}

function formatTime(ts) {
  const d = new Date(ts)
  return `${d.getMonth()+1}/${d.getDate()} ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`
}
</script>

<template>
  <div class="schemes-bar">
    <div class="sch-toggle" @click="showPanel = !showPanel">
      <span class="sch-arrow">{{ showPanel ? '▾' : '▸' }}</span>
      <span>方案管理</span>
      <span class="sch-count" v-if="schemes.length">({{ schemes.length }})</span>
    </div>

    <div v-if="showPanel" class="sch-panel">
      <div class="sch-save">
        <input v-model="saveName" class="cb-input" placeholder="方案名称" style="width:120px" @keyup.enter="onSave" />
        <button @click="onSave" class="cb-btn" :disabled="!saveName.trim()">保存当前条件</button>
      </div>

      <div v-if="schemes.length" class="sch-list">
        <div v-for="s in schemes" :key="s.name" class="sch-item">
          <span class="sch-name" :title="s.name">{{ s.name }}</span>
          <span class="sch-time">{{ formatTime(s.time) }}</span>
          <button @click="onApply(s)" class="cb-btn sch-apply">载入</button>
          <button @click="onDelete(s.name)" class="cb-btn sch-del">删除</button>
        </div>
      </div>
      <div v-else class="sch-empty">暂无已保存方案</div>
    </div>
  </div>
</template>

<style scoped>
/* shared with ConditionBuilder */
.cb-btn { padding: 3px 10px; background: var(--color-bg-tertiary); color: var(--color-text-secondary); border: 1px solid var(--color-border-primary); border-radius: var(--radius-md); font-size: var(--font-size-xs); cursor: pointer; transition: all var(--transition-fast); }
.cb-btn:hover { border-color: var(--color-accent); color: var(--color-accent-light); }
.cb-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.cb-input { padding: 2px 6px; background: var(--color-bg-input); color: var(--color-text-primary); border: 1px solid var(--color-border-primary); border-radius: var(--radius-sm); font-size: var(--font-size-sm); }
.cb-input:focus { outline: none; border-color: var(--color-accent); }

.schemes-bar { margin-bottom: var(--space-2); }
.sch-toggle { display: flex; align-items: center; gap: var(--space-1); cursor: pointer; user-select: none; padding: 2px 0; }
.sch-toggle span { font-size: var(--font-size-sm); color: var(--color-text-secondary); }
.sch-arrow { font-size: var(--font-size-xs); width: 14px; }
.sch-count { font-size: var(--font-size-xs); color: var(--color-text-muted); }

.sch-panel { margin-top: var(--space-1); padding: var(--space-2); background: var(--color-bg-tertiary); border-radius: var(--radius-md); }
.sch-save { display: flex; gap: var(--space-2); align-items: center; margin-bottom: var(--space-2); }
.sch-list { display: flex; flex-direction: column; gap: 4px; }
.sch-item { display: flex; align-items: center; gap: var(--space-2); padding: 3px 6px; border-radius: var(--radius-sm); }
.sch-item:hover { background: var(--color-bg-secondary); }
.sch-name { font-size: var(--font-size-sm); color: var(--color-text-primary); flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.sch-time { font-size: var(--font-size-xs); color: var(--color-text-muted); flex-shrink: 0; }
.sch-apply { color: var(--color-accent-light) !important; border-color: var(--color-accent) !important; }
.sch-del:hover { border-color: var(--color-danger) !important; color: var(--color-danger) !important; }
.sch-empty { font-size: var(--font-size-xs); color: var(--color-text-muted); text-align: center; padding: var(--space-2); }
</style>
