// Configuración del sistema de breadcrumbs
export const breadcrumbConfig = {
  // Configuración general
  general: {
    // Mostrar breadcrumbs por defecto
    enabled: true,
    
    // Separador entre breadcrumbs
    separator: '>',
    
    // Icono por defecto para elementos sin icono
    defaultIcon: 'fas fa-circle',
    
    // Máximo número de breadcrumbs dinámicos
    maxDynamicBreadcrumbs: 10,
    
    // Persistir historial de navegación
    persistHistory: true,
    
    // Tamaño máximo del historial
    maxHistorySize: 50
  },

  // Configuración de rutas específicas
  routes: {
    '/dashboard': {
      title: 'Dashboard',
      icon: 'fas fa-tachometer-alt',
      description: 'Panel principal del sistema'
    },
    
    '/companies': {
      title: 'Empresas',
      icon: 'fas fa-building',
      description: 'Gestión de empresas'
    },
    
    '/accounts': {
      title: 'Plan de Cuentas',
      icon: 'fas fa-list-alt',
      description: 'Administración del plan de cuentas contables'
    },
    
    '/journal': {
      title: 'Diario Contable',
      icon: 'fas fa-book',
      description: 'Registro de asientos contables'
    },
    
    '/ledger': {
      title: 'Mayor General',
      icon: 'fas fa-table',
      description: 'Mayor general de cuentas'
    },
    
    '/profile': {
      title: 'Mi Perfil',
      icon: 'fas fa-user',
      description: 'Configuración de perfil de usuario'
    },
    
    '/settings': {
      title: 'Configuración',
      icon: 'fas fa-cog',
      description: 'Configuración del sistema'
    }
  },

  // Configuración de breadcrumbs dinámicos
  dynamic: {
    // Patrones de breadcrumbs automáticos
    patterns: {
      // Patrón para cuentas
      account: {
        icon: 'fas fa-file-invoice',
        format: (account) => `${account.code} - ${account.name}`
      },
      
      // Patrón para asientos
      journalEntry: {
        icon: 'fas fa-book',
        format: (entry) => `Asiento ${entry.entry_number}`
      },
      
      // Patrón para reportes
      report: {
        icon: 'fas fa-chart-bar',
        format: (report) => report.name || report.type
      },
      
      // Patrón para filtros
      filter: {
        icon: 'fas fa-filter',
        format: (filter) => `${filter.type}: ${filter.value}`
      }
    }
  },

  // Configuración de estilos
  styles: {
    // Colores por defecto del sistema
    colors: {
      primary: '#165c6a',
      secondary: '#bb8945',
      success: '#1cc88a',
      danger: '#e74a3b',
      warning: '#f6c23e',
      info: '#36b9cc',
      light: '#f8f9fc',
      dark: '#0f3d47',
      accent: '#bb8945',
      primaryLight: '#2a7a8a',
      primaryDark: '#0f3d47'
    },
    
    // Tamaños
    sizes: {
      small: '0.75rem',
      normal: '0.875rem',
      large: '1rem'
    },
    
    // Espaciado
    spacing: {
      padding: '0.75rem 1rem',
      margin: '0 0 1rem 0'
    }
  },

  // Configuración de accesibilidad
  accessibility: {
    // Texto alternativo para iconos
    iconAltText: {
      'fas fa-home': 'Inicio',
      'fas fa-building': 'Empresas',
      'fas fa-list-alt': 'Plan de Cuentas',
      'fas fa-book': 'Diario Contable',
      'fas fa-table': 'Mayor General',
      'fas fa-user': 'Perfil',
      'fas fa-cog': 'Configuración'
    },
    
    // Etiquetas ARIA
    ariaLabels: {
      breadcrumb: 'Navegación de migas de pan',
      backButton: 'Página anterior',
      forwardButton: 'Página siguiente',
      historyButton: 'Historial de navegación'
    }
  },

  // Configuración de internacionalización
  i18n: {
    // Textos por defecto
    texts: {
      home: 'Inicio',
      back: 'Atrás',
      forward: 'Adelante',
      history: 'Historial',
      noHistory: 'No hay historial de navegación',
      loading: 'Cargando...'
    },
    
    // Idiomas soportados
    languages: ['es', 'en'],
    
    // Idioma por defecto
    defaultLanguage: 'es'
  }
}

// Funciones de utilidad para la configuración
export const breadcrumbUtils = {
  // Obtener configuración de ruta
  getRouteConfig(path) {
    return breadcrumbConfig.routes[path] || {
      title: path.split('/').pop() || 'Página',
      icon: breadcrumbConfig.general.defaultIcon,
      description: ''
    }
  },

  // Obtener patrón de breadcrumb dinámico
  getDynamicPattern(type) {
    return breadcrumbConfig.dynamic.patterns[type] || {
      icon: breadcrumbConfig.general.defaultIcon,
      format: (item) => item.name || item.label || 'Elemento'
    }
  },

  // Formatear breadcrumb dinámico
  formatDynamicBreadcrumb(type, data) {
    const pattern = breadcrumbUtils.getDynamicPattern(type)
    return {
      label: pattern.format(data),
      icon: pattern.icon,
      active: true
    }
  },

  // Validar configuración
  validateConfig() {
    const errors = []
    
    // Validar configuración general
    if (!breadcrumbConfig.general.enabled) {
      errors.push('Breadcrumbs están deshabilitados')
    }
    
    if (breadcrumbConfig.general.maxDynamicBreadcrumbs < 1) {
      errors.push('maxDynamicBreadcrumbs debe ser mayor a 0')
    }
    
    // Validar rutas
    Object.keys(breadcrumbConfig.routes).forEach(route => {
      const config = breadcrumbConfig.routes[route]
      if (!config.title) {
        errors.push(`Ruta ${route} no tiene título`)
      }
    })
    
    return errors
  },

  // Obtener configuración para un componente específico
  getComponentConfig(componentType) {
    const baseConfig = {
      general: breadcrumbConfig.general,
      styles: breadcrumbConfig.styles,
      accessibility: breadcrumbConfig.accessibility,
      i18n: breadcrumbConfig.i18n
    }
    
    switch (componentType) {
      case 'basic':
        return baseConfig
      
      case 'advanced':
        return {
          ...baseConfig,
          history: {
            enabled: true,
            maxSize: breadcrumbConfig.general.maxHistorySize,
            persist: breadcrumbConfig.general.persistHistory
          }
        }
      
      case 'custom':
        return {
          ...baseConfig,
          custom: {
            variants: ['primary', 'success', 'warning', 'danger', 'info', 'dark'],
            defaultVariant: 'primary'
          }
        }
      
      default:
        return baseConfig
    }
  }
}

// Exportar configuración por defecto
export default breadcrumbConfig
