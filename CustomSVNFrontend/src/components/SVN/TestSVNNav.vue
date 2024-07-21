<template>
  <div class="svn-header">
<!--    <el-select v-model="selectedOption" placeholder="Select Option" style="width: 200px; margin-right: 20px;">-->
<!--      <el-option-->
<!--          v-for="item in options"-->
<!--          :key="item.value"-->
<!--          :label="item.label"-->
<!--          :value="item.value">-->
<!--      </el-option>-->
<!--    </el-select>-->
    <SVNAside/>
    <el-breadcrumb separator="/">
<!--      <el-breadcrumb-item :to="{ path: '/' }">Home</el-breadcrumb-item>-->
      <el-breadcrumb-item >Home</el-breadcrumb-item>
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
// // 下拉列表的选项
// const options = [
//   {
//     value: 'option1',
//     label: 'Option 1'
//   },
//   {
//     value: 'option2',
//     label: 'Option 2'
//   },
//   {
//     value: 'option3',
//     label: 'Option 3'
//   }
// ]
//
// // 选中的选项
// const selectedOption = ref('')
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