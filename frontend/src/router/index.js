import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import GualiInput from '../views/GualiInput.vue'
import NotFound from '../views/NotFound.vue'

const routes = [
  { path: '/', component: Home },
  { path: '/input', component: GualiInput },
  { path: '/:pathMatch(.*)*', component: NotFound },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
