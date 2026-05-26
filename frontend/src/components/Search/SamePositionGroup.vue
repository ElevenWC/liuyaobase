<script setup>
import { useSearchStore } from '../../stores/useSearchStore.js'

const props = defineProps({ group: { type: Object, required: true } })
const store = useSearchStore()

const ALL_SOURCES = ['本卦', '变爻', '之卦(静爻)', '易冒伏神', '增删伏神']

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

function srcIndex(source) {
  return props.group.sources.findIndex(s => s.source === source)
}

function toggleSrc(source) {
  const idx = srcIndex(source)
  if (idx >= 0) props.group.sources.splice(idx, 1)
  else props.group.sources.push({ source, conditions: [] })
}

function addSub(srcIdx) { store.addSubCondition(props.group.id, 0, srcIdx) }
function removeSub(srcIdx, subIdx) { store.removeSubCondition(props.group.id, subIdx, srcIdx) }
</script>

<template>
  <div class="cg-card">
    <div class="cg-header">
      <span>同爻位条件组（必须同一爻位）</span>
      <button class="cg-remove" @click="store.removeConditionGroup(group.id)" title="删除">×</button>
    </div>
    <div class="cg-pos">
      <span class="cg-label">爻位：第</span>
      <select v-model="group.position" class="cb-sel">
        <option v-for="n in 6" :key="n" :value="n">{{ ['初','二','三','四','五','上'][n-1] }}爻</option>
      </select>
    </div>
    <div class="cg-sources">
      <div v-for="srcName in ALL_SOURCES" :key="srcName" class="cg-src-row">
        <label class="cg-check">
          <input type="checkbox" :checked="srcIndex(srcName) >= 0" @change="toggleSrc(srcName)" />{{ srcName }}
        </label>
        <template v-if="srcIndex(srcName) >= 0">
          <div class="cg-subs">
            <div v-for="(sc, si) in props.group.sources[srcIndex(srcName)].conditions" :key="si" class="cg-sub">
              <select v-model="sc.field" class="cb-sel" @change="sc.value=''">
                <option value="">--字段--</option>
                <option v-for="f in GEN_FIELD_OPTIONS" :key="f.v" :value="f.v">{{ f.label }}</option>
              </select>
              <select v-model="sc.operator" class="cb-sel">
                <option v-for="op in OPERATORS" :key="op" :value="op">{{ OP_DISPLAY[op] || op }}</option>
              </select>
              <select v-if="valOptions(sc.field).length" v-model="sc.value" class="cb-sel">
                <option value="">--值--</option>
                <option v-for="v in valOptions(sc.field)" :key="v.v||v" :value="v.v||v">{{ v.l||v }}</option>
              </select>
              <input v-else v-model="sc.value" class="cb-input" placeholder="输入值" />
              <button class="cg-sub-remove" @click="removeSub(srcIndex(srcName), si)">×</button>
            </div>
            <button @click="addSub(srcIndex(srcName))" class="cb-btn cg-add-btn">+</button>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
.cg-card { border: 1px solid var(--color-accent); border-radius: var(--radius-md); padding: var(--space-2); margin-bottom: var(--space-2); background: var(--color-bg-tertiary); }
.cg-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-1); font-size: var(--font-size-sm); font-weight: 600; color: var(--color-accent-light); }
.cg-remove { width: 18px; height: 18px; padding: 0; background: none; border: 1px solid var(--color-border-subtle); border-radius: var(--radius-sm); color: var(--color-text-muted); font-size: 14px; cursor: pointer; }
.cg-remove:hover { border-color: var(--color-danger); color: var(--color-danger); }
.cg-pos { margin-bottom: var(--space-1); display: flex; align-items: center; gap: var(--space-1); }
.cg-label { font-size: var(--font-size-xs); color: var(--color-text-secondary); }
.cg-sources { display: flex; flex-direction: column; gap: var(--space-1); }
.cg-src-row { display: flex; flex-direction: column; gap: 2px; }
.cg-check { font-size: var(--font-size-xs); color: var(--color-text-secondary); display: flex; align-items: center; gap: 2px; cursor: pointer; }
.cg-subs { margin-left: var(--space-4); display: flex; flex-direction: column; gap: 4px; }
.cg-sub { display: flex; align-items: center; gap: 4px; }
.cg-sub-remove { width: 16px; height: 16px; padding: 0; background: none; border: 1px solid var(--color-border-subtle); border-radius: var(--radius-sm); color: var(--color-text-muted); font-size: 12px; cursor: pointer; flex-shrink: 0; }
.cg-sub-remove:hover { border-color: var(--color-danger); color: var(--color-danger); }
.cg-add-btn { margin-top: 2px; font-size: var(--font-size-xs); padding: 1px 6px; }
</style>
