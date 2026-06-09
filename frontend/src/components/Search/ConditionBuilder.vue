<script setup>
import { ref, computed } from 'vue'
import { useSearchStore } from '../../stores/useSearchStore.js'
import { useAppStore } from '../../stores/index.js'
import { GUA_NAME_SET } from '../../constants/guaNames.js'
import SameYaoGroup from './SameYaoGroup.vue'
import SamePositionGroup from './SamePositionGroup.vue'
import FeishenGroup from './FeishenGroup.vue'

const store = useSearchStore()
const appStore = useAppStore()
const condCollapsed = ref(false)
function isGroup(c) { return !!c.groupType }

// 括号组范围：从 logicChain 中提取 [start, end] 条件索引
const bracketGroups = computed(() => {
  const chain = store.logicChain
  const groups = []
  let depth = 0, start = -1, ci = 0
  for (const item of chain) {
    if (item.type === '(') { if (depth === 0) start = ci; depth++ }
    else if (item.type === ')') { depth--; if (depth === 0 && start >= 0) { groups.push({ start, end: ci - 1 }); start = -1 } }
    else if (item.type === 'condition' || item.type === 'condition_group') ci++
  }
  return groups
})

function isGroupStart(condIdx) { return bracketGroups.value.some(g => g.start === condIdx) }
function isGroupEnd(condIdx) { return bracketGroups.value.some(g => g.end === condIdx) }
function inBracketGroup(condIdx) { return bracketGroups.value.some(g => condIdx >= g.start && condIdx <= g.end) }

function groupSummary(c) {
  if (c.groupType === 'same_yao') return `${c.id} 同一爻[${c.sources.join('/')}]`
  if (c.groupType === 'same_position') return `${c.id} 同爻位[第${c.position||1}爻]`
  if (c.groupType === 'feishen') return `${c.id} 飞神[${c.feishenType}·${c.yongshen}]`
  return c.id
}

const SCOPE_OPTIONS = [
  { v: 'ben_gua', label: '本卦' },
  { v: 'bian_yao', label: '变爻' },
  { v: 'zhi_gua', label: '之卦静爻' },
  { v: 'yimao', label: '易冒伏神' },
  { v: 'zengshan', label: '增删伏神' },
]

const FIELD_OPTIONS = [
  { v: 'ben_liuqin', label: '本卦六亲', scopes: ['ben_gua'] },
  { v: 'ben_dizhi', label: '本卦地支', scopes: ['ben_gua'] },
  { v: 'ben_shi_ying', label: '本卦世应', scopes: ['ben_gua'] },
  { v: 'ben_yao_type', label: '本卦爻类型', scopes: ['ben_gua'] },
  { v: 'ben_tiangan', label: '本卦天干', scopes: ['ben_gua'] },
  { v: 'is_dong', label: '本卦动爻', scopes: ['ben_gua'] },
  { v: 'is_an_dong', label: '本卦暗动', scopes: ['ben_gua'] },
  { v: 'zengshan_exists', label: '有伏神', scopes: ['zengshan'] },
  { v: 'liushen', label: '六神', scopes: ['ben_gua', 'bian_yao', 'zhi_gua', 'yimao', 'zengshan'] },
  { v: 'yao_position', label: '爻位', scopes: ['ben_gua', 'bian_yao', 'zhi_gua', 'yimao', 'zengshan'] },
  { v: 'zhi_liuqin', label: '之卦六亲', scopes: ['bian_yao', 'zhi_gua'] },
  { v: 'zhi_dizhi', label: '之卦地支', scopes: ['bian_yao', 'zhi_gua'] },
  { v: 'zhi_shi_ying', label: '之卦世应', scopes: ['bian_yao', 'zhi_gua'] },
  { v: 'zhi_yao_type', label: '之卦爻类型', scopes: ['bian_yao', 'zhi_gua'] },
  { v: 'yimao_liuqin', label: '易冒六亲', scopes: ['yimao'] },
  { v: 'yimao_dizhi', label: '易冒地支', scopes: ['yimao'] },
  { v: 'zengshan_liuqin', label: '增删六亲', scopes: ['zengshan'] },
  { v: 'zengshan_dizhi', label: '增删地支', scopes: ['zengshan'] },
]

function availableFields(scope) {
  if (!scope) return FIELD_OPTIONS
  return FIELD_OPTIONS.filter(f => f.scopes.includes(scope))
}

// 60甲子（给年柱/月柱/日柱下拉用）
const _GAN = ['甲','乙','丙','丁','戊','己','庚','辛','壬','癸']
const _ZHI = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥']
const JIAZI = Array.from({length:60}, (_,i) => _GAN[i%10] + _ZHI[i%12])

const TIME_FIELDS = [
  { v: 'year_pillar', label: '年柱' },
  { v: 'year_gan', label: '年干' },
  { v: 'year_zhi', label: '年支' },
  { v: 'month_pillar', label: '月柱' },
  { v: 'month_gan', label: '月干' },
  { v: 'month_zhi', label: '月支' },
  { v: 'day_pillar', label: '日柱' },
  { v: 'day_gan', label: '日干' },
  { v: 'day_zhi', label: '日支' },
  { v: 'xun_kong', label: '旬空' },
]

const GUA_FIELDS = [
  { v: 'ben_palace', label: '本卦卦宫' },
  { v: 'ben_palace_type', label: '本卦宫位' },
  { v: 'ben_special_type', label: '本卦特殊类型' },
  { v: 'zhi_palace', label: '之卦卦宫' },
  { v: 'zhi_palace_type', label: '之卦宫位' },
  { v: 'zhi_special_type', label: '之卦特殊类型' },
  { v: 'fan_yin_yimao', label: '易冒反吟' },
  { v: 'fan_yin_yaobian', label: '爻变反吟' },
  { v: 'fu_yin', label: '伏吟' },
]

