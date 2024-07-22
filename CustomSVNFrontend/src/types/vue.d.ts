// src/types/vue.d.ts
import { ComponentCustomProperties } from 'vue'

declare module '@vue/runtime-core' {
    interface ComponentCustomProperties {
        $filters: {
            formatDate: (value: string) => string
        }
    }
}