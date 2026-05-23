import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import GualiInput from '../views/GualiInput.vue'
import ImportJson from '../views/ImportJson.vue'
import TagManager from '../views/TagManager.vue'
import NotFound from '../views/NotFound.vue'

const routes = [
  { path: '/', redirect: '/guali' },
  { path: '/guali', name: 'home', component: Home },
  { path: '/input', name: 'input', component: GualiInput },
  { path: '/import', name: 'import', component: ImportJson },
  { path: '/tags', name: 'tags', component: TagManager },
  { path: '/:pathMatch(.*)*', component: NotFound },
]

export default createRouter({ history: createWebHistory(), routes })
