<template>
  <h1>commits</h1>

  <div class="commit-search">
    <el-card class="search-form">
      <el-form :model="searchForm" @submit.prevent="submitSearch">
        <el-form-item label="Revision">
          <el-input v-model="searchForm.revision"></el-input>
        </el-form-item>
        <el-form-item label="作者">
          <el-input v-model="searchForm.author"></el-input>
        </el-form-item>
        <el-form-item label="日期范围">
          <el-date-picker
              v-model="searchForm.dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
          ></el-date-picker>
        </el-form-item>
        <el-form-item label="消息关键词">
          <el-input v-model="searchForm.message"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" native-type="submit">查询</el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="search-results" v-if="commits.length">
      <template #header>
        <h3>查询结果</h3>
      </template>
      <el-table :data="commits" style="width: 100%">
        <el-table-column prop="revision" label="Revision" width="100"></el-table-column>
        <el-table-column prop="author" label="作者" width="120"></el-table-column>
        <el-table-column prop="date" label="日期" width="180"></el-table-column>
        <el-table-column prop="message" label="消息"></el-table-column>
      </el-table>
      <div class="pagination">
        <el-pagination
            @current-change="handlePageChange"
            :current-page="currentPage"
            :page-size="pageSize"
            :total="total"
            layout="total, prev, pager, next"
        ></el-pagination>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import {ref, reactive} from 'vue';
import {ElMessage} from 'element-plus';
import api from '@/services/api';

const searchForm = reactive({
  revision: '',
  author: '',
  dateRange: [],
  message: '',
});

const commits = ref([]);
const currentPage = ref(1);
const pageSize = ref(10);
const total = ref(0);

const submitSearch = async () => {
  try {
    const params = {
      revision: searchForm.revision,
      author: searchForm.author,
      date_after: searchForm.dateRange[0],
      date_before: searchForm.dateRange[1],
      search: searchForm.message,
      page: currentPage.value,
    };
    const response = await api.get('api/svn/commits/', {params});
    commits.value = response.data.results;
    total.value = response.data.count;
    ElMessage.success('查询成功');
  } catch (error) {
    console.error('Search error:', error);
    ElMessage.error('查询失败，请重试');
  }
};

const resetForm = () => {
  Object.keys(searchForm).forEach(key => {
    searchForm[key] = '';
  });
  searchForm.dateRange = [];
};

const handlePageChange = (page: number) => {
  currentPage.value = page;
  submitSearch();
};
</script>

<style scoped>
.commit-search {
  max-width: 1200px;
  margin: 0 auto;
}

.search-form,
.search-results {
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  text-align: right;
}
</style>