const LIUQIN_VALS = ['妻财', '官鬼', '父母', '兄弟', '子孙']
const SHIYING_VALS = ['世', '应']
const YAOTYPE_VALS = ['阳', '阴']
const OPERATORS = ['equals', 'not_equals']
const OP_DISPLAY = { equals: '= (等于)', not_equals: '≠ (不等于)' }
const GUA_PALACE_VALS = ['乾宫', '坤宫', '震宫', '巽宫', '坎宫', '离宫', '艮宫', '兑宫']
const PALACE_TYPE_VALS = ['本宫卦', '一世卦', '二世卦', '三世卦', '四世卦', '五世卦', '游魂卦', '归魂卦']
const SPECIAL_TYPE_VALS = ['六合', '六冲', '普通']
const FANYIN_VALS = ['无', '内卦', '外卦']
const DIZHI_VALS = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
const TIAN_GAN_VALS = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
const LIUSHEN_VALS = ['青龙', '朱雀', '勾陈', '螣蛇', '白虎', '玄武']

const SHENSHA_FIELDS = ['is_ganlu', 'dai_ganlu', 'is_yima', 'dai_yima', 'is_yangren', 'dai_yangren', 'is_taohua', 'dai_taohua', 'is_zaisha', 'dai_zaisha', 'is_jiesha', 'dai_jiesha', 'ganlu', 'yima', 'yangren', 'taohua', 'zaisha', 'jiesha']
const SHENSHA_TYPES = [
  { v: 'is_ganlu', label: '是干禄', mode: '是', shensha: '干禄' },
  { v: 'dai_ganlu', label: '带干禄', mode: '带', shensha: '干禄' },
  { v: 'is_yima', label: '是驿马', mode: '是', shensha: '驿马' },
  { v: 'dai_yima', label: '带驿马', mode: '带', shensha: '驿马' },
  { v: 'is_yangren', label: '是羊刃', mode: '是', shensha: '羊刃' },
  { v: 'dai_yangren', label: '带羊刃', mode: '带', shensha: '羊刃' },
  { v: 'is_taohua', label: '是桃花', mode: '是', shensha: '桃花' },
  { v: 'dai_taohua', label: '带桃花', mode: '带', shensha: '桃花' },
  { v: 'is_zaisha', label: '是灾煞', mode: '是', shensha: '灾煞' },
  { v: 'dai_zaisha', label: '带灾煞', mode: '带', shensha: '灾煞' },
  { v: 'is_jiesha', label: '是劫煞', mode: '是', shensha: '劫煞' },
  { v: 'dai_jiesha', label: '带劫煞', mode: '带', shensha: '劫煞' },
  { v: 'ganlu', label: '是或带干禄', mode: '是或带', shensha: '干禄' },
  { v: 'yima', label: '是或带驿马', mode: '是或带', shensha: '驿马' },
  { v: 'yangren', label: '是或带羊刃', mode: '是或带', shensha: '羊刃' },
  { v: 'taohua', label: '是或带桃花', mode: '是或带', shensha: '桃花' },
  { v: 'zaisha', label: '是或带灾煞', mode: '是或带', shensha: '灾煞' },
  { v: 'jiesha', label: '是或带劫煞', mode: '是或带', shensha: '劫煞' },
]

function isShensha(field) { return SHENSHA_FIELDS.includes(field) }
function isCount(field) { return field === '_count' }
function isKeyword(field) { return field === '_keyword' }
function isTag(field) { return field === '_tag' }
function isFushenFeishen(v) { return ['易冒伏神','增删伏神','易冒飞神','增删飞神'].includes(v) }

function level2Options(tagId) {
  if (!tagId) return []
  const parent = appStore.tagTree.find(t => t.id === tagId)
  return parent?.children || []
}

function getLogicOp(condIndex) {
  // 找到第 condIndex 个 condition 之前的 and/or 操作符
  const chain = store.logicChain
  let seen = 0
  for (let i = 0; i < chain.length; i++) {
    if (chain[i].type === 'condition' || chain[i].type === 'condition_group') {
      if (seen === condIndex) {
        // 向前找最近的 and/or
        for (let j = i - 1; j >= 0; j--) {
          if (chain[j].type === 'and' || chain[j].type === 'or') return chain[j].type
          if (chain[j].type === 'condition' || chain[j].type === 'condition_group') break
        }
        return 'and' // default
      }
      seen++
    }
  }
  return 'and'
}

function hasOpenBracket(condId) {
  const chain = store.logicChain
  const idx = chain.findIndex(l => l.id === condId)
  return idx > 0 && chain[idx - 1].type === '('
}
function hasCloseBracket(condId) {
  const chain = store.logicChain
  const idx = chain.findIndex(l => l.id === condId)
  if (idx < 0) return false
  // 向后找 )，跳过中间的 and/or/not
  for (let j = idx + 1; j < chain.length; j++) {
    if (chain[j].type === ')') return true
    if (chain[j].type === 'condition' || chain[j].type === 'condition_group') break
  }
  return false
}

function toggleLogicAt(condIndex) {
  const chain = store.logicChain
  let seen = 0
  for (let i = 0; i < chain.length; i++) {
    if (chain[i].type === 'condition' || chain[i].type === 'condition_group') {
      if (seen === condIndex) {
        for (let j = i - 1; j >= 0; j--) {
          if (chain[j].type === 'and' || chain[j].type === 'or') {
            chain[j].type = chain[j].type === 'and' ? 'or' : 'and'
            return
          }
          if (chain[j].type === 'condition' || chain[j].type === 'condition_group') break
        }
        return
      }
      seen++
    }
  }
}
const SHENGWANG_RELATIONS = ['长生', '帝旺', '墓', '绝']

