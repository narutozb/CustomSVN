<template>
  <div class="search-sort-filter-container">
    <div class="search-container">
      <span class="label">Search：</span>
      <el-select
          v-model="selectedSearchFields"
          multiple
          clearable
          collapse-tags
          placeholder="Select search fields"
          popper-class="custom-header"
          :max-collapse-tags="5"
          style="width: 240px"
          @change="handleSearchFieldChange"
      >
        <template #header>
          <el-checkbox
              v-model="checkAll"
              :indeterminate="indeterminate"
              @change="handleCheckAll"
          >
            All
          </el-checkbox>
        </template>
        <el-option
            v-for="field in searchFields"
            :key="field"
            :label="field"
            :value="field"
        />
      </el-select>
      <el-input
          v-model="localSearchQuery"
          :placeholder="searchPlaceholder"
          style="width: 300px; margin-left: 10px;"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      <el-button
          type="primary"
          @click="submitSearch"
          style="margin-left: 10px;"
      >
        Search
      </el-button>
    </div>

    <div class="sort-container">
      <span class="label">Sort By：</span>
      <el-select v-model="localSortField" placeholder="Sort by" @change="handleSort">
        <el-option v-for="field in orderingFields" :key="field" :label="field" :value="field"/>
      </el-select>
      <el-select v-model="localSortOrder" @change="handleSort">
        <el-option label="↑Ascending" value="asc"/>
        <el-option label="↓Descending" value="desc"/>
      </el-select>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, watch, PropType, computed } from 'vue';
import { Search } from '@element-plus/icons-vue';
import type { CheckboxValueType } from 'element-plus';

export default defineComponent({
  name: 'SearchSortFilterComponent',
  components: { Search },
  props: {
    searchQuery: {
      type: String,
      default: '',
    },
    sortField: {
      type: String,
      default: '',
    },
    sortOrder: {
      type: String,
      default: 'asc',
    },
    orderingFields: {
      type: Array as PropType<string[]>,
      required: true,
    },
    searchFields: {
      type: Array as PropType<string[]>,
      required: true,
    },
  },
  emits: ['search', 'sort'],
  setup(props, { emit }) {
    const localSearchQuery = ref(props.searchQuery);
    const localSortField = ref(props.sortField || (props.orderingFields.length > 0 ? props.orderingFields[0] : ''));
    const localSortOrder = ref(props.sortOrder);
    const selectedSearchFields = ref<string[]>([]);
    const checkAll = ref(false);
    const indeterminate = ref(false);

    const searchPlaceholder = computed(() => {
      if (selectedSearchFields.value.length === 0) {
        return 'Search in all fields';
      } else if (selectedSearchFields.value.length === 1) {
        return `Search in ${selectedSearchFields.value[0]}`;
      } else {
        return `Search in ${selectedSearchFields.value.length} fields`;
      }
    });

    const submitSearch = () => {
      emit('search', {
        query: localSearchQuery.value,
        fields: selectedSearchFields.value.length > 0 ? selectedSearchFields.value : props.searchFields,
      });
    };

    const handleSort = () => {
      emit('sort', {
        field: localSortField.value,
        order: localSortOrder.value,
      });
    };

    const handleCheckAll = (val: CheckboxValueType) => {
      indeterminate.value = false;
      if (val) {
        selectedSearchFields.value = props.searchFields;
      } else {
        selectedSearchFields.value = [];
      }
    };

    const handleSearchFieldChange = () => {
      if (selectedSearchFields.value.length === 0) {
        checkAll.value = false;
        indeterminate.value = false;
      } else if (selectedSearchFields.value.length === props.searchFields.length) {
        checkAll.value = true;
        indeterminate.value = false;
      } else {
        indeterminate.value = true;
      }
    };

    watch(() => props.searchQuery, (newValue) => {
      localSearchQuery.value = newValue;
    });

    watch(() => props.sortField, (newValue) => {
      localSortField.value = newValue || (props.orderingFields.length > 0 ? props.orderingFields[0] : '');
    });

    watch(() => props.orderingFields, (newValue) => {
      if (newValue.length > 0 && !localSortField.value) {
        localSortField.value = newValue[0];
        handleSort();
      }
    }, { immediate: true });

    watch(() => props.sortOrder, (newValue) => {
      localSortOrder.value = newValue;
    });

    return {
      localSearchQuery,
      localSortField,
      localSortOrder,
      selectedSearchFields,
      checkAll,
      indeterminate,
      searchPlaceholder,
      handleSort,
      handleCheckAll,
      handleSearchFieldChange,
      submitSearch,
    };
  },
});
</script>



<style scoped>
.search-sort-filter-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 20px;
}

.search-container, .sort-container {
  display: flex;
  align-items: center;
  gap: 10px;
}

.label {
  font-weight: bold;
  min-width: 120px;
}

.el-select {
  width: 150px;
}

</style>

<style lang="scss">
.custom-header {
  .el-checkbox {
    display: flex;
    height: unset;
  }
}
</style>