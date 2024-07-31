<template>
  <div v-if="commit">
    <h2>Commit Details</h2>
    <el-descriptions :column="1" border>
      <el-descriptions-item label="RepositoryName">{{ repository?.name }}</el-descriptions-item>
      <el-descriptions-item label="BranchName">{{ branch?.name }}</el-descriptions-item>
      <el-descriptions-item label="Revision">{{ commit.revision }}</el-descriptions-item>
      <el-descriptions-item label="Author">{{ commit.author }}</el-descriptions-item>
      <el-descriptions-item label="Date">{{ $filters.formatDate(commit.date) }}</el-descriptions-item>
      <el-descriptions-item label="Message">{{ commit.message }}</el-descriptions-item>
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
  </div>
</template>

<script lang="ts" setup>
import {ref, onMounted} from 'vue';
import {useRoute} from 'vue-router';
import {getCommitDetail} from '@/services/svn_api';
import type {Branch, Commit, Repository} from "@/services/interfaces";

const route = useRoute();
const commit = ref<Commit | null>(null);
const repository = ref<Repository>()
const branch = ref<Branch>()

onMounted(async () => {
  const commitId = Number(route.params.id);

  try {
    commit.value = await getCommitDetail(commitId);
    repository.value = commit.value?.repository;
    branch.value = commit.value?.branch;
  } catch (error) {
    console.error('Error fetching commit details:', error);
  }
});
</script>