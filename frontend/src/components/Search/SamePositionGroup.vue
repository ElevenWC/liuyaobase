<script setup>
import { useSearchStore } from '../../stores/useSearchStore.js'

const props = defineProps({ group: { type: Object, required: true } })
const store = useSearchStore()

const ALL_SOURCES = ['本卦', '变爻', '之卦(静爻)', '易冒伏神', '增删伏神']
const POS_LABELS = ['初爻', '二爻', '三爻', '四爻', '五爻', '上爻']

const GEN_FIELD_OPTIONS = [
  { v: 'liuqin', label: '六亲' }, { v: 'dizhi', label: '地支' },
  { v: 'shi_ying', label: '世应' }, { v: 'yao_type', label: '爻类型' },
  { v: 'tiangan', label: '天干' }, { v: 'is_dong', label: '动爻' },
  { v: 'is_an_dong', label: '暗动' }, { v: 'liushen', label: '六神' },
  { v: 'zengshan_exists', label: '有伏神' },
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
  return []
}

function srcIdx(source) { return props.group.sources.findIndex(s => s.source === source) }

function toggleSrc(source) {
  const idx = srcIdx(source)
  if (idx >= 0) props.group.sources.splice(idx, 1)
  else props.group.sources.push({ source, conditions: [] })
}

function addSub(si) { store.addSubCondition(props.group.id, si) }
function removeSub(si, ci) { store.removeSubCondition(props.group.id, ci, si) }
</script>

<template>
  <div class="cg-card">
    <div class="cg-head">
      <span class="cg-title">同爻位条件组</span>
      <span class="cg-desc">必须同一爻位</span>
      <button class="cg-del" @click="store.removeConditionGroup(group.id)" title="删除">×</button>
    </div>
    <div class="cg-pos-bar">
      <span class="cg-lbl">爻位：第</span>
      <select v-model="group.position" class="cb-sel">
        <option v-for="(lbl, i) in POS_LABELS" :key="i" :value="i+1">{{ lbl }}</option>
      </select>
    </div>
    <div v-for="srcName in ALL_SOURCES" :key="srcName" class="cg-src-row">
      <label class="cg-chk">
        <input type="checkbox" :checked="srcIdx(srcName) >= 0" @change="toggleSrc(srcName)" />{{ srcName }}
      </label>
      <template v-if="srcIdx(srcName) >= 0">
        <div class="cg-subs">
          <div v-for="(sc, si) in props.group.sources[srcIdx(srcName)].conditions" :key="si" class="cond-item">
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
            <button class="cg-sub-del" @click="removeSub(srcIdx(srcName), si)">×</button>
          </div>
          <button @click="addSub(srcIdx(srcName))" class="cb-btn">+ 条件</button>
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped>
/* shared with ConditionBuilder */
.cb-sel { padding: 2px 4px; background: var(--color-bg-input); color: var(--color-text-primary); border: 1px solid var(--color-border-primary); border-radius: var(--radius-sm); font-size: var(--font-size-sm); }
.cb-sel:focus { outline: none; border-color: var(--color-accent); }
.cb-input { padding: 2px 6px; background: var(--color-bg-input); color: var(--color-text-primary); border: 1px solid var(--color-border-primary); border-radius: var(--radius-sm); font-size: var(--font-size-sm); width: 80px; }
.cb-input:focus { outline: none; border-color: var(--color-accent); }
.cb-btn { padding: 3px 10px; background: var(--color-bg-tertiary); color: var(--color-text-secondary); border: 1px solid var(--color-border-primary); border-radius: var(--radius-md); font-size: var(--font-size-xs); cursor: pointer; transition: all var(--transition-fast); }
.cb-btn:hover { border-color: var(--color-accent); color: var(--color-accent-light); }
.cond-item { display: flex; align-items: center; gap: 4px; padding: 4px 6px; margin-bottom: 4px; background: var(--color-bg-tertiary); border-radius: var(--radius-md); flex-wrap: wrap; }
/* group-specific */
.cg-card { border: 1px solid var(--color-accent); border-radius: var(--radius-md); padding: var(--space-2); margin-bottom: var(--space-2); background: var(--color-bg-tertiary); }
.cg-head { display: flex; align-items: center; gap: var(--space-2); margin-bottom: var(--space-1); }
.cg-title { font-size: var(--font-size-sm); font-weight: 600; color: var(--color-accent-light); }
.cg-desc { font-size: var(--font-size-xs); color: var(--color-text-muted); }
.cg-del { margin-left: auto; width: 18px; height: 18px; padding: 0; background: none; border: 1px solid var(--color-border-subtle); border-radius: var(--radius-sm); color: var(--color-text-muted); font-size: 14px; cursor: pointer; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.cg-del:hover { border-color: var(--color-danger); color: var(--color-danger); }
.cg-pos-bar { display: flex; align-items: center; gap: var(--space-1); margin-bottom: var(--space-1); }
.cg-lbl { font-size: var(--font-size-xs); color: var(--color-text-secondary); }
.cg-src-row { margin-bottom: 2px; }
.cg-chk { font-size: var(--font-size-xs); color: var(--color-text-secondary); display: flex; align-items: center; gap: 2px; cursor: pointer; accent-color: var(--color-accent); }
.cg-subs { margin-left: var(--space-4); display: flex; flex-direction: column; gap: 4px; margin-top: var(--space-1); }
.cg-sub-del { width: 16px; height: 16px; padding: 0; background: none; border: 1px solid var(--color-border-subtle); border-radius: var(--radius-sm); color: var(--color-text-muted); font-size: 12px; cursor: pointer; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.cg-sub-del:hover { border-color: var(--color-danger); color: var(--color-danger); }
</style>
