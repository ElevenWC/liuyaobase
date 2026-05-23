<script setup>
</script>

<template>
  <nav class="navbar">
    <router-link to="/guali" class="brand">liuyaobase</router-link>
    <div class="nav-links">
      <router-link to="/guali">卦例</router-link>
      <router-link to="/input">手动导入</router-link>
      <router-link to="/import">JSON导入</router-link>
      <router-link to="/tags">标签</router-link>
    </div>
  </nav>
</template>

<style scoped>
.navbar {
  display: flex; align-items: center; justify-content: space-between;
  height: var(--navbar-height); padding: 0 var(--space-5);
  background: var(--color-bg-glass); backdrop-filter: blur(var(--glass-blur));
  border-bottom: 1px solid var(--glass-border);
}
.brand { color: #fff; font-weight: bold; font-size: 1.1rem; text-decoration: none; }
.nav-links { display: flex; gap: var(--space-4); }
.nav-links a { color: var(--color-text-secondary); text-decoration: none; font-size: var(--font-size-sm); transition: color var(--transition-fast); }
.nav-links a:hover, .nav-links a.router-link-active { color: var(--color-accent-light); }
</style>
