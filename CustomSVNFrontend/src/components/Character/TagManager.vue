<template>
  <div class="tag-manager">
    <h2>Tag Manager</h2>

    <SearchSortFilterComponent
        :search-query="searchQuery"
        :sort-field="sortField"
        :sort-order="sortOrder"
        :ordering-fields="orderingFields"
        :search-fields="searchFields"
        @search="handleSearch"
        @sort="handleSort"
    />
    <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[50, 100, 200]"
        :layout="'total, sizes, prev, pager, next, jumper'"
        :total="totalTags"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
    />
    <el-button type="primary" @click="showDialog()">Add New Tag</el-button>
    <el-table :data="tags" v-loading="loading" style="width: 100%">
      <el-table-column
          v-for="field in tableFields"
          :key="field.key"
          :prop="field.key"
          :label="field.label"
          :sortable="field.sortable"
      />
      <el-table-column label="Actions" width="200">
        <template #default="scope">
          <el-button size="small" @click="showDialog(scope.row)">Edit</el-button>
          <el-button size="small" type="danger" @click="confirmDelete(scope.row.id)">Delete</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="isEditing ? 'Edit Tag' : 'Add New Tag'">
      <el-form :model="currentTag">
        <el-form-item
            v-for="field in editFields"
            :key="field.key"
            :label="field.label"
            :required="field.required"
        >
          <el-input
              v-if="field.type === 'text'"
              v-model="currentTag[field.key]"
          />
          <el-input
              v-else-if="field.type === 'textarea'"
              v-model="currentTag[field.key]"
              type="textarea"
              :rows="4"
          />
          <el-switch
              v-else-if="field.type === 'switch'"
              v-model="currentTag[field.key]"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">Cancel</el-button>
          <el-button type="primary" @click="saveTag">Save</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { characterApi, FetchTagsParams } from "@/services/character_api";
import SearchSortFilterComponent from "@/components/Character/SearchSortFilterComponent.vue";

interface Tag {
  id: number;
  name: string;
  description: string;
  active: boolean;
  [key: string]: any;  // 允许动态属性
}

interface TableField {
  key: string;
  label: string;
  sortable: boolean;
  editable: boolean;
}

interface EditField {
  key: string;
  label: string;
  type: 'text' | 'textarea' | 'switch';
  required: boolean;
}

export default defineComponent({
  name: 'TagManager',
  components: {
    SearchSortFilterComponent,
  },
  setup() {
    // State
    const tags = ref<Tag[]>([]);
    const dialogVisible = ref(false);
    const isEditing = ref(false);
    const currentTag = ref<Tag>({id: 0, name: '', description: '', active: false});
    const loading = ref(false);
    const searchQuery = ref('');
    const currentPage = ref(1);
    const pageSize = ref(50);
    const totalTags = ref(0);
    const totalPages = ref(0);
    const searchFields = ref<string[]>([]);
    const orderingFields = ref<string[]>([]);
    const sortField = ref('');
    const sortOrder = ref('asc');
    const tableFields = ref<TableField[]>([]);
    const editFields = ref<EditField[]>([]);
    const selectedSearchFields = ref<string[]>([]);

    // API calls
    const fetchFilterOptions = async () => {
      try {
        const options = await characterApi.fetchTagFilterOptions();
        searchFields.value = options.search_fields;
        orderingFields.value = options.ordering_fields;
        tableFields.value = options.table_fields;
        editFields.value = options.edit_fields;
      } catch (error) {
        ElMessage.error('Failed to fetch filter options');
      }
    };

    const fetchTags = async () => {
      loading.value = true;
      try {
        const params: FetchTagsParams = {
          page: currentPage.value,
          page_size: pageSize.value,
          search: searchQuery.value,
          search_fields: selectedSearchFields.value.join(','),
          ordering: `${sortOrder.value === 'desc' ? '-' : ''}${sortField.value}`,
        };
        const response = await characterApi.fetchTags(params);
        tags.value = response.results;
        totalTags.value = response.pagination.total_items;
        totalPages.value = response.pagination.total_pages;
        currentPage.value = response.pagination.current_page;
      } catch (error) {
        ElMessage.error('Failed to fetch tags');
      } finally {
        loading.value = false;
      }
    };

    // Event handlers
    const handleSearch = ({ query, fields }: { query: string, fields: string[] }) => {
      searchQuery.value = query;
      selectedSearchFields.value = fields;
      currentPage.value = 1;
      fetchTags();
    };

    const handleSort = ({field, order}: { field: string, order: string }) => {
      sortField.value = field;
      sortOrder.value = order;
      fetchTags();
    };

    const handleSizeChange = (val: number) => {
      pageSize.value = val;
      currentPage.value = 1;
      fetchTags();
    };

    const handleCurrentChange = (val: number) => {
      currentPage.value = val;
      fetchTags();
    };

    const showDialog = (tag?: Tag) => {
      if (tag) {
        currentTag.value = {...tag};
        isEditing.value = true;
      } else {
        currentTag.value = {id: 0, name: '', description: '', active: false};
        isEditing.value = false;
      }
      dialogVisible.value = true;
    };

    const saveTag = async () => {
      try {
        if (isEditing.value) {
          await characterApi.updateTag(currentTag.value.id, currentTag.value);
          ElMessage.success('Tag updated successfully');
        } else {
          await characterApi.createTag(currentTag.value);
          ElMessage.success('Tag created successfully');
        }
        dialogVisible.value = false;
        fetchTags();
      } catch (error) {
        ElMessage.error('Failed to save tag');
      }
    };

    const confirmDelete = async (id: number) => {
      try {
        await ElMessageBox.confirm('Are you sure you want to delete this tag?', 'Warning', {
          confirmButtonText: 'OK',
          cancelButtonText: 'Cancel',
          type: 'warning',
        });
        await characterApi.deleteTag(id);
        ElMessage.success('Tag deleted successfully');
        fetchTags();
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('Failed to delete tag');
        }
      }
    };

    // Lifecycle hooks
    onMounted(async () => {
      await fetchFilterOptions();
      fetchTags();
    });

    return {
      // State
      tags, dialogVisible, isEditing, currentTag, loading, searchQuery,
      currentPage, pageSize, totalTags, searchFields,
      orderingFields, sortField, sortOrder, tableFields, editFields,
      // Methods
      handleSearch, handleSort, handleSizeChange,
      handleCurrentChange, showDialog, saveTag, confirmDelete,
    };
  },
});
</script>

<style scoped>
.tag-manager {
  /* Add any specific styles for the tag manager here */
}
</style>