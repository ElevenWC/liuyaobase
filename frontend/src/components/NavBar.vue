<script setup>
// 导航栏占位——后续模块填充菜单项
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
  height: 48px;
  padding: 0 20px;
  background: #409eff;
  color: #fff;
}
.brand {
  color: #fff;
  font-weight: bold;
  font-size: 1.1rem;
}
</style>