const COUNT_SCOPES = [
  { v: 'ben_gua', label: '本卦' },
  { v: 'zhi_gua', label: '之卦' },
  { v: 'bian_yao', label: '变爻' },
  { v: 'zengshan', label: '增删伏神' },
]
const COUNT_ATTRS = [
  { v: 'liuqin', label: '六亲', vals: LIUQIN_VALS },
  { v: 'dizhi', label: '地支', vals: DIZHI_VALS },
  { v: 'yao_type', label: '爻类型', vals: YAOTYPE_VALS },
  { v: 'is_dong', label: '动爻', vals: [{v:'true',l:'是'},{v:'false',l:'否'}] },
  { v: 'is_an_dong', label: '暗动', vals: [{v:'true',l:'是'},{v:'false',l:'否'}] },
  { v: 'zengshan_exists', label: '有伏神', vals: [{v:'true',l:'有'},{v:'false',l:'无'}] },
]
const COUNT_OPS = ['equals', 'not_equals']

function currentCountAttr(cond) {
  return COUNT_ATTRS.find(a => a.v === cond.countAttr)
}

function fieldValueOptions(field) {
  if (field === 'ben_liuqin' || field === 'zhi_liuqin' || field === 'yimao_liuqin' || field === 'zengshan_liuqin') return LIUQIN_VALS
  if (field === 'ben_shi_ying' || field === 'zhi_shi_ying') return SHIYING_VALS
  if (field === 'ben_yao_type' || field === 'zhi_yao_type') return YAOTYPE_VALS
  if (field === 'ben_dizhi' || field === 'zhi_dizhi' || field === 'yimao_dizhi' || field === 'zengshan_dizhi') return DIZHI_VALS
  if (field === 'zengshan_exists') return ['true', 'false']
  if (field === 'is_dong' || field === 'is_an_dong') return [{v:'true', l:'存在'}, {v:'false', l:'不存在'}]
  if (field === 'liushen') return LIUSHEN_VALS
  if (field === 'ben_tiangan') return TIAN_GAN_VALS
  if (field === 'yao_position') return [{v:'1',l:'初爻'},{v:'2',l:'二爻'},{v:'3',l:'三爻'},{v:'4',l:'四爻'},{v:'5',l:'五爻'},{v:'6',l:'上爻'}]
  // 卦类
  if (field === 'ben_palace' || field === 'zhi_palace') return GUA_PALACE_VALS
  if (field === 'ben_palace_type' || field === 'zhi_palace_type') return PALACE_TYPE_VALS
  if (field === 'ben_special_type' || field === 'zhi_special_type') return SPECIAL_TYPE_VALS
  if (field === 'fan_yin_yimao' || field === 'fan_yin_yaobian' || field === 'fu_yin') return FANYIN_VALS
  // 时间
  if (field === 'year_zhi' || field === 'month_zhi' || field === 'day_zhi') return DIZHI_VALS
  if (field === 'year_gan' || field === 'month_gan' || field === 'day_gan') return TIAN_GAN_VALS
  if (field === 'year_pillar' || field === 'month_pillar' || field === 'day_pillar') return JIAZI
  if (field === 'xun_kong') return ['子丑', '寅卯', '辰巳', '午未', '申酉', '戌亥']
  return []
}

function addYaoCondition() {
  store.addCondition('normal')
  const c = store.conditions[store.conditions.length - 1]
  if (c) store.updateCondition(c.id, { field: 'ben_liuqin', operator: 'equals', value: '', scope: 'ben_gua' })
}
function addRelationCondition() { store.addCondition('relation') }
function addShenshaCondition() {
  store.addCondition('normal')
  const c = store.conditions[store.conditions.length - 1]
  if (c) store.updateCondition(c.id, { field: 'is_ganlu', value: '妻财爻', operator: 'equals' })
}
function addCountCondition() {
  store.addCondition('normal')
  const c = store.conditions[store.conditions.length - 1]
  if (c) store.updateCondition(c.id, { field: '_count', scope: 'ben_gua', countAttr: 'liuqin', countValue: '妻财', operator: 'equals', value: '0' })
}
function addGuaCondition() {
  store.addCondition('normal')
  const c = store.conditions[store.conditions.length - 1]
  if (c) store.updateCondition(c.id, { field: 'ben_palace', scope: null })
}
function addTimeCondition() {
  store.addCondition('normal')
  const c = store.conditions[store.conditions.length - 1]
  if (c) store.updateCondition(c.id, { field: 'day_zhi', scope: null })
}
function addKeywordCondition() {
  store.addCondition('normal')
  const c = store.conditions[store.conditions.length - 1]
  if (c) store.updateCondition(c.id, { field: '_keyword', operator: 'equals', value: '', scope: 'shiyou' })
}
function addTagCondition() {
  store.addCondition('normal')
  const c = store.conditions[store.conditions.length - 1]
  if (c) store.updateCondition(c.id, { field: '_tag', tagId: null, tagId2: null, operator: 'equals', value: '', scope: null })
}

function keywordPlaceholder(scope) {
  if (scope === 'ben_name' || scope === 'zhi_name') return '输入标准卦名...'
  return '输入关键词...'
}

function isGuaNameInvalid(cond) {
  const scope = cond.scope || 'shiyou'
  if (scope !== 'ben_name' && scope !== 'zhi_name') return false
  const v = (cond.value || '').trim()
  return v && !GUA_NAME_SET.has(v)
}

function onKeywordEnter(cond) {
  if (isGuaNameInvalid(cond)) return
  store.executeSearch()
}

