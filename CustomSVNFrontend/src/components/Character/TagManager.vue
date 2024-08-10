<template>
  <div class="tag-manager">
    <h2>Tag Manager</h2>
    <el-button type="primary" @click="showDialog()">Add New Tag</el-button>

    <el-table :data="tags" style="width: 100%">
      <el-table-column prop="name" label="Name"/>
      <el-table-column label="Actions" width="200">
        <template #default="scope">
          <el-button size="small" @click="showDialog(scope.row)">Edit</el-button>
          <el-button size="small" type="danger" @click="confirmDelete(scope.row.id)">Delete</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="isEditing ? 'Edit Tag' : 'Add New Tag'">
      <el-form :model="currentTag">
        <el-form-item label="Name">
          <el-input v-model="currentTag.name"/>
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
import { characterApi } from "@/services/character_api";

export default defineComponent({
  name: 'TagManager',
  setup() {
    const tags = ref<Array<{ id: number; name: string }>>([]);
    const dialogVisible = ref(false);
    const isEditing = ref(false);
    const currentTag = ref({ id: 0, name: '' });

    const fetchTags = async () => {
      try {
        tags.value = await characterApi.fetchTags();
      } catch (error) {
        ElMessage.error('Failed to fetch tags');
      }
    };

    const showDialog = (tag?: { id: number; name: string }) => {
      if (tag) {
        currentTag.value = { ...tag };
        isEditing.value = true;
      } else {
        currentTag.value = { id: 0, name: '' };
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

    onMounted(fetchTags);

    return {
      tags,
      dialogVisible,
      isEditing,
      currentTag,
      showDialog,
      saveTag,
      confirmDelete,
    };
  },
});
</script>