<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import GuaCiFloat from '../shared/GuaCiFloat.vue'

const props = defineProps({
  results: { type: Array, default: () => [] },
  total: { type: Number, default: 0 },
  page: { type: Number, default: 1 },
  pageSize: { type: Number, default: 50 },
  loading: { type: Boolean, default: false },
})

const emit = defineEmits(['page-change'])

const router = useRouter()
const selected = ref([])
const activeFloats = ref([])

function openGuaCi(code, name) {
  activeFloats.value.push({ id: Date.now() + Math.random(), guaCode: code, guaName: name || code })
}
function closeFloat(id) { activeFloats.value = activeFloats.value.filter(f => f.id !== id) }

function gotoDetail(id) { router.push(`/guali?id=${id}`) }

function toggleSelect(id) {
  const idx = selected.value.indexOf(id)
  if (idx >= 0) selected.value.splice(idx, 1)
  else selected.value.push(id)
}

const totalPages = computed(() => Math.ceil(props.total / props.pageSize) || 1)

defineExpose({ selected })
</script>

<template>
  <div class="result-list">
    <div v-if="loading" class="rl-loading">检索中...</div>

    <template v-else-if="results.length">
      <div class="rl-info">共 {{ total }} 条，第 {{ page }} / {{ totalPages }} 页</div>

      <table class="rl-table">
        <thead>
          <tr>
            <th class="col-cb"><input type="checkbox" @change="(e) => selected = e.target.checked ? results.map(r=>r.id) : []" /></th>
            <th class="col-num">#</th>
            <th class="col-time">占问时间</th>
            <th class="col-shiyou">占问事由</th>
            <th class="col-ben">本卦</th>
            <th class="col-zhi">之卦</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(r, i) in results" :key="r.id" @click="gotoDetail(r.id)" class="rl-row">
            <td class="col-cb" @click.stop><input type="checkbox" :checked="selected.includes(r.id)" @change="toggleSelect(r.id)" /></td>
            <td class="col-num">{{ (page - 1) * pageSize + i + 1 }}</td>
            <td class="col-time">{{ r.zhanwen_time?.slice(0, 10) }}</td>
            <td class="col-shiyou">{{ r.zhanwen_shiyou }}</td>
            <td class="col-ben">
              <span class="rl-gua-link" @click.stop="openGuaCi(r.ben_code, r.ben_name)">{{ r.ben_code }}</span>
            </td>
            <td class="col-zhi">
              <span class="rl-gua-link" @click.stop="openGuaCi(r.zhi_code, r.zhi_name)">{{ r.zhi_code }}</span>
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
.rl-info { font-size: var(--font-size-xs); color: var(--color-text-muted); margin-bottom: var(--space-2); }

.rl-table { width: 100%; border-collapse: collapse; font-size: var(--font-size-sm); }
.rl-table th { padding: 4px 6px; text-align: left; color: var(--color-text-secondary); border-bottom: 1px solid var(--color-border-primary); font-weight: 500; }
.rl-table td { padding: 4px 6px; color: var(--color-text-primary); border-bottom: 1px solid var(--color-border-subtle); }
.rl-row { cursor: pointer; transition: background var(--transition-fast); }
.rl-row:hover { background: var(--color-bg-tertiary); }

.col-cb { width: 28px; }
.col-num { width: 32px; }
.col-time { width: 90px; white-space: nowrap; }
.col-ben, .col-zhi { width: 60px; }
.rl-gua-link { color: var(--color-accent-light); cursor: pointer; }
.rl-gua-link:hover { text-decoration: underline; }

.rl-pager { display: flex; align-items: center; justify-content: center; gap: var(--space-3); margin-top: var(--space-3); }
.rl-pager button { padding: 2px 10px; background: var(--color-bg-tertiary); color: var(--color-text-primary); border: 1px solid var(--color-border-primary); border-radius: var(--radius-sm); cursor: pointer; font-size: var(--font-size-sm); }
.rl-pager button:disabled { opacity: 0.4; cursor: not-allowed; }
.rl-pager span { font-size: var(--font-size-xs); color: var(--color-text-muted); }
</style>
