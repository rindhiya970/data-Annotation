// src/router/index.js (UPDATED)
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/authStore'
import MainLayout from '../layouts/MainLayout.vue'
import LoginView from '../views/auth/LoginView.vue'
import SignupView from '../views/auth/SignupView.vue'
import DashboardView from '../views/DashboardView.vue'
import ProjectsView from '../views/ProjectsView.vue'
import TasksView from '../views/TasksView.vue'
import AnalyticsView from '../views/AnalyticsView.vue'
import ProfileView from '../views/ProfileView.vue'
import MediaUploadView from '../views/MediaUploadView.vue'
import MediaLibraryView from '../views/MediaLibraryView.vue'
import AnnotateView from '../views/AnnotateView.vue'
import VideoDetailView from '../views/VideoDetailView.vue'
import VideoAnnotateView from '../views/VideoAnnotateView.vue'
import NotFoundView from '../views/NotFoundView.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: LoginView,
    meta: { requiresAuth: false }
  },
  {
    path: '/signup',
    name: 'Signup',
    component: SignupView,
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: MainLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/dashboard'
      },
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: DashboardView,
        meta: { requiresAuth: true }
      },
      {
        path: 'projects',
        name: 'Projects',
        component: ProjectsView,
        meta: { requiresAuth: true }
      },
      {
        path: 'tasks',
        name: 'Tasks',
        component: TasksView,
        meta: { requiresAuth: true }
      },
      {
        path: 'analytics',
        name: 'Analytics',
        component: AnalyticsView,
        meta: { requiresAuth: true }
      },
      {
        path: 'profile',
        name: 'Profile',
        component: ProfileView,
        meta: { requiresAuth: true }
      },
      {
        path: 'media/upload',
        name: 'MediaUpload',
        component: MediaUploadView,
        meta: { requiresAuth: true }
      },
      {
        path: 'media/library',
        name: 'MediaLibrary',
        component: MediaLibraryView,
        meta: { requiresAuth: true }
      },
      {
        path: 'annotate/:id',
        name: 'Annotate',
        component: AnnotateView,
        meta: { requiresAuth: true }
      },
      {
        path: 'videos/:id',
        name: 'VideoDetail',
        component: VideoDetailView,
        meta: { requiresAuth: true }
      },
      {
        path: 'video-annotate/:id',
        name: 'VideoAnnotate',
        component: VideoAnnotateView,
        meta: { requiresAuth: true }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFoundView
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const isAuthenticated = authStore.isAuthenticated

  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login')
  } else if ((to.path === '/login' || to.path === '/signup') && isAuthenticated) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router