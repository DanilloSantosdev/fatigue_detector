<template>
  <div>
    <v-row class="mb-4">
      <v-col cols="12">
        <h1 class="text-h4 font-weight-bold mb-2">
          <v-icon size="large" class="mr-2">mdi-file-document</v-icon>
          Geração de Relatórios
        </h1>
        <p class="text-subtitle-1 text-grey">
          Exporte relatórios de alertas em PDF ou Excel
        </p>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12" md="8">
        <v-card>
          <v-card-title>
            <v-icon class="mr-2">mdi-cog</v-icon>
            Configuração do Relatório
          </v-card-title>

          <v-card-text>
            <v-form ref="form">
              <!-- Período -->
              <v-row>
                <v-col cols="12">
                  <h3 class="mb-3">Período</h3>
                </v-col>
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="reportConfig.date_from"
                    label="Data Inicial"
                    type="datetime-local"
                    density="comfortable"
                    clearable
                  ></v-text-field>
                </v-col>
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="reportConfig.date_to"
                    label="Data Final"
                    type="datetime-local"
                    density="comfortable"
                    clearable
                  ></v-text-field>
                </v-col>
              </v-row>

              <v-divider class="my-4"></v-divider>

              <!-- Filtros -->
              <v-row>
                <v-col cols="12">
                  <h3 class="mb-3">Filtros</h3>
                </v-col>
                <v-col cols="12">
                  <v-select
                    v-model="reportConfig.vehicle_id"
                    :items="vehicles"
                    item-title="nome"
                    item-value="id"
                    label="Veículo (Opcional)"
                    hint="Deixe em branco para todos os veículos"
                    persistent-hint
                    clearable
                    density="comfortable"
                  >
                    <template v-slot:selection="{ item }">
                      {{ item.title }} ({{ item.raw.placa }})
                    </template>
                    <template v-slot:item="{ props, item }">
                      <v-list-item v-bind="props">
                        <template v-slot:title>
                          {{ item.title }}
                        </template>
                        <template v-slot:subtitle>
                          Placa: {{ item.raw.placa }}
                        </template>
                      </v-list-item>
                    </template>
                  </v-select>
                </v-col>
              </v-row>

              <v-divider class="my-4"></v-divider>

              <!-- Opções -->
              <v-row>
                <v-col cols="12">
                  <h3 class="mb-3">Opções</h3>
                </v-col>
                <v-col cols="12">
                  <v-checkbox
                    v-model="reportConfig.include_images"
                    label="Incluir imagens dos alertas (apenas PDF)"
                    hint="Imagens aumentam significativamente o tamanho do arquivo"
                    persistent-hint
                    density="comfortable"
                  ></v-checkbox>
                </v-col>
              </v-row>

              <v-divider class="my-4"></v-divider>

              <!-- Botões de exportação -->
              <v-row>
                <v-col cols="12">
                  <h3 class="mb-3">Formato de Exportação</h3>
                </v-col>
                <v-col cols="12" md="6">
                  <v-btn
                    color="error"
                    size="large"
                    block
                    :loading="exportingPdf"
                    @click="exportReport('pdf')"
                  >
                    <v-icon start>mdi-file-pdf-box</v-icon>
                    Exportar PDF
                  </v-btn>
                </v-col>
                <v-col cols="12" md="6">
                  <v-btn
                    color="success"
                    size="large"
                    block
                    :loading="exportingExcel"
                    @click="exportReport('excel')"
                  >
                    <v-icon start>mdi-file-excel</v-icon>
                    Exportar Excel
                  </v-btn>
                </v-col>
              </v-row>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Informações -->
      <v-col cols="12" md="4">
        <v-card color="info" dark class="mb-4">
          <v-card-title>
            <v-icon class="mr-2">mdi-information</v-icon>
            Informações
          </v-card-title>
          <v-card-text>
            <p><strong>PDF:</strong> Formato ideal para impressão e compartilhamento. Pode incluir imagens.</p>
            <p class="mt-2"><strong>Excel:</strong> Formato ideal para análise de dados. Não inclui imagens.</p>
          </v-card-text>
        </v-card>

        <v-card>
          <v-card-title>
            <v-icon class="mr-2">mdi-chart-bar</v-icon>
            Prévia de Dados
          </v-card-title>
          <v-card-text>
            <v-list dense>
              <v-list-item>
                <v-list-item-title class="font-weight-bold">Total de Veículos</v-list-item-title>
                <v-list-item-subtitle>{{ vehicles.length }}</v-list-item-subtitle>
              </v-list-item>
              <v-list-item>
                <v-list-item-title class="font-weight-bold">Total de Alertas</v-list-item-title>
                <v-list-item-subtitle>{{ totalAlerts }}</v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Snackbar para mensagens -->
    <v-snackbar v-model="snackbar" :color="snackbarColor" :timeout="3000">
      {{ snackbarText }}
      <template v-slot:actions>
        <v-btn variant="text" @click="snackbar = false">
          Fechar
        </v-btn>
      </template>
    </v-snackbar>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { reportsAPI, vehiclesAPI, alertsAPI } from '../services/api'

const vehicles = ref([])
const totalAlerts = ref(0)
const exportingPdf = ref(false)
const exportingExcel = ref(false)
const snackbar = ref(false)
const snackbarText = ref('')
const snackbarColor = ref('success')

const reportConfig = ref({
  date_from: null,
  date_to: null,
  vehicle_id: null,
  include_images: false,
})

const loadVehicles = async () => {
  try {
    const response = await vehiclesAPI.list()
    vehicles.value = response.data
  } catch (error) {
    console.error('Erro ao carregar veículos:', error)
    showSnackbar('Erro ao carregar veículos', 'error')
  }
}

const loadStats = async () => {
  try {
    const response = await alertsAPI.stats()
    totalAlerts.value = response.data.total_alerts
  } catch (error) {
    console.error('Erro ao carregar estatísticas:', error)
  }
}

const exportReport = async (format) => {
  const loadingRef = format === 'pdf' ? exportingPdf : exportingExcel
  loadingRef.value = true

  try {
    // Preparar parâmetros
    const params = {
      format,
      include_images: reportConfig.value.include_images,
    }

    if (reportConfig.value.date_from) {
      params.date_from = new Date(reportConfig.value.date_from).toISOString()
    }

    if (reportConfig.value.date_to) {
      params.date_to = new Date(reportConfig.value.date_to).toISOString()
    }

    if (reportConfig.value.vehicle_id) {
      params.vehicle_id = reportConfig.value.vehicle_id
    }

    // Fazer requisição
    const response = await reportsAPI.export(params)

    // Criar download
    const blob = new Blob([response.data], {
      type: format === 'pdf' ? 'application/pdf' : 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    })
    
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    
    const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-')
    link.download = `relatorio_fadiga_${timestamp}.${format === 'pdf' ? 'pdf' : 'xlsx'}`
    
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)

    showSnackbar(`Relatório ${format.toUpperCase()} exportado com sucesso!`, 'success')
  } catch (error) {
    console.error('Erro ao exportar relatório:', error)
    showSnackbar('Erro ao exportar relatório. Verifique se há alertas no período selecionado.', 'error')
  } finally {
    loadingRef.value = false
  }
}

const showSnackbar = (text, color = 'success') => {
  snackbarText.value = text
  snackbarColor.value = color
  snackbar.value = true
}

onMounted(() => {
  loadVehicles()
  loadStats()
})
</script>

