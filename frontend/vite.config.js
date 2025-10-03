import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'
import { BACKEND_CONFIG, FRONTEND_CONFIG } from '../scripts/vite-config-loader.js'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    port: FRONTEND_CONFIG.PORT,
    host: FRONTEND_CONFIG.HOST,
    cors: true,
    strictPort: true,
    allowedHosts: FRONTEND_CONFIG.ALLOWED_HOSTS,
    hmr: {
      host: BACKEND_CONFIG.IP,
      protocol: 'ws',
      clientPort: FRONTEND_CONFIG.PORT
    }
  }
})











