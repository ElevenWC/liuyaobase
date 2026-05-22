<script setup>
</script>

<template>
  <div class="not-found">
    <h1>404</h1>
    <p>页面未找到</p>
    <router-link to="/">返回首页</router-link>
  </div>
</template>

<style scoped>
.not-found {
  max-width: 400px;
  margin: 100px auto;
  text-align: center;
}
.not-found h1 {
  font-size: 3rem;
  color: #ccc;
  margin-bottom: 12px;
}
.not-found p {
  color: #999;
  margin-bottom: 20px;
}
</style>
