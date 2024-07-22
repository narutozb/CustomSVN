<script setup lang="ts">
import TestOptionsComponent from "@/components/SVN/TestSVNNav.vue";
import Dashboard from "@/components/SVN/DashboardTop.vue";

</script>

<template>
  <h2>SVN</h2>

  <TestOptionsComponent/>
  <RouterView/>

  <Dashboard/>

</template>
