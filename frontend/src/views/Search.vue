<script setup>
import { ref, computed, onMounted } from 'vue'
import { useSearchStore } from '../stores/useSearchStore.js'
import { useAppStore } from '../stores/index.js'
import { fetchTagTree, addGualiTag, removeGualiTag, fetchSearchResults } from '../api/index.js'
import FieldLibrary from '../components/Search/FieldLibrary.vue'
import ConditionBuilder from '../components/Search/ConditionBuilder.vue'
import RecommendedSchemes from '../components/Search/RecommendedSchemes.vue'
import ResultList from '../components/Search/ResultList.vue'

const store = useSearchStore()
const appStore = useAppStore()
const fieldLibCollapsed = ref(false)
const resultListRef = ref(null)

// 批量打标签
const batchTagging = ref(false)
const batchTagId = ref(null)
const batchTagId2 = ref(null)

const batchLevel2Options = computed(() => {
  if (!batchTagId.value) return []
  const parent = appStore.tagTree.find(t => t.id === batchTagId.value)
  return parent?.children || []
})

function selectedTagId() {
  return batchTagId2.value || batchTagId.value || null
}

onMounted(async () => {
  // 已有条件但无逻辑链时自动重建
  if (store.conditions.length && !store.logicChain.length) store.rebuildLogicChain()
  try {
    const res = await fetchTagTree()
    if (res.data.code === 200) appStore.tagTree = res.data.data || []
  } catch { /* 标签加载失败不影响检索功能 */ }
})

function selectedCount() {
  return resultListRef.value?.selected?.length || 0
}

const selectAllResults = ref(false)

async function batchAddTag(tagId) {
  if (!tagId) return

  let ids = resultListRef.value?.selected || []
  // 全选所有结果：重新查询获取全部ID
  if (selectAllResults.value && store.pagination.total > 0) {
    batchTagging.value = true
    try {
      const allRes = await fetchSearchResults({
        conditions: store.conditions,
        logic: store.logicChain,
        pagination: { page: 1, page_size: 99999 },
      })
      ids = (allRes.data.data?.results || []).map(r => r.id)
    } catch { ids = []; alert('获取全部卦例失败') }
  }

  if (!ids.length) { batchTagging.value = false; return }
  batchTagging.value = true
  let ok = 0
  for (const gualiId of ids) {
    try {
      await addGualiTag(gualiId, tagId)
      ok++
    } catch { /* 单个失败不影响其他 */ }
  }
  batchTagging.value = false
  batchTagId.value = null
  batchTagId2.value = null
  selectAllResults.value = false
  if (resultListRef.value) resultListRef.value.clearSelection()
  if (ok === ids.length) alert(`已为全部 ${ok} 个卦例添加标签`)
  else if (ok > 0) alert(`已为 ${ok}/${ids.length} 个卦例添加标签（${ids.length - ok} 个失败）`)
  else alert('添加标签失败，请检查标签是否已存在')
}

async function batchRemoveTag(tagId) {
  if (!tagId) return
  let ids = resultListRef.value?.selected || []
  if (selectAllResults.value && store.pagination.total > 0) {
    try {
      const allRes = await fetchSearchResults({ conditions: store.conditions, logic: store.logicChain, pagination: { page: 1, page_size: 99999 } })
      ids = (allRes.data.data?.results || []).map(r => r.id)
    } catch { ids = [] }
  }
  if (!ids.length) return
  if (!confirm(`确认从 ${ids.length} 个卦例中删除此标签？`)) return
  batchTagging.value = true
  let ok = 0
  for (const gualiId of ids) {
    try { await removeGualiTag(gualiId, tagId); ok++ } catch { /* skip */ }
  }
  batchTagging.value = false
  batchTagId.value = null; batchTagId2.value = null; selectAllResults.value = false
  if (resultListRef.value) resultListRef.value.clearSelection()
  if (ok === ids.length) alert(`已从全部 ${ok} 个卦例中删除标签`)
  else if (ok > 0) alert(`已从 ${ok}/${ids.length} 个卦例中删除标签（${ids.length - ok} 个失败）`)
  else alert('删除标签失败')
}

function onFieldSelect({ cat, field, type, label }) {
  if (type === 'count') {
    store.addCondition('normal')
    const c = store.conditions[store.conditions.length - 1]
    if (c) store.updateCondition(c.id, { field: '_count', scope: 'ben_gua', countAttr: 'liuqin', countValue: '妻财', operator: 'equals', value: '0' })
    return
  }
  if (field === '_keyword') {
    store.addCondition('normal')
    const c = store.conditions[store.conditions.length - 1]
    if (c) store.updateCondition(c.id, { field: '_keyword', operator: 'equals', value: '', scope: null })
    return
  }
  if (field === '_tag') {
    store.addCondition('normal')
    const c = store.conditions[store.conditions.length - 1]
    if (c) store.updateCondition(c.id, { field: '_tag', tagId: null, tagId2: null, operator: 'equals', value: '', scope: null })
    return
  }
  if (type === 'relation') {
    store.addCondition('relation')
    const c = store.conditions[store.conditions.length - 1]
    const relMap = { shengke: '生', he_chong: '合', banhe: '半合', sanhe: '三合', xiangdeng: '=', shengwang: '长生' }
    if (c && relMap[field]) store.updateCondition(c.id, { relation: relMap[field], middle_type: field === 'sanhe' ? 'yao_object' : null })
  } else {
    const id = store.addCondition('normal')
    if (cat === 'time' || cat === 'gua') {
      store.updateCondition(id, { field, scope: null })
    } else if (type === 'shensha') {
      store.updateCondition(id, { field, value: '妻财爻' })
    } else {
      // 根据字段前缀自动设 scope
      let scope = 'ben_gua'
      if (field.startsWith('zhi_')) scope = 'bian_yao'
      else if (field.startsWith('yimao_')) scope = 'yimao'
      else if (field.startsWith('zengshan_')) scope = 'zengshan'
      store.updateCondition(id, { field, scope })
    }
  }
}

