import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Lazy load components
const Login = () => import('@/views/auth/Login.vue')
const Dashboard = () => import('@/views/Dashboard.vue')
const Users = () => import('@/views/users/Users.vue')
const UserForm = () => import('@/views/users/UserForm.vue')
const Companies = () => import('@/views/companies/Companies.vue')
const CompanyForm = () => import('@/views/companies/CompanyForm.vue')
const InitialBalances = () => import('@/views/companies/InitialBalances.vue')
const Accounts = () => import('@/views/accounts/Accounts.vue')
const AccountForm = () => import('@/views/accounts/AccountForm.vue')
const Journal = () => import('@/views/journal/Journal.vue')
const JournalForm = () => import('@/views/journal/JournalForm.vue')
const Ledger = () => import('@/views/ledger/Ledger.vue')
const Reports = () => import('@/views/reports/Reports.vue')
const SRI = () => import('@/views/sri/SRI.vue')
const Audit = () => import('@/views/audit/Audit.vue')
const Profile = () => import('@/views/Profile.vue')
const Settings = () => import('@/views/Settings.vue')
const DocumentTypes = () => import('@/views/admin/DocumentTypes.vue')
const DocumentReservations = () => import('@/views/admin/DocumentReservations.vue')
const CompanySettings = () => import('@/views/companies/CompanySettings.vue')
const ConfiguracionBackend = () => import('@/views/configback/ConfiguracionBackend.vue')

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false }
  },
  {
    path: '/admin/backend-config',
    name: 'BackendConfig',
    component: ConfiguracionBackend,
    meta: { requiresAuth: true, roles: ['admin'] }
  },
  {
    path: '/companies/:id/settings',
    name: 'CompanySettings',
    component: CompanySettings,
    meta: { requiresAuth: true, permission: 'companies:update' }
  },
  {
    path: '/admin/document-types',
    name: 'DocumentTypes',
    component: DocumentTypes,
    meta: { requiresAuth: true, permission: 'companies:update' }
  },
  {
    path: '/admin/document-reservations',
    name: 'DocumentReservations',
    component: DocumentReservations,
    meta: { requiresAuth: true, permission: 'companies:update' }
  },
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/users',
    name: 'Users',
    component: Users,
    meta: { requiresAuth: true, permission: 'users:read' }
  },
  {
    path: '/users/new',
    name: 'UserNew',
    component: UserForm,
    meta: { requiresAuth: true, permission: 'users:create' }
  },
  {
    path: '/users/:id/edit',
    name: 'UserEdit',
    component: UserForm,
    meta: { requiresAuth: true, permission: 'users:update' }
  },
  {
    path: '/companies',
    name: 'Companies',
    component: Companies,
    meta: { requiresAuth: true, permission: 'companies:read' }
  },
  {
    path: '/companies/new',
    name: 'CompanyNew',
    component: CompanyForm,
    meta: { requiresAuth: true, permission: 'companies:create' }
  },
  {
    path: '/companies/:id/edit',
    name: 'CompanyEdit',
    component: CompanyForm,
    meta: { requiresAuth: true, permission: 'companies:update' }
  },
  {
    path: '/companies/:id/initial-balances',
    name: 'InitialBalances',
    component: InitialBalances,
    meta: { requiresAuth: true, permission: 'accounts:update' }
  },
  {
    path: '/accounts',
    name: 'Accounts',
    component: Accounts,
    meta: { requiresAuth: true, permission: 'accounts:read' }
  },
  {
    path: '/accounts/new',
    name: 'AccountNew',
    component: AccountForm,
    meta: { requiresAuth: true, permission: 'accounts:create' }
  },
  {
    path: '/accounts/:id/edit',
    name: 'AccountEdit',
    component: AccountForm,
    meta: { requiresAuth: true, permission: 'accounts:update' }
  },
  {
    path: '/journal',
    name: 'Journal',
    component: Journal,
    meta: { requiresAuth: true, permission: 'journal:read' }
  },
  {
    path: '/journal/new',
    name: 'JournalNew',
    component: JournalForm,
    meta: { requiresAuth: true, permission: 'journal:create' }
  },
  {
    path: '/journal/:id/edit',
    name: 'JournalEdit',
    component: JournalForm,
    meta: { requiresAuth: true, permission: 'journal:update' }
  },
  {
    path: '/ledger',
    name: 'Ledger',
    component: Ledger,
    meta: { requiresAuth: true, permission: 'reports:read' }
  },
  {
    path: '/reports',
    name: 'Reports',
    component: Reports,
    meta: { requiresAuth: true, permission: 'reports:read' }
  },
  {
    path: '/sri',
    name: 'SRI',
    component: SRI,
    meta: { requiresAuth: true, permission: 'sri:read' }
  },
  {
    path: '/audit',
    name: 'Audit',
    component: Audit,
    meta: { requiresAuth: true, permission: 'audit:read' }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile,
    meta: { requiresAuth: true }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: Settings,
    meta: { requiresAuth: true, permission: 'settings:read' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guards
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.path === '/login' && authStore.isAuthenticated) {
    next('/')
  } else if (to.meta.permission && !authStore.hasPermission(to.meta.permission)) {
    next('/')
  } else if (to.meta.roles && !authStore.hasAnyRole(to.meta.roles)) {
    next('/')
  } else {
    next()
  }
})

export default router
