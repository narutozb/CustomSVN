<template>
  <div class="race-manager">
    <h2>Race Manager</h2>
    <el-button type="primary" @click="showDialog()">Add New Race</el-button>

    <el-table :data="races" style="width: 100%">
      <el-table-column prop="name" label="Name"/>
      <el-table-column label="Actions" width="200">
        <template #default="scope">
          <el-button size="small" @click="showDialog(scope.row)">Edit</el-button>
          <el-button size="small" type="danger" @click="confirmDelete(scope.row.id)">Delete</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="isEditing ? 'Edit Race' : 'Add New Race'">
      <el-form :model="currentRace">
        <el-form-item label="Name">
          <el-input v-model="currentRace.name"/>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">Cancel</el-button>
          <el-button type="primary" @click="saveRace">Save</el-button>
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
  name: 'RaceManager',
  setup() {
    const races = ref<Array<{ id: number; name: string }>>([]);
    const dialogVisible = ref(false);
    const isEditing = ref(false);
    const currentRace = ref({ id: 0, name: '' });

    const fetchRaces = async () => {
      try {
        races.value = await characterApi.fetchRaces();
      } catch (error) {
        ElMessage.error('Failed to fetch races');
      }
    };

    const showDialog = (race?: { id: number; name: string }) => {
      if (race) {
        currentRace.value = { ...race };
        isEditing.value = true;
      } else {
        currentRace.value = { id: 0, name: '' };
        isEditing.value = false;
      }
      dialogVisible.value = true;
    };

    const saveRace = async () => {
      try {
        if (isEditing.value) {
          await characterApi.updateRace(currentRace.value.id, currentRace.value);
          ElMessage.success('Race updated successfully');
        } else {
          await characterApi.createRace(currentRace.value);
          ElMessage.success('Race created successfully');
        }
        dialogVisible.value = false;
        fetchRaces();
      } catch (error) {
        ElMessage.error('Failed to save race');
      }
    };

    const confirmDelete = async (id: number) => {
      try {
        await ElMessageBox.confirm('Are you sure you want to delete this race?', 'Warning', {
          confirmButtonText: 'OK',
          cancelButtonText: 'Cancel',
          type: 'warning',
        });
        await characterApi.deleteRace(id);
        ElMessage.success('Race deleted successfully');
        fetchRaces();
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('Failed to delete race');
        }
      }
    };

    onMounted(fetchRaces);

    return {
      races,
      dialogVisible,
      isEditing,
      currentRace,
      showDialog,
      saveRace,
      confirmDelete,
    };
  },
});
</script>