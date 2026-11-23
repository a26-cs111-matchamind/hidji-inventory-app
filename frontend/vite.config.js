import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import { VitePWA } from 'vite-plugin-pwa';

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
    VitePWA({
      registerType: 'autoUpdate',
      manifest: {
        name: 'Hidji Coffee & Matcha Inventory',
        short_name: 'Hidji Stock',
        description: 'Sistem Manajemen Persediaan dan POS Hidji Coffee & Matcha',
        theme_color: '#4A7C59',
        background_color: '#FAF9F6',
        display: 'standalone',
        icons: [
          {
            src: '/vite.svg',
            sizes: '192x192',
            type: 'image/svg+xml'
          }
        ]
      }
    })
  ]
});