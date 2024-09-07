<template>
  <el-transfer
      v-model="selectedKeys"
      :data="transferData"
      filterable
      :titles="[props.leftTitle || 'Available', props.rightTitle || 'Selected']"
      :render-content="renderContent"
      @change="handleChange"
      :style="{
        '--el-transfer-panel-width': props.panelWidth || '200px',
        '--el-font-size-base': '10px',
      }"
  >
    <template #left-footer>
      <el-button class="transfer-footer" size="small" @click="selectAll">Select All</el-button>
    </template>
    <template #right-footer>
      <el-button class="transfer-footer" size="small" @click="deselectAll">Deselect All</el-button>
    </template>
  </el-transfer>
</template>

<script lang="ts" setup>
import {ref, computed, watch} from 'vue';
import type {TransferProps} from 'element-plus';

interface TransferItem {
  key: string | number;
  label: string;
  disabled?: boolean;
}

const props = withDefaults(defineProps<{
  modelValue: (string | number)[];
  data: TransferItem[];
  leftTitle?: string;
  rightTitle?: string;
  panelWidth?: string;
  titleFontSize?: string;
}>(), {
  leftTitle: 'Available',
  rightTitle: 'Selected',
  titleFontSize: '5px'
});

const emit = defineEmits<{
  (e: 'update:modelValue', value: (string | number)[]): void;
  (e: 'change', value: (string | number)[], direction: 'left' | 'right', movedKeys: (string | number)[]): void;
}>();

const selectedKeys = ref<(string | number)[]>(props.modelValue);

watch(() => props.modelValue, (newValue) => {
  selectedKeys.value = newValue;
});

const transferData = computed(() => props.data);

const renderContent: TransferProps['renderContent'] = (h, option) => {
  return h('span', {}, option.label);
};

const handleChange = (value: (string | number)[], direction: 'left' | 'right', movedKeys: (string | number)[]) => {
  emit('update:modelValue', value);
  emit('change', value, direction, movedKeys);
};

const selectAll = () => {
  selectedKeys.value = transferData.value
      .filter(item => !item.disabled)
      .map(item => item.key);
  emit('update:modelValue', selectedKeys.value);
};

const deselectAll = () => {
  selectedKeys.value = [];
  emit('update:modelValue', selectedKeys.value);
};
</script>
<style scoped>
.transfer-footer {
  margin-left: 5px;
  padding: 4px 2px;
  font-size: 12px;
}

:deep(.el-transfer-panel) {
  width: v-bind('props.panelWidth || "250px"');
}

:deep(.el-transfer-panel__header) {
  padding: 4px 5px;
}

:deep(.el-transfer-panel__header .el-checkbox__label) {
  font-size: v-bind('props.titleFontSize');
  font-weight: bold;
}

:deep(.el-transfer-panel__header .el-checkbox__input) {
  display: none;
}

:deep(.el-transfer-panel__body) {
  height: 200px;
}

:deep(.el-checkbox__label) {
  font-size: 10px;
}

:deep(.el-transfer-panel__item) {
  height: 24px;
  line-height: 24px;
  padding: 0 5px;
}

:deep(.el-transfer__buttons) {
  padding: 0 1px;
}

:deep(.el-transfer__button) {
  padding: 8px 3px;
}

:deep(.el-transfer__button i, .el-transfer__button span) {
  font-size: 10px;
}
</style>