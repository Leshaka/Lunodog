import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import fs from 'fs'
import basicSsl from '@vitejs/plugin-basic-ssl'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  server: {
    host: '127.0.0.1',
    port: 3356,
    // if you want https
    //https: {
    //  key: fs.readFileSync('../certs/private.key'),
    //  cert: fs.readFileSync('../certs/lunodog.crt'),
    //},
  },
  plugins: [
    //basicSsl(),
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
})
