import { createApp } from 'vue'
import { createPinia } from 'pinia'

import { cfg } from './config.js'
import App from './App.vue'
import router from './router'

import './styles/themes.scss'
import './styles/fonts.scss'
import './styles/base.scss'
import './styles/bh-loader.scss'

const app = createApp(App)

app.provide('$apiURL', cfg.apiURL)
app.provide('$oauthURL', cfg.oauthURL)
app.provide('$inviteURL', cfg.inviteURL)

app.use(createPinia())
app.use(router)

app.mount('#app')
