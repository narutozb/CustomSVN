<template>
  <el-transfer
      v-model="selectedKeys"
      :data="transferData"
      filterable
      :titles="[leftTitle, rightTitle]"
      :render-content="renderContent"
      @change="handleChange"
      :style="{ '--el-transfer-panel-width': panelWidth || '400px'}"

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
  key: string;
  label: string;
  disabled?: boolean;
}

const props = defineProps<{
  modelValue: string[];
  data: TransferItem[];
  leftTitle: string;
  rightTitle: string;
  panelWidth?: string; // 新增属性

}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: string[]): void;
  (e: 'change', value: string[], direction: 'left' | 'right', movedKeys: string[]): void;
}>();

const selectedKeys = ref(props.modelValue);

watch(() => props.modelValue, (newValue) => {
  selectedKeys.value = newValue;
});

const transferData = computed(() => props.data);

const renderContent: TransferProps['renderContent'] = (h, option) => {
  return h('span', {}, option.label);
};

const handleChange = (value: string[], direction: 'left' | 'right', movedKeys: string[]) => {
  emit('update:modelValue', value);
  emit('change', value, direction, movedKeys);
};

const selectAll = () => {
  selectedKeys.value = transferData.value.filter(item => !item.disabled).map(item => item.key);
  emit('update:modelValue', selectedKeys.value);
};

const deselectAll = () => {
  selectedKeys.value = [];
  emit('update:modelValue', selectedKeys.value);
};
</script>

<style scoped>
.transfer-footer {
  margin-left: 15px;
  padding: 6px 5px;
}



</style>

