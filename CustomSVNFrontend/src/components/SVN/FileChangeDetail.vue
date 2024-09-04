<template>
  <div>
    <el-skeleton :loading="loading" animated :count="1" :rows="4">
      <template #default>
        <div v-if="fileChange">
          <h2>File Change Details</h2>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="Repository">{{ fileChange.repository.name }}</el-descriptions-item>
            <el-descriptions-item label="Path">{{ fileChange.path }}</el-descriptions-item>
            <el-descriptions-item label="Action">{{ fileChange.action }}</el-descriptions-item>
            <el-descriptions-item label="Kind">{{ fileChange.kind }}</el-descriptions-item>
          </el-descriptions>

          <h3>Associated Commits</h3>
          <el-table v-loading="commitsLoading" element-loading-text="Loading commits..." :data="relatedCommits" style="width: 100%">
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
                <router-link
                    :to="{ name: 'CommitDetail', params: { id: scope.row.id } }"
                    target="_blank"
                >
                  View Details
                </router-link>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </template>
    </el-skeleton>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import { getCommitDetailsByChangeFile, getRelatedCommits } from '@/services/svn_api';
import type { FileChangeDetails, Commit } from "@/services/interfaces";
import { ElMessage } from 'element-plus';

const route = useRoute();

const fileChange = ref<FileChangeDetails | null>(null);
const relatedCommits = ref<Commit[]>([]);
const loading = ref(true);
const commitsLoading = ref(false);

async function loadData() {
  const fileChangeId = Number(route.params.id);
  loading.value = true;

  try {
    fileChange.value = await getCommitDetailsByChangeFile(fileChangeId);
    loading.value = false;

    if (fileChange.value && fileChange.value.path) {
      commitsLoading.value = true;
      const commits = await getRelatedCommits(fileChange.value.id);
      relatedCommits.value = Array.isArray(commits) ? commits : [];
      commitsLoading.value = false;
    }
  } catch (error) {
    console.error('Error fetching file change details:', error);
    ElMessage.error('Failed to load data. Please try again later.');
    loading.value = false;
    commitsLoading.value = false;
  }
}

onMounted(loadData);

watch(() => route.params.id, loadData);
</script>