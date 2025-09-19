<template>
  <footer class="footer bg-light border-top">
    <div class="container-fluid">
      <div class="row align-items-center py-3">
        <div class="col-md-6">
          <span class="text-muted">
            &copy; {{ currentYear }} Sistema Contable  Accescont Ecuador. Todos los derechos reservados Bryam Cabrera.
          </span>
        </div>
        <div class="col-md-6 text-end">
          <span class="text-muted">
            Versión {{ version }}
          </span>
        </div>
      </div>
    </div>
  </footer>
</template>

<script>
import { computed } from 'vue'

export default {
  name: 'Footer',
  setup() {
    const currentYear = computed(() => new Date().getFullYear())
    const version = '1.0.0'

    return {
      currentYear,
      version
    }
  }
}
</script>

<style scoped>
.footer {
  margin-top: auto;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 1000;
}

body {
  padding-bottom: 80px;
}
</style>










