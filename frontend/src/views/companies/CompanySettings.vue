<template>
  <div class="company-settings-page">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h1 class="h3 mb-0">Configuración de {{ company?.name || 'Empresa' }}</h1>
        <p class="text-muted">Administra las configuraciones de la empresa</p>
      </div>
      <div>
        <router-link to="/companies" class="btn btn-outline-secondary">
          <i class="fas fa-arrow-left me-2"></i>
          Volver a Empresas
        </router-link>
      </div>
    </div>

    <div class="row g-3">
      <div class="col-md-3" v-for="card in cards" :key="card.key">
        <div class="card h-100 hover-card" role="button" @click="go(card)">
          <div class="card-body d-flex align-items-center">
            <div class="icon rounded-circle me-3" :class="card.bg">
              <i :class="card.icon"></i>
            </div>
            <div>
              <h6 class="mb-1">{{ card.title }}</h6>
              <p class="mb-0 text-muted small">{{ card.subtitle }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { onMounted, ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useCompanyStore } from '@/stores/company'

export default {
  name: 'CompanySettings',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const companyStore = useCompanyStore()
    const company = ref(null)

    const cards = computed(() => [
      { key: 'general', title: 'Información General', subtitle: 'Datos de la empresa', icon: 'fas fa-info-circle', bg: 'bg-primary text-white', to: `/companies/${route.params.id}/edit` },
      { key: 'initial', title: 'Saldos Iniciales', subtitle: 'Cuentas y saldos', icon: 'fas fa-calculator', bg: 'bg-success text-white', to: `/companies/${route.params.id}/initial-balances` },
      { key: 'docs', title: 'Tipos de Documentos', subtitle: 'Numeración y parámetros', icon: 'fas fa-file-invoice', bg: 'bg-warning text-dark', to: `/admin/document-types` },
      { key: 'res', title: 'Reservas de Números', subtitle: 'Editar/Anular reservas', icon: 'fas fa-hashtag', bg: 'bg-secondary text-white', to: `/admin/document-reservations` },
      // Placeholder for future modules
    ])

    const go = (card) => {
      if (company.value) {
        companyStore.setCurrentCompany(company.value)
      }
      router.push(card.to)
    }

    onMounted(async () => {
      try {
        company.value = await companyStore.getCompany(route.params.id)
        if (company.value) companyStore.setCurrentCompany(company.value)
      } catch (error) {
        console.error('Error in CompanySettings onMounted:', error)
      }
    })

    return { company, cards, go }
  }
}
</script>

<style scoped>
.hover-card {
  transition: transform 0.1s ease, box-shadow 0.1s ease;
}
.hover-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0,0,0,0.08);
}
.icon {
  width: 48px;
  height: 48px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
}
</style>



