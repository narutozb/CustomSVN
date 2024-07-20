<template>
  <div id="app">
    <router-view v-if="isReady"></router-view>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useUserStore } from '@/store/user';

const userStore = useUserStore();
const isReady = ref(false);

onMounted(async () => {
  await userStore.checkAuth();
  isReady.value = true;
});
</script>