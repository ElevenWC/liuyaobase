<script setup>
import { useSearchStore } from '../stores/useSearchStore.js'
import FieldLibrary from '../components/Search/FieldLibrary.vue'
import ConditionBuilder from '../components/Search/ConditionBuilder.vue'
import ResultList from '../components/Search/ResultList.vue'

const store = useSearchStore()

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
        <button class="sp-btn sp-btn-search" :disabled="store.loading" @click="store.executeSearch()">
          {{ store.loading ? '检索中...' : '搜索' }}
        </button>
        <button class="sp-btn sp-btn-clear" @click="store.conditions = []; store.logicChain = []; store.results = []">清空</button>
      </div>
    </div>

    <!-- 中部：字段库 + 条件构建 -->
    <div class="sp-main">
      <FieldLibrary @select-field="onFieldSelect" />
      <ConditionBuilder />
    </div>

    <!-- 底部：结果列表 -->
    <div class="sp-results">
      <ResultList
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
.sp-actions { display: flex; gap: var(--space-2); flex-shrink: 0; }
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

.sp-main {
  display: flex; gap: var(--space-3);
  flex: 1; min-height: 0;
}

.sp-results {
  flex-shrink: 0;
  max-height: 45%;
  overflow-y: auto;
}
</style>
