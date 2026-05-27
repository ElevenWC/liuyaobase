<script setup>
import { ref, onMounted } from 'vue'
import { useSearchStore } from '../stores/useSearchStore.js'
import { fetchTagTree, addGualiTag } from '../api/index.js'
import FieldLibrary from '../components/Search/FieldLibrary.vue'
import ConditionBuilder from '../components/Search/ConditionBuilder.vue'
import RecommendedSchemes from '../components/Search/RecommendedSchemes.vue'
import ResultList from '../components/Search/ResultList.vue'

const store = useSearchStore()
const fieldLibCollapsed = ref(false)
const resultListRef = ref(null)

// 批量打标签
const tagTree = ref([])
const showTagPicker = ref(false)
const batchTagging = ref(false)

onMounted(async () => {
  // 已有条件但无逻辑链时自动重建
  if (store.conditions.length && !store.logicChain.length) store.rebuildLogicChain()
  try {
    const res = await fetchTagTree()
    if (res.data.code === 200) tagTree.value = res.data.data || []
  } catch { /* 标签加载失败不影响检索功能 */ }
})

function flatTags(tree) {
  const result = []
  for (const node of tree) {
    result.push({ id: node.id, name: node.name, indent: '' })
    if (node.children) {
      for (const child of node.children) {
        result.push({ id: child.id, name: child.name, indent: '  └ ' })
      }
    }
  }
  return result
}

function selectedCount() {
  return resultListRef.value?.selected?.length || 0
}

async function batchAddTag(tagId) {
  const ids = resultListRef.value?.selected || []
  if (!ids.length || !tagId) return
  batchTagging.value = true
  let ok = 0
  for (const gualiId of ids) {
    try {
      await addGualiTag(gualiId, tagId)
      ok++
    } catch { /* 单个失败不影响其他 */ }
  }
  batchTagging.value = false
  showTagPicker.value = false
  // 清除选择
  if (resultListRef.value) resultListRef.value.selected = []
  if (ok > 0) alert(`已为 ${ok}/${ids.length} 个卦例添加标签`)
}

function onFieldSelect({ cat, field, type, label }) {
  if (type === 'count') {
    store.addCondition('normal')
    const c = store.conditions[store.conditions.length - 1]
    if (c) store.updateCondition(c.id, { field: '_count', scope: 'ben_gua', countAttr: 'liuqin', countValue: '妻财', operator: 'equals', value: '0' })
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
        <div v-if="selectedCount()" class="sp-batch-bar">
          <button class="sp-btn sp-btn-tag" @click="showTagPicker = !showTagPicker">
            {{ batchTagging ? '打标中...' : `批量打标签（已选 ${selectedCount()} 条）` }}
          </button>
          <div v-if="showTagPicker" class="tag-picker">
            <span v-for="t in flatTags(tagTree)" :key="t.id"
              class="tag-opt" @click="batchAddTag(t.id)">{{ t.indent }}{{ t.name }}</span>
          </div>
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

.sp-batch-bar { display: flex; align-items: center; gap: var(--space-2); margin-bottom: var(--space-2); position: relative; }
.sp-btn-tag {
  padding: 4px 12px; border-radius: var(--radius-md); font-size: var(--font-size-sm);
  cursor: pointer; border: 1px solid var(--color-accent);
  background: var(--color-bg-tertiary); color: var(--color-accent-light); transition: all var(--transition-fast);
}
.sp-btn-tag:hover { background: var(--color-accent); color: #fff; }
.tag-picker {
  position: absolute; top: 100%; left: 0; margin-top: 4px; z-index: 200;
  background: var(--color-bg-overlay); border: 1px solid var(--color-border-primary);
  border-radius: var(--radius-md); box-shadow: var(--shadow-md);
  padding: var(--space-1) 0; min-width: 140px; max-height: 240px; overflow-y: auto;
}
.tag-opt {
  display: block; padding: 4px 12px; font-size: var(--font-size-sm);
  color: var(--color-text-secondary); cursor: pointer; white-space: nowrap;
}
.tag-opt:hover { background: var(--color-bg-tertiary); color: var(--color-text-primary); }

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
