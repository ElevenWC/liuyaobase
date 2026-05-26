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

  // 字段名 → 中文标签
  const FIELD_LABELS = {
    ben_liuqin: '本卦六亲', ben_dizhi: '本卦地支', ben_shi_ying: '本卦世应', ben_yao_type: '本卦爻类型',
    ben_tiangan: '本卦天干', is_dong: '本卦动爻', is_an_dong: '本卦暗动', liushen: '六神',
    yao_position: '爻位', zengshan_exists: '有伏神',
    zhi_liuqin: '之卦六亲', zhi_dizhi: '之卦地支', zhi_shi_ying: '之卦世应', zhi_yao_type: '之卦爻类型',
    yimao_liuqin: '易冒六亲', yimao_dizhi: '易冒地支',
    zengshan_liuqin: '增删六亲', zengshan_dizhi: '增删地支',
    ben_palace: '本卦卦宫', ben_palace_type: '本卦宫位', ben_special_type: '本卦特殊类型',
    zhi_palace: '之卦卦宫', zhi_palace_type: '之卦宫位', zhi_special_type: '之卦特殊类型',
    fan_yin_yimao: '易冒反吟', fan_yin_yaobian: '爻变反吟', fu_yin: '伏吟',
    year_pillar: '年柱', year_gan: '年干', year_zhi: '年支',
    month_pillar: '月柱', month_gan: '月干', month_zhi: '月支',
    day_pillar: '日柱', day_gan: '日干', day_zhi: '日支', xun_kong: '旬空',
    is_ganlu: '是干禄', dai_ganlu: '带干禄', ganlu: '是或带干禄',
    is_yima: '是驿马', dai_yima: '带驿马', yima: '是或带驿马',
    is_yangren: '是羊刃', dai_yangren: '带羊刃', yangren: '是或带羊刃',
    is_taohua: '是桃花', dai_taohua: '带桃花', taohua: '是或带桃花',
  }
  const OP_LABELS = { equals: '=', not_equals: '≠', in: '∈', not_in: '∉', gt: '>', lt: '<', gte: '≥', lte: '≤', range: '∈' }
  const SCOPE_MAP = { ben_gua: '本卦', zhi_gua: '之卦', bian_yao: '变爻', yimao: '易冒', zengshan: '增删' }

  // 自然语言表达式预览
  const expressionPreview = computed(() => {
    if (!conditions.value.length) return '未设置条件（将返回全部卦例）'
    const parts = conditions.value.map(c => {
      // 关系条件
      if (c.relation) {
        const yu = ['长生', '帝旺', '墓', '绝'].includes(c.relation) ? '于 ' : ''
        if (c.relation === '三合') {
          const b = c.bureau ? ` ${c.bureau}局` : ''
          return `${c.left_value || '?'} ${c.middle_value || '?'} ${c.right_value || '?'} 三合${b}`
        }
        return `${c.left_value || '?'} ${c.relation} ${yu}${c.right_value || '?'}`
      }
      // 神煞条件
      const shenshaLabel = FIELD_LABELS[c.field]
      if (shenshaLabel && (c.field.startsWith('is_') || c.field.startsWith('dai_') || ['ganlu','yima','yangren','taohua'].includes(c.field))) {
        const scopeText = c.scope ? (SCOPE_MAP[c.scope] || c.scope) + ' ' : ''
        return `${scopeText}${c.value || '?'} ${shenshaLabel}`
      }
      // 普通条件
      const label = FIELD_LABELS[c.field] || c.field
      const op = OP_LABELS[c.operator] || c.operator
      const scopeText = c.scope ? (SCOPE_MAP[c.scope] || c.scope) + ' ' : ''
      return `${scopeText}${label} ${op} ${c.value || '(空)'}`
    })
    return parts.join(' AND ') + ` （第${pagination.value.page}页）`
  })

  function _genId() { return `cond_${++_condCounter}` }

  function addCondition(type) {
    const id = _genId()
    const base = { id, field: '', operator: 'equals', value: '', scope: 'ben_gua' }
    if (type === 'relation') {
      conditions.value.push({ ...base, field: '_rel', value: 'true', scope: null, left_type: 'yao_object', left_value: '', middle_type: null, middle_value: null, relation: '生', right_type: 'yao_object', right_value: '', bureau: null })
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
