import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { fetchSearchResults } from '../api/index.js'

let _condCounter = 0

export const useSearchStore = defineStore('search', () => {
  const conditions = ref([])
  const logicChain = ref([])
  const results = ref([])
  const pagination = ref({ page: 1, pageSize: 50, total: 0 })
  const sortOrder = ref('desc')
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
      // 条件组
      if (c.groupType === 'same_yao') {
        const srcs = c.sources.join('/')
        const sub = c.conditions.map(sc => `${FIELD_LABELS[sc.field] || sc.field || '(空)'} ${OP_LABELS[sc.operator] || sc.operator} ${sc.value || '(空)'}`).join(' AND ')
        return `同一爻[${srcs}](${sub})`
      }
      if (c.groupType === 'same_position') {
        const srcs = c.sources.map(s => `${s.source}(${s.conditions.map(sc => `${FIELD_LABELS[sc.field] || sc.field} ${OP_LABELS[sc.operator]} ${sc.value}`).join(',')})`).join('; ')
        return `同爻位[第${c.position}爻](${srcs})`
      }
      if (c.groupType === 'feishen') {
        return `飞神(${c.feishenType},用神${c.yongshen})`
      }
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
  function _genGroupId() { return `cg_${++_condCounter}` }

  function addCondition(type) {
    const id = _genId()
    const base = { id, field: '', operator: 'equals', value: '', scope: 'ben_gua' }
    if (type === 'relation') {
      conditions.value.push({ ...base, field: '_rel', value: 'true', scope: null, left_type: 'yao_object', left_value: '', left_scope: 'ben_gua', middle_type: null, middle_value: '', middle_scope: 'ben_gua', relation: '生', right_type: 'yao_object', right_value: '', right_scope: 'ben_gua', bureau: '' })
    } else {
      conditions.value.push(base)
    }
    _syncLogicChainForAdd(id, false)
    return id
  }

  // ── 条件组 ──

  function addConditionGroup(groupType) {
    const id = _genGroupId()
    if (groupType === 'same_yao') {
      conditions.value.push({ id, groupType: 'same_yao', sources: ['本卦'], conditions: [{ field: '', operator: 'equals', value: '' }] })
    } else if (groupType === 'same_position') {
      conditions.value.push({ id, groupType: 'same_position', position: 1, sources: [] })
    } else if (groupType === 'feishen') {
      conditions.value.push({ id, groupType: 'feishen', feishenType: '增删飞神', yongshen: '妻财' })
    }
    _syncLogicChainForAdd(id, true)
    return id
  }

  function removeConditionGroup(id) {
    conditions.value = conditions.value.filter(c => c.id !== id)
    _syncLogicChainForRemove(id)
  }

  function updateConditionGroup(id, patch) {
    const idx = conditions.value.findIndex(c => c.id === id)
    if (idx >= 0) Object.assign(conditions.value[idx], patch)
  }

  function addSubCondition(groupId, srcIdx) {
    const g = conditions.value.find(c => c.id === groupId)
    if (!g?.groupType) return
    if (g.groupType === 'same_yao') {
      g.conditions.push({ field: '', operator: 'equals', value: '' })
    } else if (g.groupType === 'same_position') {
      if (srcIdx !== undefined && g.sources[srcIdx]) {
        g.sources[srcIdx].conditions.push({ field: '', operator: 'equals', value: '' })
      } else if (g.sources.length) {
        g.sources[0].conditions.push({ field: '', operator: 'equals', value: '' })
      }
    }
  }

  function removeSubCondition(groupId, subIdx, srcIdx) {
    const g = conditions.value.find(c => c.id === groupId)
    if (!g?.groupType) return
    if (g.groupType === 'same_yao') {
      g.conditions.splice(subIdx, 1)
    } else if (g.groupType === 'same_position' && srcIdx !== undefined) {
      g.sources[srcIdx].conditions.splice(subIdx, 1)
    }
  }

  function updateSubCondition(groupId, subIdx, patch, srcIdx) {
    const g = conditions.value.find(c => c.id === groupId)
    if (!g?.groupType) return
    let target
    if (g.groupType === 'same_yao') {
      target = g.conditions[subIdx]
    } else if (g.groupType === 'same_position' && srcIdx !== undefined) {
      target = g.sources[srcIdx].conditions[subIdx]
    }
    if (target) Object.assign(target, patch)
  }

  function removeCondition(id) {
    conditions.value = conditions.value.filter(c => c.id !== id)
    _syncLogicChainForRemove(id)
  }

  function updateCondition(id, patch) {
    const idx = conditions.value.findIndex(c => c.id === id)
    if (idx >= 0) Object.assign(conditions.value[idx], patch)
  }

  function setLogic(chain) { logicChain.value = chain }

  // 增量维护逻辑链：新条件追加时默认 AND
  function _syncLogicChainForAdd(newId, isGroup) {
    const chain = logicChain.value
    if (chain.length > 0) chain.push({ type: 'and' })
    chain.push({ type: isGroup ? 'condition_group' : 'condition', id: newId })
  }

  function _syncLogicChainForRemove(removedId) {
    const chain = logicChain.value
    // 找到该 condition 在链中的位置
    const idx = chain.findIndex(l => l.id === removedId)
    if (idx < 0) return
    // 移除它前后的 AND/OR 连接器
    if (idx > 0 && (chain[idx - 1].type === 'and' || chain[idx - 1].type === 'or')) {
      chain.splice(idx - 1, 1)  // 先删前面的连接器
      const newIdx = chain.findIndex(l => l.id === removedId)
      chain.splice(newIdx, 1)     // 再删条件本身
    } else if (idx < chain.length - 1 && (chain[idx + 1].type === 'and' || chain[idx + 1].type === 'or')) {
      chain.splice(idx, 1)        // 删条件
      chain.splice(idx, 1)        // 删后面的连接器
    } else {
      chain.splice(idx, 1)        // 只有一个条件，直接删
    }
    // 如果链为空或只剩 and/or，清空
    const hasCondition = chain.some(l => l.type === 'condition' || l.type === 'condition_group')
    if (!hasCondition) logicChain.value = []
  }

  // 页面加载时，如果 logicChain 为空但有条件，重建
  function rebuildLogicChain() {
    if (logicChain.value.length > 0) return  // 已有则不动
    const chain = []
    const items = conditions.value.filter(c => c.id)
    for (let i = 0; i < items.length; i++) {
      if (i > 0) chain.push({ type: 'and' })
      chain.push({ type: items[i].groupType ? 'condition_group' : 'condition', id: items[i].id })
    }
    logicChain.value = chain
  }

  function toggleLogicOp(logicIdx) {
    const item = logicChain.value[logicIdx]
    if (!item || (item.type !== 'and' && item.type !== 'or')) return
    item.type = item.type === 'and' ? 'or' : 'and'
  }

  function toggleNot(condId) {
    // 在 condition 前插入或移除 NOT
    const idx = logicChain.value.findIndex(l => l.id === condId)
    if (idx < 0) return
    if (idx > 0 && logicChain.value[idx - 1].type === 'not') {
      logicChain.value.splice(idx - 1, 1)
    } else {
      logicChain.value.splice(idx, 0, { type: 'not' })
    }
  }

  function hasNot(condId) {
    const idx = logicChain.value.findIndex(l => l.id === condId)
    return idx > 0 && logicChain.value[idx - 1].type === 'not'
  }

  // 括号：左括号 ( 加在条件前，右括号 ) 加在条件后
  function addOpenBracket(condId) {
    const idx = logicChain.value.findIndex(l => l.id === condId)
    if (idx < 0) return
    if (idx > 0 && logicChain.value[idx - 1].type === '(') {
      logicChain.value.splice(idx - 1, 1)  // 已有则移除
    } else {
      logicChain.value.splice(idx, 0, { type: '(' })
    }
  }

  function addCloseBracket(condId) {
    const idx = logicChain.value.findIndex(l => l.id === condId)
    if (idx < 0) return
    // 向后找 )，跳过 and/or/not
    for (let j = idx + 1; j < logicChain.value.length; j++) {
      if (logicChain.value[j].type === ')') {
        logicChain.value.splice(j, 1)
        return
      }
      if (logicChain.value[j].type === 'condition' || logicChain.value[j].type === 'condition_group') break
    }
    // 找到下一个 condition 或末尾前插入 )
    let ins = idx + 1
    while (ins < logicChain.value.length && (logicChain.value[ins].type === 'and' || logicChain.value[ins].type === 'or' || logicChain.value[ins].type === 'not')) {
      ins++
    }
    logicChain.value.splice(ins, 0, { type: ')' })
  }

  function checkBracketBalance() {
    let depth = 0
    for (const item of logicChain.value) {
      if (item.type === '(') depth++
      if (item.type === ')') depth--
      if (depth < 0) return '括号不匹配：多余的右括号'
    }
    if (depth > 0) return `括号不匹配：缺少 ${depth} 个右括号`
    return null
  }

  async function executeSearch() {
    const bracketErr = checkBracketBalance()
    if (bracketErr) { alert(bracketErr); return }
    loading.value = true
    try {
      const body = {
        conditions: conditions.value,
        logic: logicChain.value,
        pagination: { page: pagination.value.page, page_size: pagination.value.pageSize },
        sort_order: sortOrder.value,
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
    addConditionGroup, removeConditionGroup, updateConditionGroup,
    addSubCondition, removeSubCondition, updateSubCondition,
    setLogic, rebuildLogicChain, toggleLogicOp, toggleNot, hasNot, addOpenBracket, addCloseBracket, checkBracketBalance,
    sortOrder, executeSearch, setPage,
    loadSchemes, saveScheme, applyScheme, deleteScheme,
  }
})
