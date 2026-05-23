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

onUnmounted(() => {
  clearTimeout(debounceTimer)
})

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
  debounceTimer = setTimeout(() => {
    page.value = 1
    loadData()
  }, 300)
}

function onTagFilter(tagId) {
  selectedTagId.value = tagId
  page.value = 1
  loadData()
}

function onPageChange(p) {
  page.value = p
  loadData()
}

function selectGuali(item) {
  store.selectGuali(item.id)
}

function totalPages() {
  return Math.ceil(total.value / pageSize)
}

function formatTime(t) {
  if (!t) return ''
  return t.slice(0, 10)
}
</script>

<template>
  <div class="guali-list">
    <div class="list-toolbar">
      <input
        v-model="keyword"
        class="search-input"
        placeholder="搜索占问事由..."
        @input="onSearch"
      />
    </div>

    <div class="tag-filters" v-if="store.tagTree.length">
      <button
        :class="{ active: !selectedTagId }"
        @click="onTagFilter(null)"
      >全部</button>
      <button
        v-for="t in store.tagTree"
        :key="t.id"
        :class="{ active: selectedTagId === t.id }"
        @click="onTagFilter(t.id)"
      >{{ t.name }}</button>
    </div>

    <div class="cards" v-if="!loading">
      <div
        v-for="item in items"
        :key="item.id"
        class="card"
        :class="{ selected: store.currentGualiId === item.id }"
        @click="selectGuali(item)"
      >
        <div class="card-time">{{ formatTime(item.zhanwen_time) }}</div>
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
.guali-list { padding: 12px; }
.list-toolbar { margin-bottom: 12px; }
.search-input { width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 4px; }
.tag-filters { margin-bottom: 12px; display: flex; gap: 6px; flex-wrap: wrap; }
.tag-filters button {
  padding: 4px 12px; border: 1px solid #ccc; border-radius: 14px;
  background: #fff; cursor: pointer; font-size: 13px;
}
.tag-filters button.active { background: #409eff; color: #fff; border-color: #409eff; }
.cards { display: flex; flex-direction: column; gap: 8px; }
.card {
  padding: 10px 12px; border: 1px solid #eee; border-radius: 6px;
  cursor: pointer; transition: background 0.2s;
}
.card:hover { background: #f5f5f5; }
.card.selected { background: #e6f0ff; border-color: #409eff; }
.card-time { font-size: 12px; color: #999; }
.card-shiyou { font-size: 14px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.card-tags { margin-top: 4px; display: flex; gap: 4px; }
.tag-badge { padding: 1px 8px; background: #e8f5e9; border-radius: 10px; font-size: 12px; }
.empty { color: #999; text-align: center; padding: 40px; }
.loading { text-align: center; padding: 40px; color: #999; }
.pagination { display: flex; justify-content: center; align-items: center; gap: 16px; margin-top: 16px; }
.pagination button { padding: 6px 16px; border: 1px solid #ccc; border-radius: 4px; background: #fff; cursor: pointer; }
.pagination button:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
