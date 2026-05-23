<script setup>
import GualiList from './GualiList.vue'
import GualiDetail from './GualiDetail.vue'
</script>

<template>
  <div class="home-layout">
    <aside class="left-panel">
      <GualiList />
    </aside>
    <main class="right-panel">
      <GualiDetail />
    </main>
  </div>
</template>

<style scoped>
.home-layout { display: flex; height: calc(100vh - 48px); background: #313c4f; }
.left-panel { width: 320px; min-width: 280px; border-right: 1px solid #555; overflow-y: auto; }
.right-panel { flex: 1; overflow-y: auto; }
</style>
