<script setup>
import { ref } from 'vue'
import GualiList from './GualiList.vue'
import GualiDetail from './GualiDetail.vue'

const leftPanelCollapsed = ref(false)
</script>

<template>
  <div class="home-layout">
    <div v-if="leftPanelCollapsed" class="fl-toggle" @click="leftPanelCollapsed = false" title="展开侧栏">
      <span>▸</span>
    </div>
    <div v-else class="left-sidebar">
      <aside class="left-panel">
        <div class="panel-header">六爻卦例管理系统</div>
        <GualiList />
      </aside>
      <div class="fl-toggle" @click="leftPanelCollapsed = true" title="收起侧栏">
        <span>◂</span>
      </div>
    </div>
    <main class="right-panel">
      <GualiDetail />
    </main>
  </div>
</template>

<style scoped>
.home-layout {
  display: flex;
  height: calc(100vh - var(--navbar-height));
  background: var(--color-bg-primary);
}
.left-panel {
  width: 340px; min-width: 280px;
  border-right: 1px solid var(--color-border-primary);
  background: var(--color-bg-glass); backdrop-filter: blur(var(--glass-blur));
  display: flex; flex-direction: column;
}
.panel-header { padding: var(--space-3); font-size: var(--font-size-md); font-weight: bold; color: var(--color-text-primary); border-bottom: 1px solid var(--color-border-primary); }
.right-panel { flex: 1; background: var(--color-bg-primary); overflow-y: auto; }

.left-sidebar { display: flex; gap: var(--space-2); flex-shrink: 0; }
.fl-toggle {
  width: 16px; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  background: var(--color-bg-secondary); border-radius: var(--radius-sm);
  cursor: pointer; color: var(--color-text-muted); font-size: 25px;
  transition: all var(--transition-fast); user-select: none;
}
.fl-toggle:hover { background: var(--color-bg-tertiary); color: var(--color-accent-light); }
</style>
