<template>
  <div>
    <v-row class="mb-4">
      <v-col cols="12">
        <h1 class="text-h4 font-weight-bold mb-2">
          <v-icon size="large" class="mr-2">mdi-view-dashboard</v-icon>
          Dashboard de Alertas
        </h1>
      </v-col>
    </v-row>

    <!-- Estatísticas -->
    <v-row>
      <v-col cols="12" sm="6" md="3">
        <v-card color="primary" dark>
          <v-card-text>
            <div class="text-h6">Total de Alertas</div>
            <div class="text-h3 font-weight-bold">{{ stats.total_alerts || 0 }}</div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card color="error" dark>
          <v-card-text>
            <div class="text-h6">Olhos Fechados</div>
            <div class="text-h3 font-weight-bold">{{ stats.eyes_closed_count || 0 }}</div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card color="warning" dark>
          <v-card-text>
            <div class="text-h6">Bocejos</div>
            <div class="text-h3 font-weight-bold">{{ stats.yawning_count || 0 }}</div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card color="error" dark>
          <v-card-text>
            <div class="text-h6">Críticos</div>
            <div class="text-h3 font-weight-bold">{{ stats.critical_count || 0 }}</div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Filtros -->
    <v-row class="mt-4">
      <v-col cols="12">
        <v-card>
          <v-card-title>
            <v-icon class="mr-2">mdi-filter</v-icon>
            Filtros
          </v-card-title>
          <v-card-text>
            <v-row>
              <v-col cols="12" md="3">
                <v-select
                  v-model="filters.vehicle_id"
                  :items="vehicles"
                  item-title="nome"
                  item-value="id"
                  label="Veículo"
                  clearable
                  density="comfortable"
                ></v-select>
              </v-col>

              <v-col cols="12" md="3">
                <v-select
                  v-model="filters.tipo"
                  :items="tipoOptions"
                  label="Tipo"
                  clearable
                  density="comfortable"
                ></v-select>
              </v-col>

              <v-col cols="12" md="3">
                <v-select
                  v-model="filters.severity"
                  :items="severityOptions"
                  label="Severidade"
                  clearable
                  density="comfortable"
                ></v-select>
              </v-col>

              <v-col cols="12" md="3" class="d-flex align-center">
                <v-btn color="primary" @click="loadAlerts" block>
                  <v-icon start>mdi-magnify</v-icon>
                  Buscar
                </v-btn>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Tabela de alertas -->
    <v-row class="mt-4">
      <v-col cols="12">
        <v-card>
          <v-card-title>
            <v-icon class="mr-2">mdi-format-list-bulleted</v-icon>
            Alertas Recentes
            <v-spacer></v-spacer>
            <v-btn icon @click="loadAlerts" :loading="loading">
              <v-icon>mdi-refresh</v-icon>
            </v-btn>
          </v-card-title>

          <v-card-text>
            <v-data-table
              :headers="headers"
              :items="alerts"
              :loading="loading"
              :items-per-page="itemsPerPage"
              @click:row="openAlertDetail"
              class="elevation-1"
              hover
            >
              <template v-slot:item.timestamp="{ item }">
                {{ formatDateTime(item.timestamp) }}
              </template>

              <template v-slot:item.vehicle="{ item }">
                <div>
                  <div class="font-weight-bold">{{ item.vehicle?.nome }}</div>
                  <div class="text-caption">{{ item.vehicle?.placa }}</div>
                </div>
              </template>

              <template v-slot:item.tipo="{ item }">
                <v-chip :color="getTypeColor(item.tipo)" size="small">
                  {{ getTypeLabel(item.tipo) }}
                </v-chip>
              </template>

              <template v-slot:item.severity="{ item }">
                <v-chip :color="getSeverityColor(item.severity)" size="small">
                  {{ getSeverityLabel(item.severity) }}
                </v-chip>
              </template>

              <template v-slot:item.ear_value="{ item }">
                {{ item.ear_value.toFixed(3) }}
              </template>

              <template v-slot:item.mar_value="{ item }">
                {{ item.mar_value.toFixed(3) }}
              </template>

              <template v-slot:item.actions="{ item }">
                <v-btn icon size="small" @click.stop="openAlertDetail(item)">
                  <v-icon>mdi-eye</v-icon>
                </v-btn>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Dialog de detalhes do alerta -->
    <AlertDetail v-model="showDetail" :alert="selectedAlert" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { alertsAPI, vehiclesAPI } from '../services/api'
import AlertDetail from '../components/AlertDetail.vue'

const loading = ref(false)
const alerts = ref([])
const vehicles = ref([])
const stats = ref({})
const selectedAlert = ref(null)
const showDetail = ref(false)
const itemsPerPage = ref(10)

const filters = ref({
  vehicle_id: null,
  tipo: null,
  severity: null,
})

const tipoOptions = [
  { title: 'Olhos Fechados', value: 'eyes_closed' },
  { title: 'Bocejo', value: 'yawning' },
]

const severityOptions = [
  { title: 'Crítico', value: 'critical' },
  { title: 'Moderado', value: 'moderate' },
]

const headers = [
  { title: 'Data/Hora', key: 'timestamp', sortable: true },
  { title: 'Veículo', key: 'vehicle', sortable: false },
  { title: 'Tipo', key: 'tipo', sortable: true },
  { title: 'Severidade', key: 'severity', sortable: true },
  { title: 'EAR', key: 'ear_value', sortable: true },
  { title: 'MAR', key: 'mar_value', sortable: true },
  { title: 'Ações', key: 'actions', sortable: false },
]

const loadAlerts = async () => {
  loading.value = true
  try {
    const params = {
      page: 1,
      page_size: 50,
      ...filters.value,
    }
    
    // Remover valores nulos
    Object.keys(params).forEach(key => {
      if (params[key] === null || params[key] === undefined) {
        delete params[key]
      }
    })
    
    console.log('🔍 Parâmetros da requisição:', params)
    const response = await alertsAPI.list(params)
    console.log('📊 Resposta da API:', response.data)
    console.log('📊 Total de alertas:', response.data.total)
    console.log('📊 Items recebidos:', response.data.items)
    console.log('📊 Quantidade de items:', response.data.items?.length || 0)
    alerts.value = response.data.items || []
  } catch (error) {
    console.error('Erro ao carregar alertas:', error)
  } finally {
    loading.value = false
  }
}

const loadStats = async () => {
  try {
    const response = await alertsAPI.stats()
    stats.value = response.data
  } catch (error) {
    console.error('Erro ao carregar estatísticas:', error)
  }
}

const loadVehicles = async () => {
  try {
    const response = await vehiclesAPI.list()
    vehicles.value = response.data
  } catch (error) {
    console.error('Erro ao carregar veículos:', error)
  }
}

const openAlertDetail = (item) => {
  selectedAlert.value = item
  showDetail.value = true
}

const formatDateTime = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleString('pt-BR')
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

onMounted(() => {
  loadAlerts()
  loadStats()
  loadVehicles()
})
</script>

