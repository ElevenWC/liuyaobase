import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import GualiInput from '../views/GualiInput.vue'
import ImportJson from '../views/ImportJson.vue'
import TagManager from '../views/TagManager.vue'
import BagongPage from '../views/BagongPage.vue'
import HuguaPage from '../views/HuguaPage.vue'
import GraphPage from '../views/GraphPage.vue'
import NotFound from '../views/NotFound.vue'

const routes = [
  { path: '/', redirect: '/guali' },
  { path: '/guali', name: 'home', component: Home },
  { path: '/jiegua', redirect: '/jiegua/bagong' },
  { path: '/jiegua/bagong', name: 'bagong', component: BagongPage },
  { path: '/jiegua/hugua', name: 'hugua', component: HuguaPage },
  { path: '/jiegua/graph', name: 'graph', component: GraphPage },
  { path: '/input', name: 'input', component: GualiInput },
  { path: '/import', name: 'import', component: ImportJson },
  { path: '/tags', name: 'tags', component: TagManager },
  { path: '/:pathMatch(.*)*', component: NotFound },
]

export default createRouter({ history: createWebHistory(), routes })