function remove(id) { store.removeCondition(id) }
</script>

<template>
  <div class="cond-builder">
    <div class="cb-header">
      <span>检索条件</span>
      <span class="cb-hint">条件间逻辑可编辑</span>
      <div class="cb-header-actions">
        <button class="cb-btn cb-btn-search" :disabled="store.loading" @click="store.executeSearch()">
          {{ store.loading ? '检索中...' : '搜索' }}
        </button>
        <button class="cb-btn" @click="condCollapsed = !condCollapsed">{{ condCollapsed ? '展开' : '折叠' }}</button>
        <button class="cb-btn cb-btn-clear" @click="store.conditions = []; store.logicChain = []; store.results = []">清空</button>
      </div>
    </div>

    <div v-show="!condCollapsed">
      <div v-if="!store.conditions.length" class="cb-empty">点击下方按钮或左侧字段库添加条件</div>

    <template v-for="(cond, ci) in store.conditions" :key="cond.id">
      <!-- 逻辑连接器（非第一个条件时显示） -->
      <div v-if="ci > 0" class="logic-bar">
        <button class="logic-btn" :class="{ 'logic-or': getLogicOp(ci) === 'or' }"
          @click="toggleLogicAt(ci)" :title="getLogicOp(ci)==='and'?'AND→OR':'OR→AND'">
          {{ getLogicOp(ci) === 'or' ? 'OR' : 'AND' }}
        </button>
      </div>

      <div class="cond-item" :class="{
        'bracket-first': isGroupStart(ci),
        'bracket-inner': inBracketGroup(ci) && !isGroupStart(ci) && !isGroupEnd(ci),
        'bracket-last': isGroupEnd(ci),
        'bracket-single': isGroupStart(ci) && isGroupEnd(ci)
      }">
        <!-- NOT 按钮 -->
        <button class="logic-not" :class="{ active: store.hasNot(cond.id) }"
          @click="store.toggleNot(cond.id)" title="取反">NOT</button>
        <!-- 括号 -->
        <button class="logic-br" :class="{ active: hasOpenBracket(cond.id) }"
          @click="store.addOpenBracket(cond.id)" title="左括号">⌈</button>
        <button class="logic-br" :class="{ active: hasCloseBracket(cond.id) }"
          @click="store.addCloseBracket(cond.id)" title="右括号">⌋</button>
        <button class="cond-remove" @click="remove(cond.id)" title="删除此条件">×</button>

      <!-- 条件组 -->
      <SameYaoGroup v-if="cond.groupType==='same_yao'" :group="cond" />
      <SamePositionGroup v-else-if="cond.groupType==='same_position'" :group="cond" />
      <FeishenGroup v-else-if="cond.groupType==='feishen'" :group="cond" />

      <!-- 爻属性条件 -->
      <template v-else-if="!cond.relation && !isShensha(cond.field) && !isCount(cond.field) && !isKeyword(cond.field) && !isTag(cond.field)">
        <select v-if="cond.scope !== null && cond.field && cond.field !== 'yao_position' && !GUA_FIELDS.find(f=>f.v===cond.field) && !TIME_FIELDS.find(f=>f.v===cond.field)" v-model="cond.scope" @change="()=>{}" class="cb-sel">
          <option v-for="s in SCOPE_OPTIONS" :key="s.v" :value="s.v">{{ s.label }}</option>
        </select>
        <select v-if="!GUA_FIELDS.find(f=>f.v===cond.field) && !TIME_FIELDS.find(f=>f.v===cond.field)" v-model="cond.field" @change="(e)=>{cond.value=''; if(e.target.value==='is_dong'||e.target.value==='is_an_dong'){cond.value='true';cond.operator='equals'}}" class="cb-sel">
          <option value="">--字段--</option>
          <option v-for="f in availableFields(cond.scope)" :key="f.v" :value="f.v">{{ f.label }}</option>
        </select>
        <select v-else-if="GUA_FIELDS.find(f=>f.v===cond.field) || TIME_FIELDS.find(f=>f.v===cond.field) || (!cond.field)" v-model="cond.field" @change="cond.scope=null" class="cb-sel">
          <option value="">--字段--</option>
          <option v-for="f in TIME_FIELDS" :key="'t'+f.v" :value="f.v">{{ f.label }}</option>
          <option disabled>──</option>
          <option v-for="f in GUA_FIELDS" :key="'g'+f.v" :value="f.v">{{ f.label }}</option>
        </select>
        <select v-model="cond.operator" class="cb-sel cb-op">
          <option v-for="op in OPERATORS" :key="op" :value="op">{{ OP_DISPLAY[op] || op }}</option>
        </select>
        <select v-if="fieldValueOptions(cond.field).length" v-model="cond.value" class="cb-sel">
          <option value="">--值--</option>
          <option v-for="v in fieldValueOptions(cond.field)" :key="v.v||v" :value="v.v||v">{{ v.l||v }}</option>
        </select>
        <input v-else v-model="cond.value" class="cb-input" placeholder="输入值" />
      </template>

      <!-- 神煞条件 -->
      <template v-else-if="isShensha(cond.field)">
        <select v-if="!String(cond.value).startsWith('cg_')" v-model="cond.scope" class="cb-sel">
          <option v-for="s in SCOPE_OPTIONS" :key="s.v" :value="s.v">{{ s.label }}</option>
        </select>
        <span v-else class="cb-hint" style="padding:2px 4px">(组)</span>
        <select v-model="cond.value" class="cb-sel">
          <option value="">--对象--</option>
          <option value="世爻">世爻</option>
          <option value="应爻">应爻</option>
          <option value="妻财爻">妻财爻</option>
          <option value="官鬼爻">官鬼爻</option>
          <option value="父母爻">父母爻</option>
          <option value="兄弟爻">兄弟爻</option>
          <option value="子孙爻">子孙爻</option>
          <option disabled>── 六神</option>
          <option value="青龙爻">青龙爻</option>
          <option value="朱雀爻">朱雀爻</option>
          <option value="勾陈爻">勾陈爻</option>
          <option value="螣蛇爻">螣蛇爻</option>
          <option value="白虎爻">白虎爻</option>
          <option value="玄武爻">玄武爻</option>
          <option disabled>── 状态</option>
          <option value="动爻">动爻</option>
          <option value="静爻">静爻</option>
          <option value="暗动爻">暗动爻</option>
          <option disabled>── 伏神/飞神</option>
          <option value="易冒伏神">易冒伏神</option>
          <option value="增删伏神">增删伏神</option>
          <option value="易冒飞神">易冒飞神</option>
          <option value="增删飞神">增删飞神</option>
          <option disabled>──</option>
          <option v-for="c in store.conditions.filter(x=>x.id!==cond.id&&x.groupType)" :key="c.id" :value="c.id">{{ groupSummary(c) }}</option>
        </select>
        <select v-model="cond.field" class="cb-sel">
          <option value="">--神煞--</option>
          <option v-for="s in SHENSHA_TYPES" :key="s.v" :value="s.v">{{ s.label }}</option>
        </select>
      </template>

      <!-- 数目判断 -->
      <template v-else-if="isCount(cond.field)">
        <select v-model="cond.scope" class="cb-sel">
          <option v-for="s in COUNT_SCOPES" :key="s.v" :value="s.v">{{ s.label }}</option>
        </select>
        <span class="cb-yu">中</span>
        <select v-model="cond.countAttr" class="cb-sel" @change="cond.countValue='';cond.value='0'">
          <option value="">--属性--</option>
          <option v-for="a in COUNT_ATTRS" :key="a.v" :value="a.v">{{ a.label }}</option>
        </select>
        <span class="cb-yu">=</span>
        <select v-if="currentCountAttr(cond)?.vals.length" v-model="cond.countValue" class="cb-sel">
          <option value="">--值--</option>
          <option v-for="v in currentCountAttr(cond).vals" :key="v.v||v" :value="v.v||v">{{ v.l||v }}</option>
        </select>
        <input v-else v-model="cond.countValue" class="cb-input" placeholder="值" style="width:60px" />
        <span class="cb-yu">的数目</span>
        <select v-model="cond.operator" class="cb-sel" style="width:90px">
          <option v-for="op in COUNT_OPS" :key="op" :value="op">{{ OP_DISPLAY[op] || op }}</option>
        </select>
        <input v-model="cond.value" class="cb-input" placeholder="0" style="width:45px" />
      </template>

      <!-- 文本搜索 -->
      <template v-else-if="isKeyword(cond.field)">
        <select v-model="cond.scope" class="cb-sel" style="width:90px">
          <option value="shiyou">占问事由</option>
          <option value="ben_name">本卦卦名</option>
          <option value="zhi_name">之卦卦名</option>
        </select>
        <span class="cb-yu">包含</span>
        <input v-model="cond.value" class="cb-input" :class="{ 'cb-input-err': isGuaNameInvalid(cond) }"
          :placeholder="keywordPlaceholder(cond.scope)"
          style="width:150px" @keyup.enter="onKeywordEnter(cond)" />
        <span v-if="isGuaNameInvalid(cond)" class="cb-err-msg">无效卦名</span>
      </template>

      <!-- 标签筛选 -->
      <template v-else-if="isTag(cond.field)">
        <span class="cb-yu">标签</span>
        <select v-model="cond.tagId" class="cb-sel" @change="cond.tagId2=null">
          <option :value="null">一级：全部</option>
          <option v-for="t in appStore.tagTree" :key="t.id" :value="t.id">{{ t.name }}</option>
          <option :value="-1">非系统标签</option>
        </select>
        <select v-if="cond.tagId && cond.tagId !== -1" v-model="cond.tagId2" class="cb-sel">
          <option :value="null">二级：全部</option>
          <option v-for="t in level2Options(cond.tagId)" :key="t.id" :value="t.id">{{ t.name }}</option>
        </select>
      </template>

      <!-- 关系条件 -->
      <template v-else>
        <!-- 左对象（共用） -->
        <select v-model="cond.left_type" class="cb-sel">
          <option value="yao_object">爻对象</option>
          <option value="time_object">时间对象</option>
          <option value="condition_group_ref">条件组引用</option>
        </select>
        <select v-if="cond.left_type==='yao_object' && !isFushenFeishen(cond.left_value)" v-model="cond.left_scope" class="cb-sel">
          <option value="ben_gua">本卦</option>
          <option value="zhi_gua">之卦</option>
          <option value="bian_yao">变爻</option>
          <option value="yimao">易冒</option>
          <option value="zengshan">增删</option>
        </select>
        <select v-if="cond.left_type==='yao_object'" v-model="cond.left_value" class="cb-sel">
          <option value="">--对象--</option>
          <option value="世爻">世爻</option>
          <option value="应爻">应爻</option>
          <option value="妻财爻">妻财爻</option>
          <option value="官鬼爻">官鬼爻</option>
          <option value="父母爻">父母爻</option>
          <option value="兄弟爻">兄弟爻</option>
          <option value="子孙爻">子孙爻</option>
          <option disabled>── 六神</option>
          <option value="青龙爻">青龙爻</option>
          <option value="朱雀爻">朱雀爻</option>
          <option value="勾陈爻">勾陈爻</option>
          <option value="螣蛇爻">螣蛇爻</option>
          <option value="白虎爻">白虎爻</option>
          <option value="玄武爻">玄武爻</option>
          <option disabled>── 状态</option>
          <option value="动爻">动爻</option>
          <option value="静爻">静爻</option>
          <option value="暗动爻">暗动爻</option>
          <option disabled>── 伏神飞神</option>
          <option value="易冒伏神">易冒伏神</option>
          <option value="增删伏神">增删伏神</option>
          <option value="易冒飞神">易冒飞神</option>
          <option value="增删飞神">增删飞神</option>
        </select>
        <select v-else-if="cond.left_type==='time_object'" v-model="cond.left_value" class="cb-sel">
          <option value="">--时间--</option>
          <option value="年支">年支</option>
          <option value="月支">月支</option>
          <option value="日支">日支</option>
        </select>
        <select v-else v-model="cond.left_value" class="cb-sel">
          <option value="">--条件ID--</option>
          <option v-for="c in store.conditions.filter(x=>x.id!==cond.id&&x.groupType)" :key="c.id" :value="c.id">{{ groupSummary(c) }}</option>
        </select>

        <!-- 三合布局：x y z 三合▼ 局▼ -->
        <template v-if="cond.relation==='三合'">
          <span class="cb-gap"></span>
          <select v-model="cond.middle_type" class="cb-sel">
            <option value="">--类型--</option>
            <option value="yao_object">爻对象</option>
            <option value="time_object">时间对象</option>
            <option value="condition_group_ref">条件组引用</option>
          </select>
          <select v-if="cond.middle_type==='yao_object' && !isFushenFeishen(cond.middle_value)" v-model="cond.middle_scope" class="cb-sel">
            <option value="ben_gua">本卦</option>
            <option value="zhi_gua">之卦</option>
            <option value="bian_yao">变爻</option>
            <option value="yimao">易冒</option>
            <option value="zengshan">增删</option>
          </select>
          <select v-if="cond.middle_type==='yao_object'" v-model="cond.middle_value" class="cb-sel">
            <option value="">--对象--</option>
            <option value="世爻">世爻</option>
            <option value="应爻">应爻</option>
            <option value="妻财爻">妻财爻</option>
            <option value="官鬼爻">官鬼爻</option>
            <option value="父母爻">父母爻</option>
            <option value="兄弟爻">兄弟爻</option>
            <option value="子孙爻">子孙爻</option>
            <option disabled>── 六神</option>
            <option value="青龙爻">青龙爻</option>
            <option value="朱雀爻">朱雀爻</option>
            <option value="勾陈爻">勾陈爻</option>
            <option value="螣蛇爻">螣蛇爻</option>
            <option value="白虎爻">白虎爻</option>
            <option value="玄武爻">玄武爻</option>
            <option disabled>── 状态</option>
            <option value="动爻">动爻</option>
            <option value="静爻">静爻</option>
            <option value="暗动爻">暗动爻</option>
            <option disabled>── 伏神飞神</option>
            <option value="易冒伏神">易冒伏神</option>
            <option value="增删伏神">增删伏神</option>
            <option value="易冒飞神">易冒飞神</option>
            <option value="增删飞神">增删飞神</option>
          </select>
          <select v-else-if="cond.middle_type==='time_object'" v-model="cond.middle_value" class="cb-sel">
            <option value="">--时间--</option>
            <option value="年支">年支</option>
            <option value="月支">月支</option>
            <option value="日支">日支</option>
          </select>
          <select v-else v-model="cond.middle_value" class="cb-sel">
            <option value="">--条件ID--</option>
            <option v-for="c in store.conditions.filter(x=>x.id!==cond.id&&x.groupType)" :key="c.id" :value="c.id">{{ groupSummary(c) }}</option>
          </select>
          <span class="cb-gap"></span>
          <select v-model="cond.right_type" class="cb-sel">
            <option value="">--类型--</option>
            <option value="yao_object">爻对象</option>
            <option value="time_object">时间对象</option>
            <option value="condition_group_ref">条件组引用</option>
          </select>
          <select v-if="cond.right_type==='yao_object' && !isFushenFeishen(cond.right_value)" v-model="cond.right_scope" class="cb-sel">
            <option value="ben_gua">本卦</option>
            <option value="zhi_gua">之卦</option>
            <option value="bian_yao">变爻</option>
            <option value="yimao">易冒</option>
            <option value="zengshan">增删</option>
          </select>
          <select v-if="cond.right_type==='yao_object'" v-model="cond.right_value" class="cb-sel">
            <option value="">--对象--</option>
            <option value="世爻">世爻</option>
            <option value="应爻">应爻</option>
            <option value="妻财爻">妻财爻</option>
            <option value="官鬼爻">官鬼爻</option>
            <option value="父母爻">父母爻</option>
            <option value="兄弟爻">兄弟爻</option>
            <option value="子孙爻">子孙爻</option>
            <option disabled>── 六神</option>
            <option value="青龙爻">青龙爻</option>
            <option value="朱雀爻">朱雀爻</option>
            <option value="勾陈爻">勾陈爻</option>
            <option value="螣蛇爻">螣蛇爻</option>
            <option value="白虎爻">白虎爻</option>
            <option value="玄武爻">玄武爻</option>
            <option disabled>── 状态</option>
            <option value="动爻">动爻</option>
            <option value="静爻">静爻</option>
            <option value="暗动爻">暗动爻</option>
            <option disabled>── 伏神飞神</option>
            <option value="易冒伏神">易冒伏神</option>
            <option value="增删伏神">增删伏神</option>
            <option value="易冒飞神">易冒飞神</option>
            <option value="增删飞神">增删飞神</option>
          </select>
          <select v-else-if="cond.right_type==='time_object'" v-model="cond.right_value" class="cb-sel">
            <option value="">--时间--</option>
            <option value="年支">年支</option>
            <option value="月支">月支</option>
            <option value="日支">日支</option>
          </select>
          <select v-else v-model="cond.right_value" class="cb-sel">
            <option value="">--条件ID--</option>
            <option v-for="c in store.conditions.filter(x=>x.id!==cond.id&&x.groupType)" :key="c.id" :value="c.id">{{ groupSummary(c) }}</option>
          </select>
          <select v-model="cond.relation" class="cb-sel">
            <optgroup label="生克合冲">
              <option value="生">生</option>
              <option value="克">克</option>
              <option value="合">合</option>
              <option value="冲">冲</option>
              <option value="半合">半合</option>
              <option value="=">=</option>
            </optgroup>
            <optgroup label="三合">
              <option value="三合">三合</option>
            </optgroup>
            <optgroup label="生旺墓绝">
              <option value="长生">长生</option>
              <option value="帝旺">帝旺</option>
              <option value="墓">墓</option>
              <option value="绝">绝</option>
            </optgroup>
          </select>
          <span class="cb-gap"></span>
          <select v-model="cond.bureau" class="cb-sel">
            <option value="">--局--</option>
            <option value="水">水局</option>
            <option value="木">木局</option>
            <option value="火">火局</option>
            <option value="金">金局</option>
          </select>
        </template>

        <!-- 非三合布局：relation▼ (于) right -->
        <template v-else>
          <select v-model="cond.relation" @change="(e)=>{if(e.target.value==='三合'&&!cond.middle_type)cond.middle_type='yao_object'}" class="cb-sel">
            <optgroup label="生克合冲">
              <option value="生">生</option>
              <option value="克">克</option>
              <option value="合">合</option>
              <option value="冲">冲</option>
              <option value="半合">半合</option>
              <option value="=">=</option>
            </optgroup>
            <optgroup label="三合">
              <option value="三合">三合</option>
            </optgroup>
            <optgroup label="生旺墓绝">
              <option value="长生">长生</option>
              <option value="帝旺">帝旺</option>
              <option value="墓">墓</option>
              <option value="绝">绝</option>
            </optgroup>
          </select>
          <span v-if="SHENGWANG_RELATIONS.includes(cond.relation)" class="cb-yu">于</span>
          <select v-model="cond.right_type" class="cb-sel">
            <option value="yao_object">爻对象</option>
            <option value="time_object">时间对象</option>
            <option value="condition_group_ref">条件组引用</option>
          </select>
          <select v-if="cond.right_type==='yao_object' && !isFushenFeishen(cond.right_value)" v-model="cond.right_scope" class="cb-sel">
            <option value="ben_gua">本卦</option>
            <option value="zhi_gua">之卦</option>
            <option value="bian_yao">变爻</option>
            <option value="yimao">易冒</option>
            <option value="zengshan">增删</option>
          </select>
          <select v-if="cond.right_type==='yao_object'" v-model="cond.right_value" class="cb-sel">
            <option value="">--对象--</option>
            <option value="世爻">世爻</option>
            <option value="应爻">应爻</option>
            <option value="妻财爻">妻财爻</option>
            <option value="官鬼爻">官鬼爻</option>
            <option value="父母爻">父母爻</option>
            <option value="兄弟爻">兄弟爻</option>
            <option value="子孙爻">子孙爻</option>
            <option disabled>── 六神</option>
            <option value="青龙爻">青龙爻</option>
            <option value="朱雀爻">朱雀爻</option>
            <option value="勾陈爻">勾陈爻</option>
            <option value="螣蛇爻">螣蛇爻</option>
            <option value="白虎爻">白虎爻</option>
            <option value="玄武爻">玄武爻</option>
            <option disabled>── 状态</option>
            <option value="动爻">动爻</option>
            <option value="静爻">静爻</option>
            <option value="暗动爻">暗动爻</option>
            <option disabled>── 伏神飞神</option>
            <option value="易冒伏神">易冒伏神</option>
            <option value="增删伏神">增删伏神</option>
            <option value="易冒飞神">易冒飞神</option>
            <option value="增删飞神">增删飞神</option>
          </select>
          <select v-else-if="cond.right_type==='time_object'" v-model="cond.right_value" class="cb-sel">
            <option value="">--时间--</option>
            <option value="年支">年支</option>
            <option value="月支">月支</option>
            <option value="日支">日支</option>
          </select>
          <select v-else v-model="cond.right_value" class="cb-sel">
            <option value="">--条件ID--</option>
            <option v-for="c in store.conditions.filter(x=>x.id!==cond.id&&x.groupType)" :key="c.id" :value="c.id">{{ groupSummary(c) }}</option>
          </select>
        </template>
      </template>
    </div>
    </template>

    <div class="cb-actions">
      <button @click="addTimeCondition" class="cb-btn">+ 时间</button>
      <button @click="addGuaCondition" class="cb-btn">+ 卦类</button>
      <button @click="addYaoCondition" class="cb-btn">+ 爻属性</button>
      <button @click="addRelationCondition" class="cb-btn">+ 关系</button>
      <button @click="addShenshaCondition" class="cb-btn">+ 神煞</button>
      <button @click="addCountCondition" class="cb-btn">+ 数目</button>
      <button @click="addKeywordCondition" class="cb-btn">+ 文本搜索</button>
      <button @click="addTagCondition" class="cb-btn">+ 标签</button>
    </div>
    <div class="cb-actions">
      <button @click="store.addConditionGroup('same_yao')" class="cb-btn cg-btn">+ 同一爻</button>
      <button @click="store.addConditionGroup('same_position')" class="cb-btn cg-btn">+ 同爻位</button>
      <button @click="store.addConditionGroup('feishen')" class="cb-btn cg-btn">+ 飞神</button>
    </div>
    </div>
  </div>
