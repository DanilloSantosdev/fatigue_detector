<template>
  <v-dialog v-model="dialog" max-width="800px">
    <v-card v-if="alert">
      <v-card-title class="d-flex align-center">
        <v-icon :color="getSeverityColor(alert.severity)" class="mr-2">
          {{ getSeverityIcon(alert.severity) }}
        </v-icon>
        <span>Detalhes do Alerta</span>
        <v-spacer></v-spacer>
        <v-btn icon @click="dialog = false">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>

      <v-divider></v-divider>

      <v-card-text>
        <v-row>
          <v-col cols="12" md="6">
            <v-list dense>
              <v-list-item>
                <v-list-item-title class="font-weight-bold">Data/Hora</v-list-item-title>
                <v-list-item-subtitle>{{ formatDateTime(alert.timestamp) }}</v-list-item-subtitle>
              </v-list-item>

              <v-list-item>
                <v-list-item-title class="font-weight-bold">Veículo</v-list-item-title>
                <v-list-item-subtitle>{{ alert.vehicle?.nome || 'N/A' }}</v-list-item-subtitle>
              </v-list-item>

              <v-list-item>
                <v-list-item-title class="font-weight-bold">Placa</v-list-item-title>
                <v-list-item-subtitle>{{ alert.vehicle?.placa || 'N/A' }}</v-list-item-subtitle>
              </v-list-item>

              <v-list-item>
                <v-list-item-title class="font-weight-bold">Motorista</v-list-item-title>
                <v-list-item-subtitle>{{ alert.vehicle?.motorista || 'N/A' }}</v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-col>

          <v-col cols="12" md="6">
            <v-list dense>
              <v-list-item>
                <v-list-item-title class="font-weight-bold">Tipo</v-list-item-title>
                <v-list-item-subtitle>
                  <v-chip :color="getTypeColor(alert.tipo)" size="small">
                    {{ getTypeLabel(alert.tipo) }}
                  </v-chip>
                </v-list-item-subtitle>
              </v-list-item>

              <v-list-item>
                <v-list-item-title class="font-weight-bold">Severidade</v-list-item-title>
                <v-list-item-subtitle>
                  <v-chip :color="getSeverityColor(alert.severity)" size="small">
                    {{ getSeverityLabel(alert.severity) }}
                  </v-chip>
                </v-list-item-subtitle>
              </v-list-item>

              <v-list-item>
                <v-list-item-title class="font-weight-bold">EAR</v-list-item-title>
                <v-list-item-subtitle>{{ alert.ear_value.toFixed(3) }}</v-list-item-subtitle>
              </v-list-item>

              <v-list-item>
                <v-list-item-title class="font-weight-bold">MAR</v-list-item-title>
                <v-list-item-subtitle>{{ alert.mar_value.toFixed(3) }}</v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-col>
        </v-row>

        <v-divider class="my-4"></v-divider>

        <!-- Imagem do alerta -->
        <div v-if="alert.image_path" class="text-center">
          <h3 class="mb-3">Captura do Momento</h3>
          <v-img
            :src="getImageUrl(alert.image_path)"
            :alt="`Alerta ${alert.id}`"
            max-height="400"
            contain
            class="rounded"
          ></v-img>
        </div>
        <div v-else class="text-center text-grey">
          <v-icon size="64" color="grey-lighten-1">mdi-image-off</v-icon>
          <p>Imagem não disponível</p>
        </div>
      </v-card-text>

      <v-divider></v-divider>

      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="primary" variant="text" @click="dialog = false">
          Fechar
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  modelValue: Boolean,
  alert: Object
})

const emit = defineEmits(['update:modelValue'])

const dialog = ref(props.modelValue)

watch(() => props.modelValue, (val) => {
  dialog.value = val
})

watch(dialog, (val) => {
  emit('update:modelValue', val)
})

const formatDateTime = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleString('pt-BR')
}

const getImageUrl = (path) => {
  return path // O proxy do Vite vai redirecionar para o backend
}

const getTypeLabel = (tipo) => {
  const labels = {
    'eyes_closed': 'Olhos Fechados',
    'yawning': 'Bocejo'
  }
  return labels[tipo] || tipo
}

const getTypeColor = (tipo) => {
  const colors = {
    'eyes_closed': 'error',
    'yawning': 'warning'
  }
  return colors[tipo] || 'grey'
}

const getSeverityLabel = (severity) => {
  const labels = {
    'critical': 'Crítico',
    'moderate': 'Moderado'
  }
  return labels[severity] || severity
}

const getSeverityColor = (severity) => {
  const colors = {
    'critical': 'error',
    'moderate': 'warning'
  }
  return colors[severity] || 'grey'
}

const getSeverityIcon = (severity) => {
  const icons = {
    'critical': 'mdi-alert-circle',
    'moderate': 'mdi-alert'
  }
  return icons[severity] || 'mdi-information'
}
</script>

