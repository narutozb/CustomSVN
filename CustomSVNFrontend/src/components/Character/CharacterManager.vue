<!--/src/components/CharacterManager.vue-->

<template>
  <div class="character-manager">
    <h1>Character Manager</h1>
    <el-button type="primary" @click="showCreateDialog">Create New Character</el-button>

    <div class="thumbnail-size-controller">
      <span>Thumbnail Size: {{ state.thumbnailSize }}px</span>
      <el-slider
          v-model="state.thumbnailSize"
          :min="THUMBNAIL_SIZE_MIN"
          :max="THUMBNAIL_SIZE_MAX"
          :step="THUMBNAIL_SIZE_STEP"
          @change="updateThumbnailSize"
      ></el-slider>
    </div>

    <el-table :data="state.characters" style="width: 100%">
      <el-table-column label="Thumbnail" :width="state.thumbnailSize + 20">
        <template #default="scope">
          <el-image
              v-if="scope.row.thumbnails && scope.row.thumbnails.length > 0"
              :src="scope.row.thumbnails[0].image"
              :preview-src-list="[scope.row.thumbnails[0].image]"
              :initial-index="0"
              fit="cover"
              :style="{ width: state.thumbnailSize + 'px', height: state.thumbnailSize + 'px' }"
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
          <el-button size="small" type="danger" @click="confirmDelete(scope.row.id!)">Delete</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="state.dialogVisible" :title="state.isEditing ? 'Edit Character' : 'Create Character'">
      <el-form :model="state.currentCharacter" label-width="120px">
        <el-form-item label="Name">
          <el-input v-model="state.currentCharacter.name"/>
        </el-form-item>
        <el-form-item label="Character ID">
          <el-input v-model="state.currentCharacter.character_id"/>
        </el-form-item>
        <el-form-item label="Description">
          <el-input v-model="state.currentCharacter.description" type="textarea"/>
        </el-form-item>
        <el-form-item label="Height">
          <el-input-number v-model="state.currentCharacter.height" :step="1"/>
        </el-form-item>
        <el-form-item label="Gender">
          <el-select v-model="state.currentCharacter.gender" placeholder="Select Gender">
            <el-option v-for="gender in state.genders" :key="gender.id" :label="gender.name" :value="gender.id"/>
          </el-select>
        </el-form-item>
        <el-form-item label="Race">
          <el-select v-model="state.currentCharacter.race" placeholder="Select Race">
            <el-option v-for="race in state.races" :key="race.id" :label="race.name" :value="race.id"/>
          </el-select>
        </el-form-item>
        <el-form-item label="Tags">
          <el-select v-model="state.currentCharacter.tags" multiple placeholder="Select Tags">
            <el-option v-for="tag in state.tags" :key="tag.id" :label="tag.name" :value="tag.id"/>
          </el-select>
        </el-form-item>
        <el-form-item label="Thumbnails">
          <el-upload
              v-model:file-list="state.fileList"
              action="#"
              list-type="picture-card"
              :auto-upload="false"
              :on-change="handleFileChange"
              :on-remove="handleFileRemove"
              :on-preview="handlePreview"
              :limit="state.maxThumbnails"
              :disabled="state.fileList.length >= state.maxThumbnails"
              drag
          >
            <el-icon v-if="state.fileList.length < state.maxThumbnails">
              <plus/>
            </el-icon>
            <template #file="{ file }">
              <img class="el-upload-list__item-thumbnail" :src="file.url" alt=""/>
              <span class="el-upload-list__item-actions">
                <span class="el-upload-list__item-preview" @click="handlePreview(file)">
                  <el-icon><zoom-in/></el-icon>
                </span>
                <span class="el-upload-list__item-delete" @click="handleFileRemove(file)">
                  <el-icon><delete/></el-icon>
                </span>
              </span>
            </template>
            <template #tip>
              <div class="el-upload__tip">
                Drag files here or click to upload. Maximum {{ state.maxThumbnails }} images allowed.
              </div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="state.dialogVisible = false">Cancel</el-button>
          <el-button type="primary" @click="confirmSave">Save</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
  <el-dialog v-model="state.previewVisible" title="Image Preview">
    <img :src="state.previewImage" style="width: 100%"/>
  </el-dialog>
</template>

