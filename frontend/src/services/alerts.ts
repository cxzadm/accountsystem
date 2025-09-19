import Swal, { SweetAlertIcon } from 'sweetalert2'

type ConfirmOptions = {
  title: string
  text?: string
  confirmButtonText?: string
  cancelButtonText?: string
  icon?: SweetAlertIcon
}

export async function confirm(options: ConfirmOptions): Promise<boolean> {
  const {
    title,
    text = '',
    confirmButtonText = 'Sí',
    cancelButtonText = 'Cancelar',
    icon = 'question'
  } = options

  const result = await Swal.fire({
    title,
    text,
    icon,
    showCancelButton: true,
    confirmButtonText,
    cancelButtonText,
    reverseButtons: true,
    focusCancel: true
  })

  return result.isConfirmed === true
}

export async function alert(
  title: string,
  text = '',
  icon: SweetAlertIcon = 'info'
) {
  await Swal.fire({ title, text, icon })
}

export const alerts = {
  confirm,
  info: (title: string, text = '') => alert(title, text, 'info'),
  success: (title: string, text = '') => alert(title, text, 'success'),
  error: (title: string, text = '') => alert(title, text, 'error'),
  warning: (title: string, text = '') => alert(title, text, 'warning')
}