</template>

<style scoped>
.cond-builder { flex: 1; background: var(--color-bg-secondary); border-radius: var(--radius-lg); padding: var(--space-3); box-shadow: var(--shadow-sm); }
.cb-header { display: flex; align-items: baseline; gap: var(--space-2); margin-bottom: var(--space-2); }
.cb-header span { font-size: var(--font-size-sm); font-weight: 600; color: var(--color-text-primary); }
.cb-hint { font-size: var(--font-size-xs); color: var(--color-text-muted); font-weight: normal; }
.cb-header-actions { margin-left: auto; display: flex; gap: var(--space-2); }
.cb-btn-search { background: var(--color-accent); color: #fff; border-color: var(--color-accent); }
.cb-btn-search:hover { filter: brightness(1.1); }
.cb-btn-search:disabled { opacity: 0.5; cursor: not-allowed; }
.cb-btn-clear:hover { border-color: var(--color-danger); color: var(--color-danger); }
.cb-empty { text-align: center; padding: var(--space-5); color: var(--color-text-muted); font-size: var(--font-size-sm); }

.cond-item { display: flex; align-items: center; gap: 4px; padding: 4px 6px; margin-bottom: 4px; background: var(--color-bg-tertiary); border-radius: var(--radius-md); flex-wrap: wrap; }
.cond-remove { width: 18px; height: 18px; padding: 0; background: none; border: 1px solid var(--color-border-subtle); border-radius: var(--radius-sm); color: var(--color-text-muted); font-size: 14px; cursor: pointer; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.cond-remove:hover { border-color: var(--color-danger); color: var(--color-danger); }

/* logic controls */
.logic-bar { display: flex; justify-content: center; padding: 2px 0; }
.logic-btn { height: 18px; padding: 0 8px; background: var(--color-bg-tertiary); color: var(--color-accent-light); border: 1px solid var(--color-accent); border-radius: var(--radius-sm); font-size: 10px; font-weight: 600; cursor: pointer; display: flex; align-items: center; }
.logic-btn:hover { background: var(--color-accent); color: #fff; }
.logic-or { color: #e67e22; border-color: #e67e22; }
.logic-or:hover { background: #e67e22; color: #fff; }
.logic-not { height: 18px; min-width: 28px; padding: 0 4px; background: none; border: 1px solid var(--color-border-subtle); border-radius: var(--radius-sm); color: var(--color-text-muted); font-size: 10px; cursor: pointer; flex-shrink: 0; display: flex; align-items: center; justify-content: center; }
.logic-not:hover { border-color: var(--color-danger); color: var(--color-danger); }
.logic-not.active { background: var(--color-danger); color: #fff; border-color: var(--color-danger); }
.logic-br { height: 18px; width: 18px; padding: 0; background: none; border: 1px solid var(--color-border-subtle); border-radius: var(--radius-sm); color: var(--color-text-muted); font-size: 11px; cursor: pointer; flex-shrink: 0; display: flex; align-items: center; justify-content: center; }
.logic-br:hover { border-color: var(--color-accent); color: var(--color-accent-light); }
.logic-br.active { background: var(--color-accent); color: #fff; border-color: var(--color-accent); }

/* bracket group card */
.bracket-first { border: 2px solid var(--color-accent); border-bottom: none; border-radius: var(--radius-md) var(--radius-md) 0 0; margin-bottom: 0; padding-bottom: 4px; }
.bracket-inner { border-left: 2px solid var(--color-accent); border-right: 2px solid var(--color-accent); border-top: none; border-bottom: none; border-radius: 0; margin-bottom: 0; margin-top: 0; }
.bracket-last { border: 2px solid var(--color-accent); border-top: none; border-radius: 0 0 var(--radius-md) var(--radius-md); padding-top: 4px; }
.bracket-single { border: 2px solid var(--color-accent); border-radius: var(--radius-md); }
.bracket-mark { display: none; }

.cb-sel { padding: 2px 4px; background: var(--color-bg-input); color: var(--color-text-primary); border: 1px solid var(--color-border-primary); border-radius: var(--radius-sm); font-size: var(--font-size-sm); }
.cb-sel:focus { outline: none; border-color: var(--color-accent); }
.cb-input { padding: 2px 6px; background: var(--color-bg-input); color: var(--color-text-primary); border: 1px solid var(--color-border-primary); border-radius: var(--radius-sm); font-size: var(--font-size-sm); width: 80px; }
.cb-input:focus { outline: none; border-color: var(--color-accent); }
.cb-input-err { border-color: var(--color-danger) !important; }
.cb-err-msg { color: var(--color-danger); font-size: var(--font-size-xs); margin-left: 4px; }
.cb-op { width: 100px; }
.cb-yu { font-size: var(--font-size-sm); color: var(--color-text-secondary); flex-shrink: 0; }
.cb-gap { width: 6px; flex-shrink: 0; }

.cb-actions { display: flex; gap: var(--space-2); margin-top: var(--space-2); }

.cb-btn { padding: 3px 10px; background: var(--color-bg-tertiary); color: var(--color-text-secondary); border: 1px solid var(--color-border-primary); border-radius: var(--radius-md); font-size: var(--font-size-xs); cursor: pointer; transition: all var(--transition-fast); }
.cb-btn:hover { border-color: var(--color-accent); color: var(--color-accent-light); }
.cb-sep { color: var(--color-border-primary); font-size: var(--font-size-xs); }
.cg-btn { border-color: var(--color-accent); color: var(--color-accent-light); }
</style>
