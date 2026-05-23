<script setup>
</script>

<template>
  <nav class="navbar">
    <router-link to="/" class="brand">liuyaobase</router-link>
  </nav>
</template>

<style scoped>
.navbar {
  display: flex;
  align-items: center;
  height: var(--navbar-height);
  padding: 0 var(--space-5);
  background: var(--color-bg-glass);
  backdrop-filter: blur(var(--glass-blur));
  border-bottom: 1px solid var(--glass-border);
  color: var(--color-text-primary);
}
.brand {
  color: #fff;
  font-weight: bold;
  font-size: 1.1rem;
  text-decoration: none;
}
</style>
