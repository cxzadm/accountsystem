<template>
  <div id="app" class="d-flex flex-column min-vh-100">
    <Navbar v-if="isAuthenticated" />
    <div class="d-flex flex-grow-1">
      <Sidebar v-if="isAuthenticated" />
      
      <main :class="{ 'with-sidebar': isAuthenticated }" class="flex-grow-1">
        <Breadcrumb v-if="isAuthenticated" />
        <div class="content-wrapper">
          <router-view />
        </div>
        <Footer v-if="isAuthenticated" />
      </main>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import Navbar from '@/components/layout/Navbar.vue'
import Sidebar from '@/components/layout/Sidebar.vue'
import Footer from '@/components/layout/Footer.vue'
import Breadcrumb from '@/components/Breadcrumb.vue'

export default {
  name: 'App',
  components: {
    Navbar,
    Sidebar,
    Footer,
    Breadcrumb
  },
  setup() {
    const authStore = useAuthStore()
    
    const isAuthenticated = computed(() => authStore.isAuthenticated)
    
    return {
      isAuthenticated
    }
  }
}
</script>

<style scoped>
.with-sidebar {
  margin-left: 250px;
  padding-top: 70px;
  transition: margin-left 0.3s ease;
}

/* Cuando el sidebar está colapsado */
body.sidebar-collapsed .with-sidebar {
  margin-left: 70px;
}

main {
  min-height: 100vh;
  padding: 0;
  padding-bottom: 0;
}

.content-wrapper {
  min-height: calc(100vh - 70px - 40px); /* Altura total - navbar - padding */
  padding: 20px;
  padding-bottom: 2rem;
}

/* Asegurar que el contenido no se superponga con el footer */
#app {
  min-height: 100vh;
}
</style>













