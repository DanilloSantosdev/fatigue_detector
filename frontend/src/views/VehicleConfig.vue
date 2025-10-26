<template>
  <div>
    <v-row class="mb-4">
      <v-col cols="12">
        <h1 class="text-h4 font-weight-bold mb-2">
          <v-icon size="large" class="mr-2">mdi-car-cog</v-icon>
          Configuração de Veículos
        </h1>
        <p class="text-subtitle-1 text-grey">
          Gerencie os veículos cadastrados no sistema
        </p>
      </v-col>
    </v-row>

    <v-row>
      <!-- Formulário de cadastro -->
      <v-col cols="12" md="4">
        <v-card>
          <v-card-title>
            <v-icon class="mr-2">{{ editingVehicle ? 'mdi-pencil' : 'mdi-plus' }}</v-icon>
            {{ editingVehicle ? 'Editar Veículo' : 'Novo Veículo' }}
          </v-card-title>

          <v-card-text>
            <v-form ref="form" @submit.prevent="saveVehicle">
              <v-text-field
                v-model="vehicleForm.nome"
                label="Nome/Descrição *"
                :rules="[v => !!v || 'Campo obrigatório']"
                required
                density="comfortable"
              ></v-text-field>

              <v-text-field
                v-model="vehicleForm.placa"
                label="Placa *"
                :rules="[v => !!v || 'Campo obrigatório']"
                required
                density="comfortable"
              ></v-text-field>

              <v-text-field
                v-model="vehicleForm.motorista"
                label="Motorista"
                density="comfortable"
              ></v-text-field>

              <v-text-field
                v-model="vehicleForm.frota"
                label="Frota"
                density="comfortable"
              ></v-text-field>

              <v-text-field
                v-model="vehicleForm.rota"
                label="Rota/Linha"
                density="comfortable"
              ></v-text-field>

              <v-divider class="my-4"></v-divider>

              <v-btn
                type="submit"
                color="primary"
                block
                :loading="saving"
              >
                <v-icon start>{{ editingVehicle ? 'mdi-content-save' : 'mdi-plus' }}</v-icon>
                {{ editingVehicle ? 'Salvar Alterações' : 'Cadastrar Veículo' }}
              </v-btn>

              <v-btn
                v-if="editingVehicle"
                color="grey"
                block
                class="mt-2"
                @click="cancelEdit"
              >
                <v-icon start>mdi-close</v-icon>
                Cancelar
              </v-btn>
            </v-form>
          </v-card-text>
        </v-card>

        <v-alert type="info" variant="tonal" class="mt-4">
          <strong>Dica:</strong> Após cadastrar o veículo, copie o ID dele para configurar no Raspberry Pi.
        </v-alert>
      </v-col>

      <!-- Lista de veículos -->
      <v-col cols="12" md="8">
        <v-card>
          <v-card-title>
            <v-icon class="mr-2">mdi-format-list-bulleted</v-icon>
            Veículos Cadastrados
            <v-spacer></v-spacer>
            <v-btn icon @click="loadVehicles" :loading="loading">
              <v-icon>mdi-refresh</v-icon>
            </v-btn>
          </v-card-title>

          <v-card-text>
            <v-list v-if="vehicles.length > 0">
              <v-list-item
                v-for="vehicle in vehicles"
                :key="vehicle.id"
                class="mb-2"
                border
                rounded
              >
                <template v-slot:prepend>
                  <v-avatar color="primary">
                    <v-icon>mdi-car</v-icon>
                  </v-avatar>
                </template>

                <v-list-item-title class="font-weight-bold">
                  {{ vehicle.nome }}
                </v-list-item-title>
                
                <v-list-item-subtitle>
                  <v-chip size="small" class="mr-2">{{ vehicle.placa }}</v-chip>
                  <span v-if="vehicle.motorista">Motorista: {{ vehicle.motorista }}</span>
                </v-list-item-subtitle>

                <v-list-item-subtitle class="mt-2">
                  <v-chip size="x-small" variant="outlined">
                    ID: {{ vehicle.id }}
                  </v-chip>
                  <v-btn
                    icon
                    size="x-small"
                    variant="text"
                    @click="copyVehicleId(vehicle.id)"
                  >
                    <v-icon size="small">mdi-content-copy</v-icon>
                  </v-btn>
                </v-list-item-subtitle>

                <template v-slot:append>
                  <v-btn
                    icon
                    size="small"
                    @click="editVehicle(vehicle)"
                  >
                    <v-icon>mdi-pencil</v-icon>
                  </v-btn>
                  <v-btn
                    icon
                    size="small"
                    color="error"
                    @click="confirmDelete(vehicle)"
                  >
                    <v-icon>mdi-delete</v-icon>
                  </v-btn>
                </template>
              </v-list-item>
            </v-list>

            <v-alert v-else type="info" variant="tonal">
              Nenhum veículo cadastrado. Cadastre o primeiro veículo ao lado.
            </v-alert>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Dialog de confirmação de exclusão -->
    <v-dialog v-model="deleteDialog" max-width="400">
      <v-card>
        <v-card-title class="text-h6">
          Confirmar Exclusão
        </v-card-title>
        <v-card-text>
          Tem certeza que deseja excluir o veículo <strong>{{ vehicleToDelete?.nome }}</strong>?
          Esta ação não pode ser desfeita.
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="deleteDialog = false">Cancelar</v-btn>
          <v-btn color="error" text @click="deleteVehicle" :loading="deleting">
            Excluir
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Snackbar -->
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
import { vehiclesAPI } from '../services/api'

