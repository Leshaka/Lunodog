import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'landing',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/AboutView.vue')
    },
    {
      path: '/oauth',
      name: 'oauth',
      component: () => import('../views/Oauth2View.vue')
    },
    {
      path: '/error',
      name: 'error',
      component: () => import('../views/ErrorView.vue'),
      props: { errorData: false }
    },
    {
      path: '/admin/servers',
      name: 'admin-servers',
      component: () => import('../views/admin/ServerListView.vue')
    },
    {
      path: '/admin/server/:guild_id/:section?',
      props: true,
      name: 'admin-server',
      component: () => import('../views/admin/ServerView.vue')
    },
  ]
})

export default router
