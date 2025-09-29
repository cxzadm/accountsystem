import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useCompanyStore } from '@/stores/company'

// Store global para breadcrumbs dinámicos
const dynamicBreadcrumbs = ref([])

export function useBreadcrumb() {
  const router = useRouter()
  const companyStore = useCompanyStore()

  // Agregar breadcrumb dinámico
  const addBreadcrumb = (breadcrumb) => {
    dynamicBreadcrumbs.value.push(breadcrumb)
  }

  // Remover breadcrumb dinámico
  const removeBreadcrumb = (index) => {
    dynamicBreadcrumbs.value.splice(index, 1)
  }

  // Limpiar breadcrumbs dinámicos
  const clearBreadcrumbs = () => {
    dynamicBreadcrumbs.value = []
  }

  // Actualizar breadcrumb específico
  const updateBreadcrumb = (index, breadcrumb) => {
    if (dynamicBreadcrumbs.value[index]) {
      dynamicBreadcrumbs.value[index] = breadcrumb
    }
  }

  // Navegar a breadcrumb específico
  const navigateToBreadcrumb = (path) => {
    if (path) {
      router.push(path)
    }
  }

  // Obtener breadcrumbs dinámicos
  const getDynamicBreadcrumbs = computed(() => dynamicBreadcrumbs.value)

  // Crear breadcrumb para cuenta específica
  const createAccountBreadcrumb = (account) => {
    return {
      label: `${account.code} - ${account.name}`,
      path: null, // No navegable
      icon: 'fas fa-file-invoice',
      active: true
    }
  }

  // Crear breadcrumb para asiento específico
  const createJournalEntryBreadcrumb = (entry) => {
    return {
      label: `Asiento ${entry.entry_number}`,
      path: null, // No navegable
      icon: 'fas fa-book',
      active: true
    }
  }

  // Crear breadcrumb para reporte específico
  const createReportBreadcrumb = (reportType, reportName) => {
    return {
      label: reportName || reportType,
      path: null, // No navegable
      icon: 'fas fa-chart-bar',
      active: true
    }
  }

  // Crear breadcrumb para filtro específico
  const createFilterBreadcrumb = (filterType, filterValue) => {
    return {
      label: `${filterType}: ${filterValue}`,
      path: null, // No navegable
      icon: 'fas fa-filter',
      active: true
    }
  }

  return {
    // Estado
    dynamicBreadcrumbs,
    getDynamicBreadcrumbs,
    
    // Métodos
    addBreadcrumb,
    removeBreadcrumb,
    clearBreadcrumbs,
    updateBreadcrumb,
    navigateToBreadcrumb,
    
    // Helpers específicos
    createAccountBreadcrumb,
    createJournalEntryBreadcrumb,
    createReportBreadcrumb,
    createFilterBreadcrumb
  }
}