function onPageChange(page) {
  store.setPage(page)
}
</script>

<template>
  <div class="search-page">
    <!-- 左字段库 + 右（条件构建+结果列表） -->
    <div class="sp-main">
      <div v-if="fieldLibCollapsed" class="fl-toggle" @click="fieldLibCollapsed = false" title="展开字段库">
        <span>▸</span>
      </div>
      <div v-else class="fl-sidebar">
        <FieldLibrary @select-field="onFieldSelect" />
        <div class="fl-toggle" @click="fieldLibCollapsed = true" title="收起字段库">
          <span>◂</span>
        </div>
      </div>
      <div class="sp-right">
        <ConditionBuilder />
        <div v-if="selectedCount() || selectAllResults" class="sp-batch-bar">
          <label class="sp-all-check"><input type="checkbox" v-model="selectAllResults" /> 全选所有结果（共 {{ store.pagination.total }} 条）</label>
          <select v-model="batchTagId" class="sp-batch-sel" @change="batchTagId2=null">
            <option :value="null">一级标签</option>
            <option v-for="t in appStore.tagTree" :key="t.id" :value="t.id">{{ t.name }}</option>
          </select>
          <select v-if="batchTagId" v-model="batchTagId2" class="sp-batch-sel">
            <option :value="null">二级标签</option>
            <option v-for="t in batchLevel2Options" :key="t.id" :value="t.id">{{ t.name }}</option>
          </select>
          <button class="sp-batch-btn sp-batch-add" :disabled="!selectedTagId()" @click="batchAddTag(selectedTagId())">
            {{ batchTagging ? '打标中...' : `加标签(${selectAllResults ? store.pagination.total : selectedCount()})` }}
          </button>
          <button class="sp-batch-btn sp-batch-del" :disabled="!selectedTagId()" @click="batchRemoveTag(selectedTagId())">
            {{ batchTagging ? '删标中...' : `删标签(${selectAllResults ? store.pagination.total : selectedCount()})` }}
          </button>
        </div>
        <RecommendedSchemes />
        <div class="sp-results">
          <ResultList ref="resultListRef"
            :results="store.results"
            :total="store.pagination.total"
            :page="store.pagination.page"
            :page-size="store.pagination.pageSize"
            :loading="store.loading"
            @page-change="onPageChange"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.search-page {
  display: flex; flex-direction: column;
  height: calc(100vh - var(--navbar-height));
  background: var(--color-bg-primary);
  padding: var(--space-3);
  gap: var(--space-3);
  box-sizing: border-box;
}

.sp-batch-bar { display: flex; align-items: center; gap: var(--space-2); margin-bottom: var(--space-2); position: relative; flex-wrap: wrap; }
.sp-all-check { font-size: var(--font-size-xs); color: var(--color-text-secondary); display: flex; align-items: center; gap: 4px; cursor: pointer; accent-color: var(--color-accent); }
.sp-batch-sel { height: 26px; padding: 0 4px; background: var(--color-bg-input); color: var(--color-text-primary); border: 1px solid var(--color-border-primary); border-radius: var(--radius-sm); font-size: var(--font-size-sm); cursor: pointer; }
.sp-batch-sel:focus { outline: none; border-color: var(--color-accent); }
.sp-batch-btn { height: 26px; padding: 0 10px; border-radius: var(--radius-md); font-size: var(--font-size-xs); cursor: pointer; border: 1px solid var(--color-accent); transition: all var(--transition-fast); }
.sp-batch-add { background: var(--color-bg-tertiary); color: var(--color-accent-light); }
.sp-batch-add:hover { background: var(--color-accent); color: #fff; }
.sp-batch-del { background: var(--color-bg-tertiary); color: var(--color-danger); border-color: var(--color-danger); }
.sp-batch-del:hover { background: var(--color-danger); color: #fff; }
.sp-batch-btn:disabled { opacity: 0.4; cursor: not-allowed; }

.sp-main {
  display: flex; gap: var(--space-3);
  flex: 1; min-height: 0;
}

/* 左侧：字段库 + 折叠按钮 */
.fl-sidebar {
  display: flex; gap: var(--space-2);
  flex-shrink: 0;
}
.fl-toggle {
  width: 16px; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  background: var(--color-bg-secondary); border-radius: var(--radius-sm);
  cursor: pointer; color: var(--color-text-muted); font-size: 25px;
  transition: all var(--transition-fast); user-select: none;
}
.fl-toggle:hover { background: var(--color-bg-tertiary); color: var(--color-accent-light); }

/* 右侧：条件构建 + 结果列表 */
.sp-right {
  flex: 1; min-width: 0;
  display: flex; flex-direction: column; gap: var(--space-3);
}

.sp-results {
  flex: 1; min-height: 0;
  overflow-y: auto;
}
</style>
