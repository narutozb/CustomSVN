<template>
  <div class="commit-details" v-loading="loading">
    <h3>Commit Details</h3>
    <el-descriptions v-if="commit" :column="1" border size="small">
      <el-descriptions-item label="Repository">{{ commit.repo_name || 'N/A' }}</el-descriptions-item>
      <el-descriptions-item label="Branch">{{ commit.branch_name || 'N/A' }}</el-descriptions-item>
      <el-descriptions-item label="Revision">{{ commit.revision || 'N/A' }}</el-descriptions-item>
      <el-descriptions-item label="Author">{{ commit.author || 'N/A' }}</el-descriptions-item>
      <el-descriptions-item label="Date">
        {{ commit.date ? formatDate(commit.date) : 'N/A' }}
      </el-descriptions-item>
      <el-descriptions-item label="Message">
        <span v-html="commit.message || 'N/A'"></span>
      </el-descriptions-item>
    </el-descriptions>

    <h4>File Changes</h4>
    <div class="file-changes-container">
      <el-table
          v-if="fileChanges.length > 0"
          :data="fileChanges"
          style="width: 100%"
          size="small"
          height="250"
      >
        <el-table-column prop="path" label="Path">
          <template #default="scope">
            <span v-html="scope.row.path"></span>
          </template>
        </el-table-column>
        <el-table-column prop="action" label="Action" width="80">
          <template #default="scope">
            <span v-html="scope.row.action"></span>
          </template>
        </el-table-column>
        <el-table-column prop="kind" label="Type" width="80">
          <template #default="scope">
            <span v-html="scope.row.kind"></span>
          </template>
        </el-table-column>
      </el-table>
    </div>
    <el-alert v-if="fileChanges.length === 0 && !loading" title="No file changes available" type="info" show-icon/>
    <el-alert v-if="error" :title="error" type="error" show-icon/>
  </div>
</template>

<script lang="ts" setup>
import { ref, watch } from 'vue';


interface Commit {
  id: number;
  revision: number;
  author: string;
  date: string;
  message: string;
  repo_name?: string;
  branch_name?: string;
  file_changes?: any[];
  // 添加其他可能的属性
}

const props = defineProps<{
  commit: Commit | null
}>();

const loading = ref(false);
const error = ref<string | null>(null);
const fileChanges = ref<any[]>([]);

const fetchFileChanges = async (commit: Commit) => {
  loading.value = true;
  error.value = null;
  try {
    fileChanges.value = commit.file_changes || [];
  } catch (err) {
    console.error('Error fetching file changes:', err);
    error.value = "An error occurred while fetching file changes";
  } finally {
    loading.value = false;
  }
};

watch(() => props.commit, (newCommit) => {
  if (!newCommit) {
    error.value = "No commit data available";
    fileChanges.value = [];
  } else {
    error.value = null;
    fetchFileChanges(newCommit);
  }
}, { immediate: true });

const formatDate = (date: string | Date) => {
  if (!date) return 'N/A';
  const d = new Date(date);
  return d.toLocaleString();
};
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

.file-changes-container {
  max-height: 250px;
  overflow-y: auto;
}

/* 保留高亮样式 */
:deep(.el-table .cell) {
  overflow: visible;
  white-space: pre-wrap;
}

:deep(mark) {
  background-color: yellow;
  padding: 0.2em 0;
}
</style>