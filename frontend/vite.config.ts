import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [react()],
  server: {
    // El navegador le habla solo a este servidor y Vite reenvía /api al backend.
    // Al ser un único origen, la cookie de sesión viaja sin configurar CORS.
    // Se usa 127.0.0.1 y no "localhost": en algunos sistemas "localhost" se
    // resuelve a IPv6 (::1), donde uvicorn no escucha, y falla con ECONNREFUSED.
    proxy: { '/api': 'http://127.0.0.1:8000' },
  },
})
