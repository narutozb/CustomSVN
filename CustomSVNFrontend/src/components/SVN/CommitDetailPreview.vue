<template>
  <div class="commit-details" v-loading="loading">
    <h3>提交详情</h3>
    <el-descriptions v-if="commit" :column="1" border size="small">
      <el-descriptions-item label="仓库名称">{{ commit.repo_name || 'N/A' }}</el-descriptions-item>
      <el-descriptions-item label="分支名称">{{ commit.branch_name || 'N/A' }}</el-descriptions-item>
      <el-descriptions-item label="版本号">{{ commit.revision || 'N/A' }}</el-descriptions-item>
      <el-descriptions-item label="作者">{{ commit.author || 'N/A' }}</el-descriptions-item>
      <el-descriptions-item label="日期">{{
          commit.date ? $filters.formatDate(commit.date) : 'N/A'
        }}
      </el-descriptions-item>
      <el-descriptions-item label="Message">
        <span v-html="commit.message || 'N/A'"></span>
      </el-descriptions-item>
    </el-descriptions>

    <h4>文件变更</h4>
    <el-table v-if="fileChanges.length > 0" :data="fileChanges" style="width: 100%" size="small">
      <el-table-column prop="path" label="路径">
        <template #default="scope">
          <span v-html="scope.row.path"></span>
        </template>
      </el-table-column>
      <el-table-column prop="action" label="操作" width="80">
        <template #default="scope">
          <span v-html="scope.row.action"></span>
        </template>
      </el-table-column>
      <el-table-column prop="kind" label="类型" width="80">
        <template #default="scope">
          <span v-html="scope.row.kind"></span>
        </template>
      </el-table-column>
    </el-table>
    <el-alert v-if="fileChanges.length === 0 && !loading" title="No file changes available" type="info" show-icon/>
    <el-alert v-if="error" :title="error" type="error" show-icon/>
  </div>
</template>

<script lang="ts" setup>
import {ref, onMounted, watch} from 'vue';
import type {Commit} from "@/services/interfaces";

const props = defineProps<{
  commit: Commit | null
  params: any
}>();

const loading = ref(false);
const error = ref<string | null>(null);
const fileChanges = ref<any[]>([]);

const fetchFileChanges = async (commitId: number) => {
  loading.value = true;
  error.value = null;
  try {
    fileChanges.value = props.commit?.file_changes
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
    if (newCommit.id) {
      fetchFileChanges(newCommit.id);
    } else {
      error.value = "Invalid commit data";
    }
  }
}, {immediate: true});

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