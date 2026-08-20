import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../store/authStore'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../views/HomeView.vue')
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue')
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/RegisterView.vue')
    },
    {
      path: '/admin',
      name: 'admin',
      component: () => import('../views/AdminDashboard.vue'),
      beforeEnter: (to, from, next) => {
        const auth = useAuthStore()
        if (auth.isAdmin) next()
        else next('/login')
      }
    },
    {
      path: '/doctor',
      name: 'doctor',
      component: () => import('../views/DoctorDashboard.vue'),
      beforeEnter: (to, from, next) => {
        const auth = useAuthStore()
        if (auth.isDoctor) next()
        else next('/login')
      }
    },
    {
      path: '/patient',
      name: 'patient',
      component: () => import('../views/PatientDashboard.vue'),
      beforeEnter: (to, from, next) => {
        const auth = useAuthStore()
        if (auth.isPatient) next()
        else next('/login')
      }
    }
  ]
})

export default router
