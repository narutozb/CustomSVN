<!--CommitDetailHover.vue-->
<template>
  <div class="commit-details" v-loading="loading">
    <h3>提交详情</h3>
    <el-descriptions v-if="commit" :column="1" border size="small">
      <el-descriptions-item label="仓库名称">{{ commit.repository?.name }}</el-descriptions-item>
      <el-descriptions-item label="分支名称">{{ commit.branch?.name }}</el-descriptions-item>
      <el-descriptions-item label="版本号">{{ commit.revision }}</el-descriptions-item>
      <el-descriptions-item label="作者">{{ commit.author }}</el-descriptions-item>
      <el-descriptions-item label="日期">{{ $filters.formatDate(commit.date) }}</el-descriptions-item>
      <el-descriptions-item label="消息">{{ commit.message }}</el-descriptions-item>
    </el-descriptions>

    <h4>文件变更</h4>
    <el-table v-if="commit" :data="commit.file_changes" style="width: 100%" size="small">
      <el-table-column prop="path" label="路径"/>
      <el-table-column prop="action" label="操作" width="80"/>
      <el-table-column prop="kind" label="类型" width="80"/>
    </el-table>
    <el-alert v-if="error" :title="error" type="error" show-icon/>
  </div>
</template>

<script lang="ts" setup>
import {ref, onMounted, watch} from 'vue';
import type {Commit} from "@/services/interfaces";
import {getCommitDetail} from '@/services/svn_api';

const props = defineProps<{
  commitId: number
}>();

const commit = ref<Commit | null>(null);
const loading = ref(false);
const error = ref<string | null>(null);

const loadCommitDetail = async () => {
  loading.value = true;
  error.value = null;
  try {
    commit.value = await getCommitDetail(props.commitId);
  } catch (err) {
    error.value = '加载提交详情失败，请重试。';
    console.error('Error loading commit detail:', err);
  } finally {
    loading.value = false;
  }
};

onMounted(loadCommitDetail);

watch(() => props.commitId, loadCommitDetail);
</script>

<style scoped>
.commit-details {
  font-size: 14px;
}

.commit-details h3 {
  margin-top: 0;
  margin-bottom: 16px;
}

.commit-details h4 {
  margin-top: 16px;
  margin-bottom: 8px;
}
</style>