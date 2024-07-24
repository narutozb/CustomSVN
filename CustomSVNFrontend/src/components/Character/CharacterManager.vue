<template>
  <div class="character-manager">
    <h1>Character Manager</h1>
    <el-button type="primary" @click="showCreateDialog">Create New Character</el-button>
    <el-table :data="characters" style="width: 100%">
      <el-table-column label="Thumbnail" width="100">
        <template #default="scope">
          <el-image
              v-if="scope.row.thumbnails && scope.row.thumbnails.length > 0"
              :src="scope.row.thumbnails[0].image"
              :preview-src-list="[scope.row.thumbnails[0].image]"
              :initial-index="0"
              fit="contain"
              :style="{ maxWidth: thumbnailSize + 'px', maxHeight: thumbnailSize + 'px', width: 'auto', height: 'auto' }"
              :preview-teleported="true"
              :title="`${scope.row.name} (ID: ${scope.row.character_id})`"
          />
        </template>
      </el-table-column>
      <el-table-column prop="name" label="Name"/>
      <el-table-column prop="character_id" label="Character ID"/>
      <el-table-column prop="gender_name" label="Gender"/>
      <el-table-column prop="race_name" label="Race"/>
      <el-table-column prop="height" label="Height"/>
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
          <el-input v-model="currentCharacter.name"/>
        </el-form-item>
        <el-form-item label="Character ID">
          <el-input v-model="currentCharacter.character_id"/>
        </el-form-item>
        <el-form-item label="Description">
          <el-input v-model="currentCharacter.description" type="textarea"/>
        </el-form-item>
        <el-form-item label="Height">
          <el-input-number v-model="currentCharacter.height" :step="0.01"/>
        </el-form-item>
        <el-form-item label="Gender">
          <el-select v-model="currentCharacter.gender" placeholder="Select Gender">
            <el-option v-for="gender in genders" :key="gender.id" :label="gender.name" :value="gender.id"/>
          </el-select>
        </el-form-item>
        <el-form-item label="Race">
          <el-select v-model="currentCharacter.race" placeholder="Select Race">
            <el-option v-for="race in races" :key="race.id" :label="race.name" :value="race.id"/>
          </el-select>
        </el-form-item>
        <el-form-item label="Tags">
          <el-select v-model="currentCharacter.tags" multiple placeholder="Select Tags">
            <el-option v-for="tag in tags" :key="tag.id" :label="tag.name" :value="tag.id"/>
          </el-select>
        </el-form-item>
        <el-form-item label="Thumbnails">
          <el-upload
              v-model:file-list="fileList"
              action="#"
              list-type="picture-card"
              :auto-upload="false"
              :on-change="handleFileChange"
              :on-remove="handleFileRemove"
              drag
          >
            <el-icon>
              <plus/>
            </el-icon>
          </el-upload>
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
import {defineComponent, ref, onMounted} from 'vue'
import {ElMessage, ElMessageBox} from 'element-plus'
import {characterApi} from "@/services/character_api"
import {Plus} from '@element-plus/icons-vue'
import type {Character} from "@/services/interfaces";

export default defineComponent({
  name: 'CharacterManager',
  components: {Plus},
  setup() {
    const characters = ref<Character[]>([])
    const genders = ref<Array<{ id: number; name: string }>>([])
    const races = ref<Array<{ id: number; name: string }>>([])
    const tags = ref<Array<{ id: number; name: string }>>([])

    const initialCharacter: Character = {
      name: '',
      character_id: '',
      description: '',
      height: null,
      gender: null,
      race: null,
      tags: [],
      thumbnails: []
    };


    const dialogVisible = ref(false)
    const currentCharacter = ref<Character>({...initialCharacter});
    const isEditing = ref(false)
    const thumbnailSize = ref(256)
    const fileList = ref<Array<{ name: string; url: string; status?: string; uid?: string }>>([])


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
      currentCharacter.value = {...initialCharacter};
      fileList.value = [];
      isEditing.value = false;
      dialogVisible.value = true;
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

    const handleFileChange = (file: any) => {
      const isImage = file.raw.type.startsWith('image/')
      if (!isImage) {
        ElMessage.error('You can only upload image files!')
        return false
      }
      return true
    }

    const handleFileRemove = (file: any) => {
      const index = fileList.value.findIndex(f => f.uid === file.uid)
      if (index !== -1) {
        fileList.value.splice(index, 1)
      }
    }

    const saveCharacter = async () => {
      try {
        const formData = new FormData()
        Object.keys(currentCharacter.value).forEach(key => {
          if (key !== 'thumbnails' && currentCharacter.value[key as keyof Character] !== null) {
            formData.append(key, currentCharacter.value[key as keyof Character] as string)
          }
        })

        // Handle existing thumbnails
        const thumbnailsToKeep = fileList.value
            .filter(file => file.status === 'success' && file.uid)
            .map(file => file.uid)
        formData.append('thumbnails', JSON.stringify(thumbnailsToKeep))

        // Handle new files
        fileList.value.forEach((file,) => {
          if (file.status === 'ready' && file.raw instanceof File) {
            formData.append(`new_thumbnails`, file.raw)
          }
        })

        if (isEditing.value && currentCharacter.value.id) {
          await characterApi.updateCharacter(currentCharacter.value.id, formData)
          ElMessage.success('Character updated successfully')
        } else {
          await characterApi.createCharacter(formData)
          ElMessage.success('Character created successfully')
        }
        dialogVisible.value = false
        fetchData()
      } catch (error) {
        console.error('Error saving character:', error)
        ElMessage.error('Failed to save character')
      }
    }

    const editCharacter = (character: Character) => {
      currentCharacter.value = {...character}
      fileList.value = character.thumbnails ? character.thumbnails.map(thumbnail => ({
        name: thumbnail.name || 'thumbnail',
        url: thumbnail.image,
        status: 'success',
        uid: thumbnail.id.toString()
      })) : []
      isEditing.value = true
      dialogVisible.value = true
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
      thumbnailSize,
      fileList,
      handleFileChange,
      handleFileRemove
    }
  }
})
</script>

