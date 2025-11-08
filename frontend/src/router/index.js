import { createRouter, createWebHashHistory } from 'vue-router'
import InputPage from '../pages/InputPage.vue'
import ListPage from '../pages/ListPage.vue'
import About from '../pages/About.vue'

const routes = [
  { path: '/', component: InputPage },
  { path: '/input', component: InputPage },
  { path: '/list', component: ListPage },
  { path: '/about', component: About },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

export default router