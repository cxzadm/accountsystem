<template>
  <div v-if="show" class="modal fade show d-block" tabindex="-1" style="background-color: rgba(0,0,0,0.5);">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">{{ isEditing ? 'Editar Cuenta' : 'Nueva Cuenta Contable' }}</h5>
          <button type="button" class="btn-close" @click="closeModal"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="saveAccount">
            <div class="row">
              <!-- Código Padre (Opcional) -->
              <div class="col-md-6 mb-3">
                <label for="parent_code" class="form-label">Código Padre (Opcional)</label>
                <select
                  class="form-select"
                  id="parent_code"
                  v-model="formData.parent_code"
                  :class="{ 'is-invalid': errors.parent_code }"
                  @change="onParentCodeChange"
                >
                  <option value="">Seleccionar cuenta padre</option>
                  <option value="__manual__">Escribir manualmente (sin padre)</option>
                  <option 
                    v-for="account in allAccounts" 
                    :key="account.id" 
                    :value="account.code"
                  >
                    {{ account.code }} - {{ account.name }}
                  </option>
                </select>
                <div v-if="errors.parent_code" class="invalid-feedback">{{ errors.parent_code }}</div>
                <small class="form-text text-muted">Seleccione una cuenta padre para autogenerar el código, o elija "Escribir manualmente" para ingresar el código manualmente.</small>
              </div>

              <!-- Código Sugerido -->
              <div class="col-md-6 mb-3">
                <label for="code" class="form-label">Código Sugerido <span class="text-danger">*</span></label>
                <input
                  type="text"
                  class="form-control"
                  id="code"
                  v-model="formData.code"
                  :class="{ 'is-invalid': errors.code }"
                  :placeholder="isEditing ? 'Código de la cuenta' : 'Se genera automáticamente'"
                  @input="onCodeInput"
                >
                <div v-if="errors.code" class="invalid-feedback">{{ errors.code }}</div>
                <small class="form-text text-muted">
                  Puede editar el código. Si selecciona un padre, se sugerirá el siguiente correlativo disponible.
                </small>
              </div>

              <!-- Nombre de la Cuenta -->
              <div class="col-md-12 mb-3">
                <label for="name" class="form-label">Cuenta <span class="text-danger">*</span></label>
                <input
                  type="text"
                  class="form-control"
                  id="name"
                  v-model="formData.name"
                  :class="{ 'is-invalid': errors.name }"
                  placeholder="Nombre de la cuenta"
                >
                <div v-if="errors.name" class="invalid-feedback">{{ errors.name }}</div>
              </div>

              <!-- Tipo de Cuenta -->
              <div class="col-md-6 mb-3">
                <label for="account_type" class="form-label">Tipo <span class="text-danger">*</span></label>
                <select
                  class="form-select"
                  id="account_type"
                  v-model="formData.account_type"
                  :class="{ 'is-invalid': errors.account_type }"
                >
                  <option value="">Seleccionar tipo</option>
                  <option value="activo">Activo</option>
                  <option value="pasivo">Pasivo</option>
                  <option value="patrimonio">Patrimonio</option>
                  <option value="ingresos">Ingresos</option>
                  <option value="gastos">Gastos</option>
                  <option value="costos">Costos</option>
                </select>
                <div v-if="errors.account_type" class="invalid-feedback">{{ errors.account_type }}</div>
              </div>

              <!-- Naturaleza -->
              <div class="col-md-6 mb-3">
                <label for="nature" class="form-label">Naturaleza <span class="text-danger">*</span></label>
                <select
                  class="form-select"
                  id="nature"
                  v-model="formData.nature"
                  :class="{ 'is-invalid': errors.nature }"
                >
                  <option value="">Seleccionar naturaleza</option>
                  <option value="deudora">Deudora</option>
                  <option value="acreedora">Acreedora</option>
                </select>
                <div v-if="errors.nature" class="invalid-feedback">{{ errors.nature }}</div>
              </div>

              <!-- Saldo Débito -->
              <div class="col-md-6 mb-3">
                <label for="initial_debit_balance" class="form-label">Saldo Débito</label>
                <input
                  type="number"
                  class="form-control"
                  id="initial_debit_balance"
                  v-model="formData.initial_debit_balance"
                  :class="{ 'is-invalid': errors.initial_debit_balance }"
                  step="0.01"
                  min="0"
                  placeholder="0.00"
                >
                <div v-if="errors.initial_debit_balance" class="invalid-feedback">{{ errors.initial_debit_balance }}</div>
              </div>

              <!-- Saldo Crédito -->
              <div class="col-md-6 mb-3">
                <label for="initial_credit_balance" class="form-label">Saldo Crédito</label>
                <input
                  type="number"
                  class="form-control"
                  id="initial_credit_balance"
                  v-model="formData.initial_credit_balance"
                  :class="{ 'is-invalid': errors.initial_credit_balance }"
                  step="0.01"
                  min="0"
                  placeholder="0.00"
                >
                <div v-if="errors.initial_credit_balance" class="invalid-feedback">{{ errors.initial_credit_balance }}</div>
              </div>
            </div>
          </form>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="closeModal">Cancelar</button>
          <button type="button" class="btn btn-primary" @click="saveAccount" :disabled="saving">
            <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
            {{ isEditing ? 'Actualizar' : 'Crear' }} Cuenta
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, watch, computed } from 'vue'
import { alerts } from '@/services/alerts'

