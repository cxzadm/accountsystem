<template>
  <nav aria-label="breadcrumb" class="custom-breadcrumb-nav">
    <div class="breadcrumb-header">
      <h5 class="breadcrumb-title">
        <i v-if="titleIcon" :class="titleIcon" class="me-2"></i>
        {{ title }}
      </h5>
      <div class="breadcrumb-actions" v-if="$slots.actions">
        <slot name="actions"></slot>
      </div>
    </div>
    
    <ol class="breadcrumb">
      <li 
        v-for="(item, index) in items" 
        :key="item.path || index"
        class="breadcrumb-item"
        :class="{ 'active': index === items.length - 1 }"
      >
        <router-link 
          v-if="!item.active && item.path" 
          :to="item.path" 
          class="breadcrumb-link"
        >
          <i v-if="item.icon" :class="item.icon" class="me-1"></i>
          {{ item.label }}
        </router-link>
        <span v-else class="breadcrumb-current">
          <i v-if="item.icon" :class="item.icon" class="me-1"></i>
          {{ item.label }}
        </span>
      </li>
    </ol>
    
    <!-- Información adicional -->
    <div v-if="description || $slots.description" class="breadcrumb-description">
      <slot name="description">
        <p class="text-muted mb-0">{{ description }}</p>
      </slot>
    </div>
  </nav>
</template>

<script>
export default {
  name: 'CustomBreadcrumb',
  props: {
    title: {
      type: String,
      required: true
    },
    titleIcon: {
      type: String,
      default: null
    },
    description: {
      type: String,
      default: null
    },
    items: {
      type: Array,
      required: true,
      validator: (items) => {
        return items.every(item => 
          typeof item === 'object' && 
          'label' in item &&
          typeof item.label === 'string'
        )
      }
    }
  }
}
</script>

<style scoped>
.custom-breadcrumb-nav {
  background: linear-gradient(135deg, #165c6a 0%, #0f3d47 100%);
  color: white;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  border-radius: 0.35rem;
  box-shadow: 0 0.15rem 1.75rem 0 rgba(22, 92, 106, 0.15);
  border: 2px solid #bb8945;
}

.breadcrumb-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.breadcrumb-title {
  margin: 0;
  font-weight: 600;
  color: white;
}

.breadcrumb-actions {
  display: flex;
  gap: 0.5rem;
}

.breadcrumb {
  margin-bottom: 0;
  background: none;
  padding: 0;
}

.breadcrumb-item {
  display: flex;
  align-items: center;
}

.breadcrumb-item + .breadcrumb-item::before {
  content: ">";
  color: #bb8945;
  font-weight: 600;
  margin: 0 0.5rem;
  font-size: 0.9rem;
}

.breadcrumb-link {
  color: rgba(255, 255, 255, 0.9);
  text-decoration: none;
  transition: all 0.15s ease-in-out;
  display: flex;
  align-items: center;
  font-weight: 500;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
}

.breadcrumb-link:hover {
  color: white;
  background-color: rgba(187, 137, 69, 0.2);
  text-decoration: none;
  transform: translateY(-1px);
}

.breadcrumb-current {
  color: white;
  font-weight: 600;
  display: flex;
  align-items: center;
  padding: 0.25rem 0.5rem;
  background-color: rgba(187, 137, 69, 0.2);
  border-radius: 0.25rem;
  border-left: 3px solid #bb8945;
}

.breadcrumb-item.active .breadcrumb-current {
  color: white;
  font-weight: 700;
}

.breadcrumb-description {
  margin-top: 0.75rem;
  padding-top: 0.75rem;
  border-top: 2px solid #bb8945;
}

.breadcrumb-description p {
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.875rem;
  line-height: 1.4;
}

/* Variantes de color */
.custom-breadcrumb-nav.variant-primary {
  background: linear-gradient(135deg, #165c6a 0%, #0f3d47 100%);
  border-color: #bb8945;
}

.custom-breadcrumb-nav.variant-success {
  background: linear-gradient(135deg, #1cc88a 0%, #17a673 100%);
  border-color: #1cc88a;
}

.custom-breadcrumb-nav.variant-warning {
  background: linear-gradient(135deg, #f6c23e 0%, #dda20a 100%);
  color: #0f3d47;
  border-color: #f6c23e;
}

.custom-breadcrumb-nav.variant-warning .breadcrumb-link {
  color: rgba(15, 61, 71, 0.8);
}

.custom-breadcrumb-nav.variant-warning .breadcrumb-link:hover {
  color: #0f3d47;
  background-color: rgba(15, 61, 71, 0.1);
}

.custom-breadcrumb-nav.variant-warning .breadcrumb-current {
  color: #0f3d47;
  background-color: rgba(15, 61, 71, 0.1);
  border-left-color: #0f3d47;
}

.custom-breadcrumb-nav.variant-danger {
  background: linear-gradient(135deg, #e74a3b 0%, #c0392b 100%);
  border-color: #e74a3b;
}

.custom-breadcrumb-nav.variant-info {
  background: linear-gradient(135deg, #36b9cc 0%, #2c9faf 100%);
  border-color: #36b9cc;
}

.custom-breadcrumb-nav.variant-dark {
  background: linear-gradient(135deg, #0f3d47 0%, #0a2a30 100%);
  border-color: #bb8945;
}

/* Iconos con color de acento */
.breadcrumb-link i,
.breadcrumb-current i {
  color: #bb8945;
  margin-right: 0.25rem;
}

.variant-warning .breadcrumb-link i,
.variant-warning .breadcrumb-current i {
  color: #0f3d47;
}

/* Responsive */
@media (max-width: 768px) {
  .custom-breadcrumb-nav {
    padding: 1rem;
    border-radius: 0;
  }
  
  .breadcrumb-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .breadcrumb-actions {
    align-self: stretch;
    justify-content: flex-end;
  }
  
  .breadcrumb-item + .breadcrumb-item::before {
    margin: 0 0.25rem;
  }
  
  .breadcrumb-link,
  .breadcrumb-current {
    padding: 0.2rem 0.4rem;
    font-size: 0.8rem;
  }
}

/* Animaciones suaves */
.breadcrumb-link {
  transition: all 0.2s ease-in-out;
}

.breadcrumb-link:hover {
  box-shadow: 0 0.125rem 0.25rem rgba(187, 137, 69, 0.15);
}

/* Efecto de hover para el contenedor */
.custom-breadcrumb-nav:hover {
  box-shadow: 0 0.25rem 2rem 0 rgba(22, 92, 106, 0.2);
  transition: box-shadow 0.3s ease-in-out;
}
</style>
