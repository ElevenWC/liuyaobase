<script setup>
import { computed } from 'vue'
import { useSearchStore } from '../../stores/useSearchStore.js'

const props = defineProps({ group: { type: Object, required: true } })
const store = useSearchStore()

const YONGSHEN_OPTS = ['妻财', '官鬼', '父母', '兄弟', '子孙']

const desc = computed(() => {
  return `含义：返回本卦中与${props.group.feishenType}(${props.group.yongshen})同爻位的爻（飞神）`
})
</script>

<template>
  <div class="cg-card">
    <div class="cg-head">
      <span class="cg-title">飞神条件组</span>
      <button class="cg-del" @click="store.removeConditionGroup(group.id)" title="删除">×</button>
    </div>
    <div class="cg-body">
      <div class="cg-row">
        <span class="cg-lbl">飞神类型：</span>
        <label class="cg-radio"><input type="radio" v-model="group.feishenType" value="增删飞神" />增删飞神</label>
        <label class="cg-radio"><input type="radio" v-model="group.feishenType" value="易冒飞神" />易冒飞神</label>
      </div>
      <div class="cg-row">
        <span class="cg-lbl">用神：</span>
        <select v-model="group.yongshen" class="cb-sel">
          <option v-for="y in YONGSHEN_OPTS" :key="y" :value="y">{{ y }}</option>
        </select>
      </div>
      <p class="cg-note">{{ desc }}</p>
      <p class="cg-note">飞神条件组总是返回所有飞神，如需限定爻位，请用 AND 连接同一爻条件组</p>
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
.cg-del { margin-left: auto; width: 18px; height: 18px; padding: 0; background: none; border: 1px solid var(--color-border-subtle); border-radius: var(--radius-sm); color: var(--color-text-muted); font-size: 14px; cursor: pointer; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.cg-del:hover { border-color: var(--color-danger); color: var(--color-danger); }
.cg-body { display: flex; flex-direction: column; gap: var(--space-1); }
.cg-row { display: flex; align-items: center; gap: var(--space-2); }
.cg-lbl { font-size: var(--font-size-xs); color: var(--color-text-secondary); }
.cg-radio { font-size: var(--font-size-xs); color: var(--color-text-secondary); display: flex; align-items: center; gap: 2px; cursor: pointer; accent-color: var(--color-accent); }
.cg-note { font-size: var(--font-size-xs); color: var(--color-text-muted); margin: 0; }
</style>
