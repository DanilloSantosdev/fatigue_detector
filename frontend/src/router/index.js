import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Reports from '../views/Reports.vue'
import VehicleConfig from '../views/VehicleConfig.vue'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard,
    meta: { title: 'Dashboard - Alertas' }
  },
  {
    path: '/reports',
    name: 'Reports',
    component: Reports,
    meta: { title: 'Relatórios' }
  },
  {
    path: '/vehicles',
    name: 'Vehicles',
    component: VehicleConfig,
    meta: { title: 'Configuração de Veículos' }
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Atualizar título da página
router.beforeEach((to, from, next) => {
  document.title = to.meta.title || 'Sistema de Detecção de Fadiga'
  next()
})

export default router

