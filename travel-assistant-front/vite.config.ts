import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  server: {
    port: 3000,
    host: true,
    proxy: {
      '/api': {
        target: process.env.VITE_API_BASE_URL || 'http://localhost:8080',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '/api/v1')
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
    chunkSizeWarningLimit: 1000,
    // 代码分割配置
    rollupOptions: {
      output: {
        // 手动分块策略
        manualChunks: {
          // 第三方库分块
          'vendor': [
            'react',
            'react-dom',
            'react-router-dom'
          ],
          // UI 组件库分块
          'ui': [
            '@radix-ui/react-slot',
            '@radix-ui/react-dialog',
            '@radix-ui/react-dropdown-menu',
            '@radix-ui/react-tabs',
            'clsx',
            'tailwind-merge'
          ],
          // 查询和状态管理分块
          'query': [
            '@tanstack/react-query',
            'axios'
          ],
          // Agent API 功能分块
          'agent': [
            // Agent 相关的自定义代码会自动分到这里
          ]
        },
        // 入口文件命名
        entryFileNames: 'assets/[name]-[hash].js',
        // 分块文件命名
        chunkFileNames: 'assets/[name]-[hash].js',
        // 资源文件命名
        assetFileNames: 'assets/[name]-[hash].[ext]'
      }
    },
    // 压缩配置
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,  // 生产环境移除 console
        drop_debugger: true
      }
    }
  }
})
