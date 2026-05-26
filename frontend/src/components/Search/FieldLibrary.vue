<script setup>
import { ref, computed } from 'vue'

const emit = defineEmits(['select-field'])

const searchText = ref('')
const collapsed = ref({})

// 6 大分类
const categories = [
  {
    key: 'time', name: '时间类',
    fields: [
      { key: 'year_pillar', label: '年柱', type: 'normal' },
      { key: 'year_gan', label: '年干', type: 'normal' },
      { key: 'year_zhi', label: '年支', type: 'normal' },
      { key: 'month_pillar', label: '月柱', type: 'normal' },
      { key: 'month_gan', label: '月干', type: 'normal' },
      { key: 'month_zhi', label: '月支', type: 'normal' },
      { key: 'day_pillar', label: '日柱', type: 'normal' },
      { key: 'day_gan', label: '日干', type: 'normal' },
      { key: 'day_zhi', label: '日支', type: 'normal' },
      { key: 'xun_kong', label: '旬空', type: 'normal' },
    ],
  },
  {
    key: 'gua', name: '卦类',
    fields: [
      { key: 'ben_palace', label: '本卦卦宫', type: 'normal' },
      { key: 'ben_palace_type', label: '本卦宫位', type: 'normal' },
      { key: 'ben_special_type', label: '本卦特殊类型', type: 'normal' },
      { key: 'zhi_palace', label: '之卦卦宫', type: 'normal' },
      { key: 'zhi_palace_type', label: '之卦宫位', type: 'normal' },
      { key: 'zhi_special_type', label: '之卦特殊类型', type: 'normal' },
      { key: 'fan_yin_yimao', label: '易冒反吟', type: 'normal' },
      { key: 'fan_yin_yaobian', label: '爻变反吟', type: 'normal' },
      { key: 'fu_yin', label: '伏吟', type: 'normal' },
    ],
  },
  {
    key: 'yao', name: '爻属性',
    fields: [
      { key: 'yao_position', label: '爻位', type: 'normal', scopes: '全部来源' },
      { key: 'ben_yao_type', label: '爻类型', type: 'normal', scopes: '仅本卦' },
      { key: 'ben_liuqin', label: '六亲', type: 'normal', scopes: '仅本卦' },
      { key: 'ben_dizhi', label: '地支', type: 'normal', scopes: '仅本卦' },
      { key: 'ben_tiangan', label: '天干', type: 'normal', scopes: '仅本卦' },
      { key: 'ben_shi_ying', label: '世应', type: 'normal', scopes: '仅本卦' },
      { key: 'is_dong', label: '动爻', type: 'normal', scopes: '仅本卦' },
      { key: 'is_an_dong', label: '暗动', type: 'normal', scopes: '仅本卦' },
      { key: 'liushen', label: '六神', type: 'normal', scopes: '全部来源' },
      { key: 'zhi_liuqin', label: '之卦六亲', type: 'normal', scopes: '仅变爻/之卦' },
      { key: 'zhi_dizhi', label: '之卦地支', type: 'normal', scopes: '仅变爻/之卦' },
      { key: 'yimao_liuqin', label: '易冒六亲', type: 'normal', scopes: '仅易冒' },
      { key: 'yimao_dizhi', label: '易冒地支', type: 'normal', scopes: '仅易冒' },
      { key: 'zengshan_liuqin', label: '增删六亲', type: 'normal', scopes: '仅增删' },
      { key: 'zengshan_dizhi', label: '增删地支', type: 'normal', scopes: '仅增删' },
    ],
  },
  {
    key: 'relation', name: '关系',
    fields: [
      { key: 'shengke', label: '生克', type: 'relation' },
      { key: 'he_chong', label: '合冲', type: 'relation' },
      { key: 'banhe', label: '半合', type: 'relation' },
      { key: 'sanhe', label: '三合', type: 'relation' },
      { key: 'xiangdeng', label: '相等', type: 'relation' },
      { key: 'shengwang', label: '生旺墓绝', type: 'relation' },
    ],
  },
  {
    key: 'shensha', name: '神煞',
    fields: [
      { key: 'is_ganlu', label: '是干禄', type: 'shensha' },
      { key: 'dai_ganlu', label: '带干禄', type: 'shensha' },
      { key: 'is_yima', label: '是驿马', type: 'shensha' },
      { key: 'dai_yima', label: '带驿马', type: 'shensha' },
      { key: 'is_yangren', label: '是羊刃', type: 'shensha' },
      { key: 'dai_yangren', label: '带羊刃', type: 'shensha' },
      { key: 'is_taohua', label: '是桃花', type: 'shensha' },
      { key: 'dai_taohua', label: '带桃花', type: 'shensha' },
    ],
  },
  {
    key: 'count', name: '数目',
    fields: [
      { key: 'count', label: '属性数目', type: 'count' },
    ],
  },
]

