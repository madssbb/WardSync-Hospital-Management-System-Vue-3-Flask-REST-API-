<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../store/authStore'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const router = useRouter()

const username = ref('')
const email = ref('')
const password = ref('')
const name = ref('')
const contact = ref('')
const dob = ref('')

const handleRegister = async () => {
    const success = await auth.register({
        username: username.value,
        email: email.value,
        password: password.value,
        name: name.value,
        contact: contact.value,
        dob: dob.value
    })
    if (success) {
        alert('Registration successful! Please login.')
        router.push('/login')
    }
}
</script>

<template>
  <div class="row justify-content-center py-5 fade-in">
    <div class="col-md-6 col-lg-5">
      <div class="card border-0 shadow-lg p-4 p-md-5">
        <div class="text-center mb-5">
            <div class="bg-success text-white rounded-circle d-inline-flex align-items-center justify-content-center mb-3" style="width: 64px; height: 64px;">
                <i class="bi bi-person-plus fs-2"></i>
            </div>
            <h2 class="fw-bold">Create Account</h2>
            <p class="text-muted">Join our healthcare platform today</p>
        </div>

        <div v-if="auth.error" class="alert alert-danger px-3 py-2 small border-0 shadow-sm mb-4">{{ auth.error }}</div>
        
        <form @submit.prevent="handleRegister">
          <div class="row g-3">
            <div class="col-md-12 mb-2">
                <label class="form-label small fw-semibold text-muted">Full Name</label>
                <input v-model="name" type="text" class="form-control bg-light border-0" placeholder="Your name" required>
            </div>
            <div class="col-md-6 mb-2">
                <label class="form-label small fw-semibold text-muted">Username</label>
                <input v-model="username" type="text" class="form-control bg-light border-0" placeholder="your-name" required>
            </div>
            <div class="col-md-6 mb-2">
                <label class="form-label small fw-semibold text-muted">Email</label>
                <input v-model="email" type="email" class="form-control bg-light border-0" placeholder="yourname@example.com" required>
            </div>
            <div class="col-md-12 mb-2">
                <label class="form-label small fw-semibold text-muted">Password</label>
                <input v-model="password" type="password" class="form-control bg-light border-0" placeholder="••••••••" required>
            </div>
            <div class="col-md-6 mb-2">
                <label class="form-label small fw-semibold text-muted">Contact Number</label>
                <input v-model="contact" type="text" class="form-control bg-light border-0" placeholder="1234567890">
            </div>
            <div class="col-md-6 mb-4">
                <label class="form-label small fw-semibold text-muted">Date of Birth</label>
                <input v-model="dob" type="date" class="form-control bg-light border-0">
            </div>
          </div>
          
          <button type="submit" class="btn btn-primary w-100 py-2 fw-bold mb-3" :disabled="auth.loading">
            <span v-if="auth.loading" class="spinner-border spinner-border-sm me-2"></span>
            Register Account
          </button>
        </form>
        
        <div class="text-center">
          <p class="text-muted small mb-0">Already have an account?</p>
          <RouterLink to="/login" class="fw-bold text-primary text-decoration-none">Sign in here</RouterLink>
        </div>
      </div>
    </div>
  </div>
</template>
