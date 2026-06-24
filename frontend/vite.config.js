import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    allowedHosts: [
      '801c42b5c78eb9921c02-pod-5trdyrq7bvgxngmfspk7sxei6q-5173.us4.cursorvm.com',
      '.loca.lt',
    ],
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})

