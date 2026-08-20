<script setup>
import { RouterView, useRouter } from 'vue-router'
import { useAuthStore } from './store/authStore'

const auth = useAuthStore()
const router = useRouter()

auth.init()

const logout = () => {
    auth.logout()
    router.push('/login')
}
</script>

<template>
  <header>
    <nav class="navbar navbar-expand-lg navbar-dark shadow-sm">
      <div class="container">
        <RouterLink class="navbar-brand d-flex align-items-center" to="/">
          <span class="me-2">🏥</span>
          <span>HMS-V2</span>
        </RouterLink>
        <button class="navbar-toggler border-0" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav ms-auto gap-2">
            <li class="nav-item">
              <RouterLink class="nav-link px-3" to="/">Home</RouterLink>
            </li>
            <template v-if="!auth.isAuthenticated">
              <li class="nav-item">
                <RouterLink class="nav-link px-3" to="/login">Login</RouterLink>
              </li>
              <li class="nav-item">
                <RouterLink class="nav-link px-3 btn btn-light text-primary fw-bold" to="/register">Register</RouterLink>
              </li>
            </template>
            <template v-else>
              <li v-if="auth.isAdmin" class="nav-item">
                <RouterLink class="nav-link px-3" to="/admin">Admin</RouterLink>
              </li>
              <li v-if="auth.isDoctor" class="nav-item">
                <RouterLink class="nav-link px-3" to="/doctor">Doctor</RouterLink>
              </li>
              <li v-if="auth.isPatient" class="nav-item">
                <RouterLink class="nav-link px-3" to="/patient">Dashboard</RouterLink>
              </li>
              <li class="nav-item dropdown">
                <a class="nav-link px-3 dropdown-toggle" href="#" id="userDropdown" role="button" data-bs-toggle="dropdown">
                  {{ auth.user.username }}
                </a>
                <ul class="dropdown-menu dropdown-menu-end shadow border-0">
                  <li><a class="dropdown-item" href="#" @click.prevent="logout">Logout</a></li>
                </ul>
              </li>
            </template>
          </ul>
        </div>
      </div>
    </nav>
  </header>

  <main class="container py-5 min-vh-100">
    <RouterView />
  </main>

  <footer class="bg-white py-5 mt-5 border-top">
    <div class="container text-center">
      <p class="text-muted mb-0">© 2026 Hospital Management System - V2. Built with Excellence.</p>
    </div>
  </footer>
</template>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

.nav-link {
  transition: all 0.2s ease;
  border-radius: 6px;
}

.nav-link:hover {
  background: rgba(255, 255, 255, 0.1);
}

.nav-link.router-link-active {
  background: rgba(255, 255, 255, 0.2);
  font-weight: 600;
}
</style>
