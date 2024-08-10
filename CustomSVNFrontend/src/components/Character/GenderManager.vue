<template>
  <div class="gender-manager">
    <h2>Gender Manager</h2>
    <el-button type="primary" @click="showDialog()">Add New Gender</el-button>

    <el-table :data="genders" style="width: 100%">
      <el-table-column prop="name" label="Name"/>
      <el-table-column label="Actions" width="200">
        <template #default="scope">
          <el-button size="small" @click="showDialog(scope.row)">Edit</el-button>
          <el-button size="small" type="danger" @click="confirmDelete(scope.row.id)">Delete</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="isEditing ? 'Edit Gender' : 'Add New Gender'">
      <el-form :model="currentGender">
        <el-form-item label="Name">
          <el-input v-model="currentGender.name"/>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">Cancel</el-button>
          <el-button type="primary" @click="saveGender">Save</el-button>
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
  name: 'GenderManager',
  setup() {
    const genders = ref<Array<{ id: number; name: string }>>([]);
    const dialogVisible = ref(false);
    const isEditing = ref(false);
    const currentGender = ref({ id: 0, name: '' });

    const fetchGenders = async () => {
      try {
        genders.value = await characterApi.fetchGenders();
      } catch (error) {
        ElMessage.error('Failed to fetch genders');
      }
    };

    const showDialog = (gender?: { id: number; name: string }) => {
      if (gender) {
        currentGender.value = { ...gender };
        isEditing.value = true;
      } else {
        currentGender.value = { id: 0, name: '' };
        isEditing.value = false;
      }
      dialogVisible.value = true;
    };

    const saveGender = async () => {
      try {
        if (isEditing.value) {
          await characterApi.updateGender(currentGender.value.id, currentGender.value);
          ElMessage.success('Gender updated successfully');
        } else {
          await characterApi.createGender(currentGender.value);
          ElMessage.success('Gender created successfully');
        }
        dialogVisible.value = false;
        fetchGenders();
      } catch (error) {
        ElMessage.error('Failed to save gender');
      }
    };

    const confirmDelete = async (id: number) => {
      try {
        await ElMessageBox.confirm('Are you sure you want to delete this gender?', 'Warning', {
          confirmButtonText: 'OK',
          cancelButtonText: 'Cancel',
          type: 'warning',
        });
        await characterApi.deleteGender(id);
        ElMessage.success('Gender deleted successfully');
        fetchGenders();
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('Failed to delete gender');
        }
      }
    };

    onMounted(fetchGenders);

    return {
      genders,
      dialogVisible,
      isEditing,
      currentGender,
      showDialog,
      saveGender,
      confirmDelete,
    };
  },
});
</script>