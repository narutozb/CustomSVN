// utils/filters.ts
import type { App } from 'vue'
import { format, parseISO } from 'date-fns'

export function registerGlobalProperties(app: App) {
    app.config.globalProperties.$filters = {
        formatDate(value: string) {
            if (!value) return ''
            return format(parseISO(value), 'yyyy-MM-dd HH:mm:ss')
        }
    }
}