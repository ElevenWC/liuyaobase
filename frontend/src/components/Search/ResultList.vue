<script setup>
import { ref, computed, watch } from 'vue'
import GuaCiFloat from '../shared/GuaCiFloat.vue'

const props = defineProps({
  results: { type: Array, default: () => [] },
  total: { type: Number, default: 0 },
  page: { type: Number, default: 1 },
  pageSize: { type: Number, default: 50 },
  loading: { type: Boolean, default: false },
  selectedId: { type: Number, default: null },
  selectAll: { type: Boolean, default: false },
  excludedIds: { type: Set, default: () => new Set() },
})

const emit = defineEmits(['page-change', 'select-guali', 'export-data', 'toggle-exclude'])

const selected = ref([])
const activeFloats = ref([])
const exportName = ref(defaultExportName())

function defaultExportName() {
  const d = new Date()
  return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}_export`
}

function doExport(fmt) {
  emit('export-data', { format: fmt, filename: exportName.value || defaultExportName() })
}

function openGuaCi(code, name) {
  activeFloats.value.push({ id: Date.now() + Math.random(), guaCode: code, guaName: name || code })
}
function closeFloat(id) { activeFloats.value = activeFloats.value.filter(f => f.id !== id) }

function onRowClick(id) { emit('select-guali', id) }

function toggleSelect(id) {
  const idx = selected.value.indexOf(id)
  if (idx >= 0) selected.value.splice(idx, 1)
  else selected.value.push(id)
}

const timeSort = ref(null)  // null=默认(倒序), 'asc'=正序
const sortedResults = computed(() => {
  if (timeSort.value !== 'asc') return props.results
  return [...props.results].sort((a, b) => (a.zhanwen_time || '').localeCompare(b.zhanwen_time || ''))
})

function toggleTimeSort() { timeSort.value = timeSort.value === 'asc' ? null : 'asc' }

const totalPages = computed(() => Math.ceil(props.total / props.pageSize) || 1)

watch(() => props.results, (v) => { if (!v?.length) { selected.value = []; timeSort.value = null } })

function clearSelection() { selected.value = [] }
defineExpose({ selected, clearSelection })
</script>

<template>
  <div class="result-list">
    <div v-if="loading" class="rl-loading">检索中...</div>

    <template v-else-if="results.length">
      <div class="rl-info-bar">
        <span class="rl-info">共 {{ total }} 条，第 {{ page }} / {{ totalPages }} 页</span>
        <div class="rl-export">
          <input v-model="exportName" class="rl-export-name" placeholder="文件名" />
          <button class="rl-export-btn" @click="doExport('csv')">导出CSV</button>
          <button class="rl-export-btn" @click="doExport('json')">导出JSON</button>
        </div>
      </div>

      <table class="rl-table">
        <thead>
          <tr>
            <th class="col-cb"><input type="checkbox"
              :checked="props.selectAll || selected.length === results.length"
              @change="(e) => { if (props.selectAll) { results.forEach(r => { if (!e.target.checked) emit('toggle-exclude', r.id) }) } else { selected = e.target.checked ? results.map(r=>r.id) : [] } }" /></th>
            <th class="col-num">#</th>
            <th class="col-time sortable" @click="toggleTimeSort">占问时间{{ timeSort === 'asc' ? ' ▲' : '' }}</th>
            <th class="col-shiyou">占问事由</th>
            <th class="col-ben">本卦</th>
            <th class="col-zhi">之卦</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(r, i) in sortedResults" :key="r.id" @click="onRowClick(r.id)" class="rl-row" :class="{ active: r.id === props.selectedId }">
            <td class="col-cb" @click.stop><input type="checkbox"
              :checked="props.selectAll ? !props.excludedIds.has(r.id) : selected.includes(r.id)"
              @change="props.selectAll ? emit('toggle-exclude', r.id) : toggleSelect(r.id)" /></td>
            <td class="col-num">{{ r.id }}</td>
            <td class="col-time">{{ r.zhanwen_time?.slice(0, 10) }}</td>
            <td class="col-shiyou">{{ r.zhanwen_shiyou }}</td>
            <td class="col-ben">
              <span class="rl-gua-link" @click.stop="openGuaCi(r.ben_code, r.ben_name)">{{ r.ben_name || r.ben_code }}</span>
            </td>
            <td class="col-zhi">
              <span v-if="r.zhi_name" class="rl-gua-link" @click.stop="openGuaCi(r.zhi_code, r.zhi_name)">{{ r.zhi_name }}</span>
            </td>
          </tr>
        </tbody>
      </table>

      <div class="rl-pager">
        <button :disabled="page <= 1" @click="emit('page-change', page - 1)">&lt;</button>
        <span>{{ page }} / {{ totalPages }}</span>
        <button :disabled="page >= totalPages" @click="emit('page-change', page + 1)">&gt;</button>
      </div>
    </template>

    <div v-else class="rl-empty">未找到符合条件的卦例</div>

    <GuaCiFloat v-for="f in activeFloats" :key="f.id" :gua-code="f.guaCode" :gua-name="f.guaName" :visible="true" @close="closeFloat(f.id)" />
  </div>
</template>

<style scoped>
.result-list { background: var(--color-bg-secondary); border-radius: var(--radius-lg); padding: var(--space-3); box-shadow: var(--shadow-sm); }
.rl-loading, .rl-empty { text-align: center; padding: var(--space-5); color: var(--color-text-muted); font-size: var(--font-size-sm); }
.rl-info-bar { display: flex; align-items: center; justify-content: space-between; margin-bottom: var(--space-2); }
.rl-info { font-size: var(--font-size-xs); color: var(--color-text-muted); }
.rl-export { display: flex; align-items: center; gap: var(--space-2); }
.rl-export-name { width: 140px; padding: 2px 6px; background: var(--color-bg-input); color: var(--color-text-primary); border: 1px solid var(--color-border-primary); border-radius: var(--radius-sm); font-size: var(--font-size-xs); }
.rl-export-name:focus { outline: none; border-color: var(--color-accent); }
.rl-export-btn { padding: 2px 8px; background: var(--color-bg-tertiary); color: var(--color-text-secondary); border: 1px solid var(--color-border-primary); border-radius: var(--radius-sm); font-size: var(--font-size-xs); cursor: pointer; transition: all var(--transition-fast); }
.rl-export-btn:hover { border-color: var(--color-accent); color: var(--color-accent-light); }

.rl-table { width: 100%; border-collapse: collapse; font-size: var(--font-size-sm); }
.rl-table th { padding: 4px 6px; text-align: left; color: var(--color-text-secondary); border-bottom: 1px solid var(--color-border-primary); font-weight: 500; }
.rl-table td { padding: 4px 6px; color: var(--color-text-primary); border-bottom: 1px solid var(--color-border-subtle); }
.rl-row { cursor: pointer; transition: background var(--transition-fast); }
.rl-row:hover { background: var(--color-bg-tertiary); }
.rl-row.active { background: var(--color-accent-soft); }

.col-cb { width: 28px; }
.col-num { width: 32px; }
.col-time { width: 90px; white-space: nowrap; }
.sortable { cursor: pointer; user-select: none; }
.sortable:hover { color: var(--color-accent); }
.col-ben, .col-zhi { width: 80px; }
.rl-gua-link { color: var(--color-accent-light); cursor: pointer; }
.rl-gua-link:hover { text-decoration: underline; }

.rl-pager { display: flex; align-items: center; justify-content: center; gap: var(--space-3); margin-top: var(--space-3); }
.rl-pager button { padding: 2px 10px; background: var(--color-bg-tertiary); color: var(--color-text-primary); border: 1px solid var(--color-border-primary); border-radius: var(--radius-sm); cursor: pointer; font-size: var(--font-size-sm); }
.rl-pager button:disabled { opacity: 0.4; cursor: not-allowed; }
.rl-pager span { font-size: var(--font-size-xs); color: var(--color-text-muted); }
</style>