<script lang="ts">
import { defineComponent, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { characterApi } from "@/services/character_api"
import { Plus, ZoomIn, Delete } from '@element-plus/icons-vue'
import type { Character, UploadFile } from "@/services/interfaces"
import { AxiosError } from 'axios'

const MAX_THUMBNAILS = 3
const THUMBNAIL_SIZE_MIN = 50
const THUMBNAIL_SIZE_MAX = 500
const THUMBNAIL_SIZE_STEP = 10

export default defineComponent({
  name: 'CharacterManager',
  components: { Plus, ZoomIn, Delete },
  setup() {
    const state = reactive({
      characters: [] as Character[],
      genders: [] as Array<{ id: number; name: string }>,
      races: [] as Array<{ id: number; name: string }>,
      tags: [] as Array<{ id: number; name: string }>,
      maxThumbnails: MAX_THUMBNAILS,
      previewVisible: false,
      previewImage: '',
      dialogVisible: false,
      currentCharacter: {} as Character,
      isEditing: false,
      thumbnailSize: 100,
      fileList: [] as UploadFile[],
    })

    const initialCharacter: Character = {
      name: '',
      character_id: '',
      description: '',
      height: null,
      gender: null,
      race: null,
      tags: null,
      thumbnails: [],
    }

    const resetCurrentCharacter = () => {
      state.currentCharacter = { ...initialCharacter }
      state.fileList = []
      state.isEditing = false
    }

    const handleError = (error: unknown, defaultMessage: string) => {
      console.error(defaultMessage, error)
      if (error instanceof Error) {
        const axiosError = error as AxiosError
        if (axiosError.response) {
          console.error('Response data:', axiosError.response.data)
          console.error('Response status:', axiosError.response.status)
          console.error('Response headers:', axiosError.response.headers)
          const responseData = axiosError.response.data as { detail?: string }
          ElMessage.error(defaultMessage + ': ' + (responseData.detail || axiosError.message))
        } else {
          ElMessage.error(defaultMessage + ': ' + axiosError.message)
        }
      } else {
        ElMessage.error('An unknown error occurred')
      }
    }

    const fetchData = async () => {
      try {
        state.characters = await characterApi.fetchCharacters()
        state.genders = await characterApi.fetchGenders()
        state.races = await characterApi.fetchRaces()
        state.tags = await characterApi.fetchTags()
      } catch (error) {
        handleError(error, 'Failed to fetch data')
      }
    }

    const showCreateDialog = () => {
      resetCurrentCharacter()
      state.dialogVisible = true
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
          handleError(error, 'An error occurred during save confirmation')
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
          handleError(error, 'An error occurred during delete confirmation')
        }
      }
    }

    const deleteCharacter = async (id: number) => {
      try {
        await characterApi.deleteCharacter(id)
        ElMessage.success('Character deleted successfully')
        fetchData()
      } catch (error) {
        handleError(error, 'Failed to delete character')
      }
    }

    const fetchMaxThumbnails = async () => {
      try {
        const response = await characterApi.fetchMaxThumbnails()
        state.maxThumbnails = response.max_thumbnails
      } catch (error) {
        handleError(error, 'Failed to fetch max thumbnails count')
      }
    }

    const handlePreview = (file: UploadFile) => {
      state.previewImage = file.url
      state.previewVisible = true
    }

    const handleFileChange = (file: UploadFile, fileList: UploadFile[]) => {
      if (file.raw) {
        const isImage = file.raw.type.startsWith('image/')
        if (!isImage) {
          ElMessage.error('You can only upload image files!')
          return false
        }
      } else {
        ElMessage.error('Invalid file')
        return false
      }

      if (fileList.length > state.maxThumbnails) {
        ElMessage.warning(`You can only upload a maximum of ${state.maxThumbnails} images.`)
        return false
      }

      if (!file.status) {
        file.status = 'ready'
      }
      return true
    }

    const handleFileRemove = (file: UploadFile) => {
      const index = state.fileList.findIndex(f => f.uid === file.uid)
      if (index !== -1) {
        state.fileList.splice(index, 1)
      }
    }

    const saveCharacter = async () => {
      try {
        const formData = new FormData()
        Object.entries(state.currentCharacter).forEach(([key, value]) => {
          if (value !== null && value !== undefined) {
            if (key === 'tags' && Array.isArray(value)) {
              value.forEach((tagId, index) => {
                formData.append(`tags[${index}]`, tagId.toString())
              })
            } else {
              formData.append(key, String(value))
            }
          }
        })

        state.fileList.forEach((file: UploadFile) => {
          if (file.status === 'ready' && file.raw instanceof File) {
            formData.append('new_thumbnails', file.raw)
          }
        })

        if (state.isEditing && state.currentCharacter.id) {
          await characterApi.updateCharacter(state.currentCharacter.id, formData)
          ElMessage.success('Character updated successfully')
        } else {
          await characterApi.createCharacter(formData)
          ElMessage.success('Character created successfully')
        }
        state.dialogVisible = false
        fetchData()
      } catch (error) {
        handleError(error, 'Failed to save character')
      }
    }

    const editCharacter = (character: Character) => {
      state.currentCharacter = { ...character }
      state.fileList = character.thumbnails ? character.thumbnails.map(thumbnail => ({
        name: thumbnail.name || 'thumbnail',
        url: thumbnail.image,
        status: 'success',
        uid: thumbnail.id.toString()
      } as UploadFile)) : []
      state.isEditing = true
      state.dialogVisible = true
    }

    const updateThumbnailSize = (newSize: number) => {
      state.thumbnailSize = newSize
    }

    onMounted(() => {
      fetchData()
      fetchMaxThumbnails()
    })

    return {
      state,
      showCreateDialog,
      confirmSave,
      confirmDelete,
      handleFileChange,
      handleFileRemove,
      handlePreview,
      editCharacter,
      updateThumbnailSize,
      THUMBNAIL_SIZE_MIN,
      THUMBNAIL_SIZE_MAX,
      THUMBNAIL_SIZE_STEP,
    }
  }
})
</script>

<style scoped>
.thumbnail-size-controller {
  margin: 20px 0;
  display: flex;
  align-items: center;
}

.thumbnail-size-controller span {
  margin-right: 10px;
  min-width: 150px;
}

.thumbnail-size-controller .el-slider {
  width: 200px;
}
</style>