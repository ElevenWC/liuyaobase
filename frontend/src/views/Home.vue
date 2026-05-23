<script setup>
import GualiList from './GualiList.vue'
import GualiDetail from './GualiDetail.vue'
</script>

<template>
  <div class="home-layout">
    <aside class="left-panel">
      <div class="panel-header">六爻卦例管理系统</div>
      <GualiList />
    </aside>
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
  overflow-y: auto;
}
.panel-header { padding: var(--space-3); font-size: var(--font-size-md); font-weight: bold; color: var(--color-text-primary); border-bottom: 1px solid var(--color-border-primary); }
.right-panel { flex: 1; background: var(--color-bg-primary); overflow-y: auto; }
</style>
