<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useAppStore } from '../stores/index.js'
import { fetchGualiList, fetchTagTree } from '../api/index.js'

const store = useAppStore()

const items = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 20
const keyword = ref('')
const selectedTagId = ref(null)
const loading = ref(false)

let debounceTimer = null

onMounted(async () => {
  await loadData()
  if (!store.tagTreeLoaded) {
    try {
      const res = await fetchTagTree()
      store.tagTree = res.data.data || []
      store.tagTreeLoaded = true
    } catch { /* ok */ }
  }
})

onUnmounted(() => clearTimeout(debounceTimer))

async function loadData() {
  loading.value = true
  try {
    const res = await fetchGualiList({
      page: page.value,
      page_size: pageSize,
      keyword: keyword.value || undefined,
      tag_id: selectedTagId.value || undefined,
    })
    items.value = res.data.data?.items || []
    total.value = res.data.data?.total || 0
  } finally {
    loading.value = false
  }
}

function onSearch() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => { page.value = 1; loadData() }, 300)
}

function onTagFilter(tagId) {
  selectedTagId.value = tagId
  page.value = 1
  loadData()
}

function onPageChange(p) { page.value = p; loadData() }
function selectGuali(item) { store.selectGuali(item.id) }

function totalPages() { return Math.ceil(total.value / pageSize) }
function formatTime(t) { return t ? t.slice(0, 10) : '' }
</script>

<template>
  <div class="guali-list">
    <div class="list-toolbar">
      <input v-model="keyword" class="search-input" placeholder="搜索占问事由..." @input="onSearch" />
    </div>

    <div class="tag-filters" v-if="store.tagTree.length">
      <button :class="{ active: !selectedTagId }" @click="onTagFilter(null)">全部</button>
      <button v-for="t in store.tagTree" :key="t.id" :class="{ active: selectedTagId === t.id }" @click="onTagFilter(t.id)">{{ t.name }}</button>
    </div>

    <div class="cards" v-if="!loading">
      <div v-for="item in items" :key="item.id"
        class="card" :class="{ selected: store.currentGualiId === item.id }"
        @click="selectGuali(item)">
        <div class="card-top">
          <span class="card-id">ID: {{ item.id }}</span>
          <span class="card-time">{{ formatTime(item.zhanwen_time) }}</span>
        </div>
        <div class="card-shiyou">{{ item.zhanwen_shiyou }}</div>
        <div class="card-tags" v-if="item.tags?.length">
          <span v-for="t in item.tags" :key="t" class="tag-badge">{{ t }}</span>
        </div>
      </div>
      <p v-if="!items.length" class="empty">暂无卦例</p>
    </div>
    <div v-else class="loading">加载中...</div>

    <div class="pagination" v-if="totalPages() > 1">
      <button :disabled="page <= 1" @click="onPageChange(page - 1)">上一页</button>
      <span>{{ page }} / {{ totalPages() }}</span>
      <button :disabled="page >= totalPages()" @click="onPageChange(page + 1)">下一页</button>
    </div>
  </div>
</template>

<style scoped>
.guali-list { padding: var(--space-3); background: transparent; }
.list-toolbar { margin-bottom: var(--space-3); }
.search-input {
  width: 100%; padding: var(--space-2); border: 1px solid var(--color-border-primary);
  border-radius: var(--radius-md); background: var(--color-bg-input);
  color: var(--color-text-primary); font-size: var(--font-size-sm);
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
}
.search-input::placeholder { color: var(--color-text-muted); }
.search-input:focus { border-color: var(--color-accent); box-shadow: var(--shadow-glow); }

.tag-filters { margin-bottom: var(--space-3); display: flex; gap: 6px; flex-wrap: wrap; }
.tag-filters button {
  padding: 4px 12px; border: 1px solid var(--color-border-primary);
  border-radius: var(--radius-full); background: var(--color-bg-secondary);
  color: var(--color-text-secondary); cursor: pointer; font-size: var(--font-size-xs);
  transition: all var(--transition-fast);
}
.tag-filters button:hover { background: var(--color-bg-tertiary); color: var(--color-text-primary); }
.tag-filters button.active { background: var(--color-accent-gradient); color: #fff; border-color: transparent; }

.cards { display: flex; flex-direction: column; gap: var(--space-2); }
.card {
  padding: var(--space-3); border: 1px solid var(--color-border-primary);
  border-radius: var(--radius-lg); background: var(--color-bg-secondary);
  cursor: pointer; box-shadow: var(--shadow-sm);
  transition: all var(--transition-fast);
}
.card:hover { background: var(--color-bg-tertiary); box-shadow: var(--shadow-md); transform: translateY(-1px); }
.card.selected { background: var(--color-accent-soft); border-color: var(--color-accent); box-shadow: var(--shadow-glow); }
.card-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-1); }
.card-id { font-size: var(--font-size-xs); color: var(--color-text-muted); font-weight: bold; }
.card-time { font-size: var(--font-size-xs); color: var(--color-text-secondary); }
.card-shiyou { font-size: var(--font-size-base); color: var(--color-text-primary); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.card-tags { margin-top: var(--space-1); display: flex; gap: var(--space-1); }
.tag-badge { padding: 1px 8px; background: var(--color-badge-bg); color: var(--color-badge-text); border-radius: var(--radius-sm); font-size: var(--font-size-xs); }

.empty, .loading { color: var(--color-text-muted); text-align: center; padding: var(--space-10); }
.pagination { display: flex; justify-content: center; align-items: center; gap: var(--space-4); margin-top: var(--space-4); }
.pagination button { padding: 6px 16px; border: 1px solid var(--color-border-primary); border-radius: var(--radius-md); background: var(--color-bg-secondary); color: var(--color-text-primary); cursor: pointer; transition: background var(--transition-fast); }
.pagination button:hover:not(:disabled) { background: var(--color-bg-tertiary); }
.pagination button:disabled { opacity: 0.4; cursor: not-allowed; }
.pagination span { color: var(--color-text-secondary); font-size: var(--font-size-sm); }
</style>
