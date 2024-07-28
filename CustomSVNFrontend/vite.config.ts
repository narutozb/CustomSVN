import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import fs from 'fs'

export default defineConfig({
    plugins: [
        vue(),
        {
            name: 'copy-config',
            generateBundle() {
                const configContent = fs.readFileSync('config.js', 'utf-8')
                this.emitFile({
                    type: 'asset',
                    fileName: 'config.js',
                    source: configContent
                })
            }
        }
    ],
    resolve: {
        alias: {
            '@': path.resolve(__dirname, './src'),
        },
    },
    build: {
        outDir: 'dist',
        assetsDir: 'assets',
        emptyOutDir: true,
        sourcemap: false,
        rollupOptions: {
            input: {
                main: path.resolve(__dirname, 'index.html'),
            },
            output: {
                assetFileNames: (assetInfo) => {
                    if (assetInfo.name === 'config.js') {
                        return 'config.js';
                    }
                    return 'assets/[name].[hash][extname]';
                }
            }
        },
    },
    base: '/', // 如果你的应用不是部署在域名根目录，要相应修改这个值
})