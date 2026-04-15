<!-- src/views/auth/SignupView.vue -->
<template>
  <div class="signup-view">
    <div class="signup-container">
      <h1>Sign Up</h1>
      
      <div v-if="authStore.error" class="error-message">
        {{ authStore.error }}
      </div>

      <div v-if="validationError" class="error-message">
        {{ validationError }}
      </div>

      <form @submit.prevent="handleSignup">
        <div class="form-group">
          <label for="name">Name</label>
          <input 
            id="name"
            v-model="form.name" 
            type="text" 
            autocomplete="name"
            required
            :disabled="authStore.loading"
          />
        </div>
        
        <div class="form-group">
          <label for="email">Email</label>
          <input 
            id="email"
            v-model="form.email" 
            type="email" 
            autocomplete="email"
            required
            :disabled="authStore.loading"
          />
        </div>
        
        <div class="form-group">
          <label for="password">Password</label>
          <input 
            id="password"
            v-model="form.password" 
            type="password" 
            autocomplete="new-password"
            required
            minlength="6"
            :disabled="authStore.loading"
          />
        </div>
        
        <div class="form-group">
          <label for="confirmPassword">Confirm Password</label>
          <input 
            id="confirmPassword"
            v-model="form.confirmPassword" 
            type="password" 
            autocomplete="new-password"
            required
            :disabled="authStore.loading"
          />
        </div>
        
        <button type="submit" :disabled="authStore.loading">
          {{ authStore.loading ? 'Creating account...' : 'Sign Up' }}
        </button>
      </form>
      
      <p>Already have an account? <router-link to="/login">Login</router-link></p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/authStore'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({
  name: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const validationError = ref(null)

const handleSignup = async () => {
  validationError.value = null

  if (form.value.password !== form.value.confirmPassword) {
    validationError.value = 'Passwords do not match'
    return
  }

  if (form.value.password.length < 6) {
    validationError.value = 'Password must be at least 6 characters'
    return
  }

  try {
    const { confirmPassword, ...registerData } = form.value
    await authStore.register(registerData)
    // After successful registration, redirect to login
    router.push('/login')
  } catch (err) {
    console.error('Registration error:', err)
  }
}
</script>

<style scoped>
/* ── Page ── */
.signup-view {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #fffef5;
  background-image: repeating-linear-gradient(
    to bottom,
    transparent 0px,
    transparent 31px,
    rgba(180, 210, 255, 0.25) 31px,
    rgba(180, 210, 255, 0.25) 32px
  );
  font-family: 'Patrick Hand', cursive;
  padding: 32px 16px;
}

/* ── Card ── */
.signup-container {
  background: #fffef5;
  border: 2px solid #1a1a1a;
  border-radius: 12px;
  box-shadow: 6px 6px 0px #1a1a1a;
  padding: 40px 36px 32px;
  width: 100%;
  max-width: 420px;
  transform: rotate(0.3deg);
}

/* ── Heading ── */
h1 {
  font-family: 'Patrick Hand', cursive;
  font-size: 2rem;
  font-weight: 700;
  color: #1a1a1a;
  text-align: center;
  margin: 0 0 28px;
  background: linear-gradient(104deg, transparent 0.5%, #fff59d 2%, #fff59d 95%, transparent 99%);
  padding: 2px 12px;
  border-radius: 3px;
  display: inline-block;
  width: 100%;
  box-sizing: border-box;
}

/* ── Error ── */
.error-message {
  background: #ffe0e0;
  color: #c0392b;
  border: 1.5px solid #1a1a1a;
  border-radius: 7px;
  box-shadow: 2px 2px 0px #1a1a1a;
  padding: 10px 14px;
  margin-bottom: 18px;
  font-size: 14px;
  font-family: 'Patrick Hand', cursive;
}

/* ── Form group ── */
.form-group {
  margin-bottom: 16px;
}

label {
  display: block;
  margin-bottom: 6px;
  font-family: 'Patrick Hand', cursive;
  font-size: 14px;
  font-weight: 700;
  color: #1a1a1a;
}

input {
  width: 100%;
  padding: 10px 12px;
  font-family: 'Patrick Hand', cursive;
  font-size: 15px;
  color: #1a1a1a;
  background: #fff;
  border: 2px dashed #1a1a1a;
  border-radius: 7px;
  box-sizing: border-box;
  outline: none;
  box-shadow: none;
}

input:focus {
  border-style: solid;
  background: #fffef5;
}

input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ── Submit button ── */
button[type="submit"] {
  width: 100%;
  padding: 12px;
  font-family: 'Patrick Hand', cursive;
  font-size: 1rem;
  font-weight: 700;
  background: #1a1a1a;
  color: #fffef5;
  border: 2px solid #1a1a1a;
  border-radius: 8px;
  box-shadow: 4px 4px 0px #4f46e5;
  cursor: pointer;
  margin-top: 8px;
}

button[type="submit"]:hover:not(:disabled) {
  box-shadow: 6px 6px 0px #4f46e5;
  transform: translate(-1px, -1px);
}

button[type="submit"]:active:not(:disabled) {
  box-shadow: 2px 2px 0px #4f46e5;
  transform: translate(2px, 2px);
}

button[type="submit"]:disabled {
  opacity: 0.45;
  cursor: not-allowed;
  box-shadow: none;
  transform: none;
}

/* ── Footer link ── */
p {
  margin-top: 20px;
  text-align: center;
  font-family: 'Patrick Hand', cursive;
  font-size: 14px;
  color: #555;
}

a {
  color: #4f46e5;
  font-weight: 700;
  text-decoration: underline;
  text-underline-offset: 3px;
}

a:hover {
  color: #1a1a1a;
}
</style>