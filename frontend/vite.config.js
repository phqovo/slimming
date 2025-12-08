import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  base: '/health/',
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src')
    }
  },
  build: {
    rollupOptions: {
      output: {
        // 为每个 chunk 生成唯一的文件名，包含 hash
        chunkFileNames: 'assets/[name]-[hash].js',
        entryFileNames: 'assets/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash].[ext]',
        // 手动分块策略
        manualChunks: (id) => {
          if (id.includes('node_modules')) {
            // 将第三方库打包到 vendor chunk
            return 'vendor'
          }
        }
      }
    },
    // 启用 CSS 代码分割
    cssCodeSplit: true,
    // 生成 manifest 文件
    manifest: true
  },
  server: {
    port: 3000,
    proxy: {
      '/health/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/health/, '')
      },
      '/health/uploads': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/health/, '')
      }
    }
  }
})
