<script setup>
import { computed } from 'vue'
import { useSearchStore } from '../../stores/useSearchStore.js'

const props = defineProps({ group: { type: Object, required: true } })
const store = useSearchStore()

const YONGSHEN_OPTS = ['妻财', '官鬼', '父母', '兄弟', '子孙']

const desc = computed(() => {
  const y = props.group.yongshen
  const t = props.group.feishenType
  return `返回本卦中与${t}(${y})同爻位的爻（飞神），总是返回所有飞神`
})
</script>

<template>
  <div class="cg-card">
    <div class="cg-header">
      <span>飞神条件组</span>
      <button class="cg-remove" @click="store.removeConditionGroup(group.id)" title="删除">×</button>
    </div>
    <div class="cg-body">
      <div class="cg-row">
        <span class="cg-label">飞神类型：</span>
        <label class="cg-radio"><input type="radio" v-model="group.feishenType" value="增删飞神" />增删飞神</label>
        <label class="cg-radio"><input type="radio" v-model="group.feishenType" value="易冒飞神" />易冒飞神</label>
      </div>
      <div class="cg-row">
        <span class="cg-label">用神：</span>
        <select v-model="group.yongshen" class="cb-sel">
          <option v-for="y in YONGSHEN_OPTS" :key="y" :value="y">{{ y }}</option>
        </select>
      </div>
      <p class="cg-desc">{{ desc }}</p>
    </div>
  </div>
</template>

<style scoped>
.cg-card { border: 1px solid var(--color-accent); border-radius: var(--radius-md); padding: var(--space-2); margin-bottom: var(--space-2); background: var(--color-bg-tertiary); }
.cg-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-1); font-size: var(--font-size-sm); font-weight: 600; color: var(--color-accent-light); }
.cg-remove { width: 18px; height: 18px; padding: 0; background: none; border: 1px solid var(--color-border-subtle); border-radius: var(--radius-sm); color: var(--color-text-muted); font-size: 14px; cursor: pointer; }
.cg-remove:hover { border-color: var(--color-danger); color: var(--color-danger); }
.cg-body { display: flex; flex-direction: column; gap: var(--space-1); }
.cg-row { display: flex; align-items: center; gap: var(--space-2); }
.cg-label { font-size: var(--font-size-xs); color: var(--color-text-secondary); }
.cg-radio { font-size: var(--font-size-xs); color: var(--color-text-secondary); display: flex; align-items: center; gap: 2px; cursor: pointer; }
.cg-desc { font-size: var(--font-size-xs); color: var(--color-text-muted); margin: 2px 0 0 0; }
</style>
