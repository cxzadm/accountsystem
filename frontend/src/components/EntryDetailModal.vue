<template>
  <div class="modal fade" :id="modalId" tabindex="-1" @click="onBackdropClick">
    <div class="modal-dialog modal-xl" @click.stop>
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Detalle del Asiento: {{ entry?.entry_number }}</h5>
          <div class="d-flex align-items-center gap-2">
            <button type="button" class="btn btn-sm btn-outline-primary" @click="onPrint">
              <i class="fas fa-print me-1"></i> Imprimir
            </button>
            <button type="button" class="btn-close" @click="hide"></button>
          </div>
        </div>
        <div class="modal-body">
          <div v-if="entry" class="mb-3">
            <div class="row">
              <div class="col-md-3"><strong>Fecha:</strong> {{ formatDate(entry.date) }}</div>
              <div class="col-md-3"><strong>Tipo:</strong> {{ entry.entry_type }}</div>
              <div class="col-md-3"><strong>Responsable:</strong> {{ entry.responsable || 'Sin responsable' }}</div>
              <div class="col-md-3"><strong>Estado:</strong> 
                <span :class="`badge bg-${getStatusColor(entry.status)}`">
                  {{ entry.status }}
                </span>
              </div>
            </div>
            <div class="row mt-2">
              <div class="col-12"><strong>Descripción:</strong> {{ entry.description }}</div>
            </div>
          </div>
          <div v-if="entry" class="table-responsive">
            <table class="table table-sm table-striped table-bordered">
              <thead>
                <tr>
                  <th>Cuenta</th>
                  <th>Nombre</th>
                  <th>Descripción</th>
                  <th>Débito</th>
                  <th>Crédito</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="line in entry.lines" :key="line.id || line.account_code">
                  <td>
                    <a href="#" @click.prevent="$emit('open-account-ledger', line.account_code)" title="Ver Mayor de la cuenta">
                      <code>{{ line.account_code }}</code>
                    </a>
                  </td>
                  <td>{{ line.account_name }}</td>
                  <td>{{ line.description || '-' }}</td>
                  <td class="text-end">
                    <span v-if="(line.debit || line.debit_amount || 0) > 0" class="text-danger fw-bold">
                      {{ formatCurrency(line.debit || line.debit_amount || 0) }}
                    </span>
                    <span v-else class="text-muted">-</span>
                  </td>
                  <td class="text-end">
                    <span v-if="(line.credit || line.credit_amount || 0) > 0" class="text-success fw-bold">
                      {{ formatCurrency(line.credit || line.credit_amount || 0) }}
                    </span>
                    <span v-else class="text-muted">-</span>
                  </td>
                </tr>
              </tbody>
              <tfoot>
                <tr class="table-dark">
                  <th colspan="3" class="text-end">TOTALES:</th>
                  <th class="text-end text-danger">
                    {{ formatCurrency(totalDebit) }}
                  </th>
                  <th class="text-end text-success">
                    {{ formatCurrency(totalCredit) }}
                  </th>
                </tr>
                <tr>
                  <th colspan="3" class="text-end">DIFERENCIA:</th>
                  <th colspan="2" class="text-end">
                    <span :class="['badge', totalDebit - totalCredit === 0 ? 'bg-success' : 'bg-danger']">
                      {{ formatCurrency(totalDebit - totalCredit) }}
                    </span>
                  </th>
                </tr>
              </tfoot>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { computed, onMounted, onBeforeUnmount } from 'vue'
import { printElement } from '@/services/print'

export default {
  name: 'EntryDetailModal',
  emits: ['open-account-ledger'],
  props: {
    modalId: { type: String, default: 'entryDetailModal' },
    entry: { type: Object, default: null }
  },
  setup(props) {
    const show = () => {
      const el = document.getElementById(props.modalId)
      if (!el) return
      if (window.bootstrap && window.bootstrap.Modal) {
        const modal = new window.bootstrap.Modal(el)
        modal.show()
      } else {
        el.classList.add('show')
        el.style.display = 'block'
        el.setAttribute('aria-hidden', 'false')
        document.body.classList.add('modal-open')
        const backdrop = document.createElement('div')
        backdrop.className = 'modal-backdrop fade show'
        backdrop.id = `${props.modalId}-backdrop`
        document.body.appendChild(backdrop)
      }
    }

    const hide = () => {
      const el = document.getElementById(props.modalId)
      if (!el) return
      if (window.bootstrap && window.bootstrap.Modal) {
        const instance = window.bootstrap.Modal.getInstance(el)
        if (instance) instance.hide()
      } else {
        el.classList.remove('show')
        el.style.display = 'none'
        el.setAttribute('aria-hidden', 'true')
        document.body.classList.remove('modal-open')
        const backdrop = document.getElementById(`${props.modalId}-backdrop`)
        if (backdrop) backdrop.remove()
      }
    }

    const onBackdropClick = (e) => {
      if (e.target && e.target.id === props.modalId) hide()
    }

    const totalDebit = computed(() => {
      if (!props.entry?.lines) return 0
      return props.entry.lines.reduce((s, l) => s + (l.debit || l.debit_amount || 0), 0)
    })
    const totalCredit = computed(() => {
      if (!props.entry?.lines) return 0
      return props.entry.lines.reduce((s, l) => s + (l.credit || l.credit_amount || 0), 0)
    })

    const onPrint = () => {
      printElement(`#${props.modalId} .modal-content`, `Asiento ${props.entry?.entry_number}`)
    }

    const formatDate = (date) => {
      if (!date) return 'N/A'
      return new Intl.DateTimeFormat('es-EC', { year: 'numeric', month: 'short', day: 'numeric' }).format(new Date(date))
    }

    const formatCurrency = (amount) => {
      return new Intl.NumberFormat('es-EC', { style: 'currency', currency: 'USD' }).format(amount)
    }

    const getStatusColor = (status) => {
      const colors = {
        draft: 'secondary',
        posted: 'success',
        reversed: 'warning'
      }
      return colors[status] || 'secondary'
    }

    onMounted(() => {})
    onBeforeUnmount(() => {})

    return { show, hide, onBackdropClick, onPrint, totalDebit, totalCredit, formatDate, formatCurrency, getStatusColor }
  }
}
</script>

<style scoped>
.modal-xl { max-width: 90%; }
.table th { font-weight: 600; }
code { background-color: #f8f9fa; padding: 0.2rem 0.4rem; border-radius: 0.25rem; font-size: 0.875em; }
</style>


