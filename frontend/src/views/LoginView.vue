<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../store/authStore'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const router = useRouter()

const username = ref('')
const password = ref('')

const handleLogin = async () => {
    const success = await auth.login(username.value, password.value)
    if (success) {
        if (auth.isAdmin) router.push('/admin')
        else if (auth.isDoctor) router.push('/doctor')
        else router.push('/patient')
    }
}
</script>

<template>
  <div class="row justify-content-center py-5 fade-in">
    <div class="col-md-6 col-lg-5">
      <div class="card border-0 shadow-lg p-4 p-md-5">
        <div class="text-center mb-5">
            <div class="bg-primary text-white rounded-circle d-inline-flex align-items-center justify-content-center mb-3" style="width: 64px; height: 64px;">
                <i class="bi bi-person-lock fs-2"></i>
            </div>
            <h2 class="fw-bold">Welcome Back</h2>
            <p class="text-muted">Enter your credentials to access your account</p>
        </div>

        <div v-if="auth.error" class="alert alert-danger px-3 py-2 small border-0 shadow-sm mb-4">{{ auth.error }}</div>
        
        <form @submit.prevent="handleLogin">
          <div class="mb-3">
            <label class="form-label small fw-semibold text-muted">Username</label>
            <input v-model="username" type="text" class="form-control bg-light border-0" placeholder="your-name" required>
          </div>
          <div class="mb-4">
            <div class="d-flex justify-content-between">
                <label class="form-label small fw-semibold text-muted">Password</label>
                <a href="#" class="small text-primary text-decoration-none">Forgot?</a>
            </div>
            <input v-model="password" type="password" class="form-control bg-light border-0" placeholder="••••••••" required>
          </div>
          <button type="submit" class="btn btn-primary w-100 py-2 fw-bold" :disabled="auth.loading">
            <span v-if="auth.loading" class="spinner-border spinner-border-sm me-2"></span>
            Sign In
          </button>
        </form>
        
        <div class="mt-5 text-center">
          <p class="text-muted small mb-0">Don't have an account?</p>
          <RouterLink to="/register" class="fw-bold text-primary text-decoration-none">Create a new account</RouterLink>
        </div>
      </div>
    </div>
  </div>
</template>
