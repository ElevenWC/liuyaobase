<script setup>
import { ref } from 'vue'
import { useSearchStore } from '../../stores/useSearchStore.js'

const store = useSearchStore()

const SCOPE_OPTIONS = [
  { v: 'ben_gua', label: '本卦' },
  { v: 'bian_yao', label: '变爻' },
  { v: 'zhi_gua', label: '之卦静爻' },
  { v: 'yimao', label: '易冒伏神' },
  { v: 'zengshan', label: '增删伏神' },
]

const FIELD_OPTIONS = [
  { v: 'ben_liuqin', label: '六亲' },
  { v: 'ben_dizhi', label: '地支' },
  { v: 'ben_shi_ying', label: '世应' },
  { v: 'ben_yao_type', label: '爻类型' },
  { v: 'ben_tiangan', label: '天干' },
  { v: 'is_dong', label: '动爻' },
  { v: 'is_an_dong', label: '暗动' },
  { v: 'zengshan_exists', label: '有伏神' },
  { v: 'liushen', label: '六神' },
  { v: 'yao_position', label: '爻位' },
  { v: 'zhi_liuqin', label: '之卦六亲' },
  { v: 'zhi_dizhi', label: '之卦地支' },
  { v: 'zhi_shi_ying', label: '之卦世应' },
  { v: 'zhi_yao_type', label: '之卦爻类型' },
  { v: 'yimao_liuqin', label: '易冒六亲' },
  { v: 'yimao_dizhi', label: '易冒地支' },
  { v: 'zengshan_liuqin', label: '增删六亲' },
  { v: 'zengshan_dizhi', label: '增删地支' },
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

const TIME_FIELDS = [
  { v: 'year_zhi', label: '年支' },
  { v: 'month_zhi', label: '月支' },
  { v: 'day_zhi', label: '日支' },
  { v: 'day_gan', label: '日干' },
  { v: 'xun_kong', label: '旬空' },
  { v: 'year_gan', label: '年干' },
  { v: 'month_gan', label: '月干' },
]

const LIUQIN_VALS = ['妻财', '官鬼', '父母', '兄弟', '子孙']
const SHIYING_VALS = ['世', '应']
const YAOTYPE_VALS = ['阳', '阴']
const OPERATORS = ['equals', 'not_equals', 'in', 'gt', 'lt', 'gte', 'lte']
const GUA_PALACE_VALS = ['乾宫', '坤宫', '震宫', '巽宫', '坎宫', '离宫', '艮宫', '兑宫']
const DIZHI_VALS = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
const LIUSHEN_VALS = ['青龙', '朱雀', '勾陈', '螣蛇', '白虎', '玄武']

function fieldValueOptions(field) {
  if (field === 'ben_liuqin' || field === 'zhi_liuqin' || field === 'yimao_liuqin' || field === 'zengshan_liuqin') return LIUQIN_VALS
  if (field === 'ben_shi_ying' || field === 'zhi_shi_ying') return SHIYING_VALS
  if (field === 'ben_yao_type' || field === 'zhi_yao_type') return YAOTYPE_VALS
  if (field === 'ben_dizhi' || field === 'zhi_dizhi' || field === 'yimao_dizhi' || field === 'zengshan_dizhi') return DIZHI_VALS
  if (field === 'is_dong' || field === 'is_an_dong' || field === 'zengshan_exists') return ['true', 'false']
  if (field === 'liushen') return LIUSHEN_VALS
  if (field === 'ben_palace' || field === 'zhi_palace') return GUA_PALACE_VALS
  if (field === 'xun_kong') return ['子丑', '寅卯', '辰巳', '午未', '申酉', '戌亥']
  if (field === 'day_zhi' || field === 'month_zhi' || field === 'year_zhi' || field === 'year_gan' || field === 'month_gan' || field === 'day_gan') return DIZHI_VALS
  return []
}

function addYaoCondition() { store.addCondition('normal') }
function addRelationCondition() { store.addCondition('relation') }
function addGuaCondition() {
  store.addCondition('normal')
  const c = store.conditions[store.conditions.length - 1]
  if (c) store.updateCondition(c.id, { field: 'ben_palace' })
}
function addTimeCondition() {
  store.addCondition('normal')
  const c = store.conditions[store.conditions.length - 1]
  if (c) store.updateCondition(c.id, { field: 'day_zhi', scope: null })
}

function remove(id) { store.removeCondition(id) }
</script>

<template>
  <div class="cond-builder">
    <div class="cb-header">
      <span>检索条件</span>
      <span class="cb-hint">（条件间为 AND 关系）</span>
    </div>

    <div v-if="!store.conditions.length" class="cb-empty">点击下方按钮或左侧字段库添加条件</div>

    <div v-for="cond in store.conditions" :key="cond.id" class="cond-item">
      <button class="cond-remove" @click="remove(cond.id)" title="删除此条件">×</button>

      <!-- 爻属性条件 -->
      <template v-if="!cond.relation">
        <select v-if="cond.scope !== null && cond.field && !GUA_FIELDS.find(f=>f.v===cond.field) && !TIME_FIELDS.find(f=>f.v===cond.field)" v-model="cond.scope" @change="()=>{}" class="cb-sel">
          <option v-for="s in SCOPE_OPTIONS" :key="s.v" :value="s.v">{{ s.label }}</option>
        </select>
        <select v-if="!GUA_FIELDS.find(f=>f.v===cond.field) && !TIME_FIELDS.find(f=>f.v===cond.field)" v-model="cond.field" @change="(e)=>{cond.value=''; if(e.target.value==='is_dong'||e.target.value==='is_an_dong'){cond.value='true';cond.operator='equals'}}" class="cb-sel">
          <option value="">--字段--</option>
          <option v-for="f in FIELD_OPTIONS" :key="f.v" :value="f.v">{{ f.label }}</option>
        </select>
        <select v-else-if="GUA_FIELDS.find(f=>f.v===cond.field) || (!cond.field)" class="cb-sel" @change="(e)=>{cond.field=e.target.value;cond.scope=null; if(e.target.value){store.updateCondition(cond.id,{field:e.target.value,scope:null})}}" :value="cond.field">
          <option value="">--卦类字段--</option>
          <option v-for="f in GUA_FIELDS" :key="f.v" :value="f.v">{{ f.label }}</option>
          <option disabled>──</option>
          <option v-for="f in TIME_FIELDS" :key="f.v" :value="f.v">{{ f.label }}</option>
        </select>
        <select v-model="cond.operator" class="cb-sel cb-op">
          <option v-for="op in OPERATORS" :key="op" :value="op">{{ op }}</option>
        </select>
        <select v-if="fieldValueOptions(cond.field).length" v-model="cond.value" class="cb-sel">
          <option value="">--值--</option>
          <option v-for="v in fieldValueOptions(cond.field)" :key="v" :value="v">{{ v }}</option>
        </select>
        <input v-else v-model="cond.value" class="cb-input" placeholder="输入值" />
      </template>

      <!-- 关系条件 -->
      <template v-else>
        <select v-model="cond.left_type" class="cb-sel">
          <option value="yao_object">爻对象</option>
          <option value="time_object">时间对象</option>
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
        </select>
        <select v-else v-model="cond.left_value" class="cb-sel">
          <option value="">--时间--</option>
          <option value="年支">年支</option>
          <option value="月支">月支</option>
          <option value="日支">日支</option>
        </select>
        <select v-model="cond.relation" class="cb-sel">
          <option value="生">生</option>
          <option value="克">克</option>
          <option value="合">合</option>
          <option value="冲">冲</option>
          <option value="半合">半合</option>
          <option value="三合">三合</option>
          <option value="=">=</option>
          <option value="长生">长生</option>
          <option value="帝旺">帝旺</option>
          <option value="墓">墓</option>
          <option value="绝">绝</option>
        </select>
        <select v-model="cond.right_type" class="cb-sel">
          <option value="yao_object">爻对象</option>
          <option value="time_object">时间对象</option>
          <option value="condition_group_ref">条件组引用</option>
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
        </select>
        <select v-else-if="cond.right_type==='time_object'" v-model="cond.right_value" class="cb-sel">
          <option value="">--时间--</option>
          <option value="年支">年支</option>
          <option value="月支">月支</option>
          <option value="日支">日支</option>
        </select>
        <select v-else v-model="cond.right_value" class="cb-sel">
          <option value="">--条件ID--</option>
          <option v-for="c in store.conditions.filter(x=>x.id!==cond.id&&!x.relation)" :key="c.id" :value="c.id">{{ c.id }}</option>
        </select>
        <select v-if="cond.relation==='三合'" v-model="cond.bureau" class="cb-sel">
          <option value="">--局--</option>
          <option value="水">水</option>
          <option value="木">木</option>
          <option value="火">火</option>
          <option value="金">金</option>
        </select>
      </template>
    </div>

    <div class="cb-actions">
      <button @click="addYaoCondition" class="cb-btn">+ 爻属性</button>
      <button @click="addRelationCondition" class="cb-btn">+ 关系</button>
      <button @click="addGuaCondition" class="cb-btn">+ 卦类</button>
      <button @click="addTimeCondition" class="cb-btn">+ 时间</button>
    </div>
  </div>
</template>

<style scoped>
.cond-builder { flex: 1; background: var(--color-bg-secondary); border-radius: var(--radius-lg); padding: var(--space-3); box-shadow: var(--shadow-sm); }
.cb-header { display: flex; align-items: baseline; gap: var(--space-2); margin-bottom: var(--space-2); }
.cb-header span { font-size: var(--font-size-sm); font-weight: 600; color: var(--color-text-primary); }
.cb-hint { font-size: var(--font-size-xs); color: var(--color-text-muted); font-weight: normal; }
.cb-empty { text-align: center; padding: var(--space-5); color: var(--color-text-muted); font-size: var(--font-size-sm); }

.cond-item { display: flex; align-items: center; gap: 4px; padding: 4px 6px; margin-bottom: 4px; background: var(--color-bg-tertiary); border-radius: var(--radius-md); flex-wrap: wrap; }
.cond-remove { width: 18px; height: 18px; padding: 0; background: none; border: 1px solid var(--color-border-subtle); border-radius: var(--radius-sm); color: var(--color-text-muted); font-size: 14px; cursor: pointer; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.cond-remove:hover { border-color: var(--color-danger); color: var(--color-danger); }

.cb-sel { padding: 2px 4px; background: var(--color-bg-input); color: var(--color-text-primary); border: 1px solid var(--color-border-primary); border-radius: var(--radius-sm); font-size: var(--font-size-sm); }
.cb-sel:focus { outline: none; border-color: var(--color-accent); }
.cb-input { padding: 2px 6px; background: var(--color-bg-input); color: var(--color-text-primary); border: 1px solid var(--color-border-primary); border-radius: var(--radius-sm); font-size: var(--font-size-sm); width: 80px; }
.cb-input:focus { outline: none; border-color: var(--color-accent); }
.cb-op { width: 70px; }

.cb-actions { display: flex; gap: var(--space-2); margin-top: var(--space-3); }
.cb-btn { padding: 3px 10px; background: var(--color-bg-tertiary); color: var(--color-text-secondary); border: 1px solid var(--color-border-primary); border-radius: var(--radius-md); font-size: var(--font-size-xs); cursor: pointer; transition: all var(--transition-fast); }
.cb-btn:hover { border-color: var(--color-accent); color: var(--color-accent-light); }
</style>
