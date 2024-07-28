<template>
  <div class="svn-header">
    <SVNAside/>
    <el-breadcrumb separator="/">
      <el-breadcrumb-item>Home</el-breadcrumb-item>
      <el-breadcrumb-item v-for="item in breadcrumbs" :key="item.path" :to="{ path: item.path }">
        {{ item.name }}
      </el-breadcrumb-item>
    </el-breadcrumb>
  </div>

</template>

<script lang="ts" setup>
import {useRoute} from 'vue-router';
import {computed, ref} from 'vue';
import {ElBreadcrumb, ElBreadcrumbItem} from 'element-plus';
import SVNAside from "@/components/SVN/SVNAside.vue";

const route = useRoute();

const breadcrumbs = computed(() => {
  const paths = route.path.split('/').filter(Boolean);
  return paths.map((path, index) => ({
    name: path.charAt(0).toUpperCase() + path.slice(1),
    path: '/' + paths.slice(0, index + 1).join('/')
  }));
});

</script>

<style scoped>
.svn-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.el-select {
  margin-right: 20px;
}
</style>