const form = ref(null)
const loading = ref(false)
const saving = ref(false)
const deleting = ref(false)
const vehicles = ref([])
const editingVehicle = ref(null)
const vehicleToDelete = ref(null)
const deleteDialog = ref(false)
const snackbar = ref(false)
const snackbarText = ref('')
const snackbarColor = ref('success')

const vehicleForm = ref({
  nome: '',
  placa: '',
  motorista: '',
  frota: '',
  rota: '',
})

const loadVehicles = async () => {
  loading.value = true
  try {
    const response = await vehiclesAPI.list()
    vehicles.value = response.data
  } catch (error) {
    console.error('Erro ao carregar veículos:', error)
    showSnackbar('Erro ao carregar veículos', 'error')
  } finally {
    loading.value = false
  }
}

const saveVehicle = async () => {
  const { valid } = await form.value.validate()
  if (!valid) return

  saving.value = true
  try {
    if (editingVehicle.value) {
      // Atualizar
      await vehiclesAPI.update(editingVehicle.value.id, vehicleForm.value)
      showSnackbar('Veículo atualizado com sucesso!', 'success')
    } else {
      // Criar novo
      await vehiclesAPI.create(vehicleForm.value)
      showSnackbar('Veículo cadastrado com sucesso!', 'success')
    }
    
    resetForm()
    loadVehicles()
  } catch (error) {
    console.error('Erro ao salvar veículo:', error)
    const message = error.response?.data?.detail || 'Erro ao salvar veículo'
    showSnackbar(message, 'error')
  } finally {
    saving.value = false
  }
}

const editVehicle = (vehicle) => {
  editingVehicle.value = vehicle
  vehicleForm.value = { ...vehicle }
}

const cancelEdit = () => {
  editingVehicle.value = null
  resetForm()
}

const confirmDelete = (vehicle) => {
  vehicleToDelete.value = vehicle
  deleteDialog.value = true
}

const deleteVehicle = async () => {
  deleting.value = true
  try {
    await vehiclesAPI.delete(vehicleToDelete.value.id)
    showSnackbar('Veículo excluído com sucesso!', 'success')
    deleteDialog.value = false
    loadVehicles()
  } catch (error) {
    console.error('Erro ao excluir veículo:', error)
    showSnackbar('Erro ao excluir veículo', 'error')
  } finally {
    deleting.value = false
  }
}

const copyVehicleId = async (id) => {
  try {
    await navigator.clipboard.writeText(id)
    showSnackbar('ID copiado para a área de transferência!', 'success')
  } catch (error) {
    console.error('Erro ao copiar ID:', error)
    showSnackbar('Erro ao copiar ID', 'error')
  }
}

const resetForm = () => {
  vehicleForm.value = {
    nome: '',
    placa: '',
    motorista: '',
    frota: '',
    rota: '',
  }
  form.value?.reset()
}

const showSnackbar = (text, color = 'success') => {
  snackbarText.value = text
  snackbarColor.value = color
  snackbar.value = true
}

onMounted(() => {
  loadVehicles()
})
</script>

