<!-- src/views/NotFoundView.vue -->
<template>
  <div class="not-found">
    <h1>404 - Page Not Found</h1>
    <p>The page you are looking for does not exist.</p>
    <router-link to="/">Go to Home</router-link>
  </div>
</template>

<script setup lang="ts">
// 不需要额外的逻辑
</script>

<style scoped>
.not-found {
  text-align: center;
  padding: 50px;
}
</style>