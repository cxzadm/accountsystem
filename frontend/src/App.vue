<template>
  <div id="app">
    <Navbar v-if="isAuthenticated" />
    <Sidebar v-if="isAuthenticated" />
    
    <main :class="{ 'with-sidebar': isAuthenticated }">
      <router-view />
    </main>
    
    <Footer v-if="isAuthenticated" />
  </div>
</template>

<script>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import Navbar from '@/components/layout/Navbar.vue'
import Sidebar from '@/components/layout/Sidebar.vue'
import Footer from '@/components/layout/Footer.vue'

export default {
  name: 'App',
  components: {
    Navbar,
    Sidebar,
    Footer
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
}

main {
  min-height: calc(100vh - 70px);
  padding: 20px;
}
</style>










