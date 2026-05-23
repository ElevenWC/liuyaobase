<script setup>
import { useRouter } from 'vue-router'
import GualiList from './GualiList.vue'
import GualiDetail from './GualiDetail.vue'

const router = useRouter()
</script>

<template>
  <div class="home-layout">
    <aside class="left-panel">
      <div class="panel-header">六爻卦例管理系统</div>
      <GualiList />
    </aside>
    <main class="right-panel">
      <div class="action-bar">
        <button @click="router.push('/input')" class="btn-action">+ 手动导入</button>
        <button @click="router.push('/import')" class="btn-action">+ JSON导入</button>
      </div>
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
.right-panel { flex: 1; background: var(--color-bg-primary); overflow-y: auto; display: flex; flex-direction: column; }
.action-bar { display: flex; gap: var(--space-2); padding: var(--space-3); border-bottom: 1px solid var(--color-border-primary); }
.btn-action { padding: 6px 16px; border: 1px solid var(--color-border-primary); border-radius: var(--radius-md); background: var(--color-bg-secondary); color: var(--color-text-primary); cursor: pointer; font-size: var(--font-size-sm); transition: border-color var(--transition-fast); }
.btn-action:hover { border-color: var(--color-accent); }
</style>
