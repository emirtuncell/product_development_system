import Vue from 'vue'
import VueRouter from 'vue-router'
import HomeView from '../views/HomeView.vue'

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
    path: '/about',
    name: 'about',
    component: () => import('../views/AboutView.vue')
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/LoginView.vue')
  },
  {
    path: '/machine',
    name: 'machine',
    component: () => import('../views/MachineView.vue')
  },
  {
    path: '/operator',
    name: 'operator',
    component: () => import('../views/OperatorView.vue')
  },
  {
    path: '/mold',
    name: 'mold',
    component: () => import('../views/MoldView.vue')
  },
  {
    path: '/product',
    name: 'product',
    component: () => import('../views/ProductView.vue')
  },
  {
    path: '/customer',
    name: 'customer',
    component: () => import('../views/CustomerView.vue')
  },
  {
    path: '/machine-mold',
    name: 'machine_mold',
    component: () => import('../views/MachineMoldView.vue')
  },
  {
    path: '/machine-operator',
    name: 'machine_operator',
    component: () => import('../views/MachineOperatorView.vue')
  },
  {
    path: '/mold-product',
    name: 'mold_product',
    component: () => import('../views/MoldProductView.vue')
  },
  {
    path: '/order',
    name: 'order',
    component: () => import('../views/OrderView.vue')
  },
  {
    path: '/order-product',
    name: 'order_product',
    component: () => import('../views/OrderProductView.vue')
  },
  {
    path: '/work-order',
    name: 'work_order',
    component: () => import('../views/WorkOrderView.vue')
  },
  {
    path: '/calendar',
    name: 'calendar',
    component: () => import('../views/CalendarView.vue')
  },
  {
    path: '/stop-cause',
    name: 'stop_cause',
    component: () => import('../views/StopCauseView.vue')
  },
  {
    path: '/scrap-cause',
    name: 'scrap_cause',
    component: () => import('../views/ScrapCauseView.vue')
  },
  {
    path: '/production',
    name: 'production',
    component: () => import('../views/ProductionView.vue')
  },
  {
    path: '/machine-production',
    name: 'machine_production',
    component: () => import('../views/MachineProductionView.vue')
  },
  {
    path: '/admin',
    name: 'admin',
    component: () => import('../views/AdminView.vue')
  },
  {
    path: '/factory-admin',
    name: 'factory_admin',
    component: () => import('../views/FactoryAdminView.vue')
  },
  {
    path: '/user',
    name: 'user',
    component: () => import('../views/UserView.vue')
  }
]

const router = new VueRouter({
  routes
})

export default router
