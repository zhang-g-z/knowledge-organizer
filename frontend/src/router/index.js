import { createRouter, createWebHashHistory } from 'vue-router'
import InputPage from '../pages/InputPage.vue'
import ListPage from '../pages/ListPage.vue'
import About from '../pages/About.vue'
import LoginPage from '../pages/LoginPage.vue'
import RegisterPage from '../pages/RegisterPage.vue'
import ChangePassword from '../pages/ChangePassword.vue'

const routes = [
  { path: '/', component: InputPage, meta: { requiresAuth: true } },
  { path: '/input', component: InputPage, meta: { requiresAuth: true } },
  { path: '/login', component: LoginPage },
  { path: '/register', component: RegisterPage },
  { path: '/change-password', component: ChangePassword, meta: { requiresAuth: true } },
  { path: '/list', component: ListPage, meta: { requiresAuth: true } },
  { path: '/about', component: About },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

// Simple auth guard using token in localStorage
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')
  if (to.meta && to.meta.requiresAuth && !token) {
    return next({ path: '/login', query: { redirect: to.fullPath } })
  }
  // if visiting login/register while already authenticated, go home
  if ((to.path === '/login' || to.path === '/register') && token) {
    return next({ path: '/' })
  }
  next()
})

export default router