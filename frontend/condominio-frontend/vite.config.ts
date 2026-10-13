import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // Em bind mount no Windows o Docker não avisa quando um arquivo muda; sem polling o HMR não atualiza
    watch: process.env.USE_POLLING ? { usePolling: true } : undefined,
    proxy: {
      // /api/blocos -> http://localhost:8000/blocos (o prefixo /api é removido)
      // No docker-compose, API_URL aponta para o container da API (http://api:8000)
      '/api': {
        target: process.env.API_URL ?? 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (caminho) => caminho.replace(/^\/api/, ''),
      },
    },
  },
})
