<script setup>
import NavBar from './components/NavBar.vue'
</script>

<template>
  <NavBar />
  <main>
    <router-view />
  </main>
  <div id="float-layer"></div>
</template>
