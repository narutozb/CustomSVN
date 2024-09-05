// src/composables/useLoadingState.ts

import { ref, Ref } from 'vue';
import { ElMessage } from 'element-plus';

interface UseLoadingStateOptions {
    loadingMessage?: string;
    errorMessage?: string;
}

export function useLoadingState(options: UseLoadingStateOptions = {}) {
    const loading = ref(false);
    const error = ref<string | null>(null);

    const {
        loadingMessage = 'Loading...',
        errorMessage = 'An error occurred. Please try again.',
    } = options;

    const startLoading = () => {
        console.log('Start loading called');
        loading.value = true;
        error.value = null;
    };

    const stopLoading = () => {
        console.log('Stop loading called');
        loading.value = false;
        console.log('New loading value:', loading.value);
    };

    const setError = (msg: string) => {
        error.value = msg;
        ElMessage.error(msg || errorMessage);
    };

    async function withLoading<T>(
        fn: () => Promise<T>,
        customLoadingMessage?: string
    ): Promise<T | undefined> {
        startLoading();
        if (customLoadingMessage) {
            ElMessage.info(customLoadingMessage);
        }
        try {
            const result = await fn();
            return result;
        } catch (e) {
            console.error(e);
            setError(e instanceof Error ? e.message : String(e));
            return undefined;
        } finally {
            stopLoading();
        }
    }

    return {
        loading,
        error,
        withLoading,
        startLoading,
        stopLoading,
        setError,
    };
}