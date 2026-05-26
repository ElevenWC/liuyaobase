<script setup>
import { ref, onMounted } from 'vue'
import { useSearchStore } from '../stores/useSearchStore.js'
import { fetchTagTree, addGualiTag } from '../api/index.js'
import FieldLibrary from '../components/Search/FieldLibrary.vue'
import ConditionBuilder from '../components/Search/ConditionBuilder.vue'
import ResultList from '../components/Search/ResultList.vue'

const store = useSearchStore()
const fieldLibCollapsed = ref(false)
const resultListRef = ref(null)

// 批量打标签
const tagTree = ref([])
const showTagPicker = ref(false)
const batchTagging = ref(false)

onMounted(async () => {
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
    // 数目判断后端联调尚未完成
    return
  }
  if (type === 'relation') {
    store.addCondition('relation')
  } else {
    const id = store.addCondition('normal')
    if (cat === 'time' || cat === 'gua') {
      store.updateCondition(id, { field, scope: null })
    } else if (type === 'shensha') {
      store.updateCondition(id, { field, value: '妻财爻' })
    } else {
      store.updateCondition(id, { field })
    }
  }
}

function onPageChange(page) {
  store.setPage(page)
}
</script>

<template>
  <div class="search-page">
    <!-- 顶部：表达式预览 + 操作 -->
    <div class="sp-toolbar">
      <div class="sp-expression">{{ store.expressionPreview }}</div>
      <div class="sp-actions">
        <button v-if="selectedCount()" class="sp-btn sp-btn-tag" @click="showTagPicker = !showTagPicker">
          {{ batchTagging ? '打标中...' : `打标签(${selectedCount()})` }}
        </button>
        <div v-if="showTagPicker" class="tag-picker">
          <span v-for="t in flatTags(tagTree)" :key="t.id"
            class="tag-opt" @click="batchAddTag(t.id)">{{ t.indent }}{{ t.name }}</span>
        </div>
        <button class="sp-btn sp-btn-search" :disabled="store.loading" @click="store.executeSearch()">
          {{ store.loading ? '检索中...' : '搜索' }}
        </button>
        <button class="sp-btn sp-btn-clear" @click="store.conditions = []; store.logicChain = []; store.results = []">清空</button>
      </div>
    </div>

    <!-- 中部：字段库 + 条件构建 -->
    <div class="sp-main">
      <div v-if="fieldLibCollapsed" class="fl-toggle collapsed" @click="fieldLibCollapsed = false" title="展开字段库">
        <span>◀</span>
      </div>
      <template v-else>
        <FieldLibrary @select-field="onFieldSelect" />
        <div class="fl-toggle" @click="fieldLibCollapsed = true" title="收起字段库">
          <span>▶</span>
        </div>
      </template>
      <ConditionBuilder />
    </div>

    <!-- 底部：结果列表 -->
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

.sp-toolbar {
  display: flex; align-items: center; gap: var(--space-3);
  padding: var(--space-2) var(--space-3);
  background: var(--color-bg-secondary);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  flex-shrink: 0;
}
.sp-expression {
  flex: 1;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  min-height: 1.5em;
}
.sp-actions { display: flex; gap: var(--space-2); flex-shrink: 0; position: relative; }
.sp-btn {
  padding: 4px 16px; border-radius: var(--radius-md); font-size: var(--font-size-sm);
  cursor: pointer; border: 1px solid var(--color-border-primary); transition: all var(--transition-fast);
}
.sp-btn-search {
  background: var(--color-accent); color: #fff; border-color: var(--color-accent);
}
.sp-btn-search:hover { filter: brightness(1.1); }
.sp-btn-search:disabled { opacity: 0.5; cursor: not-allowed; }
.sp-btn-clear {
  background: var(--color-bg-tertiary); color: var(--color-text-secondary);
}
.sp-btn-clear:hover { border-color: var(--color-danger); color: var(--color-danger); }
.sp-btn-tag {
  background: var(--color-bg-tertiary); color: var(--color-accent-light);
  border-color: var(--color-accent);
}
.sp-btn-tag:hover { background: var(--color-accent); color: #fff; }
.tag-picker {
  position: absolute; top: 100%; right: 0; margin-top: 4px; z-index: 200;
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

.fl-toggle {
  width: 18px; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  background: var(--color-bg-secondary); border-radius: var(--radius-md);
  cursor: pointer; color: var(--color-text-muted); font-size: var(--font-size-xs);
  transition: all var(--transition-fast); user-select: none;
}
.fl-toggle:hover { background: var(--color-bg-tertiary); color: var(--color-text-secondary); }
.fl-toggle.collapsed { width: 24px; }
.fl-toggle.collapsed span { transform: rotate(180deg); }

.sp-results {
  flex-shrink: 0;
  max-height: 45%;
  overflow-y: auto;
}
</style>
