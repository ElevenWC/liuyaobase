<script setup>
</script>

<template>
  <nav class="navbar">
    <router-link to="/guali" class="brand">liuyaobase</router-link>
    <div class="nav-links">
      <router-link to="/guali">卦例</router-link>
      <div class="nav-dropdown">
        <span class="dropdown-trigger">解卦 ▾</span>
        <div class="dropdown-menu">
          <router-link to="/jiegua/bagong">八宫变化</router-link>
          <router-link to="/jiegua/hugua">互卦</router-link>
        </div>
      </div>
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
.nav-links { display: flex; align-items: center; gap: var(--space-4); }
.nav-links a { color: var(--color-text-secondary); text-decoration: none; font-size: var(--font-size-sm); transition: color var(--transition-fast); }
.nav-links a:hover, .nav-links a.router-link-active { color: var(--color-accent-light); }

.nav-dropdown { position: relative; }
.dropdown-trigger { color: var(--color-text-secondary); font-size: var(--font-size-sm); cursor: pointer; user-select: none; }
.dropdown-trigger:hover { color: var(--color-accent-light); }
.dropdown-menu {
  display: none; position: absolute; top: 100%; left: 0;
  background: var(--color-bg-secondary); border: 1px solid var(--color-border-primary);
  border-radius: var(--radius-md); padding: var(--space-1) 0; min-width: 100px;
  box-shadow: var(--shadow-md); z-index: 100;
}
.nav-dropdown:hover .dropdown-menu { display: block; }
.dropdown-menu a {
  display: block; padding: 4px 12px; color: var(--color-text-secondary);
  font-size: var(--font-size-sm); text-decoration: none; white-space: nowrap;
}
.dropdown-menu a:hover { background: var(--color-bg-tertiary); color: var(--color-accent-light); }
</style>
