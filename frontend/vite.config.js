import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

// Configuración del backend
const BACKEND_CONFIG = {
  IP: '192.168.68.113',
  PORT: '8000',
  PROTOCOL: 'http'
}

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    port: 5173,
    host: '0.0.0.0',
    cors: true,
    strictPort: true,
    allowedHosts: ['accescontserver.sytes.net', '192.168.68.113'],
    hmr: {
      host: BACKEND_CONFIG.IP,
      protocol: 'ws',
      clientPort: 5173
    }
  }
})











