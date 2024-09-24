<template>
  <el-card v-loading="loading" :element-loading-text="loadingMessage">
    <template #header>
      <h2>Commit Details</h2>
    </template>
    <template v-if="commit">
      <el-descriptions :column="1" border>
        <el-descriptions-item label="RepositoryName">{{ repository?.name }}</el-descriptions-item>
        <el-descriptions-item label="BranchName">{{ branch?.name }}</el-descriptions-item>
        <el-descriptions-item label="Revision">{{ commit.revision }}</el-descriptions-item>
        <el-descriptions-item label="Author">{{ commit.author }}</el-descriptions-item>
        <el-descriptions-item label="Date">{{ $filters.formatDate(commit.date) }}</el-descriptions-item>
        <el-descriptions-item label="Message111">{{ commit.message }}</el-descriptions-item>
      </el-descriptions>

      <h3>File Changes</h3>
      <el-table :data="commit.file_changes" style="width: 100%">
        <el-table-column prop="path" label="Path">
          <template #default="scope">
            <router-link :to="{
              name: 'FileChangeDetail',
              params: {
                id: scope.row.id,
                repositoryId: repository?.id,
                branchId: branch?.id
              }
            }">
              {{ scope.row.path }}
            </router-link>
          </template>
        </el-table-column>
        <el-table-column prop="action" label="Action"></el-table-column>
        <el-table-column prop="kind" label="Kind"></el-table-column>
      </el-table>
    </template>
    <el-alert v-else-if="error" :title="error" type="error" show-icon />
  </el-card>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { getRepositories, getCommitDetail, getBranches } from '@/services/svn_api';
import type { Branch, Commit, Repository } from "@/services/interfaces";
import { useLoadingState } from '@/composables/useLoadingState';

const route = useRoute();
const commit = ref<Commit | null>(null);
const repository = ref<Repository>();
const branch = ref<Branch>();

const { loading, error, withLoading } = useLoadingState({
  loadingMessage: 'Loading commit details...',
  errorMessage: 'Failed to load commit details. Please try again.'
});

const loadingMessage = 'Loading commit details...';

const loadData = async () => {
  const commitId = Number(route.params.id);

  await withLoading(async () => {
    commit.value = await getCommitDetail(commitId);
    repository.value = commit.value?.repository;
    branch.value = commit.value?.branch;
  });
};

onMounted(loadData);
</script>