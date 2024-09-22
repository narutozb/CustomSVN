<template>
  <el-card v-loading="isLoading" element-loading-text="Loading data...">
    <template #header>
      <h2>File Change Details</h2>
    </template>
    <template v-if="fileChange">
      <el-descriptions :column="1" border>
        <el-descriptions-item label="Repository">{{ fileChange.repository?.name }}</el-descriptions-item>
        <el-descriptions-item label="Path">{{ fileChange.path }}</el-descriptions-item>
        <el-descriptions-item label="Action">{{ fileChange.action }}</el-descriptions-item>
        <el-descriptions-item label="Kind">{{ fileChange.kind }}</el-descriptions-item>
        <el-descriptions-item label="Suffix">{{ fileChange.suffix }}</el-descriptions-item>
      </el-descriptions>

      <h3>Associated Commits</h3>
      <el-table :data="relatedCommits" style="width: 100%">
        <el-table-column label="Revision" width="120">
          <template #default="{ row }">
            <template v-if="enableHover">
              <el-popover
                placement="right"
                :width="400"
                trigger="hover"
                :show-after="100"
              >
                <template #default>
                  <div class="commit-details">
                    <h4>Commit Details</h4>
                    <el-descriptions :column="1" border>
                      <el-descriptions-item label="Repository">{{ fileChange.repository?.name }}</el-descriptions-item>
                      <el-descriptions-item label="Revision">{{ row.revision }}</el-descriptions-item>
                      <el-descriptions-item label="Author">{{ row.author }}</el-descriptions-item>
                      <el-descriptions-item label="Date">{{ formatDate(row.date) }}</el-descriptions-item>
                      <el-descriptions-item label="Message">{{ row.message }}</el-descriptions-item>
                    </el-descriptions>
                  </div>
                </template>
                <template #reference>
                  <router-link
                    v-if="row.id"
                    :to="{ name: 'CommitDetail', params: { id: row.id.toString() } }"
                    class="revision-link"
                  >
                    {{ row.revision }}
                  </router-link>
                </template>
              </el-popover>
            </template>
            <template v-else>
              <router-link
                v-if="row.id"
                :to="{ name: 'CommitDetail', params: { id: row.id.toString() } }"
                class="revision-link"
              >
                {{ row.revision }}
              </router-link>
            </template>
          </template>
        </el-table-column>
        <el-table-column prop="author" label="Author" width="150" />
        <el-table-column prop="date" label="Date" width="200">
          <template #default="{ row }">
            {{ formatDate(row.date) }}
          </template>
        </el-table-column>
        <el-table-column prop="message" label="Message" />
      </el-table>
    </template>
    <el-alert v-else-if="error" :title="error" type="error" show-icon />
  </el-card>
</template>

<script lang="ts" setup>
import { ref, onMounted, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { getCommitDetailsByChangeFile, getRelatedCommits } from '@/services/svn_api';
import type { FileChangeDetails, Commit } from "@/services/interfaces";
import { ElMessage } from 'element-plus';

const router = useRouter();
const route = useRoute();

const fileChange = ref<FileChangeDetails | null>(null);
const relatedCommits = ref<Commit[]>([]);
const isLoading = ref(false);
const error = ref<string | null>(null);

// 新增：配置项来控制是否启用 Hover 功能
const enableHover = ref(false); // 默认启用 Hover 功能，可以根据需要修改默认值

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString();
};

async function loadData() {
  const fileChangeId = Number(route.params.id);
  isLoading.value = true;
  error.value = null;

  try {
    fileChange.value = await getCommitDetailsByChangeFile(fileChangeId);
    if (fileChange.value?.id) {
      relatedCommits.value = await getRelatedCommits(fileChange.value.id);
    }
  } catch (e) {
    console.error('Error in loadData:', e);
    error.value = 'Failed to load data. Please try again.';
    ElMessage.error(error.value);
  } finally {
    isLoading.value = false;
  }
}

onMounted(loadData);

watch(() => route.params.id, (newId, oldId) => {
  if (newId !== oldId) {
    loadData();
  }
});
</script>

<style scoped>
.commit-details {
  font-size: 14px;
}

.commit-details h4 {
  margin-top: 0;
  margin-bottom: 16px;
}

.revision-link {
  text-decoration: none;
  color: #409EFF;
}

.revision-link:hover {
  text-decoration: underline;
}
</style>