export default {
  name: 'AccountFormModal',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    account: {
      type: Object,
      default: null
    },
    companyId: {
      type: String,
      required: true
    },
    allAccounts: {
      type: Array,
      default: () => []
    },
    onSave: {
      type: Function,
      required: true
    }
  },
  emits: ['close'],
  setup(props, { emit }) {
    const saving = ref(false)
    const userEditedCode = ref(false)
    
    const formData = reactive({
      code: '',
      name: '',
      account_type: '',
      nature: '',
      parent_code: '',
      initial_debit_balance: 0,
      initial_credit_balance: 0,
      description: '',
      is_editable: true
    })

    const errors = reactive({})

    const isEditing = computed(() => !!props.account)

    // Limpiar errores
    const clearErrors = () => {
      Object.keys(errors).forEach(key => {
        delete errors[key]
      })
    }

    // Resetear formulario
    const resetForm = () => {
      Object.assign(formData, {
        code: '',
        name: '',
        account_type: '',
        nature: '',
        parent_code: '',
        initial_debit_balance: 0,
        initial_credit_balance: 0,
        description: '',
        is_editable: true
      })
      userEditedCode.value = false
      clearErrors()
    }

    // Cargar datos de cuenta para edición
    const loadAccountData = () => {
      if (props.account) {
        Object.assign(formData, {
          code: props.account.code || '',
          name: props.account.name || '',
          account_type: props.account.account_type || '',
          nature: props.account.nature || '',
          parent_code: props.account.parent_code || '',
          initial_debit_balance: props.account.initial_debit_balance || 0,
          initial_credit_balance: props.account.initial_credit_balance || 0,
          description: props.account.description || '',
          is_editable: props.account.is_editable !== false
        })
        userEditedCode.value = false
      }
    }


    // Validar formulario
    const validateForm = () => {
      clearErrors()
      let isValid = true

      if (!formData.code.trim()) {
        errors.code = 'El código es requerido'
        isValid = false
      }

      if (!formData.name.trim()) {
        errors.name = 'El nombre es requerido'
        isValid = false
      }

      if (!formData.account_type) {
        errors.account_type = 'El tipo es requerido'
        isValid = false
      }

      if (!formData.nature) {
        errors.nature = 'La naturaleza es requerida'
        isValid = false
      }

      // Validar que el código no exista (solo para nuevas cuentas)
      if (!isEditing.value) {
        const existingAccount = props.allAccounts.find(acc => acc.code === formData.code)
        if (existingAccount) {
          errors.code = 'Ya existe una cuenta con este código'
          isValid = false
        }
      }

      return isValid
    }

    // Guardar cuenta
    const saveAccount = async () => {
      if (!validateForm()) {
        return
      }

      saving.value = true
      try {
        const isManual = formData.parent_code === '__manual__'
        const payload = {
          ...formData,
          parent_code: isManual ? '' : formData.parent_code
        }
        await props.onSave(payload)
        alerts.success('Éxito', `Cuenta ${isEditing.value ? 'actualizada' : 'creada'} correctamente`)
        closeModal()
      } catch (error) {
        console.error('Error saving account:', error)
        alerts.error('Error', `Error al ${isEditing.value ? 'actualizar' : 'crear'} la cuenta`)
      } finally {
        saving.value = false
      }
    }

    // Cerrar modal
    const closeModal = () => {
      resetForm()
      emit('close')
    }

    // Cambio en código - ya no es necesario porque el código se genera automáticamente
    const onCodeInput = () => {
      userEditedCode.value = true
    }

    // Cambio en código padre
    const onParentCodeChange = () => {
      userEditedCode.value = false
      if (formData.parent_code === '__manual__') {
        // Modo manual: no autogenerar ni forzar tipo/naturaleza
        return
      }
      generateSuggestedCode()
      updateTypeAndNatureFromParent()
    }

    // Generar código sugerido basado en el padre
    const generateSuggestedCode = () => {
      if (formData.parent_code === '__manual__' || userEditedCode.value) {
        return
      }
      if (!formData.parent_code) {
        // Si no hay padre, sugerir código basado en tipo
        const typeCodes = {
          'activo': '1',
          'pasivo': '2',
          'patrimonio': '3',
          'ingresos': '4',
          'gastos': '5',
          'costos': '6'
        }
        formData.code = typeCodes[formData.account_type] || '1'
        return
      }

      // Buscar el padre seleccionado
      const parentAccount = props.allAccounts.find(acc => acc.code === formData.parent_code)
      if (!parentAccount) {
        formData.code = formData.parent_code + '01'
        return
      }

      // Obtener todos los hijos del padre
      const children = props.allAccounts.filter(acc => 
        acc.parent_code === formData.parent_code && 
        acc.code.startsWith(formData.parent_code) &&
        acc.code !== formData.parent_code
      )

      if (children.length === 0) {
        // Primer hijo
        formData.code = formData.parent_code + '01'
      } else {
        // Encontrar el siguiente número disponible
        const parentCodeLength = formData.parent_code.length
        const childNumbers = children
          .map(child => {
            const childSuffix = child.code.substring(parentCodeLength)
            return parseInt(childSuffix) || 0
          })
          .sort((a, b) => a - b)

        let nextNumber = 1
        for (const num of childNumbers) {
          if (num === nextNumber) {
            nextNumber++
          } else {
            break
          }
        }

        // Formatear con ceros a la izquierda (2 dígitos)
        formData.code = formData.parent_code + nextNumber.toString().padStart(2, '0')
      }
    }

    // Actualizar tipo y naturaleza basado en el padre
    const updateTypeAndNatureFromParent = () => {
      if (!formData.parent_code || formData.parent_code === '__manual__') {
        return
      }

      const parentAccount = props.allAccounts.find(acc => acc.code === formData.parent_code)
      if (parentAccount) {
        // Si no se ha seleccionado tipo, usar el del padre
        if (!formData.account_type) {
          formData.account_type = parentAccount.account_type
        }
        // Si no se ha seleccionado naturaleza, usar la del padre
        if (!formData.nature) {
          formData.nature = parentAccount.nature
        }
      }
    }

    // Watchers
    watch(() => props.show, (newVal) => {
      if (newVal) {
        loadAccountData()
      }
    })

    watch(() => props.account, () => {
      if (props.show) {
        loadAccountData()
      }
    })

    // Generar código cuando cambie el tipo de cuenta (si no hay padre)
    watch(() => formData.account_type, () => {
      if (!formData.parent_code || formData.parent_code === '__manual__') {
        generateSuggestedCode()
      }
    })

    return {
      formData,
      errors,
      saving,
      isEditing,
      saveAccount,
      closeModal,
      onCodeInput,
      onParentCodeChange
    }
  }
}
</script>

<style scoped>
.list-group-item {
  cursor: pointer;
}

.list-group-item:hover {
  background-color: #f8f9fa;
}

.modal.show {
  display: block !important;
}
</style>
