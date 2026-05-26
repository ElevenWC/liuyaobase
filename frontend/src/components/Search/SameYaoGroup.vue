<script setup>
import { useSearchStore } from '../../stores/useSearchStore.js'

const props = defineProps({ group: { type: Object, required: true } })
const store = useSearchStore()

const SOURCES = ['本卦', '变爻', '之卦(静爻)', '易冒伏神', '增删伏神']

const GEN_FIELD_OPTIONS = [
  { v: 'liuqin', label: '六亲' }, { v: 'dizhi', label: '地支' },
  { v: 'shi_ying', label: '世应' }, { v: 'yao_type', label: '爻类型' },
  { v: 'tiangan', label: '天干' }, { v: 'yao_position', label: '爻位' },
  { v: 'is_dong', label: '动爻' }, { v: 'is_an_dong', label: '暗动' },
  { v: 'liushen', label: '六神' }, { v: 'zengshan_exists', label: '有伏神' },
]

const OPERATORS = ['equals', 'not_equals', 'in', 'not_in', 'gt', 'lt', 'gte', 'lte', 'range']
const OP_DISPLAY = { equals: '=', not_equals: '≠', in: '∈', not_in: '∉', gt: '>', lt: '<', gte: '≥', lte: '≤', range: '↔' }
const LIUQIN_VALS = ['妻财', '官鬼', '父母', '兄弟', '子孙']
const SHIYING_VALS = ['世', '应']
const YAOTYPE_VALS = ['阳', '阴']
const DIZHI_VALS = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
const TIAN_GAN_VALS = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
const LIUSHEN_VALS = ['青龙', '朱雀', '勾陈', '螣蛇', '白虎', '玄武']

function valOptions(field) {
  if (field === 'liuqin') return LIUQIN_VALS
  if (field === 'shi_ying') return SHIYING_VALS
  if (field === 'yao_type') return YAOTYPE_VALS
  if (field === 'dizhi') return DIZHI_VALS
  if (field === 'tiangan') return TIAN_GAN_VALS
  if (field === 'is_dong' || field === 'is_an_dong') return [{ v: 'true', l: '存在' }, { v: 'false', l: '不存在' }]
  if (field === 'zengshan_exists') return ['true', 'false']
  if (field === 'liushen') return LIUSHEN_VALS
  if (field === 'yao_position') return [{ v: '1', l: '初爻' }, { v: '2', l: '二爻' }, { v: '3', l: '三爻' }, { v: '4', l: '四爻' }, { v: '5', l: '五爻' }, { v: '6', l: '上爻' }]
  return []
}

function toggleSrc(src) {
  const idx = props.group.sources.indexOf(src)
  if (idx >= 0) props.group.sources.splice(idx, 1)
  else props.group.sources.push(src)
}

function addSub() { store.addSubCondition(props.group.id) }
function removeSub(idx) { store.removeSubCondition(props.group.id, idx) }
</script>

<template>
  <div class="cg-card">
    <div class="cg-head">
      <span class="cg-title">同一爻条件组</span>
      <span class="cg-desc">满足任一来源即可</span>
      <button class="cg-del" @click="store.removeConditionGroup(group.id)" title="删除此条件组">×</button>
    </div>
    <div class="cg-src-bar">
      <span class="cg-lbl">来源：</span>
      <label v-for="s in SOURCES" :key="s" class="cg-chk">
        <input type="checkbox" :checked="group.sources.includes(s)" @change="toggleSrc(s)" />{{ s }}
      </label>
    </div>
    <div class="cg-body">
      <div v-for="(sc, i) in group.conditions" :key="i" class="cond-item">
        <select v-model="sc.field" class="cb-sel" @change="sc.value=''">
          <option value="">--字段--</option>
          <option v-for="f in GEN_FIELD_OPTIONS" :key="f.v" :value="f.v">{{ f.label }}</option>
        </select>
        <select v-model="sc.operator" class="cb-sel" style="width:72px">
          <option v-for="op in OPERATORS" :key="op" :value="op">{{ OP_DISPLAY[op] || op }}</option>
        </select>
        <select v-if="valOptions(sc.field).length" v-model="sc.value" class="cb-sel">
          <option value="">--值--</option>
          <option v-for="v in valOptions(sc.field)" :key="v.v||v" :value="v.v||v">{{ v.l||v }}</option>
        </select>
        <input v-else v-model="sc.value" class="cb-input" placeholder="输入值" />
        <button class="cg-sub-del" @click="removeSub(i)" title="删除">×</button>
      </div>
    </div>
    <button @click="addSub" class="cb-btn">+ 条件</button>
  </div>
</template>

<style scoped>
.cg-card { border: 1px solid var(--color-accent); border-radius: var(--radius-md); padding: var(--space-2); margin-bottom: var(--space-2); background: var(--color-bg-tertiary); }
.cg-head { display: flex; align-items: center; gap: var(--space-2); margin-bottom: var(--space-1); }
.cg-title { font-size: var(--font-size-sm); font-weight: 600; color: var(--color-accent-light); }
.cg-desc { font-size: var(--font-size-xs); color: var(--color-text-muted); }
.cg-del { margin-left: auto; width: 18px; height: 18px; padding: 0; background: none; border: 1px solid var(--color-border-subtle); border-radius: var(--radius-sm); color: var(--color-text-muted); font-size: 14px; cursor: pointer; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.cg-del:hover { border-color: var(--color-danger); color: var(--color-danger); }
.cg-src-bar { display: flex; flex-wrap: wrap; align-items: center; gap: var(--space-1); margin-bottom: var(--space-1); }
.cg-lbl { font-size: var(--font-size-xs); color: var(--color-text-secondary); }
.cg-chk { font-size: var(--font-size-xs); color: var(--color-text-secondary); display: flex; align-items: center; gap: 2px; cursor: pointer; accent-color: var(--color-accent); }
.cg-body { display: flex; flex-direction: column; gap: 4px; margin-bottom: var(--space-1); }
.cg-sub-del { width: 16px; height: 16px; padding: 0; background: none; border: 1px solid var(--color-border-subtle); border-radius: var(--radius-sm); color: var(--color-text-muted); font-size: 12px; cursor: pointer; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.cg-sub-del:hover { border-color: var(--color-danger); color: var(--color-danger); }
</style>
