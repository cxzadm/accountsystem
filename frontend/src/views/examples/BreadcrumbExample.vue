<template>
  <div class="breadcrumb-example">
    <h2>Ejemplos de Breadcrumbs</h2>
    
    <!-- Ejemplo 1: Breadcrumb Básico -->
    <div class="example-section">
      <h4>1. Breadcrumb Básico</h4>
      <p>Breadcrumb automático basado en la ruta actual.</p>
      <Breadcrumb />
    </div>
    
    <!-- Ejemplo 2: Breadcrumb Avanzado -->
    <div class="example-section">
      <h4>2. Breadcrumb Avanzado con Historial</h4>
      <p>Breadcrumb con controles de navegación y historial persistente.</p>
      <AdvancedBreadcrumb :show-controls="true" />
    </div>
    
    <!-- Ejemplo 3: Breadcrumb Personalizado -->
    <div class="example-section">
      <h4>3. Breadcrumb Personalizado</h4>
      <p>Breadcrumb completamente personalizable con título y acciones, usando los colores del sistema.</p>
      <CustomBreadcrumb
        title="Gestión de Cuentas"
        title-icon="fas fa-list-alt"
        description="Administra el plan de cuentas contables de la empresa"
        :items="customBreadcrumbItems"
        variant="primary"
      >
        <template #actions>
          <button class="btn btn-sm btn-accent me-2" @click="exportData">
            <i class="fas fa-download me-1"></i>
            Exportar
          </button>
          <button class="btn btn-sm btn-primary-dark" @click="importData">
            <i class="fas fa-upload me-1"></i>
            Importar
          </button>
        </template>
      </CustomBreadcrumb>
    </div>
    
    <!-- Ejemplo 4: Breadcrumbs Dinámicos -->
    <div class="example-section">
      <h4>4. Breadcrumbs Dinámicos</h4>
      <p>Demostración de breadcrumbs que se agregan dinámicamente.</p>
      
      <div class="demo-controls mb-3">
        <button class="btn btn-primary me-2" @click="addAccountBreadcrumb">
          <i class="fas fa-plus me-1"></i>
          Agregar Cuenta
        </button>
        <button class="btn btn-warning me-2" @click="addFilterBreadcrumb">
          <i class="fas fa-filter me-1"></i>
          Agregar Filtro
        </button>
        <button class="btn btn-info me-2" @click="addReportBreadcrumb">
          <i class="fas fa-chart-bar me-1"></i>
          Agregar Reporte
        </button>
        <button class="btn btn-danger" @click="clearDynamicBreadcrumbs">
          <i class="fas fa-trash me-1"></i>
          Limpiar
        </button>
      </div>
      
      <div class="breadcrumb-preview">
        <h6>Breadcrumbs Dinámicos Actuales:</h6>
        <div v-if="dynamicBreadcrumbs.length === 0" class="text-muted">
          No hay breadcrumbs dinámicos
        </div>
        <div v-else class="breadcrumb-list">
          <div 
            v-for="(breadcrumb, index) in dynamicBreadcrumbs" 
            :key="index"
            class="breadcrumb-item-preview"
          >
            <i v-if="breadcrumb.icon" :class="breadcrumb.icon" class="me-2"></i>
            <span>{{ breadcrumb.label }}</span>
            <button 
              class="btn btn-sm btn-outline-danger ms-2"
              @click="removeBreadcrumb(index)"
            >
              <i class="fas fa-times"></i>
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Ejemplo 5: Diferentes Variantes -->
    <div class="example-section">
      <h4>5. Variantes de Color</h4>
      <p>Diferentes estilos de breadcrumb personalizado.</p>
      
      <div class="variants-grid">
        <div class="variant-item">
          <h6>Primaria (Sistema)</h6>
          <CustomBreadcrumb
            title="Variante Primaria"
            :items="[{ label: 'Inicio', path: '/', icon: 'fas fa-home' }, { label: 'Ejemplo', active: true, icon: 'fas fa-star' }]"
            variant="primary"
          />
        </div>
        
        <div class="variant-item">
          <h6>Éxito</h6>
          <CustomBreadcrumb
            title="Variante Éxito"
            :items="[{ label: 'Inicio', path: '/', icon: 'fas fa-home' }, { label: 'Ejemplo', active: true, icon: 'fas fa-check' }]"
            variant="success"
          />
        </div>
        
        <div class="variant-item">
          <h6>Advertencia</h6>
          <CustomBreadcrumb
            title="Variante Advertencia"
            :items="[{ label: 'Inicio', path: '/', icon: 'fas fa-home' }, { label: 'Ejemplo', active: true, icon: 'fas fa-exclamation-triangle' }]"
            variant="warning"
          />
        </div>
        
        <div class="variant-item">
          <h6>Peligro</h6>
          <CustomBreadcrumb
            title="Variante Peligro"
            :items="[{ label: 'Inicio', path: '/', icon: 'fas fa-home' }, { label: 'Ejemplo', active: true, icon: 'fas fa-times' }]"
            variant="danger"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import Breadcrumb from '@/components/Breadcrumb.vue'
