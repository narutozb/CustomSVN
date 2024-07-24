<template>
  <div class="character-manager">
    <h1>Character Manager</h1>
    <el-button type="primary" @click="showCreateDialog">Create New Character</el-button>
    <el-table :data="characters" style="width: 100%">
      <el-table-column prop="name" label="Name" />
      <el-table-column prop="character_id" label="Character ID" />
      <el-table-column prop="gender_name" label="Gender" />
      <el-table-column prop="race_name" label="Race" />
      <el-table-column prop="height" label="Height" />
      <el-table-column label="Actions" width="200">
        <template #default="scope">
          <el-button size="small" @click="editCharacter(scope.row)">Edit</el-button>
          <el-button size="small" type="danger" @click="confirmDelete(scope.row.id)">Delete</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="isEditing ? 'Edit Character' : 'Create Character'">
      <el-form :model="currentCharacter" label-width="120px">
        <el-form-item label="Name">
          <el-input v-model="currentCharacter.name" />
        </el-form-item>
        <el-form-item label="Character ID">
          <el-input v-model="currentCharacter.character_id" />
        </el-form-item>
        <el-form-item label="Description">
          <el-input v-model="currentCharacter.description" type="textarea" />
        </el-form-item>
        <el-form-item label="Height">
          <el-input-number v-model="currentCharacter.height" :step="0.01" />
        </el-form-item>
        <el-form-item label="Gender">
          <el-select v-model="currentCharacter.gender" placeholder="Select Gender">
            <el-option v-for="gender in genders" :key="gender.id" :label="gender.name" :value="gender.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="Race">
          <el-select v-model="currentCharacter.race" placeholder="Select Race">
            <el-option v-for="race in races" :key="race.id" :label="race.name" :value="race.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="Tags">
          <el-select v-model="currentCharacter.tags" multiple placeholder="Select Tags">
            <el-option v-for="tag in tags" :key="tag.id" :label="tag.name" :value="tag.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">Cancel</el-button>
          <el-button type="primary" @click="confirmSave">Save</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { characterApi } from "@/services/character_api";

export default defineComponent({
  name: 'CharacterManager',
  setup() {
    const characters = ref([])
    const genders = ref([])
    const races = ref([])
    const tags = ref([])
    const dialogVisible = ref(false)
    const currentCharacter = ref({})
    const isEditing = ref(false)

    const fetchData = async () => {
      try {
        characters.value = await characterApi.fetchCharacters()
        genders.value = await characterApi.fetchGenders()
        races.value = await characterApi.fetchRaces()
        tags.value = await characterApi.fetchTags()
      } catch (error) {
        console.error('Error fetching data:', error)
        ElMessage.error('Failed to fetch data')
      }
    }

    const showCreateDialog = () => {
      currentCharacter.value = {}
      isEditing.value = false
      dialogVisible.value = true
    }

    const editCharacter = (character: any) => {
      currentCharacter.value = { ...character }
      isEditing.value = true
      dialogVisible.value = true
    }

    const confirmSave = async () => {
      try {
        await ElMessageBox.confirm(
            'Are you sure you want to save these changes?',
            'Confirm Save',
            {
              confirmButtonText: 'Yes',
              cancelButtonText: 'No',
              type: 'warning',
            }
        )
        await saveCharacter()
      } catch (error) {
        if (error !== 'cancel') {
          console.error('Error in save confirmation:', error)
          ElMessage.error('An error occurred during save confirmation')
        }
      }
    }

    const saveCharacter = async () => {
      try {
        if (isEditing.value) {
          await characterApi.updateCharacter(currentCharacter.value.id, currentCharacter.value)
          ElMessage.success('Character updated successfully')
        } else {
          await characterApi.createCharacter(currentCharacter.value)
          ElMessage.success('Character created successfully')
        }
        dialogVisible.value = false
        fetchData()
      } catch (error) {
        console.error('Error saving character:', error)
        ElMessage.error('Failed to save character')
      }
    }

    const confirmDelete = async (id: number) => {
      try {
        await ElMessageBox.confirm(
            'Are you sure you want to delete this character?',
            'Confirm Delete',
            {
              confirmButtonText: 'Yes',
              cancelButtonText: 'No',
              type: 'warning',
            }
        )
        await deleteCharacter(id)
      } catch (error) {
        if (error !== 'cancel') {
          console.error('Error in delete confirmation:', error)
          ElMessage.error('An error occurred during delete confirmation')
        }
      }
    }

    const deleteCharacter = async (id: number) => {
      try {
        await characterApi.deleteCharacter(id)
        ElMessage.success('Character deleted successfully')
        fetchData()
      } catch (error) {
        console.error('Error deleting character:', error)
        ElMessage.error('Failed to delete character')
      }
    }

    onMounted(fetchData)

    return {
      characters,
      genders,
      races,
      tags,
      dialogVisible,
      currentCharacter,
      isEditing,
      showCreateDialog,
      editCharacter,
      confirmSave,
      confirmDelete,
    }
  }
})
</script>