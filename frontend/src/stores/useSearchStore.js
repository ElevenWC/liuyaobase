import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { fetchSearchResults } from '../api/index.js'

let _condCounter = 0

export const useSearchStore = defineStore('search', () => {
  const conditions = ref([])
  const logicChain = ref([])
  const results = ref([])
  const pagination = ref({ page: 1, pageSize: 50, total: 0 })
  const loading = ref(false)

  // 自然语言表达式预览
  const expressionPreview = computed(() => {
    if (!conditions.value.length) return '未设置条件（将返回全部卦例）'
    const parts = conditions.value.map(c => {
      const scopeText = c.scope ? { ben_gua: '本卦', zhi_gua: '之卦', bian_yao: '变爻', yimao: '易冒', zengshan: '增删' }[c.scope] || c.scope : ''
      return scopeText ? `${scopeText}${c.field}${c.operator}${c.value}` : `${c.field} ${c.operator} ${c.value}`
    })
    return parts.join(' AND ') + ` （第${pagination.value.page}页）`
  })

  function _genId() { return `cond_${++_condCounter}` }

  function addCondition(type) {
    const id = _genId()
    const base = { id, field: '', operator: 'equals', value: '', scope: 'ben_gua' }
    if (type === 'relation') {
      conditions.value.push({ ...base, field: '_rel', value: 'true', scope: null, left_type: 'yao_object', left_value: '', relation: '生', right_type: 'yao_object', right_value: '', bureau: null })
    } else {
      conditions.value.push(base)
    }
    return id
  }

  function removeCondition(id) {
    conditions.value = conditions.value.filter(c => c.id !== id)
    logicChain.value = logicChain.value.filter(l => l.id !== id)
  }

  function updateCondition(id, patch) {
    const idx = conditions.value.findIndex(c => c.id === id)
    if (idx >= 0) Object.assign(conditions.value[idx], patch)
  }

  function setLogic(chain) { logicChain.value = chain }

  async function executeSearch() {
    loading.value = true
    try {
      const body = {
        conditions: conditions.value,
        logic: logicChain.value,
        pagination: { page: pagination.value.page, page_size: pagination.value.pageSize },
      }
      const res = await fetchSearchResults(body)
      if (res.data.code === 200 && res.data.data) {
        results.value = res.data.data.results || []
        pagination.value.total = res.data.data.total || 0
      }
    } catch { results.value = [] }
    finally { loading.value = false }
  }

  function setPage(page) { pagination.value.page = page; executeSearch() }

  // 自定义方案 localStorage
  const STORAGE_KEY = 'c3_search_schemes'

  function loadSchemes() {
    try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]') } catch { return [] }
  }

  function saveScheme(name) {
    const schemes = loadSchemes()
    // 去重同名
    const exist = schemes.findIndex(s => s.name === name)
    const entry = { name, conditions: JSON.parse(JSON.stringify(conditions.value)), logic: JSON.parse(JSON.stringify(logicChain.value)), time: Date.now() }
    if (exist >= 0) schemes[exist] = entry
    else schemes.push(entry)
    localStorage.setItem(STORAGE_KEY, JSON.stringify(schemes))
  }

  function applyScheme(scheme) {
    conditions.value = JSON.parse(JSON.stringify(scheme.conditions))
    logicChain.value = JSON.parse(JSON.stringify(scheme.logic || []))
    executeSearch()
  }

  function deleteScheme(name) {
    const schemes = loadSchemes().filter(s => s.name !== name)
    localStorage.setItem(STORAGE_KEY, JSON.stringify(schemes))
  }

  return {
    conditions, logicChain, results, pagination, loading,
    expressionPreview, addCondition, removeCondition, updateCondition,
    setLogic, executeSearch, setPage,
    loadSchemes, saveScheme, applyScheme, deleteScheme,
  }
})
