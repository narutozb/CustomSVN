<template>
  <div v-if="fileChange">
    <h2>File Change Details</h2>
    <el-descriptions :column="1" border>
      <el-descriptions-item label="Path">{{ fileChange.path }}</el-descriptions-item>
      <el-descriptions-item label="Action">{{ fileChange.action }}</el-descriptions-item>
      <el-descriptions-item label="Kind">{{ fileChange.kind }}</el-descriptions-item>
    </el-descriptions>

    <h3>Associated Commits</h3>
    <el-table :data="relatedCommits" style="width: 100%">
      <el-table-column prop="revision" label="Revision" width="100"></el-table-column>
      <el-table-column prop="author" label="Author" width="150"></el-table-column>
      <el-table-column prop="date" label="Date" width="200">
        <template #default="scope">
          {{ $filters.formatDate(scope.row.date) }}
        </template>
      </el-table-column>
      <el-table-column prop="message" label="Message"></el-table-column>
      <el-table-column label="Actions" width="120">
        <template #default="scope">
          <el-button size="small" @click="viewCommitDetails(scope.row.id)">View Details</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { getFileChangeDetail, getRelatedCommits } from '@/services/svn_api';
import type { FileChange, Commit } from "@/services/interfaces";

const route = useRoute();
const router = useRouter();
const fileChange = ref<FileChange | null>(null);
const relatedCommits = ref<Commit[]>([]);

onMounted(async () => {
  const fileChangeId = Number(route.params.id);
  try {
    fileChange.value = await getFileChangeDetail(fileChangeId);
    if (fileChange.value && fileChange.value.path) {
      const commits = await getRelatedCommits(fileChange.value.path);
      if (Array.isArray(commits)) {
        relatedCommits.value = commits;
      } else {
        console.error('Unexpected data format for related commits');
        relatedCommits.value = [];
      }
    }
  } catch (error) {
    console.error('Error fetching file change details:', error);
  }
});

const viewCommitDetails = (commitId: number) => {
  router.push({ name: 'CommitDetail', params: { id: commitId } });
};
</script>