const filtered = computed(() => {
  if (!searchText.value) return categories
  const q = searchText.value.toLowerCase()
  return categories.map(cat => ({
    ...cat,
    fields: cat.fields.filter(f => f.label.toLowerCase().includes(q) || f.key.includes(q)),
  })).filter(cat => cat.fields.length)
})

function toggle(key) { collapsed.value[key] = !collapsed.value[key] }

function onSelect(cat, field) {
  emit('select-field', { cat: cat.key, field: field.key, type: field.type, label: field.label })
}
</script>

<template>
  <div class="field-library">
    <div class="fl-header">字段库</div>
    <input v-model="searchText" class="fl-search" placeholder="搜索字段..." />

    <div class="fl-cats">
      <div v-for="cat in filtered" :key="cat.key" class="fl-cat">
        <div class="fl-cat-name" @click="toggle(cat.key)">
          <span class="fl-arrow">{{ collapsed[cat.key] ? '▸' : '▾' }}</span>
          {{ cat.name }}
          <span class="fl-count">{{ cat.fields.length }}</span>
        </div>
        <div v-if="!collapsed[cat.key]" class="fl-fields">
          <span v-for="f in cat.fields" :key="f.key"
            class="fl-field" :class="{ 'fl-field-limited': f.scopes && f.scopes !== '全部来源' }" :title="f.scopes || ''" @click="onSelect(cat, f)">{{ f.label }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.field-library { width: 270px; flex-shrink: 0; background: var(--color-bg-secondary); border-radius: var(--radius-lg); padding: var(--space-3); box-shadow: var(--shadow-sm); }
.fl-header { font-size: var(--font-size-sm); font-weight: 600; color: var(--color-text-primary); margin-bottom: var(--space-2); }
.fl-search { width: 100%; padding: 3px 8px; background: var(--color-bg-input); color: var(--color-text-primary); border: 1px solid var(--color-border-primary); border-radius: var(--radius-md); font-size: var(--font-size-sm); margin-bottom: var(--space-2); box-sizing: border-box; }
.fl-search:focus { outline: none; border-color: var(--color-accent); }

.fl-cats { display: flex; flex-direction: column; gap: 2px; }
.fl-cat-name { display: flex; align-items: center; gap: 4px; padding: 3px 4px; font-size: var(--font-size-sm); color: var(--color-text-secondary); cursor: pointer; border-radius: var(--radius-sm); user-select: none; }
.fl-cat-name:hover { background: var(--color-bg-tertiary); }
.fl-arrow { font-size: 10px; width: 12px; }
.fl-count { margin-left: auto; font-size: var(--font-size-xs); color: var(--color-text-muted); }

.fl-fields { display: flex; flex-wrap: wrap; gap: 3px; padding: 2px 0 6px 16px; }
.fl-field { padding: 1px 8px; background: var(--color-bg-tertiary); border-radius: var(--radius-sm); font-size: var(--font-size-xs); color: var(--color-text-secondary); cursor: pointer; transition: all var(--transition-fast); }
.fl-field:hover { background: var(--color-accent); color: #fff; }
.fl-field-limited { color: var(--color-text-muted); border: 1px dashed var(--color-border-subtle); }
</style>