import AdvancedBreadcrumb from '@/components/AdvancedBreadcrumb.vue'
import CustomBreadcrumb from '@/components/CustomBreadcrumb.vue'
import { useBreadcrumb } from '@/composables/useBreadcrumb'

export default {
  name: 'BreadcrumbExample',
  components: {
    Breadcrumb,
    AdvancedBreadcrumb,
    CustomBreadcrumb
  },
  setup() {
    const { 
      dynamicBreadcrumbs, 
      addBreadcrumb, 
      removeBreadcrumb, 
      clearBreadcrumbs,
      createAccountBreadcrumb,
      createFilterBreadcrumb,
      createReportBreadcrumb
    } = useBreadcrumb()

    // Breadcrumb personalizado de ejemplo
    const customBreadcrumbItems = ref([
      {
        label: 'Inicio',
        path: '/',
        icon: 'fas fa-home'
      },
      {
        label: 'Empresas',
        path: '/companies',
        icon: 'fas fa-building'
      },
      {
        label: 'Mi Empresa',
        path: '/companies/123',
        icon: 'fas fa-building'
      },
      {
        label: 'Plan de Cuentas',
        active: true,
        icon: 'fas fa-list-alt'
      }
    ])

    // Funciones de demostración
    const addAccountBreadcrumb = () => {
      const account = {
        code: '3010101',
        name: 'Juan Pérez'
      }
      const breadcrumb = createAccountBreadcrumb(account)
      addBreadcrumb(breadcrumb)
    }

    const addFilterBreadcrumb = () => {
      const breadcrumb = createFilterBreadcrumb('Tipo', 'Activo')
      addBreadcrumb(breadcrumb)
    }

    const addReportBreadcrumb = () => {
      const breadcrumb = createReportBreadcrumb('balance', 'Balance General')
      addBreadcrumb(breadcrumb)
    }

    const clearDynamicBreadcrumbs = () => {
      clearBreadcrumbs()
    }

    const exportData = () => {
      alert('Función de exportación ejecutada')
    }

    const importData = () => {
      alert('Función de importación ejecutada')
    }

    return {
      dynamicBreadcrumbs,
      customBreadcrumbItems,
      addAccountBreadcrumb,
      addFilterBreadcrumb,
      addReportBreadcrumb,
      clearDynamicBreadcrumbs,
      removeBreadcrumb,
      exportData,
      importData
    }
  }
}
</script>

<style scoped>
.breadcrumb-example {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.example-section {
  margin-bottom: 3rem;
  padding: 1.5rem;
  border: 1px solid #dee2e6;
  border-radius: 0.5rem;
  background-color: #f8f9fa;
}

.example-section h4 {
  color: #495057;
  margin-bottom: 1rem;
}

.example-section p {
  color: #6c757d;
  margin-bottom: 1rem;
}

.demo-controls {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.breadcrumb-preview {
  background: white;
  padding: 1rem;
  border-radius: 0.375rem;
  border: 1px solid #dee2e6;
}

.breadcrumb-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.breadcrumb-item-preview {
  display: flex;
  align-items: center;
  padding: 0.5rem;
  background-color: #f8f9fa;
  border-radius: 0.25rem;
  border: 1px solid #dee2e6;
}

.variants-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
}

.variant-item {
  background: white;
  padding: 1rem;
  border-radius: 0.5rem;
  border: 1px solid #dee2e6;
}

.variant-item h6 {
  margin-bottom: 1rem;
  color: #495057;
}

/* Responsive */
@media (max-width: 768px) {
  .breadcrumb-example {
    padding: 1rem;
  }
  
  .example-section {
    padding: 1rem;
  }
  
  .variants-grid {
    grid-template-columns: 1fr;
  }
  
  .demo-controls {
    flex-direction: column;
  }
  
  .demo-controls .btn {
    width: 100%;
  }
}
</style>
